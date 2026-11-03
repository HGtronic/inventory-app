<template>
  <div>
    <h1>Settings</h1>
    <p class="sub">Workspace preferences</p>
    <div class="box">
      <h3>Workspace</h3>
      <label>Workspace name<br /><input v-model="workspace" /></label>
      <label>Default currency<br />
        <select v-model="currency"><option>USD</option><option>EUR</option><option>GBP</option></select>
      </label>
      <label class="check"><input type="checkbox" v-model="digest" /> Send weekly digest email</label>
      <button class="primary" @click="saved = true">Save changes</button>
      <span v-if="saved" class="saved">Saved</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineProps({ search: String, quarter: String })
const workspace = ref('Pipeline Inc.')
const currency = ref('USD')
const digest = ref(true)
const saved = ref(false)
</script>

<style scoped>
label { display: block; margin-bottom: 15px; font-size: 14px; color: #444; }
input:not([type]), select { margin-top: 5px; padding: 7px 9px; border: 1px solid #ccc; border-radius: 3px; width: 300px; }
.check { display: flex; gap: 7px; align-items: center; }
.saved { margin-left: 11px; color: #059669; font-size: 14px; }
</style>
