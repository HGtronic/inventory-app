<script setup>
import SideNav from "./SideNav.vue";

defineProps({
  currentUser: Object,
});
</script>

<template>
  <div class="layout">
    <header class="layout-header">
      <span class="brand">Shop Admin</span>
    </header>
    <aside class="layout-sidebar">
      <SideNav :current-user="currentUser" />
    </aside>
    <main class="layout-main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  grid-template-rows: 56px 1fr;
  grid-template-areas:
    "header header"
    "sidebar main";
  height: 100vh;
}

.layout-header {
  grid-area: header;
  display: flex;
  align-items: center;
  padding: 0 24px;
  color: #f8fafc;
  background: #0f172a;
}

.brand {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.layout-sidebar {
  grid-area: sidebar;
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
}

.layout-main {
  grid-area: main;
  padding: 24px;
  overflow-y: auto;
}
</style>
