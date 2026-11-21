# Issue tracker: local markdown

This repo keeps its tickets as markdown files under `.scratch/` — no server,
nothing to install. Decide once whether `.scratch/` is committed (a shared
history) or git-ignored (private to this machine), and say which here.

## Layout

```
.scratch/
  <work-slug>/
    SPEC.md               ← the requirements spec, if there is one
    tickets/
      01-<slug>.md        ← one file per ticket, numbered in build order
      02-<slug>.md
```

Every ticket file starts with two lines:

```
Status: <triage label from triage-labels.md, or closed>
Blocked by: 01-<slug>.md   (or none)
```

then the ticket body. Discussion goes at the bottom under `## Notes`, one dated
entry per comment, oldest first.

| When a skill needs to… | Do this |
|---|---|
| publish a ticket | write the next numbered file in the work's `tickets/` folder (create the folders if needed) |
| read a ticket | open the file — the user usually gives the path or the number |
| list tickets with a label | search the `Status:` lines, e.g. `grep -l "^Status: needs-triage" .scratch/*/tickets/*.md` |
| add to the discussion | append a dated entry under `## Notes` |
| change the triage label | edit the `Status:` line |
| record a blocker | list the blocking files on the `Blocked by:` line |
| close | set `Status: closed` and add a note saying why |
