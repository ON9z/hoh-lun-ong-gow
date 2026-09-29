# Optimization work has **no "done"** — only a "**stop**" — so give it a stop condition, not a completion condition

判据： **optimization / research / improvement tasks: `done_when` is forbidden; only `stop_when` is allowed.**
⚠ And `stop_when` must take one of exactly two shapes:

```
stop_when: within a fixed window, changes of this class = 0
stop_when: number of triggering events = 0
```

⛔ **"done / optimal / closed out" is not a stop condition** — it is undecidable.
⚠ **A task without `stop_when` is not closed** (⚠ even if it looks like a lot of work happened).

---

## Why

⭐⭐ **"Optimize", "research", "improve" have no completion state**: **every optimization produces
new things that could be optimized** — ⚠ that is not a failure of execution, it is **the definition of
this kind of task**. ⇒ ⭐ **Writing `done_when` for it is writing an assertion that is permanently false** ✓

⚠ And **the cost lands in one concrete place**: ⭐ **my previous answer to the operator was
"half achieved" — and that answer was itself wrong**, because it **encouraged continuing**
("we are halfway there"). ⇒ ⭐ **An undecidable completion condition provides indefinite justification
for continuing to invest** ✓

**Instance (a single-user, single-machine long-running automation system, 2026-09-29)**:
⭐ The operator asked **twice**: "**is the mechanism work done?**"
⭐ I answered once with "**half achieved**" (⚠ itemised: bytes saved, which metrics did not improve) —
⚠ and **he asked again** ⇒ ⭐ **he was not asking for progress. He was asking to stop.** ✓

⚠ Why could I not answer "stop"? ⭐ Because I **assumed "done" is a thing**, and it is not:

| | Criterion |
|---|---|
| ⭐ **"done"** | ⛔ **no criterion** — ⭐ say so plainly (⚠ do not invent one; an invented one will be taken as real) |
| ⭐⭐ **"stop"** | ✅ **has one**: **no unfreeze event ⇒ changes of this class = 0** |

⭐⭐ **⇒ The shape of stopping**: turn it from a "**default task source**" into an "**unfreeze event source**" —
⭐ **not by willpower, but by it no longer appearing in the default queue** ✓
⚠ And **only three kinds of unfreeze** (any one is required before touching it):
**① an explicit human instruction ② a reproducible task blockage ③ a safety / data-consistency /
wrong-persisted-state incident** ⇒ ⭐ **it re-freezes automatically once fixed** ✓

⚠⚠ **And "what does not count as a reason" matters just as much** (⚠ otherwise it comes back through the side door):
⭐ **"we found N more things to optimize" · "the metrics look bad" · "it could be more elegant"** ⇒
⭐ **that is just the fact that this work is unbounded** ✓

---

## Criterion (for the next person)

⭐ When you are handed an "optimize X" task, write `stop_when` **before** starting:
- ⚠ Cannot write one ⇒ ⭐ **this task has no end and you will keep going** (⚠ while every step looks productive)
- ⭐ Can write one ⇒ ⚠ **then ask: can the thing this condition constrains satisfy it itself?**
  (e.g. "no more things to optimize" — ⚠ that is defined by the object being optimized; it is permanently false)

⚠ **Kindred**: `#26` (a mechanism that serves itself) —— ⭐ **#26 says "the budget all went into the machinery";
this one says "how to make it stop"** ✓
