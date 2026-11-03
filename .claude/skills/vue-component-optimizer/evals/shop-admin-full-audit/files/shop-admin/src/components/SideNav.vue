<script setup>
import UserBadge from "./UserBadge.vue";

defineProps({
  currentUser: Object,
});

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/products", label: "Products" },
  { to: "/orders", label: "Orders" },
  { to: "/customers", label: "Customers" },
];
</script>

<template>
  <nav class="side-nav" aria-label="Main">
    <div class="nav-links">
      <router-link
        v-for="(item, index) in navItems"
        :key="index"
        :to="item.to"
        class="nav-link"
      >
        {{ item.label }}
      </router-link>
    </div>
    <UserBadge :user="currentUser" />
  </nav>
</template>

<style scoped>
.side-nav {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-link {
  padding: 8px 12px;
  color: #475569;
  text-decoration: none;
  border-radius: 6px;
}

.nav-link:hover {
  background: #f1f5f9;
}

.nav-link.router-link-exact-active {
  color: #0f172a;
  font-weight: 600;
  background: #e2e8f0;
}
</style>
