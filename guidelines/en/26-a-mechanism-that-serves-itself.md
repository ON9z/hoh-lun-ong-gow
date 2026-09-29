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
