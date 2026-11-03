<script setup>
import { ref } from "vue";
import AppLayout from "./components/AppLayout.vue";

const currentUser = ref({
  name: "Dana Whitfield",
  role: "Admin",
  avatarInitials: "DW",
});
</script>

<template>
  <AppLayout :current-user="currentUser">
    <router-view />
  </AppLayout>
</template>
