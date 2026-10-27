# Contract checklist — the part that must be exact

This is the enforced surface: the minimum that has to be right for familiar core to route to your
specialty at all, and for a folder copy of it to be safe to merge into anyone's project (including,
eventually, an official adoption alongside familiar's own extensions). Nothing here is a style
opinion — it's what familiar core's
[`extension-contract.md`](https://github.com/familiar-md/familiar/blob/main/familiar-workspace/.familiar/core/extension-contract.md)
actually requires. Run `python check_extension.py` first (it checks most of this list mechanically),
then work through the rest by hand; there is no installer to catch a mistake for you.

- [ ] **`id` and `namespace` match**, are lowercase, hyphenated, and identical to each other in
      `familiar-extension.json`.
- [ ] **`type` is `"specialty"`** (the other values — `workflow`, `enforcement`, `integration` — are
      for different kinds of extension; don't pick one to sound more official).
- [ ] **`core` range is accurate.** Don't widen it past what you've actually verified against; don't
      leave the template's placeholder range in place without checking it against current
      `familiar-workspace/.familiar/core/extension-contract.md`.
- [ ] **Every route ID begins with `<namespace>.`** — core route IDs are reserved, and a route
      outside your namespace is a contract violation, not just a style issue.
- [ ] **Every route has a real `select_when`.** This is the one line a session uses to decide whether
      your skill is the match for a request — a vague or copy-pasted trigger means your skill either
      never fires or fires on the wrong requests.
- [ ] **`routes`, `skills`, and `agents` in the manifest match what's actually on disk** — no route
      pointing at a skill folder that doesn't exist, no skill left out of the manifest.
- [ ] **Skill folders exist in both `.claude/skills/` and `.agents/skills/`**, with matching content
      (the two copies are byte-identical except for `agents/openai.yaml` and the `name` line). Each
      `SKILL.md` has `name` and `description` frontmatter: `name: ili-<skill>` in `.claude/skills/`,
      `name: <skill>` in `.agents/skills/`.
- [ ] **Every skill folder under `.agents/skills/` has `agents/openai.yaml`** — the per-skill Codex
      invocation policy (`interface.display_name`, `policy.allow_implicit_invocation`). It is required
      for every skill, whether or not the skill dispatches a subagent. `.claude/skills/` has no
      equivalent file.
- [ ] **Every subagent is namespaced `<namespace>-<agent>`** in its filename, its declared `name`,
      and every skill's dispatch reference to it, and has exactly three host copies:
      `.claude/agents/<namespace>-<agent>.md`, `.codex/agents/<namespace>-<agent>.toml`, and
      `.gemini/agents/<namespace>-<agent>.md`.
- [ ] **No ID collides with core or another named extension** — compare your route IDs, skill
      folder names, and agent names against the project's `.familiar/routes.md`, its skill and agent
      folders, and any extension you list under `compatible_with`.
      `python check_extension.py --project <project root>` does this against a real project; nothing
      checks it at drop-in time.
- [ ] **`_about.md` lists exactly the paths your package adds**, so removal is possible without an
      uninstaller.
- [ ] **Capabilities are honest.** `required` is only what genuinely can't degrade; everything else
      is `optional` with a real `unavailable_behavior` (`hide`, `degrade`, or `report-unavailable`) —
      don't claim `degrade` and then fail hard when the capability is missing.

`check_extension.py` does not check the last two items (what `_about.md` lists, and whether your
capability claims are honest), or whether your `core` range is accurate — those need a human.

This list is deliberately narrow. It says nothing about how many skills you should have, how a
procedure should be written, or what your specialty should cover — see
`BUILDING-YOUR-SPECIALTY.md` for that.
