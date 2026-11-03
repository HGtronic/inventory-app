---
type: llm
focus: trace
weight: 1
---

Flags useI18n() being called inside per-row formatters (formatDate in Dashboard or Orders, or translatePeriod in Demand), which creates new computeds on every call, when the setup-level instance could be reused
