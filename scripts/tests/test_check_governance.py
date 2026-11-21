"""Unit tests for scripts/check_governance.py.

Each test builds a small throwaway repo with one defect and asserts the
checker reports it — so the checker itself can't silently stop catching the
drift it exists to catch (GitHub issue #1).

Run: python3 -m unittest discover -s scripts/tests -v
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_governance as cg  # noqa: E402


def skill_md(name, description="Does a thing. Use when testing.", body="", extra=""):
    return f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# {name}\n\n{body}"


# How a draft hides itself from `npx skills add`.
INTERNAL = 'metadata:\n  internal: "true"\n'


class FixtureRepo:
    """A minimal valid repo: one skill per published bucket, one draft."""

    SKILLS = {
        ("data-engineering", "alpha"): "",
        ("management", "beta"): "",
        ("productivity", "gamma"): "",
        ("setup", "delta"): "",
        ("in-progress", "draft-one"): "",
    }

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="gov-test-"))
        for (bucket, name), body in self.SKILLS.items():
            extra = INTERNAL if bucket in cg.DRAFT_BUCKETS else ""
            self.write(f"skills/{bucket}/{name}/SKILL.md",
                       skill_md(name, body=body, extra=extra))
        buckets = "\n".join(f"* `{b}/`" for b in cg.PUBLISHED_BUCKETS + cg.DRAFT_BUCKETS)
        self.write("CLAUDE.md", f"# Governance\n\n{buckets}\n")
        self.write("CONTEXT.md", f"# Context\n\n{buckets}\n")
        published = [k for k in self.SKILLS if k[0] in cg.PUBLISHED_BUCKETS]
        self.write_plugin([f"./skills/{b}/{n}" for b, n in published])
        self.write(".claude-plugin/marketplace.json", json.dumps(
            {"name": "pack", "owner": {"name": "x"},
             "plugins": [{"name": "pack", "source": "./"}]}))
        self.write("README.md", "# Pack\n\n" + "\n".join(
            f"- **[{n}](skills/{b}/{n}/SKILL.md)** — {n}." for b, n in published) + "\n")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_plugin(self, skills, **extra):
        self.write(".claude-plugin/plugin.json",
                   json.dumps(dict({"name": "pack", "skills": skills}, **extra)))

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    def replace(self, rel, old, new):
        text = self.read(rel)
        assert old in text, f"{old!r} not in {rel}"
        self.write(rel, text.replace(old, new))

    def run(self, **kw):
        return cg.run(self.root, **kw)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class GovernanceTest(unittest.TestCase):
    def setUp(self):
        self.repo = FixtureRepo()
        self.addCleanup(self.repo.cleanup)

    # helpers --------------------------------------------------------------

    def messages(self, report, check=None, level="errors"):
        return [f"{w}: {m}" for c, w, m in getattr(report, level)
                if check is None or c == check]

    def assertClean(self, report):
        self.assertEqual(self.messages(report), [], "expected no errors")

    def assertFlags(self, report, check, *fragments, level="errors"):
        found = self.messages(report, check, level)
        for fragment in fragments:
            self.assertTrue(any(fragment in m for m in found),
                            f"no [{check}] {level[:-1]} containing {fragment!r}; got {found}")

    # the baseline ---------------------------------------------------------

    def test_fixture_is_clean(self):
        report = self.repo.run()
        self.assertClean(report)
        self.assertEqual(report.warnings, [])

    # issue #1: plugin.json drift -----------------------------------------

    def test_plugin_entry_with_no_skill_on_disk(self):
        self.repo.write_plugin(["./skills/data-engineering/alpha",
                                "./skills/data-engineering/keys",
                                "./skills/management/beta", "./skills/productivity/gamma",
                                "./skills/setup/delta"])
        self.assertFlags(self.repo.run(), "manifest", "`./skills/data-engineering/keys` has no SKILL.md")

    def test_published_skill_missing_from_plugin(self):
        self.repo.write_plugin(["./skills/data-engineering/alpha", "./skills/setup/delta",
                                "./skills/management/beta"])
        self.assertFlags(self.repo.run(), "manifest",
                         "`./skills/productivity/gamma` is missing from the `skills` array")

    def test_plugin_without_skills_array(self):
        self.repo.write(".claude-plugin/plugin.json", json.dumps({"name": "pack"}))
        self.assertFlags(self.repo.run(), "manifest", "needs a `skills` array")

    def test_draft_in_plugin(self):
        self.repo.write_plugin(["./skills/data-engineering/alpha", "./skills/management/beta",
                                "./skills/productivity/gamma", "./skills/setup/delta",
                                "./skills/in-progress/draft-one"])
        self.assertFlags(self.repo.run(), "manifest", "is a draft")

    def test_plugin_duplicate_and_bad_prefix(self):
        self.repo.write_plugin(["./skills/data-engineering/alpha", "./skills/data-engineering/alpha",
                                "skills/management/beta", "./skills/productivity/gamma",
                                "./skills/setup/delta"])
        self.assertFlags(self.repo.run(), "manifest", "listed twice", "must start with ./")

    def test_marketplace_must_list_the_plugin(self):
        self.repo.write(".claude-plugin/marketplace.json", json.dumps(
            {"name": "pack", "plugins": [{"name": "other", "source": "./"}]}))
        self.assertFlags(self.repo.run(), "manifest", "lists no plugin named `pack`")

    # issue #1: README catalogue drift -------------------------------------

    def test_readme_link_to_missing_skill(self):
        self.repo.replace("README.md", "](skills/management/beta/SKILL.md)",
                          "](skills/management/beta/SKILL.md)\n- **[old](skills/management/old/SKILL.md)** — gone.")
        self.assertFlags(self.repo.run(), "links", "broken link `skills/management/old/SKILL.md`")

    def test_published_skill_missing_from_readme(self):
        self.repo.replace("README.md", "- **[gamma](skills/productivity/gamma/SKILL.md)** — gamma.\n", "")
        self.assertFlags(self.repo.run(), "catalogue", "published skill `gamma` isn't linked")

    def test_readme_link_text_must_be_skill_name(self):
        self.repo.replace("README.md", "[gamma](", "[Gamma skill](")
        self.assertFlags(self.repo.run(), "catalogue", "should be the skill name `gamma`")

    def test_draft_in_readme(self):
        self.repo.replace("README.md", "# Pack\n",
                          "# Pack\n\n- [draft-one](skills/in-progress/draft-one/SKILL.md)\n")
        self.assertFlags(self.repo.run(), "catalogue", "lists draft skill `draft-one`")

    # buckets ----------------------------------------------------------------

    def test_unknown_bucket_is_an_error_not_skipped(self):
        # The old CI skipped buckets it didn't know, so renaming a bucket
        # silently switched the checks off.
        self.repo.write("skills/modeling/keys/SKILL.md", skill_md("keys"))
        self.assertFlags(self.repo.run(), "buckets", "unknown bucket")

    def test_configured_bucket_missing(self):
        shutil.rmtree(self.repo.root / "skills" / "management")
        self.repo.write_plugin(["./skills/data-engineering/alpha", "./skills/productivity/gamma",
                                "./skills/setup/delta"])
        self.repo.replace("README.md", "- **[beta](skills/management/beta/SKILL.md)** — beta.\n", "")
        self.assertFlags(self.repo.run(), "buckets", "configured published bucket is missing")

    def test_skill_folder_without_skill_md(self):
        self.repo.write("skills/data-engineering/empty/notes.md", "# notes\n")
        self.assertFlags(self.repo.run(), "buckets", "has no SKILL.md")

    def test_bucket_must_be_documented(self):
        self.repo.replace("CLAUDE.md", "* `management/`\n", "")
        self.assertFlags(self.repo.run(), "buckets", "doesn't describe the `management/` bucket")

    # frontmatter --------------------------------------------------------------

    def test_name_must_match_folder(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md", skill_md("alpha-renamed"))
        self.assertFlags(self.repo.run(), "frontmatter", "doesn't match its folder `alpha/`")

    def test_missing_description_and_bad_name(self):
        self.repo.write("skills/setup/delta/SKILL.md", "---\nname: Delta_Skill\n---\n# x\n")
        self.assertFlags(self.repo.run(), "frontmatter", "missing `description`", "must be 1-64 chars")

    def test_description_too_long(self):
        self.repo.write("skills/setup/delta/SKILL.md", skill_md("delta", "x" * 1100))
        self.assertFlags(self.repo.run(), "frontmatter", "description is 1100 chars")

    def test_folded_block_description_parses(self):
        self.repo.write("skills/setup/delta/SKILL.md",
                        "---\nname: delta\ndescription: >\n  Line one\n  line two.\n---\n# d\n")
        meta, err = cg.parse_frontmatter(self.repo.read("skills/setup/delta/SKILL.md"))
        self.assertIsNone(err)
        self.assertEqual(meta["description"], "Line one line two.")
        self.assertClean(self.repo.run())

    def test_duplicate_names_across_buckets(self):
        self.repo.write("skills/in-progress/alpha/SKILL.md", skill_md("alpha"))
        self.assertFlags(self.repo.run(), "frontmatter", "name `alpha` is also used by")

    def test_no_frontmatter(self):
        self.repo.write("skills/setup/delta/SKILL.md", "# Delta\n")
        self.assertFlags(self.repo.run(), "frontmatter", "no YAML frontmatter")

    # links ----------------------------------------------------------------------

    def test_case_mismatched_link(self):
        self.repo.write("skills/data-engineering/alpha/SCD2.md", "# SCD2\n")
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="See [scd2.md](./scd2.md)."))
        self.assertFlags(self.repo.run(), "links", "the file is `SCD2.md`")

    def test_link_to_missing_subfolder(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="Read [spark](./references/spark.md)."))
        self.assertFlags(self.repo.run(), "links", "broken link `./references/spark.md`")

    def test_links_in_code_are_ignored(self):
        body = ("Inline `[x](./nope.md)` is fine.\n\n```md\n[y](./also-nope.md)\n```\n"
                "And a [url](https://example.com) and an [anchor](#top).")
        self.repo.write("skills/data-engineering/alpha/SKILL.md", skill_md("alpha", body=body))
        self.assertClean(self.repo.run())

    def test_broken_link_in_draft_only_warns(self):
        self.repo.write("skills/in-progress/draft-one/SKILL.md",
                        skill_md("draft-one", body="[gone](./GONE.md)", extra=INTERNAL))
        report = self.repo.run()
        self.assertClean(report)
        self.assertFlags(report, "links", "broken link `./GONE.md`", level="warnings")

    # backticked paths and reachability --------------------------------------------

    def test_backticked_file_with_wrong_case_or_folder(self):
        self.repo.write("skills/data-engineering/alpha/PREVENTION.md", "# P\n")
        self.repo.write("skills/data-engineering/alpha/SKILL.md", skill_md(
            "alpha", body="See `references/prevention.md` and `prevention.md`."))
        self.assertFlags(self.repo.run(), "paths",
                         "`references/prevention.md` doesn't exist here",
                         "`prevention.md` doesn't exist here")

    def test_consumer_repo_paths_are_not_flagged(self):
        # docs/agents/domain.md names a file in the *user's* repo; the skill
        # ships a seed template with the same basename.
        self.repo.write("skills/setup/delta/domain.md", "# seed\n")
        self.repo.write("skills/setup/delta/SKILL.md", skill_md(
            "delta", body="Seed `docs/agents/domain.md` from [domain.md](./domain.md)."))
        self.assertClean(self.repo.run())

    def test_unreachable_reference_file(self):
        self.repo.write("skills/data-engineering/alpha/ORPHAN.md", "# never linked\n")
        self.assertFlags(self.repo.run(), "reachable", "ORPHAN.md")

    def test_reachable_transitively_and_by_backticks(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="Open `A.md` first."))
        self.repo.write("skills/data-engineering/alpha/A.md", "Then [B](./B.md).\n")
        self.repo.write("skills/data-engineering/alpha/B.md", "# B\n")
        self.assertClean(self.repo.run())

    # cross-skill references ------------------------------------------------------------

    def test_soft_reference_to_unknown_skill(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="Then model it (see `star-schemas` if installed)."))
        self.assertFlags(self.repo.run(), "references", "`star-schemas` is not a skill in this pack")

    def test_soft_reference_to_published_skill_is_fine(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="Profile first (see `gamma` if\ninstalled)."))
        self.assertClean(self.repo.run())

    def test_published_skill_relying_on_draft(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", body="See `draft-one` if installed."))
        self.assertFlags(self.repo.run(), "references", "`draft-one` is a draft")

    def test_drafts_may_reference_each_other(self):
        self.repo.write("skills/in-progress/draft-two/SKILL.md",
                        skill_md("draft-two", extra=INTERNAL))
        self.repo.write("skills/in-progress/draft-one/SKILL.md",
                        skill_md("draft-one", body="Pairs with `draft-two` if installed.",
                                 extra=INTERNAL))
        report = self.repo.run()
        self.assertClean(report)
        self.assertEqual(report.warnings, [])

    def test_retired_skill_anywhere_in_backticks(self):
        # No "if installed" here: retired names are caught regardless.
        self.repo.write("skills/setup/delta/SKILL.md",
                        skill_md("delta", body="The producer skill (`refine-context`) writes it."))
        self.assertFlags(self.repo.run(), "references",
                         "`refine-context` is a retired skill — its content is now in gather-requirements")

    def test_retired_skill_in_description(self):
        self.repo.write("skills/setup/delta/SKILL.md",
                        skill_md("delta", "Run before dimensional-modeling. Use when setting up."))
        self.assertFlags(self.repo.run(), "references", "(description): `dimensional-modeling`")

    def test_related_skills_list_is_checked(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md", skill_md(
            "alpha", body="## Related skills\n\n* `gamma` — fine.\n* `ghost-skill` — not real.\n"))
        report = self.repo.run()
        self.assertFlags(report, "references", "`ghost-skill` is not a skill in this pack")
        self.assertFalse(any("`gamma`" in m for m in self.messages(report, "references")))

    def test_column_names_near_installed_are_not_skills(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md", skill_md(
            "alpha", body="Every column has a `classification` (see `gamma` if installed)."))
        self.assertClean(self.repo.run())

    def test_named_external_skill_is_allowed(self):
        self.repo.write("skills/management/beta/SKILL.md",
                        skill_md("beta", body="Use the `docx` skill to convert."))
        self.assertClean(self.repo.run())

    # what `npx skills add` offers --------------------------------------------

    def test_draft_must_be_hidden_from_the_installer(self):
        self.repo.write("skills/in-progress/draft-one/SKILL.md", skill_md("draft-one"))
        self.assertFlags(self.repo.run(), "installer", "draft isn't marked internal")

    def test_published_skill_must_not_be_hidden(self):
        self.repo.write("skills/data-engineering/alpha/SKILL.md",
                        skill_md("alpha", extra=INTERNAL))
        self.assertFlags(self.repo.run(), "installer", "published skill is marked")

    def test_internal_flag_spellings(self):
        for value in ("true", '"true"', "'1'"):
            self.repo.write("skills/in-progress/draft-one/SKILL.md",
                            skill_md("draft-one", extra=f"metadata:\n  internal: {value}\n"))
            self.assertClean(self.repo.run())
        self.repo.write("skills/in-progress/draft-one/SKILL.md",
                        skill_md("draft-one", extra='metadata:\n  internal: "false"\n'))
        self.assertFlags(self.repo.run(), "installer", "draft isn't marked internal")

    # files git ignores ------------------------------------------------------

    def git_init(self):
        subprocess.run(["git", "init", "-q", str(self.repo.root)], check=True)

    @unittest.skipUnless(shutil.which("git"), "needs git")
    def test_git_ignored_files_are_skipped(self):
        self.git_init()
        self.repo.write(".gitignore", ".local/\n.DS_Store\n")
        self.repo.write(".local/old/README.md", "[gone](./missing.md)\n")
        self.repo.write(".local/old/skills/engineering/x/SKILL.md", "no frontmatter")
        self.repo.write("skills/data-engineering/.DS_Store", "")
        self.repo.write("skills/data-engineering/alpha/.DS_Store", "")
        self.assertClean(self.repo.run())

    @unittest.skipUnless(shutil.which("git"), "needs git")
    def test_untracked_files_git_would_add_are_still_checked(self):
        self.git_init()
        self.repo.write("notes/README.md", "[gone](./missing.md)\n")
        self.repo.write("skills/data-engineering/alpha/NOTES.md", "orphan")
        report = self.repo.run()
        self.assertFlags(report, "links", "broken link `./missing.md`")
        self.assertFlags(report, "reachable", "alpha/NOTES.md")

    # Claude Code validator cross-check ------------------------------------------------

    def test_claude_report_must_provide_exactly_published_skills(self):
        report_path = self.repo.root / "claude.json"
        report_path.write_text(json.dumps({"success": True, "provides": {
            "skills": ["pack:alpha", "pack:beta", "pack:gamma", "pack:draft-one"]}}))
        report = self.repo.run(claude_report=report_path)
        self.assertFlags(report, "claude", "would not load published skill `delta`",
                         "would load `draft-one`")

    def test_claude_report_clean(self):
        report_path = self.repo.root / "claude.json"
        report_path.write_text(json.dumps({"success": True, "provides": {
            "skills": ["pack:alpha", "pack:beta", "pack:gamma", "pack:delta"]}}))
        self.assertClean(self.repo.run(claude_report=report_path))


class RealRepoTest(unittest.TestCase):
    """The repo this test lives in must pass its own governance."""

    def test_repo_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_governance.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
