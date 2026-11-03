#!/usr/bin/env python3
"""Static scan of a Vue 3 source tree for performance, reuse and structure candidates.

Usage:
    python3 scan_components.py <src-dir> [--json] [--only path/inside/src ...]

Everything this reports is a CANDIDATE. Regex-level analysis can't tell whether a
list has 10 rows or 10,000, whether a function is cheap, or whether two similar
blocks are meant to diverge. Read the code at each location before turning a
candidate into a finding, and drop the ones that don't hold up.

Sections:
  components   size, API style, reactive primitive counts per .vue file
  template     v-for without :key / keyed by index, v-if+v-for on one element,
               array/date work inside template expressions, per-row function calls,
               inline object/array props inside loops, zero-arg functions called
               from the template that build derived data (computed candidates)
  script       deep watchers, listeners/intervals without cleanup, prop mutation
  duplication  copy-pasted code blocks across files, same-named functions in
               several files, identical CSS rule bodies, one class styled in many files

Stdlib only.
"""
import difflib
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}
HEAVY = re.compile(r"\.(filter|find|findIndex|findLast|sort|reduce|map|flatMap|some|every|slice|concat)\(|"
                   r"new Date\(|JSON\.(parse|stringify)\(|Object\.(keys|values|entries)\(|"
                   r"new Intl\.\w+\(")
CALL = re.compile(r"(?<![\w.$])([A-Za-z_]\w*)\s*\(")
# Calls that are cheap or unavoidable in templates (i18n, casts, Math helpers)
CHEAP_CALLS = {"t", "$t", "tc", "te", "d", "n", "String", "Number", "Boolean", "parseInt",
               "parseFloat", "isNaN", "Math", "Array", "if", "for", "while", "switch", "return",
               "function", "typeof"}
ATTR = re.compile(r"""([:@#]?[\w\-.:\[\]$]+)(?:\s*=\s*("([^"]*)"|'([^']*)'))?""")
INTERP = re.compile(r"\{\{(.*?)\}\}", re.S)
SCRIPT = re.compile(r"<script([^>]*)>(.*?)</script>", re.S | re.I)
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
CSS_RULE = re.compile(r"([^{}@;]+)\{([^{}]*)\}")
FUNC_DEF = re.compile(
    r"(?:^|\n)[ \t]*(?:export\s+)?(?:async\s+)?(?:function\s+(\w+)\s*\(([^)]*)\)"
    r"|(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?(?:\(([^)]*)\)|(\w+))\s*=>"
    r"|(\w+)\s*\(([^)]*)\)\s*\{)")
NOT_FUNCS = {"if", "for", "while", "switch", "catch", "function", "return", "setup", "data",
             "mounted", "created", "unmounted", "beforeUnmount", "onMounted", "watch",
             "computed", "then", "else"}


def line_of(text, offset, base=1):
    return base + text.count("\n", 0, offset)


def match_brace(text, open_idx):
    """Index just past the brace matching text[open_idx] ('{'), skipping strings."""
    depth, i, quote = 0, open_idx, None
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(text)


def split_sfc(text):
    """Return (template, template_start_line, [(script, line, attrs)], [(style, line)])."""
    template, tline = "", 1
    m = re.search(r"^<template[^>]*>", text, re.M)
    if m:
        ends = [e.start() for e in re.finditer(r"^</template>", text, re.M) if e.start() > m.end()]
        if ends:
            template = text[m.end():ends[-1]]
            tline = line_of(text, m.end())
    scripts = [(s.group(2), line_of(text, s.start(2)), s.group(1)) for s in SCRIPT.finditer(text)]
    styles = [(s.group(1), line_of(text, s.start(1))) for s in STYLE.finditer(text)]
    return template, tline, scripts, styles


def scan_tags(tpl):
    """Yield dicts for opening/closing tags in a Vue template, respecting quoted attributes."""
    i, n = 0, len(tpl)
    while i < n:
        if tpl.startswith("<!--", i):
            j = tpl.find("-->", i)
            i = n if j < 0 else j + 3
            continue
        if tpl[i] != "<" or i + 1 >= n:
            i += 1
            continue
        if tpl[i + 1] == "/":
            j = tpl.find(">", i)
            if j < 0:
                break
            yield {"kind": "close", "name": tpl[i + 2:j].strip().lower(), "start": i, "end": j + 1}
            i = j + 1
            continue
        if not (tpl[i + 1].isalpha()):
            i += 1
            continue
        j, quote = i + 1, None
        while j < n:
            c = tpl[j]
            if quote:
                if c == quote:
                    quote = None
            elif c in "'\"":
                quote = c
            elif c == ">":
                break
            j += 1
        raw = tpl[i + 1:j]
        name_m = re.match(r"[\w\-.:]+", raw)
        name = name_m.group(0) if name_m else ""
        attrs = {}
        for a in ATTR.finditer(raw[len(name):]):
            val = a.group(3) if a.group(3) is not None else a.group(4)
            attrs[a.group(1)] = val if val is not None else ""
        yield {"kind": "open", "name": name, "lname": name.lower(), "attrs": attrs,
               "self": raw.rstrip().endswith("/"), "start": i, "end": j + 1}
        i = j + 1


def template_findings(tpl, base, script_funcs):
    out = []
    opens, stack, loops = [], [], []
    for tag in scan_tags(tpl):
        if tag["kind"] == "open":
            opens.append(tag)
            if not tag["self"] and tag["lname"] not in VOID:
                stack.append(tag)
            if "v-for" in tag["attrs"]:
                tag["loop_end"] = None
                loops.append(tag)
        else:
            while stack:
                t = stack.pop()
                if "v-for" in t["attrs"]:
                    t["loop_end"] = tag["end"]
                if t["lname"] == tag["name"]:
                    break
    for t in loops:
        if t.get("loop_end") is None:
            t["loop_end"] = t["end"]  # self-closing component with v-for

    def ln(off):
        return line_of(tpl, off, base)

    # Loop-level checks
    for t in loops:
        vfor = t["attrs"]["v-for"]
        key = t["attrs"].get(":key", t["attrs"].get("v-bind:key", t["attrs"].get("key")))
        head = re.match(r"\s*\(?\s*([\w$]+)\s*(?:,\s*([\w$]+))?\s*(?:,\s*([\w$]+))?\s*\)?\s+(?:in|of)\s+(.+)", vfor)
        source = head.group(4).strip() if head else vfor
        index_var = head.group(2) if head else None
        static_range = bool(re.fullmatch(r"\d+", source))
        item = {"line": ln(t["start"]), "tag": t["name"], "v_for": vfor}
        if key is None and t["lname"] != "template":
            out.append({**item, "check": "v-for-without-key"})
        elif key is not None and index_var and key.strip() == index_var:
            out.append({**item, "check": "v-for-key-is-index", "static_source": static_range,
                        "note": "fine for static/never-reordered lists"})
        if "v-if" in t["attrs"]:
            out.append({**item, "check": "v-if-with-v-for-same-element", "v_if": t["attrs"]["v-if"]})
        if HEAVY.search(source):
            out.append({**item, "check": "array-work-in-v-for-source", "source": source})

    # Expression-level checks
    exprs = []
    for t in opens:
        for k, v in t["attrs"].items():
            if v and (k.startswith(":") or k.startswith("v-bind") or k in ("v-if", "v-else-if", "v-show", "v-html", "v-text")):
                exprs.append((t["start"], k, v, t))
    for m in INTERP.finditer(tpl):
        exprs.append((m.start(), "{{}}", m.group(1), None))

    def enclosing_loop(off):
        inner = [l for l in loops if l["start"] < off < l["loop_end"]]
        return max(inner, key=lambda l: l["start"]) if inner else None

    per_loop_calls = defaultdict(set)
    for off, attr, expr, tag in exprs:
        if attr in (":key",):
            continue
        loop = enclosing_loop(off) if tag is None or tag not in loops else enclosing_loop(off - 1)
        if tag is not None and tag in loops:
            loop = tag  # attributes on the v-for element itself run per item
        if HEAVY.search(expr):
            out.append({"check": "array-or-date-work-in-template", "line": ln(off), "attr": attr,
                        "expr": " ".join(expr.split())[:120], "inside_v_for": loop is not None})
        if loop is not None:
            for name in CALL.findall(expr):
                if name not in CHEAP_CALLS:
                    per_loop_calls[(loop["start"], loop["attrs"]["v-for"])].add(name)
            if tag is not None and attr.startswith(":") and re.match(r"\s*[\[{]", expr) and \
                    (tag["name"][:1].isupper() or "-" in tag["name"]):
                out.append({"check": "inline-object-prop-in-loop", "line": ln(off), "component": tag["name"],
                            "attr": attr, "expr": " ".join(expr.split())[:80]})
    for (start, vfor), names in per_loop_calls.items():
        out.append({"check": "function-calls-per-row", "line": ln(start), "v_for": vfor,
                    "functions": sorted(names), "note": "cost depends on what each function does"})

    # Zero-arg functions that build derived data, called from the template
    for name, info in script_funcs.items():
        if info["params"] == 0 and info["derives"]:
            calls = len(re.findall(r"(?<![\w.$])" + re.escape(name) + r"\s*\(\s*\)", tpl))
            if calls:
                out.append({"check": "computed-candidate", "function": name, "template_calls": calls,
                            "defined_at": info["line"], "note": "re-runs on every render; computed caches"})
    return out


def script_functions(script, base):
    funcs = {}
    for m in FUNC_DEF.finditer(script):
        name = m.group(1) or m.group(3) or m.group(6)
        params = m.group(2) if m.group(1) else (m.group(4) if m.group(3) else m.group(7))
        if m.group(3) and m.group(5):
            params = m.group(5)
        if not name or name in NOT_FUNCS:
            continue
        brace = script.find("{", m.end() - 1)
        arrow_expr = m.group(3) is not None and not script[m.end():m.end() + 3].lstrip().startswith("{")
        if arrow_expr:
            end = script.find("\n", m.end())
            body = script[m.end():end if end > 0 else len(script)]
        elif brace < 0 or brace - m.end() > 5:
            continue
        else:
            body = script[brace:match_brace(script, brace)]
        nparams = 0 if not (params or "").strip() else len([p for p in params.split(",") if p.strip()])
        funcs[name] = {"line": line_of(script, m.start() + (1 if script[m.start()] == "\n" else 0), base),
                       "params": nparams, "body": body,
                       "derives": bool(re.search(r"\.(filter|sort|reduce|map|flatMap)\(", body))}
    return funcs


def script_findings(script, base, rel, tpl):
    out = []
    for m in re.finditer(r"deep\s*:\s*true", script):
        out.append({"check": "deep-watcher", "line": line_of(script, m.start(), base),
                    "note": "check how large the watched structure is"})
    for add, remove, label in (("addEventListener", "removeEventListener", "event-listener"),
                               ("setInterval", "clearInterval", "interval")):
        adds = [m for m in re.finditer(add + r"\(\s*(['\"]?)([\w:-]*)", script)]
        removed = set(re.findall(remove + r"\(\s*['\"]?([\w:-]*)", script))
        for m in adds:
            ev = m.group(2)
            if (label == "interval" and not removed) or (label == "event-listener" and ev not in removed):
                out.append({"check": f"{label}-without-cleanup", "line": line_of(script, m.start(), base),
                            "target": ev or "?"})
    # Prop mutation
    props = set()
    pm = re.search(r"defineProps\s*\(\s*([\[{])", script) or re.search(r"\bprops\s*:\s*([\[{])", script)
    if pm:
        start = pm.start(1)
        if pm.group(1) == "[":
            end = script.find("]", start)
            props = set(re.findall(r"['\"](\w+)['\"]", script[start:end]))
        else:
            block = script[start:match_brace(script, start)]
            depth, cur = 0, ""
            for ch in block[1:-1]:
                if ch in "{[(":
                    depth += 1
                elif ch in "}])":
                    depth -= 1
                if depth == 0:
                    cur += ch
            props = set(re.findall(r"(?:^|[,\n])\s*['\"]?(\w+)['\"]?\s*:", cur))
    tm = re.search(r"withDefaults\s*\(\s*defineProps<\{(.*?)\}>", script, re.S) or \
        re.search(r"defineProps<\{(.*?)\}>", script, re.S)
    if tm:
        props |= set(re.findall(r"(\w+)\??\s*:", tm.group(1)))
    for m in re.finditer(r"\bprops\.(\w+)((?:\.\w+|\[[^\]]+\])*)\s*(=(?!=)|\+\+|--|\.(?:push|pop|splice|shift|unshift|sort|reverse)\()",
                         script):
        out.append({"check": "prop-mutation", "line": line_of(script, m.start(), base),
                    "prop": m.group(1), "expr": m.group(0)[:80]})
    for p in props:
        for m in re.finditer(r"\bthis\." + p + r"((?:\.\w+|\[[^\]]+\])*)\s*(=(?!=)|\.(?:push|splice)\()", script):
            out.append({"check": "prop-mutation", "line": line_of(script, m.start(), base),
                        "prop": p, "expr": m.group(0)[:80]})
        if re.search(r'v-model="\s*' + p + r'\b', tpl):
            out.append({"check": "v-model-on-prop", "prop": p,
                        "note": "binding v-model to a prop (or its fields) mutates parent state"})
    return out, props


def norm_line(s):
    s = re.sub(r"//.*$", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    if not s or s in ("{", "}", "})", "},", ")", "]", "],", "});", "</div>", "<div>") or \
            s.startswith(("import ", "/*", "*", "<!--")):
        return None
    return s


def find_duplicate_blocks(sources, window=6):
    """sources: {rel: [(lineno, text)]} -> list of clusters of copy-pasted blocks."""
    norm = {}
    for rel, lines in sources.items():
        norm[rel] = [(ln, n) for ln, raw in lines if (n := norm_line(raw))]
    index = defaultdict(list)
    for rel, nl in norm.items():
        for i in range(len(nl) - window + 1):
            h = hashlib.md5("\n".join(x[1] for x in nl[i:i + window]).encode()).hexdigest()
            index[h].append((rel, i))
    covered, clusters = set(), {}
    for h, occ in index.items():
        files = {r for r, _ in occ}
        if len(files) < 2:
            continue
        for a in range(len(occ)):
            for b in range(a + 1, len(occ)):
                (ra, ia), (rb, ib) = occ[a], occ[b]
                if ra == rb or (ra, ia) in covered or (rb, ib) in covered:
                    continue
                k = 0
                while ia + k < len(norm[ra]) and ib + k < len(norm[rb]) and norm[ra][ia + k][1] == norm[rb][ib + k][1]:
                    k += 1
                for j in range(k - window + 1):
                    covered.add((ra, ia + j))
                    covered.add((rb, ib + j))
                key = hashlib.md5("\n".join(x[1] for x in norm[ra][ia:ia + k]).encode()).hexdigest()
                c = clusters.setdefault(key, {"lines": k, "preview": [x[1] for x in norm[ra][ia:ia + 3]],
                                              "locations": set()})
                c["locations"].add(f"{ra}:{norm[ra][ia][0]}-{norm[ra][ia + k - 1][0]}")
                c["locations"].add(f"{rb}:{norm[rb][ib][0]}-{norm[rb][ib + k - 1][0]}")
    result = [{"normalized_lines": c["lines"], "copies": len(c["locations"]),
               "locations": sorted(c["locations"]), "preview": c["preview"]} for c in clusters.values()]
    return sorted(result, key=lambda c: -c["normalized_lines"] * c["copies"])


def scan(src, only=None):
    src = Path(src)
    files = sorted(p for p in src.rglob("*") if p.suffix in (".vue", ".js", ".ts")
                   and not {"node_modules", "dist"} & set(p.parts) and not p.name.endswith(".d.ts"))
    report = {"files_scanned": len(files), "components": [], "template": [], "script": [],
              "duplication": {}}
    code_sources, func_index, css_index, selector_index = {}, defaultdict(list), defaultdict(list), defaultdict(set)
    async_boilerplate = []

    for f in files:
        rel = str(f.relative_to(src))
        text = f.read_text(encoding="utf-8", errors="replace")
        focus = not only or any(rel.startswith(o.rstrip("/")) for o in only)
        if f.suffix == ".vue":
            tpl, tline, scripts, styles = split_sfc(text)
            script_all = "\n".join(s for s, _, _ in scripts)
            api = "script-setup" if any("setup" in a for _, _, a in scripts) else \
                "options-setup()" if re.search(r"\bsetup\s*\(", script_all) else \
                "options" if re.search(r"\b(data|methods|computed)\s*[:(]", script_all) else "none"
            funcs = {}
            for s, sl, _ in scripts:
                funcs.update(script_functions(s, sl))
            if focus:
                report["components"].append({
                    "file": rel, "lines": text.count("\n") + 1,
                    "template_lines": tpl.count("\n"), "script_lines": script_all.count("\n"),
                    "style_lines": sum(s.count("\n") for s, _ in styles), "api": api,
                    "refs": len(re.findall(r"\b(ref|shallowRef)\s*[(<]", script_all)),
                    "reactive": len(re.findall(r"\breactive\s*[(<]", script_all)),
                    "computed": len(re.findall(r"\bcomputed\s*[(<]", script_all)),
                    "watchers": len(re.findall(r"\bwatch(Effect)?\s*\(", script_all)),
                    "functions": len(funcs),
                    "child_components": len(set(re.findall(r"<([A-Z]\w+)", tpl))),
                })
                for item in template_findings(tpl, tline, funcs):
                    report["template"].append({"file": rel, **item})
                for s, sl, _ in scripts:
                    found, _ = script_findings(s, sl, rel, tpl)
                    report["script"].extend({"file": rel, **x} for x in found)
            lines = []
            for s, sl, _ in scripts:
                lines += [(sl + i, l) for i, l in enumerate(s.split("\n"))]
            lines += [(tline + i, l) for i, l in enumerate(tpl.split("\n"))]
            code_sources[rel] = lines
            if re.search(r"\bloading\s*=\s*ref\(", script_all) and re.search(r"\berror\s*=\s*ref\(", script_all) \
                    and "finally" in script_all:
                async_boilerplate.append(f"{rel}:{line_of(text, re.search(r'loading\s*=\s*ref', text).start())}")
            for s, sl in styles:
                for m in CSS_RULE.finditer(s):
                    sel = " ".join(m.group(1).split())
                    decls = sorted(d.strip().lower() for d in m.group(2).split(";") if ":" in d)
                    if sel.startswith(("from", "to", "@")) or re.fullmatch(r"[\d.%, ]+", sel):
                        continue
                    for single in sel.split(","):
                        single = single.strip()
                        if re.fullmatch(r"\.[\w-]+", single):
                            selector_index[single].add(rel)
                    if len(decls) >= 3:
                        css_index["; ".join(decls)].append(f"{rel}:{line_of(s, m.start(1) + len(m.group(1)) - len(m.group(1).lstrip()), sl)} {sel[:60]}")
        else:
            funcs = script_functions(text, 1)
            code_sources[rel] = list(enumerate(text.split("\n"), 1))
            if focus:
                found, _ = script_findings(text, 1, rel, "")
                report["script"].extend({"file": rel, **x} for x in found)
        for name, info in funcs.items():
            func_index[name].append((rel, info))

    report["duplication"]["code_blocks"] = find_duplicate_blocks(code_sources)[:25]
    report["duplication"]["async_state_boilerplate"] = sorted(async_boilerplate)
    same_name = []
    for name, defs in func_index.items():
        files_ = {r for r, _ in defs}
        if len(files_) < 2 or len(name) < 4:
            continue
        bodies = [" ".join(i["body"].split()) for _, i in defs]
        ratios = [difflib.SequenceMatcher(None, bodies[0], b).ratio() for b in bodies[1:]]
        # Same name but unrelated bodies across only two files is usually a wrapper
        # (e.g. a component method calling the api.js function of the same name)
        if len(files_) == 2 and ratios and min(ratios) < 0.4:
            continue
        same_name.append({"function": name, "files": [f"{r}:{i['line']}" for r, i in defs],
                          "min_body_similarity": round(min(ratios), 2) if ratios else 1.0})
    report["duplication"]["same_named_functions"] = sorted(same_name, key=lambda x: -len(x["files"]))
    report["duplication"]["identical_css_rules"] = sorted(
        [{"declarations": k, "locations": v} for k, v in css_index.items() if len({x.split(":")[0] for x in v}) >= 2],
        key=lambda x: -len(x["locations"]))[:20]
    report["duplication"]["class_styled_in_many_files"] = sorted(
        [{"selector": s, "files": sorted(fs)} for s, fs in selector_index.items() if len(fs) >= 3],
        key=lambda x: -len(x["files"]))[:20]
    report["components"].sort(key=lambda c: -c["lines"])
    return report


def print_report(r):
    print(f"Scanned {r['files_scanned']} files. All items are candidates: confirm each in the code.\n")
    print("== Components (largest first) ==")
    print(f"  {'lines':>5} {'tpl':>4} {'js':>4} {'css':>4}  {'api':<15} ref comp watch fn  file")
    for c in r["components"]:
        print(f"  {c['lines']:>5} {c['template_lines']:>4} {c['script_lines']:>4} {c['style_lines']:>4}  "
              f"{c['api']:<15} {c['refs']:>3} {c['computed']:>4} {c['watchers']:>5} {c['functions']:>2}  {c['file']}")
    apis = {c["api"] for c in r["components"]}
    if len(apis) > 1:
        print(f"  mixed API styles: {', '.join(sorted(apis))}")
    print(f"\n== Template candidates ({len(r['template'])}) ==")
    for t in sorted(r["template"], key=lambda x: (x["check"], x["file"], x.get("line", 0))):
        if t["check"] == "function-calls-per-row":
            continue
        extra = {k: v for k, v in t.items() if k not in ("check", "file", "line")}
        print(f"  [{t['check']}] {t['file']}:{t.get('line', '?')}  {json.dumps(extra)[:160]}")
    rows = [t for t in r["template"] if t["check"] == "function-calls-per-row"]
    if rows:
        print(f"\n== Functions called per row inside v-for ({len(rows)} loops; inspect only for big lists or costly bodies) ==")
        for t in rows:
            print(f"  {t['file']}:{t['line']}  {t['v_for'][:50]}  -> {', '.join(t['functions'])}")
    print(f"\n== Script candidates ({len(r['script'])}) ==")
    for s in sorted(r["script"], key=lambda x: (x["check"], x["file"])):
        extra = {k: v for k, v in s.items() if k not in ("check", "file", "line")}
        print(f"  [{s['check']}] {s['file']}:{s.get('line', '?')}  {json.dumps(extra)[:140]}")
    d = r["duplication"]
    print(f"\n== Copy-pasted code blocks ({len(d['code_blocks'])}, >=6 matching normalized lines) ==")
    for c in d["code_blocks"]:
        print(f"  {c['normalized_lines']} lines x{c['copies']}: {', '.join(c['locations'])}")
        print(f"      {' | '.join(c['preview'])[:140]}")
    ab = d["async_state_boilerplate"]
    if len(ab) >= 2:
        print(f"\n== loading/error/try-finally state hand-rolled in {len(ab)} components (composable candidate) ==")
        print("  " + ", ".join(ab))
    print(f"\n== Same-named functions in several files ({len(d['same_named_functions'])}) ==")
    for f in d["same_named_functions"]:
        print(f"  {f['function']:<28} similarity>={f['min_body_similarity']:<5} {', '.join(f['files'])}")
    print(f"\n== Identical CSS rule bodies across files ({len(d['identical_css_rules'])}) ==")
    for c in d["identical_css_rules"]:
        print(f"  x{len(c['locations'])} {{{c['declarations'][:90]}}}")
        for loc in c["locations"][:6]:
            print(f"      {loc}")
    print(f"\n== Same class styled in 3+ files ({len(d['class_styled_in_many_files'])}) ==")
    for c in d["class_styled_in_many_files"]:
        print(f"  {c['selector']:<24} {len(c['files'])} files: {', '.join(c['files'])}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only")
        only = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        args = args[:1]
    result = scan(args[0], only)
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, default=list))
    else:
        print_report(result)
