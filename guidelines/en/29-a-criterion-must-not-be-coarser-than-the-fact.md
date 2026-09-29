# A criterion must not be **coarser** than the fact — otherwise you may output a **candidate set**, never a **count**

判据： **write down two things first — the smallest unit of the fact, and the unit your criterion matches on.**
If the criterion's unit is wider, **what you produced is not a count. It is a candidate set.**

Executable shape:

```
fact_unit:  <the smallest unit of the fact>
match_unit: <the unit my criterion matches on>
mode:       candidate | count      # whenever match_unit is strictly wider, it can only be candidate
```

⚠ **To upgrade from `candidate` to `count` — a number you may draw a conclusion from — you must show
false positives = 0 on known counter-examples or a golden sample.** Cannot show it ⇒ stay at candidate.

---

## Why

⭐⭐ **When the criterion is one notch coarser than the fact, it sweeps in things that are not the target —
and what it sweeps in looks exactly like the target.** ⚠ So you get a number that is **credible and wrong**.

⚠ **The asymmetry matters**: a **miss** (criterion narrower than the fact) is usually caught by some other check.
⚠ A **sweep-in** (criterion wider) ⛔ **is caught by nothing** — because the extra items **look real** ✓

⭐ And the cost is not just a wrong number: **you will act on that number** —
⚠ and you will then change something that was **already correct**.

**Instance (a single-user, single-machine long-running automation system, 2026-09-29) — three times in one day**:

| The fact I wanted | ⚠ The criterion I used | What I reported | The truth | What the false positives were |
|---|---|---|---|---|
| Is a status field **pending**? | "the cell **contains** a pending word" | **146** | **26** | ⚠ the word appeared in a **narrative** and in a **quoted history** |
| Is a pending item **reachable**? | "its id **appears literally** in the entry point" | **33~44** | **0** | ⚠ the entry point **by design lists no bodies**, it gives **a route** |
| Does a code path **lack** an exclusion? | "does **this line** contain that string" | **7** | **5** | ⚠ the string was split across two lines — **the other line had it** |

⚠⚠ **The third one cost the most**: those 2 false positives sat on a **core business path** ⇒
**acting on the wrong criterion would have changed a critical piece of code that was already correct** ✓

⭐ The shared shape in all three: **the criterion's scope is one notch coarser than the fact** —
from "this line" to "this cell", from "this value" to "this passage", from "this route" to "this literal".

---

## Criterion (for the next person)

⭐ Before writing any "**is there X** / **is this Y**" criterion, answer two questions:
1. **Can X appear outside the unit I am scanning?** (a concatenation splits a statement across lines ·
   a decision spans several branches · the constant is defined elsewhere · one meaning has two implementations)
2. **Is my criterion's unit the same as the fact's unit?**

⚠ Cannot answer #2 ⇒ **your scope is a guess** ⇒ ⭐ **the output must be labelled candidate,
and must state what you excluded**.

⚠ **Kindred**: `#23` (you wrote a criterion — did you enumerate where it applies?) ——
⭐ **#23 governs the number of places; this one governs the width** ✓
