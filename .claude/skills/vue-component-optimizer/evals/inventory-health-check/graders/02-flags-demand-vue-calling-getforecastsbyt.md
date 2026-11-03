---
type: llm
focus: trace
weight: 1
---

Flags Demand.vue calling getForecastsByTrend() repeatedly from the template (about 12 filter passes per render, plus slice in the v-for source) and recommends a computed grouping
