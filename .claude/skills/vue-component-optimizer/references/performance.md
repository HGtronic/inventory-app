# Runtime performance patterns

Each pattern has: what to look for, why it matters, the fix, and when **not** to flag it. Size is the deciding factor for most of these, so always estimate how many items or renders are involved before ranking.

## Contents

1. Keys in `v-for`
2. `v-if` and `v-for` on the same element
3. Derived data recomputed instead of cached
4. Per-row lookups and O(n×m) work
5. Expensive formatting per row
6. Watchers: deep, redundant, or doing a computed's job
7. Reactivity depth for large read-only data
8. Rendering big lists all at once
9. Unstable props and render scope
10. Leaks: listeners, intervals, observers, subscriptions
11. Redundant or racing fetches
12. Smaller items

---

## 1. Keys in `v-for`

**Look for:** `v-for` without `:key`, or `:key="index"` / `:key="i"` on a list that can be sorted, filtered, inserted into or removed from.

**Why:** Vue reuses DOM and component instances by key. With index keys, after a sort or delete the instance that held row 3's state now shows row 4's data. This matters most when rows contain inputs, checkboxes, expanded/collapsed state, child components with local state, or transitions, because then it's a visible **bug**, not a speed issue. Without state it still causes more DOM patching than needed.

**Fix:** Key by a stable unique id from the data (`item.id`, `sku`, `order.id + '-' + line.sku`). If the data truly has none, derive one when loading (don't use `Math.random()` in the template, which remounts every render).

**Don't flag:** static lists that never reorder (`v-for="n in 5" :key="n"` skeleton placeholders, hardcoded nav items, a fixed set of months), or an index key on a read-only, stateless sub-list that's always replaced wholesale. Mention it as Low at most.

**Severity:** High if rows hold state and the list can reorder/filter; Medium for large dynamic stateless lists; otherwise Low or skip.

## 2. `v-if` and `v-for` on the same element

**Look for:** `<li v-for="u in users" v-if="u.active">`.

**Why:** In Vue 3, `v-if` has higher precedence than `v-for`, so the condition runs before `u` exists. It either throws ("Property 'u' was accessed during render but is not defined") or silently uses an outer variable. In Vue 2 the precedence was reversed, so this often appears in migrated code. When the condition doesn't depend on the item (`v-if="showList"`), it works but reads ambiguously.

**Fix:** Filter in a computed (`activeUsers`) and loop over that, or move the `v-if` to a wrapping `<template v-for>` / inner element.

**Severity:** High when the condition references the loop variable (it's broken); Low when it doesn't.

## 3. Derived data recomputed instead of cached

**Look for:**

- a method that filters/sorts/aggregates and is called from the template (`{{ filteredProducts().length }}` and `v-for="p in filteredProducts()"`): it runs on **every** render, once per call site
- array work inline in the template or in the `v-for` source (`v-for="x in items.filter(...).sort(...)"`)
- `.sort()` on a reactive array in a template or computed. It sorts in place, which mutates state during render and can trigger render loops. Copy first (`[...items].sort()` or `toSorted()`).

**Why:** `computed` caches until its dependencies change. Methods and inline expressions re-run whenever the component re-renders for **any** reason (typing in an unrelated input, a timer, a hover state).

**Fix:** Move the derivation into a `computed`. For a family of variants (`getForecastsByTrend('increasing')`, `('stable')`, `('decreasing')`), compute one grouped object (`forecastsByTrend.value.increasing`) instead of three method calls each scanning the list.

**Don't flag:** methods that take the row as an argument and do O(1) work (`getStatusClass(order.status)`); `computed` can't take arguments and caching them gains nothing.

**Severity:** Medium usually; High when the list is large and the component re-renders often (search input, timers), or when an in-place sort mutates state.

## 4. Per-row lookups and O(n×m) work

**Look for:** inside `v-for` (in the template or in a function called per row): `.find()`, `.filter()`, `.some()`, `.includes()` over **another** collection (`categories.find(c => c.id === p.categoryId)`), `indexOf` on big arrays, or building a map/regex/date object per row.

**Why:** 2,000 products × 50 categories = 100,000 comparisons per render, repeated on each keystroke in a search box.

**Fix:** Build a lookup once in a computed (`const categoryById = computed(() => new Map(categories.value.map(c => [c.id, c])))`) and use `categoryById.value.get(p.categoryId)`. Or join the data once when it loads.

**Don't flag:** lookups into tiny fixed tables (a 5-entry status map), or small lists (tens of rows).

## 5. Expensive formatting per row

**Look for:** `new Intl.NumberFormat(...)` / `new Intl.DateTimeFormat(...)` created inside a function called per row; `toLocaleString(locale, options)` with an options object in hot loops; `new Date(str)` parsing repeated for the same row in several cells.

**Why:** Creating Intl formatters is expensive (much more than using one). At thousands of cells per render it shows up in profiles.

**Fix:** Create formatter instances once at module level (or in a computed keyed by locale/currency if those are reactive) and call `.format()`.

**Don't flag:** this in small tables. A shared formatter is still good for reuse reasons (see reuse.md), but don't call it a performance problem below a few hundred cells.

## 6. Watchers: deep, redundant, or doing a computed's job

**Look for:**

- `watch(bigArray, ..., { deep: true })` or watching a `reactive()` object that holds a large dataset. Deep watching traverses the whole structure on every change.
- a watcher whose only job is to assign another ref from its source (`watch(items, v => total.value = sum(v))`). That's a `computed`.
- `watch(filters, load, { immediate: true })` **plus** `onMounted(load)`, which fetches twice on mount.
- watchers that trigger a fetch on every keystroke without debounce.

**Fix:** Replace derive-and-assign watchers with `computed`. Watch the specific fields that matter (`() => [filters.status, filters.month]`), not the whole object deeply. Keep one source of the initial load. Debounce text-driven fetches (250-400 ms).

**Don't flag:** `deep: true` on a small settings object (a handful of fields) persisted to localStorage. That's fine and idiomatic.

## 7. Reactivity depth for large read-only data

**Look for:** thousands of objects loaded into `ref([...])` / `reactive` that are only ever replaced wholesale, never mutated field by field (API results, chart series, lookup tables).

**Why:** `ref` makes every nested object a reactive proxy. That costs memory and slows access in hot loops.

**Fix:** `shallowRef` (replace `.value` to update) or `markRaw` for immutable lookup data. Comment the reason, since a later field-level mutation would silently stop updating the UI.

**Don't flag:** small or medium data (hundreds of rows); data whose fields are edited in place (inline-editable tables). Recommend only with a size estimate.

## 8. Rendering big lists all at once

**Look for:** `v-for` over a list that can hold more than ~500-1,000 rows with non-trivial row markup, with no pagination, "load more" or virtualization.

**Fix, in order of preference:**

1. Paginate or limit server-side if the API supports it (often it should anyway).
2. Client-side pagination or "show more" (a computed slice).
3. Virtual scrolling (`@tanstack/vue-virtual`, `vue-virtual-scroller`) when users really need to scroll everything. It changes layout and accessibility semantics (find-in-page, row heights), so it's a bigger change.

`v-memo` on rows can help when a big list re-renders but few rows change. It's a niche tool: mention it only when that's precisely the situation, and list exactly which dependencies go in the memo array.

## 9. Unstable props and render scope

**Look for:**

- inline objects, arrays or arrow functions passed as props to child **components** inside a loop (`<ProductRow :options="{ currency: 'USD' }">`, `:format="v => v.toFixed(2)"`). A new identity each render makes every child re-render even when nothing changed.
- a fast-changing value (clock, mouse position, a search input's text, an animation frame) held in a big parent component, so the whole parent template re-renders on each change.

**Fix:** Hoist constant objects to module scope or a computed. Move fast-changing state into a small child component (e.g. a `SearchBox` that emits a debounced query), so only that child re-renders.

**Don't flag:** inline objects on plain elements (`:style="{ width: x + '%' }"` on a `<div>`), which is normal; or inline props on a handful of light children.

## 10. Leaks: listeners, intervals, observers, subscriptions

**Look for:** `window`/`document` `addEventListener`, `setInterval`, `IntersectionObserver`/`ResizeObserver`, websocket or event-bus subscriptions created in `onMounted`/`mounted`/`setup` without matching cleanup in `onUnmounted`/`onBeforeUnmount`. Also handlers added with an inline arrow function, which can't be removed because the reference differs.

**Why:** Each mount adds another listener. After navigating back and forth, handlers fire N times, run against unmounted components, and keep them in memory.

**Fix:** Keep a reference to the handler and remove it in `onUnmounted`, or clear the interval or disconnect the observer. A small `useEventListener` composable (or VueUse's, if present) prevents the whole class of bug.

**Severity:** High for components that mount repeatedly (routed views, modals, list rows); Medium for the root App.

## 11. Redundant or racing fetches

**Look for:** the same endpoint fetched by several components on one screen; refetching on filter changes the endpoint ignores; no guard against out-of-order responses when filters change quickly (an older slow response overwriting a newer one).

**Fix:** Lift the fetch to the parent or a shared composable or store; only watch the filters the endpoint uses; track a request id or use `AbortController` so stale responses are dropped.

## 12. Smaller items (usually Low)

- `v-show` vs `v-if`: frequently toggled panels are cheaper with `v-show`; rarely shown heavy content (modals, tabs never opened) is cheaper with `v-if`.
- Large static subtrees re-rendered with their parent: `v-once` for content that never changes after first render.
- Destructuring a `reactive()` object or a composable's returned reactive state loses reactivity (use `toRefs`). Since Vue 3.5, destructured `defineProps` in `<script setup>` stays reactive; in earlier versions it doesn't. Check the version before flagging.
- `computed` with side effects (fetching, mutating other state), which should be watchers or actions.
