<template>
  <div class="user-menu">
    <button class="avatar" @click="open = !open">{{ initials }}</button>
    <div v-if="open" class="dropdown">
      <div class="who"><strong>{{ name }}</strong><br /><small>{{ email }}</small></div>
      <a href="#" @click.prevent="open = false">Profile</a>
      <a href="#" @click.prevent="$emit('sign-out'); open = false">Sign out</a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({ name: String, email: String })
defineEmits(['sign-out'])
const open = ref(false)
const initials = computed(() => props.name.split(' ').map(p => p[0]).join(''))
</script>

<style scoped>
.user-menu { position: relative; }
.avatar { width: 36px; height: 36px; border-radius: 50%; border: 2px solid #60a5fa; background: #111827; color: white; font-weight: 700; cursor: pointer; }
.dropdown { position: absolute; right: 0; top: 46px; background: white; color: #111; border-radius: 7px; box-shadow: 0 6px 18px rgba(0,0,0,.18); min-width: 190px; z-index: 60; }
.who { padding: 12px 15px; border-bottom: 1px solid #eee; font-size: 14px; }
.dropdown a { display: block; padding: 9px 15px; color: #374151; text-decoration: none; font-size: 14px; }
.dropdown a:hover { background: #f3f4f6; }
</style>
