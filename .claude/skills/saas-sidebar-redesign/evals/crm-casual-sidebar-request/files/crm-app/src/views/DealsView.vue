<template>
  <div>
    <h1>Deals</h1>
    <p class="sub">Drag-free board view by stage</p>
    <div class="board">
      <div v-for="s in stages" :key="s" class="col">
        <div class="col-head">{{ s }} <span>{{ byStage(s).length }}</span></div>
        <div v-for="c in byStage(s)" :key="c.id" class="deal">
          <div class="deal-name">{{ c.company }}</div>
          <div class="deal-meta">{{ c.name }} · ${{ c.value.toLocaleString() }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { contacts, stages } from '../data'
defineProps({ search: String, quarter: String })
const byStage = (s) => contacts.filter(c => c.stage === s)
</script>

<style scoped>
.board { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.col { background: #f0f0f0; border-radius: 5px; padding: 11px; min-height: 300px; }
.col-head { font-weight: bold; font-size: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; }
.col-head span { color: #888; font-weight: normal; }
.deal { background: white; border: 1px solid #ddd; border-radius: 4px; padding: 10px 12px; margin-bottom: 9px; }
.deal-name { font-weight: 600; font-size: 14px; }
.deal-meta { font-size: 12px; color: #777; margin-top: 3px; }
</style>
