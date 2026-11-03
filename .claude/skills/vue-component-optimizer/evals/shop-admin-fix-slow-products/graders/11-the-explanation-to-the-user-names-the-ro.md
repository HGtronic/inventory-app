---
type: llm
focus: trace
weight: 1
---

The explanation to the user names the root causes: index keys moving row state on sort, and per-keystroke re-filtering/sorting of all products (function called repeatedly, per-row lookups, every row rendered)
