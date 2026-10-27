# Building your specialty — guidance, not a gate

Nothing in this file is required by the contract. `CONTRACT-CHECKLIST.md` covers what has to be
exact; this is the part that's genuinely yours to design. Treat it as a set of defaults worth
deviating from on purpose, not a shape to force your domain into.

## How many skills

As many as your domain has distinct, user-invoked flows — not one skill per verb. A specialty that
assesses a product, assesses a competitor, and compares the two head to head has three skills,
because those are three things a person actually runs, at different times, sometimes without the
others. If you find yourself
writing a skill that only ever gets run immediately before or after another one with no independent
value, consider whether it's really one flow.

## What goes in a skill vs. in shared standards

A `SKILL.md` is the orchestration: what to ask before starting, the procedure, the guardrails, the
page or output shape. Detail that's genuinely reusable across more than one skill — a scoring
rubric, a schema, a set of definitions — belongs in a shared file under your package's
`familiar-system/` folder (for example an `evidence-standards.md` that every skill lists under its
Required context), referenced by name from each skill rather than restated. If only one skill will ever read it, it can just live in
that skill's `SKILL.md`.

## Writing the procedure itself

A few things worth keeping even though they're not enforced:

- **Name the minimum inputs and halt without them.** Don't let a skill guess at something the user
  needs to actually decide.
- **Confirm scope before doing expensive work**, especially anything that fans out to subagents or
  hits an external source — a wrong assumption caught before the fan-out is cheap; caught after, it
  isn't.
- **Never fabricate.** An unretrievable fact is reported as missing, not inferred, estimated, or
  filled from memory. This one is a core-wide rule (`CORE-NO-FABRICATION`) even though it isn't
  contract-checkable — treat it as non-negotiable regardless.
- **Say what you didn't do and why**, particularly when a capability degraded or a source couldn't be
  reached. A silent gap is worse than a stated one.

## Subagents

Only add one if a piece of work genuinely benefits from an isolated context — a fan-out over many
independent items (one study, one record, one document at a time) where the dispatching skill needs
structured results back, not prose. A subagent gets none of the calling session's context
automatically, so its own file has to carry everything it needs to do its job alone. If your
specialty doesn't have that shape, skip it — `example-agent` in this template is only there to show
the required namespacing and per-host mirroring; delete it if you don't need it.

## Voice and formatting

If you're dropping this into a project that also uses familiar core's own `voice.md` and
`plain-language.md`, match their register rather than inventing your own — a specialty that reads
like a different product than the core it's embedded in is a worse experience than one that's plainer
than you'd like.

## Longer reference

If you want the fuller internal standard this guidance is condensed from — invocation modes,
calibration, why order matters where it does — it's documented at
[`writing-great-skills`](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md),
which familiar's own maintainer-facing skill-authoring standard is adapted from. Useful background,
not a requirement.
