# Component styles

Global styles for the shared building blocks. Apply them to the classes the app **already uses**: rename selectors below to match (e.g. if the app's cards are `.panel`, style `.panel`). Don't rename classes in templates just to fit this file.

All values come from `tokens.md`.

## Base

```css
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  color: var(--color-text-secondary);
  background: var(--color-bg);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4 { color: var(--color-text); line-height: var(--leading-tight); margin: 0; }
:focus-visible { outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }
```

## Page header

Same structure on every page: title + optional description on the left, optional actions on the right.

```css
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-8);
}
.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: var(--weight-bold);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-1);
}
.page-header p { color: var(--color-text-muted); font-size: var(--text-sm); margin: 0; }
```

## Cards

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin: calc(-1 * var(--space-6)) calc(-1 * var(--space-6)) var(--space-5);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}
.card-title { font-size: var(--text-base); font-weight: var(--weight-semibold); color: var(--color-text); }
```

The negative-margin header makes the divider line run edge to edge. If cards in the app contain a table directly after the header, also let the table bleed: `.card > .table-container { margin: 0 calc(-1 * var(--space-6)); }`.

## Stat / KPI cards

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  padding: var(--space-5) var(--space-6);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.stat-card:hover { border-color: var(--color-border-strong); box-shadow: var(--shadow-sm); }
.stat-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}
.stat-value {
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
  letter-spacing: -0.02em;
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}
```

Status-colored stat values (`.stat-card.warning .stat-value` etc.) keep working. Point them at `--color-warning` and the other status tokens.

## Tables

```css
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
thead { background: var(--color-surface-muted); }
th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}
td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border);
}
tbody tr:last-child td { border-bottom: none; }
tbody tr { transition: background var(--transition-fast); }
tbody tr:hover { background: var(--color-surface-muted); }
```

Right-align numeric columns if the template already marks them (e.g. a `.num` class). Don't add classes to every cell just for this.

## Badges

Soft background, strong text, small radius. Keep existing modifier names (`.success`, `.warning`, `.high`, `.increasing`...) and map each to a status pair:

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  line-height: 1.5;
  white-space: nowrap;
}
.badge.success { background: var(--color-success-soft); color: var(--color-success-strong); }
.badge.warning { background: var(--color-warning-soft); color: var(--color-warning-strong); }
.badge.danger  { background: var(--color-danger-soft);  color: var(--color-danger-strong); }
.badge.info    { background: var(--color-info-soft);    color: var(--color-info-strong); }
```

## Buttons

```css
.btn, button.primary, button.secondary {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
  height: 36px;
  padding: 0 var(--space-4);
  border-radius: var(--radius-md);
  font: inherit;
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}
.btn-primary, button.primary { background: var(--color-accent); color: #fff; border: 1px solid var(--color-accent); }
.btn-primary:hover, button.primary:hover { background: var(--color-accent-hover); }
.btn-secondary, button.secondary { background: var(--color-surface); color: var(--color-text); border: 1px solid var(--color-border); }
.btn-secondary:hover, button.secondary:hover { background: var(--color-surface-muted); }
```

Only add selectors for button classes the app actually uses.

## Form controls / filter bar

```css
select, input[type="text"], input[type="search"], input[type="number"], input[type="date"] {
  height: 36px;
  padding: 0 var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: var(--text-sm);
}
select:hover, input:hover { border-color: var(--color-border-strong); }
select:focus, input:focus { outline: none; border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-focus-ring); }

/* Global filter sub-bar under the top bar */
.filters-bar {
  position: sticky;
  top: var(--topbar-height);
  z-index: var(--z-sticky);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--space-3) var(--page-gutter);
}
.filters-grid { display: flex; flex-wrap: wrap; gap: var(--space-4); align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: var(--space-1); min-width: 160px; }
.filter-group label { font-size: var(--text-xs); font-weight: var(--weight-medium); color: var(--color-text-muted); }
```

A filter component usually has scoped styles. Edit them in that component and keep its `v-model` bindings and emitted events untouched.

## Modals

```css
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.45); z-index: var(--z-modal); display: grid; place-items: center; padding: var(--space-4); }
.modal { background: var(--color-surface); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); width: min(640px, 100%); max-height: calc(100vh - var(--space-16)); overflow: auto; }
.modal-header { padding: var(--space-5) var(--space-6); border-bottom: 1px solid var(--color-border); }
.modal-body { padding: var(--space-6); }
.modal-footer { padding: var(--space-4) var(--space-6); border-top: 1px solid var(--color-border); display: flex; justify-content: flex-end; gap: var(--space-3); }
```

Modals often live in their own components with scoped styles. The essential fix is the z-index (above sidebar/topbar). Restyling their internals is optional polish, so only do it if it stays low-risk.

## Loading, empty, error states

```css
.loading, .empty-state {
  padding: var(--space-12) var(--space-6);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
.error {
  background: var(--color-danger-soft);
  border: 1px solid color-mix(in srgb, var(--color-danger) 25%, transparent);
  color: var(--color-danger-strong);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
}
```
