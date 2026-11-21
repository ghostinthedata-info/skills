# Issue tracker: GitHub

This repo tracks work in GitHub Issues, through the `gh` command-line tool.
Run it from inside the clone — `gh` works out the repository from the git
remote.

| When a skill needs to… | Run |
|---|---|
| publish a ticket | `gh issue create --title "<title>" --label "<label>" --body-file <file>` — write the body to a file first, so long markdown survives intact |
| read a ticket and its discussion | `gh issue view <number> --comments` |
| list open tickets with a label | `gh issue list --state open --label "<label>" --json number,title,labels` |
| add to the discussion | `gh issue comment <number> --body-file <file>` |
| change the triage label | `gh issue edit <number> --add-label "<new>" --remove-label "<old>"` |
| record a blocker | put `Blocked by: #<number>, #<number>` on the first line of the body; use GitHub's issue relationships as well if your organisation has them |
| close | `gh issue close <number> --comment "<why>"` |

Labels must exist before they can be applied. Create any that are missing
once, with `gh label create "<label>"`, using the strings in
`triage-labels.md`.
