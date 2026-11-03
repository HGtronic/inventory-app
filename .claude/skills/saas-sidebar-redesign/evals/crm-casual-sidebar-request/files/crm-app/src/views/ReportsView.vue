<template>
  <div>
    <h1>Reports</h1>
    <p class="sub">Pipeline value by stage ({{ quarter }})</p>
    <div class="box">
      <h3>Value by stage</h3>
      <div v-for="row in rows" :key="row.stage" class="bar-row">
        <div class="bar-label">{{ row.stage }}</div>
        <div class="bar-track"><div class="bar" :style="{ width: row.pct + '%' }"></div></div>
        <div class="bar-val">${{ row.value.toLocaleString() }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { contacts, stages } from '../data'
defineProps({ search: String, quarter: String })
const rows = computed(() => {
  const vals = stages.map(stage => ({ stage, value: contacts.filter(c => c.stage === stage).reduce((s, c) => s + c.value, 0) }))
  const max = Math.max(...vals.map(v => v.value))
  return vals.map(v => ({ ...v, pct: Math.round((v.value / max) * 100) }))
})
</script>

<style scoped>
.bar-row { display: grid; grid-template-columns: 110px 1fr 100px; gap: 11px; align-items: center; margin-bottom: 11px; }
.bar-label { font-size: 14px; }
.bar-track { background: #eee; height: 13px; border-radius: 3px; }
.bar { background: #3b82f6; height: 13px; border-radius: 3px; }
.bar-val { text-align: right; font-size: 14px; }
</style>
