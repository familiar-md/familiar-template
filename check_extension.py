#!/usr/bin/env python3
"""Check a familiar specialty extension against extension contract 1.1.

Usage:
    python check_extension.py [path] [--project <familiar project root>]

`path` is the extension repo root (the folder holding .claude/, .agents/, .codex/, .gemini/ and
.familiar/extensions/<id>/package/familiar-extension.json). It defaults to the folder this script
sits in. With --project, the extension is also checked for collisions against that project's core
route IDs, skill folders, and agent names.

Standard library only. Exit code 0 when no check FAILs, 1 otherwise. WARN never fails.

This script re-implements, by hand, the rules in the contract's manifest schema
(`.familiar/extension-manifest.schema.json` in familiar-workspace); it does not need `jsonschema`.
Contract: https://github.com/familiar-md/familiar/blob/main/familiar-workspace/.familiar/core/extension-contract.md
"""

# familiar's floor is Python 3.10. On anything older, stop with a plain message instead of a traceback.
import sys
if sys.version_info < (3, 10):
    sys.exit("familiar needs Python 3.10 or newer, but this is Python %d.%d (%s). Install Python 3.10+ "
             "(.familiar/scripts/doctor.py says how), then run this again with it." % (*sys.version_info[:2], sys.executable))

import argparse
import json
import re
import sys
from pathlib import Path

CONTRACT_VERSION = "1.1"

# The closed capability vocabulary. Copied from familiar-workspace/.familiar/capabilities.json
# ("capabilities" array, version 1.0). If core adds a capability, update this list.
CAPABILITIES = [
    "project-instructions", "explicit-skills", "implicit-skills", "user-invocation-control",
    "named-subagents", "mechanical-enforcement", "file-read", "file-write", "document-tools",
    "background-work", "authenticated-knowledge", "external-retrieval", "hosted-publication",
]

TYPES = ["workflow", "specialty", "enforcement", "integration"]
UNAVAILABLE = ["hide", "degrade", "report-unavailable"]
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SCHEMA_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+$")
PLACEHOLDER_NAMES = ("yourspecialty", "example-skill", "example-agent")
PLACEHOLDER_TEXT = "replace with"

TOP_KEYS = {"contract", "id", "display_name", "version", "core", "type", "namespace",
            "contributions", "capabilities", "unavailable_behavior", "compatible_with",
            "conflicts", "package"}
TOP_REQUIRED = ["contract", "id", "display_name", "version", "core", "type", "namespace",
                "contributions", "capabilities", "unavailable_behavior", "package"]
CONTRIB_KEYS = {"routes", "skills", "agents", "state_surfaces", "checkin_fragments", "track_presets"}
CONTRIB_REQUIRED = ["routes", "skills", "agents", "state_surfaces"]


class Report:
    def __init__(self):
        self.fails = 0
        self.warns = 0

    def _emit(self, tag, name, detail):
        print("%-4s  %s%s" % (tag, name, (" -- " + detail) if detail else ""))

    def passed(self, name, detail=""):
        self._emit("PASS", name, detail)

    def fail(self, name, detail):
        self.fails += 1
        self._emit("FAIL", name, detail)

    def warn(self, name, detail):
        self.warns += 1
        self._emit("WARN", name, detail)

    def check(self, name, problems, ok_detail=""):
        """PASS when `problems` is empty, otherwise one FAIL line per problem."""
        if problems:
            for p in problems:
                self.fail(name, p)
        else:
            self.passed(name, ok_detail)


def is_str_list(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def frontmatter(path):
    """Return the simple key: value frontmatter of a markdown file, or None if there is none."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("\"'")
    return None


def toml_string(text, key):
    m = re.search(r"^%s\s*=\s*\"((?:[^\"\\]|\\.)*)\"" % re.escape(key), text, re.M)
    return m.group(1) if m else None


def files_under(root):
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


def validate_manifest(m, r):
    """Hand-written equivalent of extension-manifest.schema.json. Returns problems list."""
    problems = []
    if not isinstance(m, dict):
        return ["manifest root is not a JSON object"]
    for k in TOP_REQUIRED:
        if k not in m:
            problems.append("missing required field `%s`" % k)
    for k in m:
        if k not in TOP_KEYS:
            problems.append("unknown top-level field `%s` (schema forbids extras)" % k)
    if m.get("contract") != CONTRACT_VERSION:
        problems.append("`contract` must be \"%s\", got %r" % (CONTRACT_VERSION, m.get("contract")))
    for k in ("id", "namespace"):
        if k in m and not (isinstance(m[k], str) and ID_RE.match(m[k])):
            problems.append("`%s` must match ^[a-z][a-z0-9-]*$, got %r" % (k, m[k]))
    for k in ("display_name", "core"):
        if k in m and not (isinstance(m[k], str) and m[k]):
            problems.append("`%s` must be a non-empty string" % k)
    if "version" in m and not (isinstance(m["version"], str) and VERSION_RE.match(m["version"])):
        problems.append("`version` must be semantic (e.g. 0.1.0), got %r" % (m["version"],))
    if "type" in m and m["type"] not in TYPES:
        problems.append("`type` must be one of %s, got %r" % (TYPES, m["type"]))
    if "unavailable_behavior" in m and m["unavailable_behavior"] not in UNAVAILABLE:
        problems.append("`unavailable_behavior` must be one of %s, got %r"
                        % (UNAVAILABLE, m["unavailable_behavior"]))
    for k in ("compatible_with", "conflicts"):
        if k in m and not (is_str_list(m[k]) and len(set(m[k])) == len(m[k])):
            problems.append("`%s` must be a list of unique strings" % k)

    c = m.get("contributions")
    if "contributions" in m:
        if not isinstance(c, dict):
            problems.append("`contributions` must be an object")
        else:
            for k in CONTRIB_REQUIRED:
                if k not in c:
                    problems.append("`contributions` missing required `%s`" % k)
            for k in c:
                if k not in CONTRIB_KEYS:
                    problems.append("unknown `contributions.%s`" % k)
            for k in ("skills", "agents", "checkin_fragments", "track_presets"):
                if k in c and not (is_str_list(c[k]) and len(set(c[k])) == len(c[k])):
                    problems.append("`contributions.%s` must be a list of unique strings" % k)
            routes = c.get("routes")
            if "routes" in c:
                if not isinstance(routes, list):
                    problems.append("`contributions.routes` must be a list")
                else:
                    for i, rt in enumerate(routes):
                        if not isinstance(rt, dict):
                            problems.append("routes[%d] is not an object" % i)
                            continue
                        for k in ("id", "skill", "select_when"):
                            if not (isinstance(rt.get(k), str) and rt.get(k)):
                                problems.append("routes[%d] needs a non-empty string `%s`" % (i, k))
                        for k in rt:
                            if k not in ("id", "skill", "select_when"):
                                problems.append("routes[%d] has unknown field `%s`" % (i, k))
            surfaces = c.get("state_surfaces")
            if "state_surfaces" in c:
                if not isinstance(surfaces, list):
                    problems.append("`contributions.state_surfaces` must be a list")
                else:
                    for i, s in enumerate(surfaces):
                        if not isinstance(s, dict):
                            problems.append("state_surfaces[%d] is not an object" % i)
                            continue
                        for k in ("path", "schema_version", "update_behavior", "scaffold"):
                            if k not in s:
                                problems.append("state_surfaces[%d] missing `%s`" % (i, k))
                        for k in s:
                            if k not in ("path", "schema_version", "update_behavior", "scaffold"):
                                problems.append("state_surfaces[%d] has unknown field `%s`" % (i, k))
                        for k in ("path", "update_behavior"):
                            if k in s and not (isinstance(s[k], str) and s[k]):
                                problems.append("state_surfaces[%d].%s must be a non-empty string" % (i, k))
                        if "schema_version" in s and not (isinstance(s["schema_version"], str)
                                                          and SCHEMA_VERSION_RE.match(s["schema_version"])):
                            problems.append("state_surfaces[%d].schema_version must look like 1.0" % i)
                        if "scaffold" in s and not isinstance(s["scaffold"], bool):
                            problems.append("state_surfaces[%d].scaffold must be true or false" % i)

    cap = m.get("capabilities")
    if "capabilities" in m:
        if not isinstance(cap, dict):
            problems.append("`capabilities` must be an object")
        else:
            for k in ("required", "optional"):
                if k not in cap:
                    problems.append("`capabilities` missing `%s`" % k)
                elif not (is_str_list(cap[k]) and len(set(cap[k])) == len(cap[k])):
                    problems.append("`capabilities.%s` must be a list of unique strings" % k)
            for k in cap:
                if k not in ("required", "optional"):
                    problems.append("unknown `capabilities.%s`" % k)

    pkg = m.get("package")
    if "package" in m:
        if not isinstance(pkg, dict):
            problems.append("`package` must be an object")
        else:
            if "update_source" not in pkg:
                problems.append("`package` missing `update_source`")
            elif not (pkg["update_source"] is None or isinstance(pkg["update_source"], str)):
                problems.append("`package.update_source` must be a string or null")
            for k in pkg:
                if k != "update_source":
                    problems.append("unknown `package.%s`" % k)
    return problems


def core_route_ids(project):
    path = project / ".familiar" / "routes.md"
    if not path.is_file():
        path = project / ".familiar" / "core" / "routes.md"
    if not path.is_file():
        return None
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
        if m:
            ids.add(m.group(1))
    return ids


def check_project_collisions(project, manifest, skills, agents, r):
    ns = manifest["namespace"]
    ids = core_route_ids(project)
    if ids is None:
        r.fail("project: core routes", "no .familiar/routes.md under %s" % project)
    else:
        mine = [rt["id"] for rt in manifest["contributions"]["routes"]]
        bad = ["route `%s` collides with a core route ID" % i for i in mine if i in ids]
        r.check("project: route IDs vs core routes.md", bad, "%d core route IDs read" % len(ids))

    # Skills/agents already present from *this* extension (a previous drop-in) are not collisions.
    own_skills, own_agents = set(skills), {"%s-%s" % (ns, a) for a in agents}
    other_skills, other_agents = set(), set()
    ext_dir = project / ".familiar" / "extensions"
    if ext_dir.is_dir():
        for mf in ext_dir.glob("*/package/familiar-extension.json"):
            try:
                other = json.loads(mf.read_text(encoding="utf-8"))
                oc = other["contributions"]
                if other.get("id") == manifest["id"]:
                    continue
                other_skills.update(oc.get("skills", []))
                other_agents.update("%s-%s" % (other["namespace"], a) for a in oc.get("agents", []))
            except (ValueError, KeyError, OSError, TypeError):
                pass
    skill_dir = project / ".claude" / "skills"
    present = {p.name for p in skill_dir.iterdir() if p.is_dir()} if skill_dir.is_dir() else set()
    bad = []
    for s in skills:
        if s in present and s in other_skills:
            bad.append("skill `%s` collides with another installed extension's skill" % s)
        elif s in present and not (project / ".familiar" / "extensions" / manifest["id"]).is_dir():
            bad.append("skill `%s` collides with an existing project/core skill folder" % s)
    r.check("project: skill folders vs project", bad, "%d project skill folders read" % len(present))

    agent_dir = project / ".claude" / "agents"
    present_a = {p.stem for p in agent_dir.glob("*.md")} if agent_dir.is_dir() else set()
    bad = []
    for a in sorted(own_agents):
        if a in present_a and a in other_agents:
            bad.append("agent `%s` collides with another installed extension's agent" % a)
        elif a in present_a and not (project / ".familiar" / "extensions" / manifest["id"]).is_dir():
            bad.append("agent `%s` collides with an existing project/core agent" % a)
    r.check("project: agent names vs project", bad, "%d project agents read" % len(present_a))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check a familiar extension against contract %s."
                                 % CONTRACT_VERSION)
    ap.add_argument("path", nargs="?", default=str(Path(__file__).resolve().parent),
                    help="extension repo root (default: the folder containing this script)")
    ap.add_argument("--project", help="familiar project root, to check for ID collisions with core")
    args = ap.parse_args(argv)

    root = Path(args.path).resolve()
    r = Report()
    print("Checking %s against extension contract %s\n" % (root, CONTRACT_VERSION))

    # --- manifest ---------------------------------------------------------------------------
    found = sorted(root.glob(".familiar/extensions/*/package/familiar-extension.json"))
    if len(found) != 1:
        r.fail("manifest: exactly one found",
               "found %d under .familiar/extensions/*/package/" % len(found))
        return finish(r)
    r.passed("manifest: exactly one found", found[0].relative_to(root).as_posix())
    mpath = found[0]
    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        r.fail("manifest: valid JSON", str(e))
        return finish(r)
    r.passed("manifest: valid JSON")
    problems = validate_manifest(manifest, r)
    r.check("manifest: fields match the schema", problems)
    if problems:
        return finish(r)

    ns, mid = manifest["namespace"], manifest["id"]
    contrib = manifest["contributions"]
    skills, agents = contrib["skills"], contrib["agents"]
    pkg_dir = mpath.parent  # .familiar/extensions/<id>/package

    bad = []
    if mid != ns:
        bad.append("`id` (%s) != `namespace` (%s)" % (mid, ns))
    if pkg_dir.parent.name != mid:
        bad.append("extension folder `%s` != id `%s`" % (pkg_dir.parent.name, mid))
    r.check("identity: id == namespace == extensions/<id> folder name", bad, mid)

    # --- routes -----------------------------------------------------------------------------
    bad = []
    seen = set()
    for rt in contrib["routes"]:
        if not rt["id"].startswith(ns + "."):
            bad.append("route `%s` does not start with `%s.`" % (rt["id"], ns))
        if rt["id"] in seen:
            bad.append("duplicate route ID `%s`" % rt["id"])
        seen.add(rt["id"])
        if not rt["select_when"].strip():
            bad.append("route `%s` has an empty select_when" % rt["id"])
        if rt["skill"] not in skills:
            bad.append("route `%s` names skill `%s`, which is not in `skills`" % (rt["id"], rt["skill"]))
    r.check("routes: namespace prefix, unique IDs, skill listed", bad,
            "%d route(s)" % len(contrib["routes"]))
    bad = ["route `%s` still has the template placeholder select_when" % rt["id"]
           for rt in contrib["routes"] if PLACEHOLDER_TEXT in rt["select_when"].lower()]
    r.check("routes: select_when written (no \"Replace with\" placeholder)", bad)

    # --- skills -----------------------------------------------------------------------------
    claude_skills = root / ".claude" / "skills"
    agents_skills = root / ".agents" / "skills"
    on_claude = {p.name for p in claude_skills.iterdir() if p.is_dir()} if claude_skills.is_dir() else set()
    on_agents = {p.name for p in agents_skills.iterdir() if p.is_dir()} if agents_skills.is_dir() else set()
    want = set(skills)
    for label, on_disk in ((".claude/skills/", on_claude), (".agents/skills/", on_agents)):
        bad = []
        for s in sorted(want - on_disk):
            bad.append("manifest skill `%s` has no folder" % s)
        for s in sorted(on_disk - want):
            bad.append("folder `%s` is not in the manifest `skills`" % s)
        r.check("skills: manifest == %s on disk" % label, bad, "%d skill(s)" % len(want))

    bad = []
    for s in sorted(want & on_claude):
        for host in (".claude", ".agents"):
            md = root / host / "skills" / s / "SKILL.md"
            if not md.is_file():
                if host == ".claude" or s in on_agents:
                    bad.append("%s/skills/%s/SKILL.md is missing" % (host, s))
                continue
            fm = frontmatter(md)
            if fm is None:
                bad.append("%s/skills/%s/SKILL.md has no frontmatter" % (host, s))
                continue
            for k in ("name", "description"):
                if not fm.get(k):
                    bad.append("%s/skills/%s/SKILL.md frontmatter lacks `%s`" % (host, s, k))
            # Claude Code's copy is named ili-<folder> so its `/` menu groups familiar skills under /ili.
            expected = "ili-" + s if host == ".claude" else s
            if fm.get("name") and fm["name"] != expected:
                bad.append("%s/skills/%s/SKILL.md `name: %s` != `%s`" % (host, s, fm["name"], expected))
    r.check("skills: SKILL.md has name + description frontmatter", bad)

    bad = []
    for s in sorted(want & on_claude & on_agents):
        a = files_under(claude_skills / s)
        b = {k: v for k, v in files_under(agents_skills / s).items() if k != "agents/openai.yaml"}
        for k in sorted(set(a) - set(b)):
            bad.append("%s exists in .claude/skills/%s but not .agents/skills/%s" % (k, s, s))
        for k in sorted(set(b) - set(a)):
            bad.append("%s exists in .agents/skills/%s but not .claude/skills/%s" % (k, s, s))
        for k in sorted(set(a) & set(b)):
            mine = a[k].read_bytes()
            if k == "SKILL.md":
                mine = mine.replace(("name: ili-" + s).encode(), ("name: " + s).encode(), 1)
            if mine != b[k].read_bytes():
                bad.append("%s differs between .claude/skills/%s and .agents/skills/%s" % (k, s, s))
    r.check(".claude vs .agents skill copies byte-identical (except agents/openai.yaml and the ili- name)", bad)

    bad = []
    for s in sorted(on_agents):
        y = agents_skills / s / "agents" / "openai.yaml"
        if not y.is_file():
            bad.append(".agents/skills/%s/agents/openai.yaml is missing" % s)
        elif "allow_implicit_invocation" not in y.read_text(encoding="utf-8"):
            bad.append(".agents/skills/%s/agents/openai.yaml has no policy.allow_implicit_invocation" % s)
    r.check("skills: every .agents/skills/<skill>/ has agents/openai.yaml", bad)

    # --- agents -----------------------------------------------------------------------------
    bad = []
    expected = {"%s-%s" % (ns, a) for a in agents}
    for a in agents:
        full = "%s-%s" % (ns, a)
        md_hosts = ((".claude/agents/%s.md" % full), (".gemini/agents/%s.md" % full))
        for rel in md_hosts:
            p = root / rel
            if not p.is_file():
                bad.append("%s is missing" % rel)
                continue
            fm = frontmatter(p)
            if fm is None or fm.get("name") != full:
                bad.append("%s declared name must be `%s`" % (rel, full))
            elif not fm.get("description"):
                bad.append("%s has no description" % rel)
        rel = ".codex/agents/%s.toml" % full
        p = root / rel
        if not p.is_file():
            bad.append("%s is missing" % rel)
        else:
            text = p.read_text(encoding="utf-8")
            if toml_string(text, "name") != full:
                bad.append("%s declared name must be `%s`" % (rel, full))
            for k in ("description", "developer_instructions"):
                if not toml_string(text, k):
                    bad.append("%s has no `%s`" % (rel, k))
    for rel_dir, suffix in ((".claude/agents", ".md"), (".codex/agents", ".toml"), (".gemini/agents", ".md")):
        d = root / rel_dir
        if d.is_dir():
            for p in sorted(d.glob("*" + suffix)):
                if p.stem not in expected:
                    bad.append("%s/%s is not listed in the manifest `agents`" % (rel_dir, p.name))
    r.check("agents: <ns>-<agent> in .claude, .codex, .gemini; names match; none unlisted", bad,
            "%d agent(s)" % len(agents))

    # --- fragments, capabilities ------------------------------------------------------------
    bad = []
    for frag in contrib.get("checkin_fragments", []):
        if not (pkg_dir / frag).is_file():
            bad.append("checkin fragment `%s` not found under %s" % (frag, pkg_dir.relative_to(root).as_posix()))
    r.check("checkin_fragments: paths exist", bad)

    bad = []
    caps = manifest["capabilities"]
    for k in ("required", "optional"):
        for c in caps[k]:
            if c not in CAPABILITIES:
                bad.append("%s capability `%s` is not in the closed vocabulary" % (k, c))
    for c in set(caps["required"]) & set(caps["optional"]):
        bad.append("capability `%s` is both required and optional" % c)
    r.check("capabilities: names from the closed vocabulary", bad)

    # --- placeholders -----------------------------------------------------------------------
    names = [mid, ns] + skills + agents
    hits = sorted({n for n in names for ph in PLACEHOLDER_NAMES if ph in n})
    if hits:
        r.warn("placeholders: names still contain template placeholders", ", ".join(hits))
    else:
        r.passed("placeholders: no template placeholder names")

    # --- optional: collisions with a project ------------------------------------------------
    if args.project:
        project = Path(args.project).resolve()
        if not project.is_dir():
            r.fail("project: path", "%s is not a directory" % project)
        else:
            check_project_collisions(project, manifest, skills, agents, r)

    return finish(r)


def finish(r):
    print("\n%d FAIL, %d WARN" % (r.fails, r.warns))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
