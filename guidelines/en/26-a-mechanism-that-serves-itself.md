# Mechanism self-service rate — the machinery of a long-running automated system will **eat the whole budget**, while **every guard reports green**

判据：**"Of the last N pieces of output, how many touched the reason this system exists at all?"**
⚠ **Cannot answer it / it tends toward 0** ⇒ ⭐ **the machinery is spinning on itself** — ⚠ and **this is not a failure of any guard**:
**because no guard measures "where did the effort go" at all**.

**⇒ Why**: a guard by definition checks **one invariant** (the ledger is honest / docs match reality / filenames are clean).
⭐ **They are all LOCAL criteria** ⇒ each can be **true forever inside its own scope**,
⚠ while **the aggregate budget can flow 100% into the machinery itself** — **not one of them turns red**.
⚠ Worse: **the more complete the machinery, the more tables / ledgers / manifests it must maintain** ⇒
⇒ **the direction is self-catalysing**: everything the machinery produces becomes something the machinery must now maintain.

⚠ **⚠ And it is very hard to notice, because 【every step looks like work】**:
every round produces output (commits, reports, audits, fixes), **every piece of output is genuine and useful**,
⭐ it is just that **the thing they serve is the machinery itself**.

**实例 (single-operator single-machine automated system, measured 2026-09-29)**:
The user asked "**should there be this many guards (I think there is a defect)**". ⭐ I first measured the guards themselves:
**12 guards = 5 invariant families, not one a duplicate of another** (each maps to a **different** recorded incident)
⇒ ⭐ **the defect is not in the number of guards**.

⚠ So what should I have measured? ⭐ **The last 60 commits (inside 4.4 hours)**:

| Category | Commits |
|---|---|
| The machinery itself (guards / hook / handoff anchor / indexes / external consults / self-audits / design docs / audit snapshots) | **~50 (83%)** |
| Task domain (data-pipeline fixes · backfill verification · caliber decisions) | ~10 (17%) |
| ⭐⭐ **The reason the system exists** (producing a real business result) | **0** |

⭐⭐ **Conclusion**: **the defect is not the number of guards, it is that 【no guard measures this sentence】**.
⚠ And **the very round that wrote this rule** is one more machinery round: **40 minutes, 0 business output**.

**⇒ 做法**:

① **Build an output-composition meter**, ⛔ not a gate:
   classify the last N pieces of output by path/title and print **each category's share**.
   ⚠ **⛔ Do not wire it into the commit hook** — ⭐ that is **one more guard**, the **opposite** of "lighten the machinery".
   Keep it as a **diagnostic**: **run it by hand, or once per round at wrap-up**.
② **Write the criterion in a form 【that depends on no threshold】**:
   ⚠ "machinery share > 0.7 ⇒ red" **looks** like a criterion, but it is **a floating line** (measured 0.67 — two commits from it).
   ⭐ Use a **binary fact** instead: "**business results produced in this window = 0**" — ⚠ it contains **no tunable parameter**.
③ **⚠ The meter must disclose its own soft spot**: keyword classification **cannot tell "mentions" from "produces"**
   (measured: the single commit "containing a business word" was **a document correction that merely mentioned the word** — ⛔ it produced nothing)
   ⇒ ⭐ **when you print the number, print this blind spot with it**.

**⚠️ Boundaries with rules 13 / 20**:
- **13** (admission ≠ cleanup) says "**one guard** only admits and never reclaims ⇒ **the class it governs** accumulates monotonically" —
  ⚠ that is an imbalance **inside one guard**;
- **20** (a hazard hidden by a default) says "**one path** never fired so far" —
  ⚠ that is the existence of **one concrete path**;
- **THIS rule** says "**every guard is fine, while the whole output flows into the machinery itself**" — ⚠ that is the **system level**,
  ⚠ and **no single guard can ever detect it** (because every guard's criterion is local).

⚠ **Common thread**: they all treat "**seeing only a part and taking it for the whole**",
⚠ and **this one is the most expensive**: 13 / 20 cost you **a class of objects** or **one path**,
**this one costs you 【the entire budget of the system】 — and it looks like it is working, every single second.**

---

## ⭐⭐ Revision (2026-09-29): move the measurement from a **static count** to an **in-flight interference count**

⚠ The window statistic above — "of the last N commits, how many touched the system's purpose" — is a
**window statistic**. ⭐ It **is right, but it is late**: ⚠ it is **after the fact**, ⚠ and **the cost was
paid while the real work was happening** ✓

⭐⭐ **In-flight criterion (⚠ decidable on the spot, ⛔ no window needed)**:

```
① Before starting: declare the 【non-machinery deliverable】 of this run.
② During it: any action that does 【not change that deliverable】 and 【does not clear a stated
   blockage】 counts as one 【machinery action】.
③ Passing condition: machinery actions = 0.
```

⚠ **If machinery actions > 0** ⇒ ⭐ that **is one in-flight interference** ⇒ **only two legitimate exits**:
**stop, or re-declare this run as a machinery task** (⚠ ⛔ not "I'll just do this one thing on the way").

⭐ In one line: **while doing the real work, any action that does not advance it is the machinery borrowing this run.**

⚠ **The unit of accounting therefore changes**:
- ⚠ old: **share of machinery output** (⚠ it drifts toward 100% by itself, while **every day looks like progress**)
- ⭐ new: **in one non-machinery task, machinery actions / rework rounds** (⚠ **it is 0 or it is not, on the spot**) ✓

---

## ⭐⭐ Revision (2026-10-01): the **pricing** that makes the machinery eat the budget — closing is dearer than re-checking

判据：**"In this machinery, what does 【the correct action】 have to pay — and what does 【the cheaper action that replaces it】 have to pay?"**
⚠ **If the latter is cheaper, and the former additionally carries risk ⇒ the agent will systematically do only the latter** ✓

**⇒ Why** (this is the half this rule was missing — the first two revisions said "the machinery eats the budget", ⛔ they never said **why it gets selected**):
in this machinery, **closing** one item means **registering an exemption item by item** (⚠ it collides with a
guard, it needs a human to read it, it needs a citation);
while **re-checking** one item **collides with nothing** ⇒ ⭐ **both produce a "commit", and only the former
reduces the open-item count** ✓
⇒ so **rationally picking the cheaper one** is exactly **what this machinery incentivises** ✓

⭐ **And a layer harder than "dearer" (added 2026-10-01, ⚠ first-hand measurement)**: in that system, **lowering the
open-item count is blocked by an explicit rule** — the rule reads, verbatim: "**the leading marker is the item's
own declaration — you may not change it to change the count**".
⇒ ⭐ **So "closing one" is not 【expensive】, it is 【not permitted by default】** ✓
⚠ And that rule **is itself correct** (what it blocks is exactly "close things wrongly so the number looks good")
⇒ ⭐ **but its price is that the count 【cannot fall quickly, by design】**,
⭐ so **seeing "net 0" over a given window neither proves idleness nor proves the machinery is broken** —
⚠ **it may simply be 【a number that does not accept cleanup by design】** ✓
⇒ ⭐⭐ **The right move is not to drive it down, but to**: ① do the ones that are **genuinely actionable**
② move the **non-actionable** ones (waiting on an external person / on an external condition / periodic and never
closable / explicitly held) **off the main list** ✓

⚠ **⚠ And it is very hard to notice, because 【both actions look like work】**:
every commit is genuine, every one has wording, every one passes the checks, ⭐ it is just that **they changed no state at all**.

**Instance (single-operator single-machine automated system, measured 2026-10-01)**: ⭐ measured over a **3.6-hour / 51-commit** window:

| Category | Commits | Share |
|---|---|---|
| Machinery / records (handoff anchor · snapshots · design docs · memory · skills) | 20 | 39% |
| Task · **read-only re-checking** (re-checking / recomputing / correcting wording, **changes no state**) | 15 | 29% |
| Task · action (implementing / opening a work item / registering into a queue) | 10 | 20% |
| Unclassified | 6 | 12% |

⭐ **And of those 10 "action" commits, only 2 actually brought the open-item count down** ⇒
⭐⭐ **the net result of 3.6 hours = 2 closed · 2 opened = net 0** ✓

⭐ **Plus one of the same origin**: that "open-item total" is itself a **composite metric** — it mixes
genuine to-dos / waiting on an external person / waiting on an external condition / **periodic, never closable** / **done but not closed** / no re-check trace
⇒ ⚠ **optimising it as a KPI produces a reverse incentive** (⭐ e.g. **closing items wrongly** to bring the number down) ✓
⇒ ⭐ **The right move: bucket by "can this be acted on" first, ⭐ watch 【the actionable bucket】, ⛔ not the total** ✓
