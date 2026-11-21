# Triage labels

The pack's skills talk about five triage **roles**. This file maps each role to
the label your tracker actually uses, so skills apply your labels instead of
inventing new ones.

| Role (what a skill asks for) | Your label | Use it when |
|---|---|---|
| needs evaluation | `needs-triage` | It's new and nobody has assessed it yet |
| waiting on the reporter | `needs-info` | It can't move until someone answers a question |
| ready for an agent | `ready-for-agent` | It's specified well enough that an agent can finish it with no further conversation |
| ready for a person | `ready-for-human` | It needs human judgement, access an agent doesn't have, or a conversation with someone |
| won't do | `wontfix` | It's been decided against, with the reason written on the ticket |

Change the middle column to whatever your tracker already uses (`bug:triage`,
`status/blocked`, …). Skills ask for the role in the first column and apply
the label in the second.
