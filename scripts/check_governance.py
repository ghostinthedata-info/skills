#!/usr/bin/env python3
"""Governance checks for the ghost-skills pack.

Enforces the rules in CLAUDE.md so the skills tree, the README catalogue and
the plugin manifest can't drift apart again (GitHub issue #1):

  buckets      every folder under skills/ is a known bucket; every known
               bucket exists and is named in CLAUDE.md and CONTEXT.md
  frontmatter  every SKILL.md has a name and a description; the name matches
               its folder (Agent Skills spec) and is unique in the repo
  manifest     .claude-plugin/plugin.json lists exactly the published skills,
               and every path in it exists
  catalogue    README.md links each published skill's name to its SKILL.md,
               and lists no drafts
  links        every relative Markdown link resolves, with exact case
  paths        a backticked file name inside a skill matches a real file
  references   a soft reference to another skill names a published skill
  reachable    every file in a published skill is reachable from SKILL.md

Usage:
  python3 scripts/check_governance.py [--root DIR]
  python3 scripts/check_governance.py --claude-report report.json

The second form also checks the JSON report of
`claude plugin validate --json .` and fails unless Claude Code's loader
provides exactly the published skills.

Exits 1 if any check fails. Problems inside draft skills (skills/in-progress/)
are reported as warnings, so they surface before a draft is promoted.
Standard library only; runs on Python 3.8+.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# --- Configuration -----------------------------------------------------------

# Buckets whose skills ship in the pack (README + plugin.json), and buckets
# that hold drafts (in neither). Adding a bucket means updating CLAUDE.md and
# CONTEXT.md too; the "buckets" check enforces that.
PUBLISHED_BUCKETS = ("data-engineering", "management", "productivity", "setup")
DRAFT_BUCKETS = ("in-progress",)

# Skills that were renamed, merged or removed. A backticked mention of one is
# a stale reference. When you retire or rename a skill, add it here with where
# its content went (None = removed outright).
RETIRED_SKILLS = {
    "conformed-dimensions": "data-modelling (DIMENSIONS.md)",
    "data-as-a-product": None,
    "data-vault": None,
    "dimensional-modeling": "data-modelling (DIMENSIONS.md)",
    "fact-table-design": "data-modelling (FACT-TABLES.md)",
    "incident-comms": "data-incident-management",
    "keys": "data-modelling (KEYS.md)",
    "master-data-management": None,
    "metadata-and-lineage": None,
    "pipeline-design": "solution-design",
    "refine-context": "gather-requirements",
    "slowly-changing-dimensions": "data-modelling (SCD-TYPES.md)",
    "spark-performance": "performance-tuning (SPARK.md)",
}

# Skills from other packs that ours may name, e.g. "use the `docx` skill".
EXTERNAL_SKILLS = {"docx"}

PLUGIN_JSON = ".claude-plugin/plugin.json"
MARKETPLACE_JSON = ".claude-plugin/marketplace.json"
MAX_NAME = 64
MAX_DESCRIPTION = 1024

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
LIST_ITEM_RE = re.compile(r"^\s*(?:[*+-]|\d+[.)])\s+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
CATALOGUE_TARGET_RE = re.compile(r"^(?:\./)?skills/([^/]+)/([^/]+)/SKILL\.md$")
# A backticked token, optionally bold: `name` or **`name`**
TOKEN_RE = re.compile(r"\*{0,2}`([^`\n]+)`\*{0,2}")
SKILL_WORD_NEAR_RE = (
    re.compile(r"\*{0,2}`([a-z0-9-]+)`\*{0,2}\s+skills?\b"),  # `x` skill
    re.compile(r"\bskills?\s*\(\s*\*{0,2}`([a-z0-9-]+)`"),     # skill (`x`)
)
FILE_TOKEN_RE = re.compile(r"^[A-Za-z0-9_./-]+\.[A-Za-z0-9]+$")
# The pack's soft-reference idiom: "(see `x` if installed)", "if `x` is not
# installed". Plain "installed" is too loose ("one installed from another pack").
SOFT_REF_RE = re.compile(r"\b(?:if|is|isn't|are|aren't|not)\s+installed\b", re.I)


# --- Reporting ---------------------------------------------------------------

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add(self, check, where, message, draft=False):
        (self.warnings if draft else self.errors).append((check, where, message))

    def print(self, out=sys.stdout):
        for label, items in (("error", self.errors), ("warning", self.warnings)):
            for check, where, message in items:
                out.write(f"{label}: [{check}] {where}: {message}\n")
        out.write(
            f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s)\n"
        )


# --- Repo model --------------------------------------------------------------

class Skill:
    def __init__(self, bucket, folder, published, meta, meta_error):
        self.bucket = bucket
        self.folder = folder                    # Path to the skill folder
        self.dir_name = folder.name
        self.published = published
        self.meta = meta or {}
        self.meta_error = meta_error

    @property
    def name(self):
        return self.meta.get("name")

    @property
    def rel_skill_md(self):
        return f"skills/{self.bucket}/{self.dir_name}/SKILL.md"

    @property
    def plugin_path(self):
        return f"./skills/{self.bucket}/{self.dir_name}"


def parse_frontmatter(text):
    """Return (meta, error) for a SKILL.md.

    Handles what skills use: `key: value`, quoted values, plain scalars that
    continue on indented lines, and `>` / `|` block scalars.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "no YAML frontmatter (the first line must be ---)"
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, "frontmatter is never closed with ---"
    meta, i = {}, 1
    while i < end:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
        i += 1
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        block = []
        while i < end and (lines[i][:1] in (" ", "\t") or not lines[i].strip()):
            block.append(lines[i].strip())
            i += 1
        if value[:1] in (">", "|"):
            joiner = " " if value.startswith(">") else "\n"
            value = joiner.join(b for b in block if b)
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            value = " ".join([value] + [b for b in block if b]).strip()
        meta[key] = value
    return meta, None


def load_skills(root, report):
    """Discover skills and check the bucket layout."""
    skills_dir = root / "skills"
    skills = []
    if not skills_dir.is_dir():
        report.add("buckets", "skills/", "no skills/ folder")
        return skills
    known = set(PUBLISHED_BUCKETS) | set(DRAFT_BUCKETS)
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_file():
            report.add("buckets", rel(root, entry),
                       "stray file at the top of skills/ (skills live in skills/<bucket>/<name>/)")
        elif entry.name not in known:
            report.add("buckets", rel(root, entry) + "/",
                       f"unknown bucket — known buckets are {sorted(known)}; "
                       "add it to PUBLISHED_BUCKETS or DRAFT_BUCKETS (and CLAUDE.md)")
    for bucket in PUBLISHED_BUCKETS + DRAFT_BUCKETS:
        bucket_dir = skills_dir / bucket
        published = bucket in PUBLISHED_BUCKETS
        if not bucket_dir.is_dir():
            if published:
                report.add("buckets", f"skills/{bucket}/",
                           "configured published bucket is missing — remove it from "
                           "PUBLISHED_BUCKETS (and CLAUDE.md) or restore it")
            continue
        for folder in sorted(p for p in bucket_dir.iterdir() if p.is_dir()):
            skill_md = folder / "SKILL.md"
            if not skill_md.is_file():
                report.add("buckets", rel(root, folder) + "/",
                           "folder in a bucket has no SKILL.md", draft=not published)
                continue
            meta, error = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            skills.append(Skill(bucket, folder, published, meta, error))
        for stray in sorted(p for p in bucket_dir.iterdir() if p.is_file()):
            report.add("buckets", rel(root, stray),
                       "stray file in a bucket (skills live in skills/<bucket>/<name>/)",
                       draft=not published)
    for path in sorted(skills_dir.rglob("SKILL.md")):
        depth = len(path.relative_to(skills_dir).parts)
        if depth != 3:
            report.add("buckets", rel(root, path),
                       "SKILL.md at the wrong depth (expected skills/<bucket>/<name>/SKILL.md)")
    return skills


def rel(root, path):
    return Path(os.path.relpath(path, root)).as_posix()


# --- Markdown helpers --------------------------------------------------------

def prose_lines(text):
    """Yield (line_no, line) outside fenced code blocks, inline code blanked."""
    fence = None
    for no, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield no, line


def blank_code_spans(line):
    return CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)


def prose_units(text):
    """Group prose into paragraphs/list items: [(first_line_no, text, heading)].

    The heading is the nearest heading above the unit, so callers can treat a
    "Related skills" list differently from body text.
    """
    units, current, start, heading = [], [], None, ""
    previous_no = None

    def flush():
        if current:
            units.append((start, " ".join(current), heading))

    for no, line in prose_lines(text):
        h = HEADING_RE.match(line)
        breaks = (not line.strip() or h or LIST_ITEM_RE.match(line)
                  or (previous_no is not None and no != previous_no + 1))
        if breaks:
            flush()
            current, start = [], None
        if h:
            heading = h.group(1)
        elif line.strip():
            if start is None:
                start = no
            current.append(line.strip())
        previous_no = no
    flush()
    return units


def exists_exact(root, path):
    """True if `path` exists under `root` with exactly this case."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    here = root
    for part in parts:
        if part in ("", "."):
            continue
        if part == "..":
            here = here.parent
            continue
        try:
            if part not in os.listdir(here):
                return False
        except (NotADirectoryError, FileNotFoundError):
            return False
        here = here / part
    return True


def markdown_files(root):
    ignored = {".git", "node_modules", ".scratch", ".agents"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in ignored)
        for f in sorted(filenames):
            if f.endswith(".md"):
                yield Path(dirpath) / f


def is_draft_file(root, path):
    parts = Path(rel(root, path)).parts
    return len(parts) > 1 and parts[0] == "skills" and parts[1] in DRAFT_BUCKETS


# --- Checks ------------------------------------------------------------------

def check_bucket_docs(root, report):
    for doc in ("CLAUDE.md", "CONTEXT.md"):
        path = root / doc
        if not path.is_file():
            report.add("buckets", doc, "missing (it documents the buckets)")
            continue
        text = path.read_text(encoding="utf-8")
        for bucket in PUBLISHED_BUCKETS + DRAFT_BUCKETS:
            if f"`{bucket}/`" not in text:
                report.add("buckets", doc,
                           f"doesn't describe the `{bucket}/` bucket (expected the text `{bucket}/`)")


def check_frontmatter(root, skills, report):
    seen = {}
    for s in skills:
        where = rel(root, s.folder / "SKILL.md")
        draft = not s.published
        if s.meta_error:
            report.add("frontmatter", where, s.meta_error, draft)
            continue
        name, description = s.meta.get("name"), s.meta.get("description")
        if not name:
            report.add("frontmatter", where, "missing `name`", draft)
        else:
            if name != s.dir_name:
                report.add("frontmatter", where,
                           f"name `{name}` doesn't match its folder `{s.dir_name}/` "
                           "(the Agent Skills spec requires them to match)", draft)
            if not NAME_RE.match(name) or len(name) > MAX_NAME:
                report.add("frontmatter", where,
                           f"name `{name}` must be 1-{MAX_NAME} chars of a-z, 0-9 and "
                           "single hyphens", draft)
            if name in RETIRED_SKILLS:
                report.add("frontmatter", where,
                           f"name `{name}` is listed in RETIRED_SKILLS — pick another "
                           "name or un-retire it", draft)
        if not description:
            report.add("frontmatter", where, "missing `description`", draft)
        elif len(description) > MAX_DESCRIPTION:
            report.add("frontmatter", where,
                       f"description is {len(description)} chars (max {MAX_DESCRIPTION})",
                       draft)
        if name:
            if name in seen:
                report.add("frontmatter", where,
                           f"name `{name}` is also used by {seen[name]}")
            else:
                seen[name] = where


def load_json(root, relpath, report, check):
    path = root / relpath
    if not path.is_file():
        report.add(check, relpath, "missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        report.add(check, relpath, f"invalid JSON: {e}")
        return None


def check_manifest(root, skills, report):
    plugin = load_json(root, PLUGIN_JSON, report, "manifest")
    if plugin is None:
        return None
    entries = plugin.get("skills")
    if not isinstance(entries, list):
        report.add("manifest", PLUGIN_JSON,
                   "needs a `skills` array — with skills nested in bucket folders, "
                   "Claude Code discovers none of them on its own")
        return plugin
    by_path = {s.plugin_path: s for s in skills}
    published = {s.plugin_path for s in skills if s.published}
    listed = set()
    for i, entry in enumerate(entries):
        where = f"{PLUGIN_JSON} skills[{i}]"
        if not isinstance(entry, str):
            report.add("manifest", where, "entry is not a string")
            continue
        normalized = entry.rstrip("/")
        if not normalized.startswith("./"):
            report.add("manifest", where, f"`{entry}` must start with ./")
            normalized = "./" + normalized.lstrip("./")
        if normalized in listed:
            report.add("manifest", where, f"`{entry}` is listed twice")
        listed.add(normalized)
        target = root / normalized[2:]
        if not (exists_exact(root, target / "SKILL.md")):
            report.add("manifest", where,
                       f"`{entry}` has no SKILL.md — the loader will report a load failure")
        elif normalized in by_path and not by_path[normalized].published:
            report.add("manifest", where,
                       f"`{entry}` is a draft — drafts must not be in plugin.json")
    for path in sorted(published - listed):
        report.add("manifest", PLUGIN_JSON,
                   f"published skill `{path}` is missing from the `skills` array")

    market = load_json(root, MARKETPLACE_JSON, report, "manifest")
    if market is not None:
        names = [p.get("name") for p in market.get("plugins", []) if isinstance(p, dict)]
        if plugin.get("name") not in names:
            report.add("manifest", MARKETPLACE_JSON,
                       f"lists no plugin named `{plugin.get('name')}` (plugin.json's name)")
    return plugin


def check_catalogue(root, skills, report):
    readme = root / "README.md"
    if not readme.is_file():
        report.add("catalogue", "README.md", "missing")
        return
    links = {}
    for no, line in prose_lines(readme.read_text(encoding="utf-8")):
        for m in LINK_RE.finditer(blank_code_spans(line)):
            target = m.group(2).split("#", 1)[0]
            if CATALOGUE_TARGET_RE.match(target):
                links.setdefault(target.lstrip("./") if target.startswith("./") else target,
                                 []).append((no, m.group(1)))
    for s in skills:
        found = links.get(s.rel_skill_md, [])
        if s.published and not found:
            report.add("catalogue", "README.md",
                       f"published skill `{s.dir_name}` isn't linked — add "
                       f"[{s.dir_name}]({s.rel_skill_md})")
        if not s.published and found:
            for no, _ in found:
                report.add("catalogue", f"README.md:{no}",
                           f"lists draft skill `{s.dir_name}` — drafts must not be catalogued")
        for no, text in found:
            shown = text.replace("*", "").replace("`", "").strip()
            if s.published and shown != s.dir_name:
                report.add("catalogue", f"README.md:{no}",
                           f"link text `{shown}` should be the skill name `{s.dir_name}`")


def check_links(root, report):
    for path in markdown_files(root):
        draft = is_draft_file(root, path)
        text = path.read_text(encoding="utf-8")
        for no, line in prose_lines(text):
            for m in LINK_RE.finditer(blank_code_spans(line)):
                target = m.group(2)
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                    continue                    # URL, mailto:, or in-page anchor
                clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not clean:
                    continue
                base = root if clean.startswith("/") else path.parent
                resolved = Path(os.path.normpath(base / clean.lstrip("/")))
                where = f"{rel(root, path)}:{no}"
                if not str(resolved).startswith(str(root)):
                    report.add("links", where, f"`{target}` points outside the repo", draft)
                elif not exists_exact(root, resolved):
                    hint = case_hint(resolved)
                    report.add("links", where, f"broken link `{target}`{hint}", draft)


def case_hint(resolved):
    parent = resolved.parent
    if parent.is_dir():
        for name in os.listdir(parent):
            if name.lower() == resolved.name.lower():
                return f" (the file is `{name}` — names are case-sensitive)"
    return ""


def check_paths_and_reachability(root, skills, report):
    """Backticked file names must match real files; every file must be reachable."""
    for s in skills:
        files = sorted(p for p in s.folder.rglob("*") if p.is_file())
        rel_files = {p.relative_to(s.folder).as_posix(): p for p in files}
        lower = {k.lower(): k for k in rel_files}
        basenames = {}
        for k in rel_files:
            basenames.setdefault(Path(k).name.lower(), k)
        subdirs = {p.name for p in s.folder.iterdir() if p.is_dir()}
        mentions = {}                          # file in skill -> files it mentions
        for k, p in rel_files.items():
            if p.suffix != ".md":
                continue
            found = set()
            for no, line in prose_lines(p.read_text(encoding="utf-8")):
                for m in LINK_RE.finditer(blank_code_spans(line)):
                    target = unquote(m.group(2).split("#", 1)[0])
                    joined = os.path.normpath((Path(k).parent / target).as_posix())
                    if joined in rel_files:
                        found.add(joined)
                for m in TOKEN_RE.finditer(line):
                    token = m.group(1).strip()
                    if not FILE_TOKEN_RE.match(token) or token.startswith(("/", "~")):
                        continue
                    if token in rel_files:
                        found.add(token)
                        continue
                    sibling = os.path.normpath((Path(k).parent / token).as_posix())
                    if sibling in rel_files:
                        found.add(sibling)
                        continue
                    # Only judge tokens that point inside the skill: a bare file
                    # name, ./x, references/x, or a sub-folder the skill has.
                    # Paths like docs/agents/domain.md name files in the
                    # *consumer's* repo and may share a name with a seed template.
                    head = token.split("/", 1)[0] if "/" in token else None
                    internal = (head is None or head in (".", "references")
                                or (s.folder / head).is_dir()
                                or any(d.lower() == head.lower() for d in subdirs))
                    if not internal:
                        continue
                    real = lower.get(token.lower()) or basenames.get(Path(token).name.lower())
                    if real and real != token:
                        report.add("paths", f"{rel(root, p)}:{no}",
                                   f"`{token}` doesn't exist here — did you mean `{real}`?",
                                   draft=not s.published)
            mentions[k] = found
        seen, todo = {"SKILL.md"}, ["SKILL.md"]
        while todo:
            for nxt in mentions.get(todo.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        for k in sorted(set(rel_files) - seen):
            report.add("reachable", rel(root, rel_files[k]),
                       "not linked or named from SKILL.md (directly or via another "
                       "reference file), so the agent will never load it",
                       draft=not s.published)


def check_references(root, skills, report):
    published = {s.dir_name for s in skills if s.published}
    drafts = {s.dir_name for s in skills if not s.published}
    files = [root / "README.md", root / "CLAUDE.md", root / "CONTEXT.md"]
    for s in skills:
        files.extend(sorted(s.folder.rglob("*.md")))

    def judge(name, where, draft, soft, strong=False):
        """soft: the token sits in a soft-reference context ("if installed",
        a Related-skills list). strong: it's right next to the word "skill",
        so even a one-word name is clearly meant as a skill."""
        if name in RETIRED_SKILLS:
            new = RETIRED_SKILLS[name]
            hint = f"its content is now in {new}" if new else "it was removed"
            report.add("references", where, f"`{name}` is a retired skill — {hint}", draft)
        elif not soft or name in published or name in EXTERNAL_SKILLS:
            return
        elif name in drafts:
            if not draft:                    # drafts may lean on each other
                report.add("references", where,
                           f"`{name}` is a draft in skills/in-progress/ — published "
                           "skills can't rely on it (inline the rule, or promote it)")
        elif "-" in name or strong:
            # One-word tokens in an "if installed" paragraph are usually column
            # or field names (`id`, `classification`), so only flag those when
            # they're explicitly called a skill.
            report.add("references", where, f"`{name}` is not a skill in this pack", draft)

    for path in files:
        if not path.is_file():
            continue
        draft = is_draft_file(root, path)
        text = path.read_text(encoding="utf-8")
        if path.name == "SKILL.md":
            meta, _ = parse_frontmatter(text)
            for name in RETIRED_SKILLS:
                if "-" in name and re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])",
                                             (meta or {}).get("description", "")):
                    judge(name, f"{rel(root, path)} (description)", draft, soft=False)
        for no, unit, heading in prose_units(text):
            where = f"{rel(root, path)}:{no}"
            soft_context = (SOFT_REF_RE.search(unit)
                            or re.search(r"related skills", heading, re.I))
            names = set()
            for m in TOKEN_RE.finditer(unit):
                token = m.group(1).strip()
                if NAME_RE.match(token):
                    names.add(token)
            near = {m.group(1) for rx in SKILL_WORD_NEAR_RE for m in rx.finditer(unit)}
            for name in sorted(names):
                judge(name, where, draft, soft=bool(soft_context) or name in near,
                      strong=name in near)


def check_claude_report(path, skills, plugin, report):
    """Compare `claude plugin validate --json` output with the published set."""
    where = str(path)
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        report.add("claude", where, f"can't read the validator report: {e}")
        return
    if not data.get("success"):
        report.add("claude", where, "`claude plugin validate` reported errors")
    provided = (data.get("provides") or {}).get("skills")
    if provided is None:
        report.add("claude", where, "report has no provides.skills list")
        return
    prefix = f"{(plugin or {}).get('name', '')}:"
    got = {p[len(prefix):] if p.startswith(prefix) else p for p in provided}
    want = {s.dir_name for s in skills if s.published}
    for name in sorted(want - got):
        report.add("claude", where, f"Claude Code would not load published skill `{name}`")
    for name in sorted(got - want):
        report.add("claude", where, f"Claude Code would load `{name}`, which isn't published")


def run(root, claude_report=None):
    root = Path(root).resolve()
    report = Report()
    skills = load_skills(root, report)
    check_bucket_docs(root, report)
    check_frontmatter(root, skills, report)
    plugin = check_manifest(root, skills, report)
    check_catalogue(root, skills, report)
    check_links(root, report)
    check_paths_and_reachability(root, skills, report)
    check_references(root, skills, report)
    if claude_report:
        check_claude_report(claude_report, skills, plugin, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=Path(__file__).resolve().parent.parent,
                        help="repo root (default: this script's repo)")
    parser.add_argument("--claude-report", metavar="JSON",
                        help="output of `claude plugin validate --json .` to cross-check")
    args = parser.parse_args(argv)
    report = run(args.root, args.claude_report)
    report.print()
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
