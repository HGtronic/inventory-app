<template>
  <div>
    <div class="top">
      <div>
        <h1>Contacts</h1>
        <p class="sub">{{ filtered.length }} of {{ contacts.length }} contacts</p>
      </div>
      <button class="primary" @click="added++">+ New contact</button>
    </div>
    <p v-if="added" class="added">{{ added }} draft contact(s) created</p>
    <div class="box">
      <table>
        <thead><tr><th>Name</th><th>Company</th><th>Email</th><th>Stage</th><th>Owner</th></tr></thead>
        <tbody>
          <tr v-for="c in filtered" :key="c.id">
            <td>{{ c.name }}</td><td>{{ c.company }}</td><td>{{ c.email }}</td>
            <td><span class="tag" :class="c.stage">{{ c.stage }}</span></td><td>{{ c.owner }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!filtered.length" style="padding: 30px; text-align: center; color: #999">No contacts match "{{ search }}"</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { contacts } from '../data'
const props = defineProps({ search: String, quarter: String })
const added = ref(0)
const filtered = computed(() => {
  const q = (props.search || '').toLowerCase()
  return contacts.filter(c => !q || c.name.toLowerCase().includes(q) || c.company.toLowerCase().includes(q))
})
</script>

<style scoped>
.top { display: flex; justify-content: space-between; align-items: flex-start; }
.added { background: #ecfdf5; color: #065f46; padding: 10px 13px; border-radius: 4px; margin: 0 0 15px; }
</style>
