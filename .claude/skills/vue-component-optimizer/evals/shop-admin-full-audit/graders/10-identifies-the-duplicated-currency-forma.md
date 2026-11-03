---
type: llm
focus: trace
weight: 1
---

Identifies the duplicated currency formatters (formatPrice, formatMoney, formatCurrency), points out that utils/format.js already has formatCurrency, and notes CustomersView's copy rounds to whole dollars unlike the others
