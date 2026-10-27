---
name: familiar-yourspecialty-example-agent
description: PLACEHOLDER — one paragraph stating exactly what this subagent does and does not do, and which skill(s) dispatch it. Delete this agent entirely if your specialty doesn't need one (see BUILDING-YOUR-SPECIALTY.md → Subagents).
model: sonnet
tools: WebSearch, WebFetch
maxTurns: 20
---

# familiar-yourspecialty-example-agent — PLACEHOLDER

This file carries its own rules because a dispatched subagent gets its own isolated context — nothing
the calling session read (bootstrap, project state, the dispatching skill's own instructions) carries
over automatically. Nothing else is loaded for you. Replace this whole file with your real subagent.

## Your input

State exactly what the caller passes in, and the scope of work this agent does — one unit at a time
(one record, one document, one item), returning structured results rather than prose.

## Return this schema, exactly

Define the fixed output shape the calling skill can assemble across every dispatch without
re-parsing free text.

## Guardrails

- **Never fabricate** anything this agent cannot verify from its own input.
- State any other hard rule this agent must not cross regardless of what it's asked.
