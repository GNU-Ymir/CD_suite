# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Issue tracking (Linear)

Issues for this repo are tracked in Linear, team **Ymir** (key `YMI`, id
`43b9b28b-ad88-40b2-a3b7-e7ba31ad62fc`), workspace `ymir-bootstrap`. There is no Linear MCP tool
installed in this environment — read/write issues via the Linear GraphQL API directly
(`https://api.linear.app/graphql`), authenticated with the `$LINEAR_API_KEY` environment
variable (passed as-is in the `Authorization` header, no `Bearer` prefix). That variable lives in
the user's interactive shell — a fresh subprocess may not inherit it; check with
`[ -z "$LINEAR_API_KEY" ]` before use, and never print the key itself.

- Create an issue:
  ```bash
  curl -s -X POST https://api.linear.app/graphql \
    -H "Content-Type: application/json" \
    -H "Authorization: $LINEAR_API_KEY" \
    -d '{"query": "mutation IssueCreate($input: IssueCreateInput!) { issueCreate(input: $input) { success issue { id identifier url } } }", "variables": {"input": {"teamId": "43b9b28b-ad88-40b2-a3b7-e7ba31ad62fc", "title": "...", "description": "..."}}}'
  ```
- Read/search issues (e.g. by team):
  ```bash
  curl -s -X POST https://api.linear.app/graphql \
    -H "Content-Type: application/json" \
    -H "Authorization: $LINEAR_API_KEY" \
    -d '{"query": "query { team(id: \"43b9b28b-ad88-40b2-a3b7-e7ba31ad62fc\") { issues { nodes { id identifier title state { name } url } } } }"}'
  ```
- Look up a single issue by identifier (e.g. `YMI-35`) via the `issue(id: "...")` query, or
  `issueUpdate(id: ..., input: {...})` to change state/assignee/etc.
- Team discovery (only needed if working across other Linear workspaces/teams):
  `query { teams { nodes { id key name } } }`.

The branch currently checked out is generally named `YMI-<issue_number>-<short-description>`
(e.g. `YMI-34-coverage-by-files`) — the `YMI-<issue_number>` part is the Linear issue key, so it
can be used to look up the issue this branch's work is tracked against (`issue(id: "YMI-34")` or
by matching `identifier` in a team issue list).
