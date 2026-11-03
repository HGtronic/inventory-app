<template>
  <div>
    <h1>Dashboard</h1>
    <p class="sub">Pipeline overview for {{ quarter }}</p>
    <div class="kpis">
      <div class="kpi"><div class="label">Open pipeline</div><div class="num">${{ openValue.toLocaleString() }}</div></div>
      <div class="kpi"><div class="label">Customers</div><div class="num">{{ customers }}</div></div>
      <div class="kpi"><div class="label">Leads</div><div class="num">{{ leads }}</div></div>
      <div class="kpi"><div class="label">Win rate</div><div class="num">{{ winRate }}%</div></div>
    </div>
    <div class="box">
      <h3>Largest opportunities</h3>
      <table>
        <thead><tr><th>Contact</th><th>Company</th><th>Stage</th><th>Value</th></tr></thead>
        <tbody>
          <tr v-for="c in top" :key="c.id">
            <td>{{ c.name }}</td><td>{{ c.company }}</td>
            <td><span class="tag" :class="c.stage">{{ c.stage }}</span></td>
            <td>${{ c.value.toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { contacts } from '../data'
defineProps({ search: String, quarter: String })
const openValue = computed(() => contacts.filter(c => c.stage !== 'Customer').reduce((s, c) => s + c.value, 0))
const customers = computed(() => contacts.filter(c => c.stage === 'Customer').length)
const leads = computed(() => contacts.filter(c => c.stage === 'Lead').length)
const winRate = computed(() => Math.round((customers.value / contacts.length) * 100))
const top = computed(() => [...contacts].sort((a, b) => b.value - a.value).slice(0, 5))
</script>
