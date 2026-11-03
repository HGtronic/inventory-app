# Structure and maintainability patterns

These findings are about how easy the code is to change safely. They rarely justify High severity on their own, except where they hide bugs (prop mutation) or block other fixes.

## 1. Oversized components

Line count is a symptom, not the problem. A 900-line component that is mostly a long CSS block is less concerning than a 400-line one juggling five unrelated concerns.

**Look for:** components where the template has several independent sections with their own state and handlers (a KPI row, a chart, a table with its own sorting and pagination, a modal launcher); scripts with many unrelated refs/computed/functions; long `<style>` blocks for sub-sections.

**Fix:** Name the seams. For each section, say what moves where:

- a section of template + its state + handlers → a child component (with the props it needs and the events it emits)
- logic shared or reusable across sections → a composable
- styles move with their markup

Give the resulting rough structure ("Dashboard.vue → `KpiCards`, `OrderHealthChart`, `TopProductsTable`, `BacklogPanel` + `useDashboardData`") and note what state must stay in the parent (shared filters, data loaded once and passed down).

**Severity:** Medium when the component mixes several responsibilities that are edited independently; Low otherwise. Effort is usually M or L.

## 2. Prop mutation and v-model on props

**Look for:** `props.filters.status = 'x'`, `props.items.push(...)`, `this.value = ...` on a prop, `v-model="someProp"` or `v-model="someProp.field"` in a child.

**Why:** Vue only warns on reassigning a top-level prop. Mutating a prop's nested fields **silently** changes the parent's state, so data flows in both directions and becomes hard to trace. It's a common source of "the filter changed by itself" bugs.

**Fix:** Emit an event (`emit('update:filters', { ...props.filters, status })`), use `defineModel()` (Vue 3.4+), or copy into local state when the child needs a draft (`const draft = ref({ ...props.filters })`) and emit on save.

**Severity:** High if the parent's state actually changes unexpectedly or other components read it; Medium otherwise.

## 3. Prop drilling

**Look for:** a prop passed through two or more components that don't use it, only forward it (App → Layout → Sidebar → UserBadge).

**Fix:** `provide`/`inject` for tree-scoped values (current user, theme, form context), a composable with shared module-level state, or the project's store (Pinia) if it has one. Keep explicit props for things the intermediate components should know about.

**Don't flag:** one level of passing, or intermediate components that use the prop themselves.

## 4. Mixed API styles

**Look for:** some components in `<script setup>`, others in Options API or `setup()` returning objects. The scanner's components table shows this.

**Why:** It's a consistency and onboarding cost, not a performance issue. `<script setup>` compiles to slightly leaner code, but that's negligible.

**Fix:** Recommend a direction (usually `<script setup>` for Vue 3 projects) and converting **opportunistically**, when a file is being changed anyway. Never as part of a performance or reuse fix.

**Severity:** Low.

## 5. Undeclared or untyped interfaces

- emitted events not declared in `defineEmits` / `emits` (fallthrough to root listeners, no docs)
- props without types or defaults where the component clearly assumes a shape
- components reaching into parents (`$parent`) or children (`$refs` used for data rather than DOM)

**Severity:** Low, unless it's causing a real bug (a declared-but-wrong default, for instance).

## 6. Dead code

**Look for:** components never imported, views not registered in the router, functions or computed never referenced, unused imports, commented-out blocks. Grep before claiming something is unused, including dynamic imports, string-based component names and route definitions.

**Fix:** Delete it (it stays in git history). If it's a half-finished feature, ask rather than delete.

**Severity:** Low, but list it, since it's cheap to fix and it pollutes searches and duplication counts.

## 7. Global state in composables

A composable that defines refs at module level (outside the function) shares one state across every caller. That's often deliberate (a filter bar driving every view), so don't flag it as a bug. Only flag it if a component uses it expecting independent state (two instances on one page interfering).
