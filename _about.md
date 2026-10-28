# familiar-template

Generic starter for building a familiar specialty extension. Not itself a specialty — a scaffold you
rename and fill in. See `README.md` for the "Use this template" and rename workflow.

**Status:** template, not a package meant to run as-is. Everything under `familiar-yourspecialty` and
`example-skill`/`example-agent` is a placeholder to replace, not working content.

## Installing this into a project

This folder is a drop-in package, not an installer, once you've renamed it into your own specialty.
To add it to an existing [familiar-workspace](https://github.com/familiar-md/familiar/tree/main/familiar-workspace)-based project:

1. Copy these five folders — `.claude/`, `.agents/`, `.codex/`, `.gemini/`, `.familiar/` — into the
   project's root, merging with what's already there. Nothing in them overwrites core files; they
   only add skill, agent, and extension-package paths. **Copy only those five.** This folder also
   holds `_about.md`, `VERSION`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
   `CORE-RULES.md`, `BUILDING-YOUR-SPECIALTY.md`, `CONTRACT-CHECKLIST.md`, and `check_extension.py`,
   which belong to the package's source repo, not to a project: copying the three entry files would
   replace the project's own, copying `_about.md` would overwrite the core folder guide at the
   project root, and `VERSION` would sit there looking like the project's own.
2. Open your AI assistant in the project as usual. No install step, no restart beyond
   opening a new session — skills and agents are discovered by file presence.

Depends on familiar core `>=1.0.0 <2.0.0` (see `familiar-extension.json`).

## Removing it again

There is no ownership record and no uninstaller, so removal is deleting exactly what step 1 added —
name your own skill folders and agent files here once you've renamed them, one line per path, so a
user can delete exactly those. At minimum:

```text
.claude/skills/<skill>/  and  .agents/skills/<skill>/   -- each skill folder, including its
                                                           agents/openai.yaml (the per-skill Codex
                                                           policy; it lives inside the skill folder)
.claude/agents/<namespace>-<agent>.md      -- if you added a subagent
.codex/agents/<namespace>-<agent>.toml
.gemini/agents/<namespace>-<agent>.md
.familiar/extensions/<namespace>/
```

Delete nothing else. `.familiar/` itself, `.familiar/core/`, and every content folder are core's or
the user's. Open a new session afterwards — skills and agents are read at session start, so a removed
skill stays listed until the host restarts.

## Namespacing note

A bundled agent is a plugin-scoped contribution materialized as `<namespace>-<agent>` — its filename
and every dispatch reference must carry that prefix so it cannot collide with an agent from core or
another extension. See `extension-contract.md` → Composition and collisions in core for the full
rule.
