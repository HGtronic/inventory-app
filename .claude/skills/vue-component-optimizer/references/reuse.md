# Code reuse patterns

Reuse findings pay off when the duplicated thing changes together. The goal is fewer places to edit and fewer ways for copies to drift apart, not fewer lines.

## How to evaluate a duplication candidate

1. **Count the real copies.** Use the scanner's duplication sections as a start, then grep for the function name, the class name, or a distinctive line. Two copies is usually Low; three or more is where extraction clearly pays (the rule of three).
2. **Diff the copies.** Put them side by side. Identical copies make an easy, safe extraction. Copies that have **diverged** need a closer look:
   - If the divergence is accidental (one handles `null`, another crashes; one uses `toFixed(2)`, another rounds to whole dollars), that's a user-visible inconsistency. Report it in the finding, and consider ranking it High.
   - If the divergence is deliberate (different business rules), the shared part may be smaller than it looks. Extract only that part, or leave it.
3. **Check what's already shared.** Look in `composables/`, `utils/`, `components/`, global CSS. The best fix is often "use the helper that already exists", and that should be said explicitly.
4. **Ask whether they change for the same reason.** Two tables with similar markup that serve different features may evolve differently. Don't merge them into one configurable component just because they look alike today.

## What to extract, and into what

| Duplicated thing                                                                                                                                                                                 | Extract into                                           | Notes                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pure functions: formatters, mappers, status→class/label tables, math                                                                                                                             | a `utils/` module                                      | Easiest and safest. Keep behavior identical; if copies diverged, pick one behavior explicitly and say which.                                        |
| Stateful logic: loading/error/data refs with try/finally, filter watching, pagination, sorting, selection, debounced search, localStorage persistence, dropdown open/close/blur, Escape-to-close | a composable (`useXxx`) returning refs and functions   | Must work when used several times on one screen (state created inside the function, not at module level, unless shared state is the point).         |
| Markup and behavior: modal shell (overlay, container, header, close button, Escape, transition), status badge, empty/loading/error states, stat card                                             | a shared component with props and slots                | Slots over boolean props. A `BaseModal` with `title` prop, default slot and `footer` slot beats `<Modal :showFooter :showClose :wide :danger ...>`. |
| CSS rules repeated across components (the same class styled the same way in several scoped blocks)                                                                                               | global stylesheet or the shared component's own styles | When the markup moves into a shared component, its styles move with it and the copies disappear. Otherwise a global class or CSS variables.         |

### Example: async state composable

When several views hand-roll the same loading/error/try-finally pattern:

```js
// composables/useAsyncData.js
import { ref, shallowRef } from "vue";

// Shared loading/error handling for view-level fetches. `fetcher` returns a promise.
// Stale responses are ignored so fast filter changes can't overwrite newer data.
export function useAsyncData(fetcher, { initial = null } = {}) {
  const data = shallowRef(initial);
  const loading = ref(false);
  const error = ref(null);
  let requestId = 0;

  async function run(...args) {
    const id = ++requestId;
    loading.value = true;
    error.value = null;
    try {
      const result = await fetcher(...args);
      if (id === requestId) data.value = result;
    } catch (e) {
      if (id === requestId) error.value = e?.message ?? String(e);
    } finally {
      if (id === requestId) loading.value = false;
    }
  }

  return { data, loading, error, run };
}
```

Adapt it to the codebase: keep the existing error message format, the existing `loading` initial value (a view that starts with `loading = true` shows a spinner on first paint, and changing that changes the UI), and the existing data shape. If the project already uses VueUse or a query library, point at that instead.

### Example: modal shell component

When several modals copy the overlay, header, close button, transition and Escape handling:

```vue
<!-- components/BaseModal.vue -->
<script setup>
import { onMounted, onUnmounted } from "vue";
const props = defineProps({ isOpen: Boolean, title: String });
const emit = defineEmits(["close"]);
const onKey = (e) => {
  if (e.key === "Escape" && props.isOpen) emit("close");
};
onMounted(() => document.addEventListener("keydown", onKey));
onUnmounted(() => document.removeEventListener("keydown", onKey));
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
        <div
          class="modal-container"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
        >
          <header class="modal-header">
            <h3 class="modal-title">
              <slot name="title">{{ title }}</slot>
            </h3>
            <button
              class="close-button"
              aria-label="Close"
              @click="emit('close')"
            >
              ×
            </button>
          </header>
          <div class="modal-body"><slot /></div>
          <footer v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
```

Keep the class names the copies used, so the existing look doesn't change and any global or test selectors still match. Copy the visual details (icon SVG, widths) from the existing modals rather than inventing new ones. Only add `Teleport` if the existing modals already escape their parent or have stacking problems; otherwise it's a behavior change worth calling out.

## Migration plan to include in the finding

For M/L reuse findings, suggest the order: create the shared piece, migrate one consumer, verify it renders identically, then migrate the rest one by one. List the consumers. This makes the finding actionable and lets the user stop halfway.

## Don't flag

- Two-line snippets or one-line helpers duplicated twice. A shared module for `capitalize` isn't worth the import.
- Similar-looking code with different reasons to change (two forms with the same field layout for different domain objects).
- Framework boilerplate that every component has (`defineProps`, `emit('close')`, `const { t } = useI18n()`). The scanner's copy-paste detector sometimes matches these; drop them.
- Generated or vendored code.
