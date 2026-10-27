---
name: example-skill
description: PLACEHOLDER — replace with a human-facing one-line description of what running this skill produces. If this stays model-invoked (disable-model-invocation not set to true), this line is what a session reads to decide whether to select it — write it as a trigger, not a summary.
disable-model-invocation: true
---

# familiar-yourspecialty — Example Skill

PLACEHOLDER. Replace this whole file with your real skill. What follows is a minimal skeleton showing
the sections a `SKILL.md` is expected to carry: a context contract, minimum inputs and confirmations,
a numbered procedure, guardrails, and what happens next.

## Context contract

- **Required context:** name every file this skill must read before doing anything — core files
  (e.g. `.familiar/core/voice.md`), project state, and any shared standards file under this
  extension's `familiar-system/`.
- **Conditional context:** anything read only in some runs — a specific input type, a prior page for
  reconciliation, and so on.
- **Excluded context:** state plainly what this skill must not read (other projects, undeclared
  extension content, unrelated project areas).
- **Updates:** exactly which files this skill writes or updates, and where.
- **Capabilities:** which capabilities this skill needs, matching `familiar-extension.json`'s
  `required`/`optional` lists, and what it does when an optional one is missing.
- **Completion:** one sentence stating what "done" looks like — the artifact this skill leaves
  behind, described concretely enough that its absence is an obvious failure.

## Before you start

**Minimum inputs — halt without them:** list the facts this skill cannot proceed without, and where
it should look for them before asking the user to repeat something already captured (e.g.
`5-System/project-context.md`).

**Confirm before doing expensive work:** anything worth checking with the user before a fan-out,
an external call, or an irreversible write.

## Procedure

Replace with your real, numbered procedure. Keep steps that exist for a concrete correctness or
safety reason; drop ceremony that doesn't change an outcome.

1. Step one.
2. Step two.
3. Write the output.

## Guardrails

- **Never fabricate** a fact this skill cannot verify (`CORE-NO-FABRICATION`). Report it as missing
  instead.
- State any other hard rule specific to this skill's domain.

## After

State what the user should do next, and whether this skill chains into another one automatically or
waits for the user to invoke the next step themselves.
