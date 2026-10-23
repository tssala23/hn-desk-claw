# HN Desk

A Claw that keeps a dashboard of the day's top Hacker News stories.

Ask it to build the dashboard and it fetches the front page, writes short
notes, and publishes ten story cards to a self-contained HTML dashboard
("HN Desk — Front Page"). Titles and story text are treated as untrusted data.

## Install

Clone this repo, then add the claw to your OpenClaw instance:

```
git clone https://github.com/tssala23/hn-desk-claw.git
openclaw claws add ./hn-desk-claw --agent-id hn-desk --workspace <your-workspace-dir>
```

Requires `OPENCLAW_EXPERIMENTAL_CLAWS=1` and an instance that allows ClawHub
skill installation (for the hacker-news dependency).

## What's inside

- Agent `hn-desk` with a focused purpose (see `CLAW.md`, `workspace/AGENTS.md`).
- Bundled `hn-dashboard` skill: template + Python helper that fill and publish
  the dashboard (`workspace/skills/hn-dashboard/`, `workspace/templates/`,
  `workspace/scripts/`).
- Tool profile limited to `read, write, exec`, workspace-only filesystem
  (`profiles/openclaw.yml`).

## Dependency

Pulls one ClawHub skill for reading Hacker News:
`@ivangdavila/hacker-news@1.0.0`. Your instance must allow ClawHub skill
installation for this to resolve.

## Reaches the network only at

`hn.algolia.com` and `hacker-news.firebaseio.com` (public Hacker News APIs).
No credentials required.
