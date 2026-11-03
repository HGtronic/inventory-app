---
name: saas-sidebar-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - replace the top navigation bar with a vertical left sidebar, introduce a consistent spacing/color/typography token system, and polish page headers, cards, tables, filters and form controls across every view without changing app behavior. Use this skill whenever the user wants to modernize, restyle, refresh, re-skin or "make professional" a Vue 3 / Vite frontend, move navigation into a sidebar, build an app shell or admin/dashboard layout, fix inconsistent spacing or padding across pages, or make a Vue app look like a polished SaaS product - even if they never say "sidebar" or "redesign".
---

# SaaS Sidebar Redesign (Vue 3)

Turn a Vue 3 app with a top nav bar into a modern SaaS layout: a fixed left sidebar for navigation, a slim top bar for page context and utilities, and a content area where every view follows one spacing and typography system.

**The one rule that matters most:** this is a visual redesign. Routes, data fetching, props/emits, filter state, i18n keys and event handlers keep working exactly as before. A broken filter or a dropped profile menu is a regression that screenshots won't show, so treat behavior preservation as the definition of done, with looks second.

## Workflow

Work through these phases in order. The survey matters most: most failed redesigns come from something nobody noticed in the old header.

### 1. Survey the app before touching anything

Read, don't edit yet. Collect:

- **Project rules.** Read `CLAUDE.md`, `.claude/agents/*`, `README`, any `docs/` design notes. They can mandate things like "delegate .vue edits to agent X", "no emojis in UI", or a fixed palette. **An existing design system or palette wins over this skill's defaults.** Your job is to apply it consistently, not to replace it.
- **Routes.** Find the router (`src/main.js`, `src/router/index.{js,ts}`). The route list becomes the sidebar's nav items. Note paths, names and any `meta`.
- **The current shell.** Usually `App.vue` or `src/layouts/*`. List *every* element in the header: brand/logo, subtitle, nav links, global filters, language switcher, profile/user menu, notifications, search. Each one needs a new home in the plan. Nothing gets silently dropped.
- **Global styles.** Find where shared classes live (unscoped `<style>` in `App.vue`, `src/assets/main.css`, `style.css`). These shared classes (`.card`, `.page-header`, `table`, `.badge`...) are your highest-leverage edit points.
- **Styling stack.** Plain CSS / scoped styles? Tailwind? A component library (Vuetify, PrimeVue, Element Plus, Naive UI)? With a library, use its own primitives (e.g. `v-navigation-drawer`, its theme tokens) instead of hand-rolling. The CSS in this skill's references is for plain-CSS apps, and for library apps it serves only as a visual target.
- **Hidden layout coupling.** Run the audit script (below) or grep for values tied to the old header's height: `top: 70px`, `calc(100vh - 64px)`, `scroll-margin-top`, `position: sticky|fixed`, and `z-index`. When the header changes height or moves, these break silently. Typical cases are a sticky filter bar sitting at the wrong offset or a modal ending up behind the sidebar.
- **Component style.** Does the codebase use `<script setup>` or `setup()` in Options syntax? JS or TS? Match it in any new component.

Run the bundled audit to get spacing/color inconsistencies and coupling in one pass:

```bash
python3 <this-skill-dir>/scripts/audit_styles.py <path-to-client>/src
```

It prints raw spacing values that fall off a 4px scale, the distinct hardcoded colors, and lines that look coupled to header height. Use it again at the end to confirm the cleanup.

Then **write a short plan** (in your reply or a scratch file) covering: the shell layout, where each header element moves, the token values (derived from the existing palette), and the files you'll touch. If the project requires delegating `.vue` edits to a specialist subagent, this plan is what you hand over, together with the relevant reference files. If you can't delegate (for example you are already a subagent), do the edits yourself.

### 2. Establish design tokens

Read `references/tokens.md`. Define CSS custom properties on `:root` in the global stylesheet: spacing (4px base), neutral and accent colors, status colors, radii, shadows, type scale, and layout dimensions (`--sidebar-width`, `--topbar-height`, ...).

Derive the values from what's already there. Keep the app's accent color and map its existing grays onto the neutral scale. Tokens exist so that "consistent spacing" is enforceable. Once they exist, every later edit should reach for a token rather than a raw value.

### 3. Build the app shell

Read `references/shell.md`. It contains a sidebar component, the layout CSS and the responsive behavior. In short:

- **Layout:** CSS grid with two columns (sidebar | main). The sidebar is sticky and full height. The main column holds a sticky top bar and the scrolling content. Global filters belong *inside* the main column (in the top bar or a sub-bar beneath it), never spanning under the sidebar.
- **Sidebar:** brand at the top. Nav items are generated from one array (path, label, icon), optionally grouped into sections. Utilities (language, profile, settings) go in the sidebar footer or the top bar. Choose one place and be consistent.
- **Active state:** use `router-link`'s built-in classes (`router-link-active` / `router-link-exact-active`). The root route `/` must match exactly, or "Overview" stays highlighted on every page.
- **Icons:** inline SVG, 18-20px, `stroke="currentColor"`, so color follows text state. Don't add an icon dependency unless the project already has one, and never use emojis as icons.
- **Collapsible + responsive:** a collapse toggle shrinks the sidebar to icon-only (remember the choice in `localStorage`, wrapped in try/catch). Below ~1024px the sidebar becomes an off-canvas drawer opened from a menu button in the top bar, with an overlay. It closes on route change, overlay click and Escape.
- **Accessibility:** `<nav aria-label="Main">`, `aria-current="page"` on the active link (router-link adds it), visible `:focus-visible` rings, and `aria-label`/`title` on icon-only items.

Move the old header's contents to their planned homes, then delete the old header markup *and* its CSS so no dead styles linger.

### 4. Polish the views

Read `references/components.md`. Work from the largest leverage point down:

1. **Shared/global classes first.** Rewrite `.page-header`, `.card`, `.stat-card`, tables, badges, buttons, inputs/selects, and loading/error/empty states using tokens. One edit here restyles every page.
2. **Then each view's scoped styles.** Replace raw spacing and colors with tokens where they map cleanly (`1.25rem` → `var(--space-5)`, `#64748b` → `var(--color-text-muted)`). Fix layout assumptions the old shell imposed, such as `max-width: 1600px; margin: 0 auto` on content that now sits beside a sidebar.
3. **Templates only where needed.** Keep class names that JS, tests or other components depend on. Don't restructure markup for its own sake. When you must (e.g. adding a page-header actions slot), keep the bindings untouched.

Consistency rules that make it look professional:
- One page gutter (`--space-8` desktop, `--space-4` mobile), applied in one place: the content container, not each view.
- One grid gap for card/stat grids (`--space-6`), one card padding (`--space-6`), one section spacing (`--space-8`).
- Page title, subtitle and actions laid out the same way on every page.
- Numbers in tables and stats use `font-variant-numeric: tabular-nums`.
- Prefer borders + very subtle shadows over heavy shadows, and restrained color: accent for active/primary only, status colors for status only.

Leave charts' geometry alone. Only swap hardcoded colors for tokens if that is trivial and safe.

### 5. Verify

Don't report done until all of these pass:

1. **Build:** `npm run build` (or the project's build script) succeeds with no new warnings about missing components or imports.
2. **Every route renders:** start the dev server and visit each route. Use Playwright MCP tools if available; otherwise use whatever browser tooling exists. If none exists, say so explicitly rather than claiming visual verification.
3. **Check at desktop (1440×900) and mobile (390×844)** on each route:
   - the sidebar lists every route, and exactly one item is active, the correct one
   - no element overlaps another (especially formerly-sticky bars) and there is no horizontal page scroll
   - dropdowns and the profile menu aren't clipped by `overflow: hidden` on the sidebar
   - modals open *above* the sidebar and the top bar (z-index)
   - the mobile drawer opens, closes on navigation, and closes on Escape
4. **Behavior:** change a global filter and confirm data still updates. Open each modal that was reachable from the old header.
5. **Console:** no new errors or Vue warnings.
6. **Re-run the audit script** and confirm off-scale spacing dropped substantially.

Save screenshots of each route (desktop + mobile) if the user or the environment wants artifacts.

### 6. Report

Summarize briefly:
- the new layout, and where each old header element now lives
- the token system (point to where it's defined)
- files changed, with one line each
- verification results: build, routes checked, console state, screenshots location
- anything deliberately left alone (charts, third-party widgets) or not verified

## Common pitfalls

- **Overview always highlighted:** the `/` link matches every route unless you use exact matching.
- **Sticky offsets:** a filter bar with `top: 70px` floats in the wrong place once the header is gone. Switch it to `top: var(--topbar-height)` or make it part of the top bar.
- **Content too wide or double-padded:** views that still center themselves with `max-width` and padding, inside a content area that also pads.
- **Sidebar scroll traps:** give the nav list `overflow-y: auto` and keep the footer pinned. Don't put `overflow: hidden` on the whole sidebar if dropdowns open from it.
- **Modal stacking:** modals need a z-index above the sidebar and top bar. Use the `--z-*` tokens.
- **Lost utilities:** the language switcher or profile menu vanishes because it was only in the old header. Check it against your survey list.
- **Hardcoded labels → i18n:** if nav labels used `t('nav.x')`, keep using those keys. Don't hardcode English over them.
