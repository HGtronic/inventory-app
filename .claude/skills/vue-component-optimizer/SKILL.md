---
name: vue-component-optimizer
description: Analyze the component structure of a Vue 3 app and recommend prioritized, evidence-backed optimizations for runtime performance (slow lists, needless re-renders, reactivity misuse, leaks), code reuse (copy-pasted logic that should be composables, repeated markup that should be shared components, duplicated styles and helpers) and maintainability (oversized components, prop drilling, prop mutation, mixed API styles). It writes a findings report with file:line evidence and concrete fixes, then applies only the fixes the user picks and verifies them. Use this skill whenever someone asks to audit, review, analyze or "clean up" Vue components, asks why a Vue page or list is slow or sluggish, wants to find duplicated code or refactor for reuse, asks what should become a composable or shared component, or wants a Vue codebase health check, even if they never say "optimize". Not for visual redesigns, and bundle size or lazy loading only when asked.
---

# Vue component optimizer

The job is to find what's actually worth changing in a Vue 3 codebase, prove each point with evidence from the code, rank it so the user knows what to do first, and only then change code they've agreed to.

The value of the report depends on its precision. A report with 40 generic tips ("use computed", "consider v-memo") is worse than one with 8 findings that are each real, located and sized. Every finding you write should survive the user opening the file at the line you cite. When you're unsure whether something matters, check (count the rows, read the function, find the data source) instead of hedging in the report.

## Workflow

### 1. Scope and ground rules

- **Work out what's being asked.** Is it the whole app, one view, or one component? Does the user want a report only, a report and then fixes, or fixes now ("fix the worst performance problems")? If they've already said which fixes to apply, you'll skip the question in step 5.
- **Read the project's rules** before anything else: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, lint config. They may mandate who edits `.vue` files (for example a delegated subagent), a preferred API style, or comment conventions. Your suggestions and your edits both have to fit those rules.
- **Check versions** in `package.json`: Vue minor version (3.4 added `defineModel` and smarter computed triggering; 3.5 made destructured `defineProps` reactive), vue-router, any state library (Pinia), and existing helpers like VueUse. Don't suggest things the installed version can't do, and prefer what the project already depends on over new dependencies.

### 2. Map the codebase

Run the scanner on the source directory:

```bash
python3 <skill-dir>/scripts/scan_components.py <app>/src            # human-readable
python3 <skill-dir>/scripts/scan_components.py <app>/src --json     # for scripting
python3 <skill-dir>/scripts/scan_components.py <app>/src --only views/Orders.vue   # scoped run
```

It lists component sizes and API styles, template and script candidates (index keys, `v-if`+`v-for`, array work in templates, per-row calls, deep watchers, listeners without cleanup, prop mutation), and cross-file duplication (copy-pasted blocks, same-named helpers, identical CSS rules, hand-rolled loading/error state). With `--only`, duplication is still computed across the whole tree, so a scoped review still sees that a component's helper exists elsewhere.

**Everything it prints is a candidate, not a finding.** It can't tell a 5-row list from a 5,000-row one, a trivial function from an expensive one, or deliberate divergence from accidental. That judgment is your job in step 3.

Then read what the scanner can't see:

- **Where data comes from and how big it gets.** Find the API calls, mock data or fixtures, and estimate realistic list sizes. A performance finding without a size estimate is a guess. Say "Inventory renders all ~3,000 items unpaginated (server/data/inventory.json)" rather than "large lists may be slow".
- **What's already shared**: `composables/`, `utils/`, `components/` (base/shared ones), global CSS. A reuse finding should point at an existing helper when one exists ("Spending.vue redefines `formatCurrency` instead of importing `utils/currency.js`").
- **The router and the app shell**, to know which components mount often, which stay mounted, and which views are reachable at all (unrouted views are dead code).

### 3. Confirm candidates and look for more

Read the code at every candidate location. Keep it if it's real and matters; drop it otherwise. Remember the dropped ones: they go in the "Checked and left alone" section so the user sees you looked.

Use the reference files for the patterns, what to look for that the scanner misses, and, just as important, when **not** to flag something:

- `references/performance.md`: keys, `v-if`/`v-for`, derived data, per-row lookups, watchers, reactivity depth, big lists, render scope, leaks, redundant fetches
- `references/reuse.md`: composables, utilities, shared components, shared styles, the rule of three, diverged copies
- `references/structure.md`: oversized components, prop drilling, prop mutation, API-style mix, dead code

Two things raise a finding's value and are easy to miss:

- **Diverged copies.** When a helper is copied into several files, diff the copies. If one handles `null` and another doesn't, or one rounds and another truncates, that's an inconsistency bug users can already see, not just duplication.
- **Correctness hidden as performance.** An index key on a list whose rows hold local state (inputs, checkboxes, expanded state) is a bug: state stays with the position when the list is sorted or filtered. A `v-if` beside `v-for` on the same element doesn't do what it looks like in Vue 3, because `v-if` is evaluated first. Rank these by the bug, not the speed.

### 4. Prioritize and write the report

**Severity** (rank by real-world impact, not by how textbook the pattern is):

- **High**: a correctness bug or likely bug (state on the wrong row, prop mutation leaking into parent state, a leak in a frequently mounted component, copies that already behave differently), or a slowdown users will feel with realistic data (O(n×m) work per render on a large list, a deep watcher over thousands of objects, thousands of rows rendered at once).
- **Medium**: real but bounded cost, or duplication that slows every future change (boilerplate repeated in 3+ files, a component mixing several responsibilities that are hard to change independently).
- **Low**: hygiene and consistency (API-style mix, untyped props, small helpers duplicated twice).

**Effort**: S (under an hour, local change), M (a new composable or component plus migrating its users), L (touches many files or needs design decisions).

Write the report to a file: `vue-optimization-report.md` at the project root unless the user names another place. Then give a short summary in chat: counts by severity, the top three things to do, and the file path. Use this structure:

```markdown
# Vue component review: <app or scope>

## Summary

<scope (files reviewed), version notes, 2-3 sentences on the overall picture>

| ID  | Finding                                               | Category    | Severity | Effort | Where                  |
| --- | ----------------------------------------------------- | ----------- | -------- | ------ | ---------------------- |
| P1  | Inventory table keyed by index while rows hold inputs | Performance | High     | S      | views/Inventory.vue:52 |
| R1  | ...                                                   | Reuse       | Medium   | M      | 8 views                |

**Recommended order:** P1, R2, P3 ... (quick high-value wins first, then the ones that unblock others)

## Performance

### P1. <title>

- **Where:** `views/Inventory.vue:52` (and every copy, each with file:line)
- **Evidence:** <short code excerpt, counts, data size>
- **Why it matters:** <the concrete consequence in this app, not the general rule>
- **Suggested change:** <code sketch of the fix, adapted to this codebase's style>
- **Risk:** <behavior that could change, things to test>

## Reuse

### R1. ...

## Structure

### S1. ...

## Checked and left alone

- `components/LanguageSwitcher.vue:34` index-free loop over 2 locales calling `getLanguageName`: trivially cheap, not worth changing.
- ...
```

Number findings by category (P, R, S) so the user can answer "do P1, P3 and R2". Keep each finding tight. The code sketch matters more than the prose. Merge findings that share one fix ("the six modals each re-implement overlay, header, close button and Escape handling" is one reuse finding with six locations, not six findings).

### 5. Offer fixes

Unless the user already told you what to apply (or asked for a report only), stop after the report and ask which findings to apply. Recommend a set: usually the High items plus cheap Mediums. If you have a question tool, use a multi-select listing the finding IDs and titles. Otherwise list them and ask.

If the user said up front to fix things ("fix the top performance issues", "go ahead and refactor the duplication"), apply that subset without asking again. Say in the report which findings you applied, and leave the rest as suggestions.

### 6. Apply the chosen fixes

- **Delegate if the project requires it.** If its rules say `.vue` edits go to a specific subagent, delegate each change with the finding text, file:line and suggested change. Otherwise do it yourself.
- **One finding at a time,** smallest behavior-preserving change. Don't fold unrelated cleanups into a fix.
- **Preserve interfaces:** props, emits, slots, exposed methods, route names, CSS classes other files or tests depend on, the values a view renders. A reuse refactor is done when every consumer renders exactly what it rendered before.
- **Match the file's existing style.** A performance fix in an Options-API `setup()` component stays in that style. Converting API styles is its own finding, and only done if the user picked it.
- **Add short comments for non-obvious changes** (why a `shallowRef`, why a Map lookup), especially if the project asks for that.
- **Verify after the batch:** run the build, run the existing tests, re-run the scanner to confirm the candidates are gone, and if you can run the app, exercise the affected screens (sort/filter the list, open and close the modal, submit the form) and watch the console for Vue warnings. For performance fixes, a before/after measurement on realistic data (render time, number of renders, request count) is more convincing than an assertion.
- **Update the report:** add a "Status" column (Applied / Not applied) and an "Applied changes and verification" section listing the files changed and how you verified them, including anything you couldn't verify.

## Things that make reports worse

- **Generic advice without a location.** "Consider using `v-memo`" isn't a finding. If you can't name the file and say why it matters there, leave it out.
- **Micro-optimizations ranked high.** A cheap formatter called per row in a 20-row table doesn't matter. Reserve High for things a user or a future developer will actually feel.
- **Premature abstraction.** Two similar blocks that change for different reasons should stay separate. Use the rule of three, and prefer a small composable over a configurable mega-component with ten boolean props.
- **Recommending new dependencies casually.** Suggest a virtual scroller only when the list size justifies it, and say what you'd use.
- **Silent behavior changes.** If a fix changes what users see (a sort becomes stable, a fixed bug changes output), say so in the finding and in the summary.
