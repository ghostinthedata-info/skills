# Issue tracker: GitLab

This repo tracks work in GitLab Issues, through the
[`glab`](https://gitlab.com/gitlab-org/cli) command-line tool. Run it from
inside the clone — `glab` works out the project from the git remote, including
self-hosted GitLab.

| When a skill needs to… | Run |
|---|---|
| publish a ticket | `glab issue create --title "<title>" --label "<label>" --description "<body>"` |
| read a ticket and its discussion | `glab issue view <number> --comments` |
| list open tickets with a label | `glab issue list --label "<label>"` (add `--output json` for machine-readable output; check `glab issue list --help` if your version differs) |
| add to the discussion | `glab issue note <number> --message "<text>"` — GitLab calls comments *notes* |
| change the triage label | `glab issue update <number> --label "<new>" --unlabel "<old>"` |
| record a blocker | put `Blocked by: #<number>, #<number>` on the first line of the description; use GitLab's "blocks" linked items as well if your tier has them |
| close | add a note saying why, then `glab issue close <number>` (it takes no closing comment) |

GitLab calls pull requests *merge requests*: `glab mr create`, `glab mr view`,
`glab mr note`.
