# App shell: sidebar + top bar + content

Contents
1. Layout structure
2. `AppSidebar.vue` template
3. `App.vue` shell wiring
4. Layout CSS
5. Responsive behavior
6. Where things go

Adapt names, script style (`<script setup>` vs `setup()`), and JS/TS to match the project.

---

## 1. Layout structure

```
┌────────────┬─────────────────────────────────────────┐
│ Brand      │ Top bar: [menu] Page title    utilities │  ← sticky, --topbar-height
│            ├─────────────────────────────────────────┤
│ Nav item   │ Filter sub-bar (optional, sticky)       │  ← top: var(--topbar-height)
│ Nav item ● │─────────────────────────────────────────│
│ Nav item   │                                         │
│            │   <router-view />                       │
│ ─ section  │   inside .content (max-width, gutter)   │
│ Nav item   │                                         │
│            │                                         │
│ [footer:   │                                         │
│  user/lang]│                                         │
└────────────┴─────────────────────────────────────────┘
  --sidebar-width
```

## 2. `AppSidebar.vue`

Put it in `src/components/` (or `src/layouts/` if the project has one). The nav items are props, so the sidebar knows nothing about specific routes.

```vue
<template>
  <aside
    class="sidebar"
    :class="{ 'is-collapsed': collapsed, 'is-open': mobileOpen }"
  >
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true">{{ brandInitial }}</div>
      <div v-if="!collapsed" class="brand-text">
        <span class="brand-name">{{ brandName }}</span>
        <span v-if="brandSubtitle" class="brand-subtitle">{{ brandSubtitle }}</span>
      </div>
    </div>

    <nav class="sidebar-nav" aria-label="Main">
      <template v-for="section in sections" :key="section.id">
        <div v-if="section.label && !collapsed" class="nav-section-label">
          {{ section.label }}
        </div>
        <router-link
          v-for="item in section.items"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ 'is-active': isActive(item) }"
          :title="collapsed ? item.label : undefined"
          :aria-label="collapsed ? item.label : undefined"
          @click="$emit('navigate')"
        >
          <span class="nav-icon" aria-hidden="true" v-html="item.icon" />
          <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" :collapsed="collapsed" />
      <button
        type="button"
        class="collapse-toggle"
        :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        @click="$emit('toggle-collapse')"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"
             :style="{ transform: collapsed ? 'rotate(180deg)' : 'none' }">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  // [{ id, label?, items: [{ to, label, icon (SVG string), exact? }] }]
  sections: { type: Array, required: true },
  brandName: { type: String, required: true },
  brandSubtitle: { type: String, default: '' },
  collapsed: { type: Boolean, default: false },
  mobileOpen: { type: Boolean, default: false }
})
defineEmits(['toggle-collapse', 'navigate'])

const route = useRoute()
const brandInitial = computed(() => props.brandName.trim().charAt(0).toUpperCase())

// The root path must match exactly, otherwise it is "active" on every page.
// Other items also match nested paths (e.g. /orders/123 keeps "Orders" lit).
const isActive = (item) => {
  if (item.exact || item.to === '/') return route.path === item.to
  return route.path === item.to || route.path.startsWith(item.to + '/')
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  z-index: var(--z-sidebar);
  transition: width var(--transition-base);
}
.sidebar.is-collapsed { width: var(--sidebar-width-collapsed); }

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.brand-mark {
  width: 32px; height: 32px;
  display: grid; place-items: center;
  border-radius: var(--radius-md);
  background: var(--color-text);
  color: var(--color-surface);
  font-weight: var(--weight-bold);
  font-size: var(--text-sm);
  flex-shrink: 0;
}
.brand-text { display: flex; flex-direction: column; min-width: 0; }
.brand-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;          /* long nav scrolls; the footer stays pinned */
  padding: var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.nav-section-label {
  padding: var(--space-4) var(--space-3) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-subtle);
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 36px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}
.nav-item:hover { background: var(--color-surface-muted); color: var(--color-text); }
.nav-item.is-active { background: var(--color-accent-soft); color: var(--color-accent); }
.nav-item:focus-visible { outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }
.is-collapsed .nav-item { justify-content: center; padding: 0; }
.nav-icon { display: inline-flex; width: 20px; height: 20px; flex-shrink: 0; }
.nav-icon :deep(svg) { width: 20px; height: 20px; }
.nav-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sidebar-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  flex-shrink: 0;
}
.collapse-toggle {
  display: inline-flex; align-items: center; justify-content: center;
  height: 32px;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
}
.collapse-toggle:hover { background: var(--color-surface-muted); color: var(--color-text); }

/* Off-canvas drawer on small screens; see section 5 */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0; top: 0;
    width: var(--sidebar-width);
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    box-shadow: var(--shadow-lg);
  }
  .sidebar.is-open { transform: translateX(0); }
  .sidebar.is-collapsed { width: var(--sidebar-width); }
  .collapse-toggle { display: none; }
}
</style>
```

### Icons

Use inline SVG strings with `stroke="currentColor"` so they inherit the nav item's color. A 24×24 viewBox and stroke-width 1.75 give a modern, light look. Example set, outline style, generic shapes:

```js
const svg = (d) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`

export const icons = {
  home:      svg('<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>'),
  grid:      svg('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'),
  box:       svg('<path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>'),
  cart:      svg('<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 12h12L22 7H6"/>'),
  clipboard: svg('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1"/><path d="M9 10h6M9 14h6"/>'),
  wallet:    svg('<rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 10h18"/><circle cx="16.5" cy="15" r="1"/>'),
  chart:     svg('<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
  trending:  svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>'),
  file:      svg('<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6"/><path d="M8 13h8M8 17h5"/>'),
  users:     svg('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M21.5 20a6.5 6.5 0 0 0-4-6"/>'),
  settings:  svg('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>'),
  menu:      svg('<path d="M4 6h16M4 12h16M4 18h16"/>'),
}
```

The SVG strings are static constants written by you, so `v-html` is safe here. Never pass user data through it.

## 3. `App.vue` shell wiring

Build the nav config next to the shell (or in `src/navigation.js`). Keep i18n: if labels came from `t('nav.x')`, use `computed` so they react to language changes.

```vue
<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': collapsed }">
    <AppSidebar
      :sections="navSections"
      :brand-name="t('nav.companyName')"
      :brand-subtitle="t('nav.subtitle')"
      :collapsed="collapsed"
      :mobile-open="mobileOpen"
      @toggle-collapse="toggleCollapse"
      @navigate="mobileOpen = false"
    >
      <template #footer="{ collapsed }">
        <!-- utilities that used to live in the header, if you put them here -->
      </template>
    </AppSidebar>

    <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen = false" />

    <div class="app-main">
      <header class="topbar">
        <button type="button" class="menu-button" aria-label="Open navigation" @click="mobileOpen = true">
          <span v-html="icons.menu" aria-hidden="true" />
        </button>
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-actions">
          <!-- e.g. <LanguageSwitcher /> <ProfileMenu ... /> with original props/emits -->
        </div>
      </header>

      <!-- Global filters, if the app has them: inside the main column only -->
      <!-- <FilterBar /> -->

      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- Modals stay at the root, unchanged -->
  </div>
</template>
```

Script essentials (adapt to the file's existing style; keep all existing state and handlers):

```js
const collapsed = ref(readCollapsed())
const mobileOpen = ref(false)

function readCollapsed() {
  try { return localStorage.getItem('sidebar-collapsed') === '1' } catch { return false }
}
function toggleCollapse() {
  collapsed.value = !collapsed.value
  try { localStorage.setItem('sidebar-collapsed', collapsed.value ? '1' : '0') } catch {}
}

// Close the drawer on navigation and on Escape
const route = useRoute()
watch(() => route.path, () => { mobileOpen.value = false })
const onKey = (e) => { if (e.key === 'Escape') mobileOpen.value = false }
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))

// Title for the top bar: the active nav item's label
const currentTitle = computed(() => {
  const items = navSections.value.flatMap(s => s.items)
  const match = items.find(i => i.to === '/' ? route.path === '/' : route.path.startsWith(i.to))
  return match?.label ?? ''
})
```

If views already render their own big `<h2>` page header, consider whether the top bar title duplicates it. Two common resolutions: show a breadcrumb-style small title in the top bar (e.g. `text-sm`, muted), or omit it and keep the view header. Don't show the same large heading twice.

## 4. Layout CSS (global)

```css
.app-shell {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);  /* minmax(0,…) prevents wide tables from blowing out the column */
  min-height: 100vh;
  background: var(--color-bg);
}
.app-main { display: flex; flex-direction: column; min-width: 0; }

.topbar {
  position: sticky;
  top: 0;
  z-index: var(--z-topbar);
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 0 var(--page-gutter);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(8px);
  border-bottom: 1px solid var(--color-border);
}
.topbar-title {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.menu-button {
  display: none;
  width: 36px; height: 36px;
  align-items: center; justify-content: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}
.menu-button svg { width: 20px; height: 20px; }

.content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-8) var(--page-gutter) var(--space-12);
}

.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: var(--z-overlay);
}

@media (max-width: 1024px) {
  .app-shell { grid-template-columns: minmax(0, 1fr); }
  .menu-button { display: inline-flex; }
}
```

On small screens the sidebar is `position: fixed` with `z-index: var(--z-sidebar)`. Give it a higher z-index there than the overlay so the drawer sits above the dimmed page:

```css
@media (max-width: 1024px) { .sidebar { z-index: calc(var(--z-overlay) + 1); } }
```

(Put this in the sidebar's scoped styles alongside its other mobile rules.)

## 5. Responsive behavior

| Width | Sidebar | Top bar |
|---|---|---|
| > 1024px | in-flow column, expanded or collapsed (user choice) | title + utilities |
| ≤ 1024px | off-canvas drawer, hidden by default, overlay when open | menu button + title + utilities |
| ≤ 640px | same drawer | hide low-priority utilities' text labels and keep icons |

Filter bars with many selects should wrap (`flex-wrap: wrap` or `grid auto-fit`) instead of scrolling horizontally on mobile.

## 6. Where things go

| Old header element | New home |
|---|---|
| Logo / company name / subtitle | Sidebar brand block |
| Nav links | Sidebar nav (from config array) |
| Global filter bar | Sticky sub-bar under the top bar (`top: var(--topbar-height)`), main column only, or folded into the top bar if it's 1-2 controls |
| Search | Top bar, left-aligned after the title |
| Language switcher, notifications | Top bar actions (right) |
| Profile / user menu | Top bar right, or sidebar footer (pick one) |
| Secondary links (settings, help) | Sidebar footer or a bottom nav section |

Keep components' props and emits exactly as they were wired in the old header. Moving a component means moving its tag with all its attributes.
