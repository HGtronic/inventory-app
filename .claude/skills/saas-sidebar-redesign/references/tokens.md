# Design tokens

Put these on `:root` in the global stylesheet (unscoped `<style>` in `App.vue`, or `src/assets/main.css`, whichever the app already uses for globals). They are **defaults**. If the project already defines a palette (in CLAUDE.md, a theme file, or consistently used hex values), substitute those values and keep the token names.

## How to derive values from the existing app

1. Run `scripts/audit_styles.py` and look at the color frequency list.
2. The most-used saturated color on links/active states is the **accent**. Keep it.
3. Map the existing grays to the neutral roles below by lightness: page background is the lightest, borders come next, muted text is mid, primary text is darkest.
4. Keep existing status colors if they exist, but make sure each has a soft background + strong foreground pair.

## Default token block

```css
:root {
  /* Spacing: 4px base. Use only these for padding, margin and gap. */
  --space-0: 0;
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */

  /* Neutrals (slate) */
  --color-bg: #f8fafc;            /* page background */
  --color-surface: #ffffff;       /* cards, sidebar, top bar */
  --color-surface-muted: #f1f5f9; /* hover rows, table header, subtle fills */
  --color-border: #e2e8f0;
  --color-border-strong: #cbd5e1;
  --color-text: #0f172a;          /* headings, primary text */
  --color-text-secondary: #334155;/* body text in tables */
  --color-text-muted: #64748b;    /* labels, subtitles, inactive nav */
  --color-text-subtle: #94a3b8;   /* placeholders, section labels */

  /* Accent */
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;
  --color-accent-soft: #eff6ff;   /* active nav background, info fills */
  --color-focus-ring: rgba(37, 99, 235, 0.35);

  /* Status: soft background + strong foreground */
  --color-success: #059669;  --color-success-soft: #ecfdf5;  --color-success-strong: #065f46;
  --color-warning: #d97706;  --color-warning-soft: #fffbeb;  --color-warning-strong: #92400e;
  --color-danger:  #dc2626;  --color-danger-soft:  #fef2f2;  --color-danger-strong:  #991b1b;
  --color-info:    #2563eb;  --color-info-soft:    #eff6ff;  --color-info-strong:    #1e40af;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Shadows: subtle; borders do most of the separation work */
  --shadow-xs: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 12px 32px rgba(15, 23, 42, 0.12);

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --text-xs: 0.75rem;    /* 12px: table headers, badges, section labels */
  --text-sm: 0.875rem;   /* 14px: body, nav items, table cells */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px: card titles */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px: page titles */
  --text-3xl: 1.875rem;  /* 30px: stat values */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;

  /* Layout */
  --sidebar-width: 248px;
  --sidebar-width-collapsed: 72px;
  --topbar-height: 56px;
  --content-max-width: 1440px;
  --page-gutter: var(--space-8);

  /* Stacking: modals must sit above sidebar/topbar */
  --z-sticky: 20;
  --z-topbar: 30;
  --z-sidebar: 40;
  --z-overlay: 90;
  --z-dropdown: 100;
  --z-modal: 1000;

  /* Motion */
  --transition-fast: 120ms ease;
  --transition-base: 200ms ease;
}

@media (max-width: 768px) {
  :root { --page-gutter: var(--space-4); }
}
```

## Mapping raw values to tokens

When converting existing CSS, round to the nearest step. Off-scale values are usually accidents, not design intent:

| Raw value | Token |
|---|---|
| 0.125rem, 0.188rem, 2-3px | `--space-1` (or drop) |
| 0.313rem, 0.375rem, 5-6px | `--space-1` / `--space-2` |
| 0.5rem, 0.563rem, 0.625rem | `--space-2` / `--space-3` |
| 0.75rem, 0.813rem, 0.875rem | `--space-3` |
| 1rem, 1.125rem | `--space-4` |
| 1.25rem, 1.375rem | `--space-5` |
| 1.5rem, 1.75rem | `--space-6` |
| 2rem, 2.25rem | `--space-8` |

Font sizes such as 0.813rem, 0.938rem and 1.375rem snap to the nearest `--text-*` step.

Exception: leave values alone where the exact number does real work, such as chart geometry, SVG coordinates, 1px borders, or icon sizes.
