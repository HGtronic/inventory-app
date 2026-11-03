<template>
  <div id="layout">
    <div class="header">
      <div class="header-inner">
        <router-link to="/" class="brand">Pipeline<span>CRM</span></router-link>
        <div class="links">
          <router-link to="/" exact-active-class="current">Dashboard</router-link>
          <router-link to="/contacts" active-class="current">Contacts</router-link>
          <router-link to="/deals" active-class="current">Deals</router-link>
          <router-link to="/reports" active-class="current">Reports</router-link>
          <router-link to="/settings" active-class="current">Settings</router-link>
        </div>
        <input v-model="search" class="search" type="search" placeholder="Search contacts..." />
        <button class="bell" @click="showNotes = !showNotes">
          Alerts <span class="count" v-if="notifications.length">{{ notifications.length }}</span>
        </button>
        <UserMenu name="Sam Carter" email="sam@pipeline.example" @sign-out="signedOut = true" />
      </div>
      <div v-if="showNotes" class="notes">
        <div v-for="n in notifications" :key="n.id" class="note">{{ n.text }}</div>
      </div>
    </div>
    <div class="subbar">
      <span>Quarter:</span>
      <select v-model="quarter">
        <option>Q1</option><option>Q2</option><option>Q3</option><option>Q4</option>
      </select>
      <span class="hint">Showing data for {{ quarter }} {{ signedOut ? '(signed out)' : '' }}</span>
    </div>
    <div class="page">
      <router-view :search="search" :quarter="quarter" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UserMenu from './components/UserMenu.vue'

const search = ref('')
const quarter = ref('Q3')
const showNotes = ref(false)
const signedOut = ref(false)
const notifications = ref([
  { id: 1, text: 'Noah Kim opened your proposal' },
  { id: 2, text: 'Deal "Tidewater renewal" moved to Customer' }
])
</script>

<style scoped>
.header { background: #1f2937; color: white; position: sticky; top: 0; z-index: 50; }
.header-inner { display: flex; align-items: center; padding: 14px 22px; gap: 18px; height: 64px; }
.brand { color: white; font-weight: 800; font-size: 19px; text-decoration: none; margin-right: 30px; }
.brand span { color: #60a5fa; margin-left: 3px; }
.links { display: flex; gap: 6px; }
.links a { color: #d1d5db; text-decoration: none; padding: 7px 13px; border-radius: 5px; font-size: 15px; }
.links a:hover { background: #374151; }
.links a.current { background: #3b82f6; color: white; }
.search { margin-left: auto; padding: 7px 11px; border-radius: 5px; border: none; width: 220px; }
.bell { background: #374151; color: white; border: none; padding: 7px 12px; border-radius: 5px; cursor: pointer; }
.count { background: #ef4444; border-radius: 10px; padding: 1px 7px; margin-left: 5px; font-size: 12px; }
.notes { position: absolute; right: 120px; top: 60px; background: white; color: #111; box-shadow: 0 4px 14px rgba(0,0,0,.2); border-radius: 6px; width: 280px; }
.note { padding: 11px 14px; border-bottom: 1px solid #eee; font-size: 14px; }
.subbar { position: sticky; top: 64px; background: #f3f4f6; padding: 9px 22px; display: flex; gap: 10px; align-items: center; border-bottom: 1px solid #ddd; font-size: 14px; z-index: 40; }
.hint { color: #6b7280; }
.page { padding: 26px 22px; max-width: 1280px; margin: 0 auto; }
</style>
