# Agent brief: building a familiar extension

You are working in a copy of `familiar-template`, helping the user build a **familiar extension**: a
set of skills (and optionally worker agents) for one specialty, such as marketing, consulting or
proposal writing, that drops onto a familiar project and works alongside familiar core.

This folder is **not** a familiar project. Do not look for a `.familiar-project` marker, do not
emit a `familiar bound` line, and do not apply core's project rules to this folder itself. Those
rules apply to the skills you write, which will run inside a project.

## Read first, in this order

1. `README.md`: what the template is and the rename steps.
2. `CORE-RULES.md`: the rules every skill inherits from core (grounding, no fabrication, the project
   boundary, where state lives, retrieval, capabilities). Treat it as binding for anything you write.
3. `CONTRACT-CHECKLIST.md`: what must be exactly right for core to route to the extension.
4. `BUILDING-YOUR-SPECIALTY.md`: guidance on how many skills, what goes where, and how to write a
   procedure.
5. The placeholders you will replace: `.familiar/extensions/familiar-yourspecialty/package/familiar-extension.json`,
   `.claude/skills/example-skill/SKILL.md`, and `.claude/agents/familiar-yourspecialty-example-agent.md`.

If a familiar project or release is available on this machine, read its `.familiar/core/` files when
`CORE-RULES.md` points at them; they are authoritative. Never guess at core behavior you cannot
read: say what you could not confirm.

## How to work with the user

1. **Interview before building.** Ask what the specialty is, who runs it, and which distinct jobs
   they do at different times. Each job a person actually starts on its own is one skill. Propose
   the skill list, each with a one-line trigger, and get a yes before creating files.
2. **Pick the namespace with them.** `familiar-<specialty>`, lowercase and hyphenated, stable once
   published. Rename every `familiar-yourspecialty` and `example-*` placeholder (README → Quickstart
   lists every place).
3. **Write each skill in both copies.** `.claude/skills/<skill>/SKILL.md` has `name: ili-<skill>`;
   `.agents/skills/<skill>/SKILL.md` is identical except `name: <skill>`, and its folder also gets
   `agents/openai.yaml`. Keep the manifest's `routes` and `skills` in step with the folders.
4. **Every skill gets a full Context contract** (Required, Conditional and Excluded context,
   Updates, Capabilities, Completion), as in the example skill. Declare every file the skill writes.
5. **Check as you go.** Run `python check_extension.py` after each skill. Before calling it done,
   work through `CONTRACT-CHECKLIST.md` with the user, including the items the script cannot check.
6. **Test in a real project.** Have the user copy only `.claude/`, `.agents/`, `.codex/`,
   `.gemini/` and `.familiar/` onto a scratch copy of a familiar project, open a new session there,
   and run each skill once. `python check_extension.py --project <that project>` checks for name
   collisions with core.
7. **Update `_about.md`** so it lists exactly the paths the extension adds, for clean removal.

## Do not

- Copy or edit core files. The extension adds paths; it never changes core's.
- Write rules that contradict `CORE-RULES.md`, for example a skill that deletes files, writes into
  `1-Inputs/`, or answers project questions from general knowledge.
- Invent capabilities, paths or core behavior. If something cannot be confirmed, say so.

When the extension is ready to share, suggest publishing it as its own public repo with the
`familiar-extension` topic, so others can find it.
