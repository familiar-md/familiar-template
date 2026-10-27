# The core rules your skills live inside

Your extension does not run on its own. It runs inside a familiar project, where core's bootstrap,
routing and state rules are already in force. A skill that ignores them still loads, but it will
fight the project it is in. This file condenses what a skill author needs from core. The
authoritative text is in any familiar project (or the
[familiar repo](https://github.com/familiar-md/familiar/tree/main/familiar-workspace/.familiar/core)):
`.familiar/core/bootstrap.md` for the rules, `routes.md` for routing, `state-schema.md` for where
state lives, and `extension-contract.md` for the manifest. When this summary and those files
disagree, those files win.

## How a request reaches your skill

A session opens in the project and reads the host entry file (`CLAUDE.md`, `AGENTS.md` or
`GEMINI.md`), which loads the small bootstrap. The bootstrap reads the user's preferences and the
project's name, then shows a one-line `familiar bound` check at the top of its first reply. For
each request it picks exactly one route from `.familiar/routes.md` (core's) or from an extension
manifest's `routes` (yours), opens that one skill, and reads only the context that skill's
**Context contract** declares. Nothing else is loaded.

So for your skill:

- **Your route's `select_when` is how you get chosen.** Write it as the trigger a user's request
  would match, not a summary.
- **Your Context contract is all the skill gets.** If a file is not listed under Required or
  Conditional context, the skill must not expect it to be read. List what it must not read under
  Excluded context.
- **Explicit start beats matching.** On Claude Code a user types `/ili-<skill>`; on Codex
  `$<skill>`; on Gemini CLI they ask for it by name. A skill with
  `disable-model-invocation: true` is user-only: the agent names it and waits, never runs it.

## The rules, by ID

Every skill inherits these from `bootstrap.md`. Cite them by ID in your guardrails, never by number.

| Rule | What it means for a skill |
|---|---|
| `CORE-GROUND` | Claims about the project come from material the skill actually read; claims about the world come from attributable sources. A failed or blocked read is a gap to report, never something to fill in. |
| `CORE-NO-FABRICATION` | Never invent facts, dates, amounts, decisions, citations, paths, capabilities, or "done". Say what must be confirmed. |
| `CORE-WORKSPACE-SILO` | The project folder is the boundary for reads and writes. Files come in through `1-Inputs/` or a file the user names; nothing reaches into another project. |
| `CORE-NO-DELETE` | Never delete project files. Flag obsolete material for the user to remove. |
| `CORE-COPY-ON-EDIT` | Never overwrite a source in `1-Inputs/` or an existing draft; write a dated copy. Change authoritative state only where your Context contract declares it under **Updates**. |
| `CORE-STALE-WRITE` | Before editing a living state file, read its revision marker. If it changed since you read it, stop, reread, and reconcile. |
| `CORE-SCOPE` | Change only what the task needs. No tidying of neighbouring files, no loading unrelated history. |
| `CORE-HUMAN-APPROVAL` | Ask before overwriting, publishing, sending, installing, changing a status, or any other consequential step your route does not already authorize. |
| `CORE-PLAIN-NAMES` | Talk to the user in plain words; show an ID or code only beside its name. |
| `CORE-INSTRUCTIONS-READONLY` | A skill never edits core's or another extension's instruction files. |
| `CORE-PROGRESSIVE-DISCLOSURE` | Load one skill and its declared context, nothing more. Keep big reference material in separate files the skill opens only when needed. |

## Where things live

Paths are relative to the project root. Read before you write; write only what your **Updates**
line declares.

| Folder | Owner | Use from a skill |
|---|---|---|
| `1-Inputs/` | The user | Read sources (`Sources/`), examples (`Examples/`) and templates (`Templates/`). Never write or edit here. |
| `2-Drafts/` | The agent | Deliverables waiting for the user's review. Save with `.familiar/scripts/draft_save.py`: `next` gives the versioned path to write, `register` adds the file's row to `_draft-index.md`. |
| `3-Knowledge/` | The agent | One page per ingested source, cataloged in `_knowledge-index.md`. Read the index first, then the page. To add a page, follow core's ingest rules (`.familiar/core/ingest.md`) rather than writing your own format. |
| `4-Trackers/` | The agent | `tasks.md`, `timeline.md`, `meetings.md`. Follow the column rules in `state-schema.md` → Tracker conventions exactly; scripts and the hub parse them. |
| `5-System/` | The agent | Config, context, status snapshot and log, decisions, handoffs, preferences, notes. Most of it belongs to core's own skills: leave status, memory and handoffs to `save`, `handoff` and `checkin` unless your skill truly owns a change. |

**Your own state.** If your specialty needs a file of its own (a register, a tracker), declare it in
the manifest under `contributions.state_surfaces` with its `path`, `schema_version`,
`update_behavior` and `scaffold` (`state-schema.md` → Extension state surfaces). Never put state in
your package folder; `.familiar/extensions/<id>/package/` is replaced on every update.

## Retrieval: answer from the project, not from memory

- **Look it up, then answer.** For a question about the project's own material, use
  `3-Knowledge/_knowledge-index.md` to find the page, then quote it. Core ships a `lookup` worker
  that returns verbatim quotes with citation anchors; a skill can dispatch it instead of reading
  pages itself. For the open web, core's `web-lookup` returns the primary source with URL and date.
- **Check the worker is available.** Before dispatching any worker, check this host's
  `named-subagents` row in `.familiar/installed.json`. Unless it is `active`, do the worker's job
  inline as `.familiar/core/retrieval-fallback.md` describes. Never call a worker that is not there.
- **Cite what you used.** Every project claim in an output points at the page or source it came
  from; anything that could not be found is listed as missing.

## Capabilities: say what you need, and what happens without it

Your manifest lists `required` and `optional` capabilities, using only the names in core's
`.familiar/capabilities.json` (`check_extension.py` checks this). A host missing a required capability cannot run your route. For each optional one, choose
`unavailable_behavior`: `hide`, `degrade` (and really degrade), or `report-unavailable`. Never write
a skill that silently assumes a capability; check `.familiar/installed.json` the way core does.

## Context every skill of a kind must load

- **A skill that writes any file** lists `.familiar/core/file-handling.md` under Required context.
  It holds the naming, versioning, copy-on-edit and `2-Drafts/` saving rules; core's own gates fail
  a core skill that writes files without it.
- **A skill that writes to the user or produces a document** lists `.familiar/core/voice.md` and
  `.familiar/core/plain-language.md`, and matches their register. Users should not be
able to tell where core stops and your extension starts.
