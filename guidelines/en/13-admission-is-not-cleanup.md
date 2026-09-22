# Admission is not cleanup: a guard that only admits will **accumulate monotonically**

判据：When you write any guard of the "**single instance / dedupe / cap**" kind, can you answer "**the ones that already got in -- who removes them?**" If you cannot, then every object it lets through **stays forever and accumulates**, while the guard **looks like it is working every second**.

**⇒ Why**: this kind of guard only ever answers one question -- "**should I let this one in right now**".
It can stop **new** arrivals, but it has no authority at all over the ones **already inside**.
**⇒ So its failure mode is not "it missed one" -- it is monotone growth.** This is different from
"a criterion that is always true": there the criterion **never speaks**; here it **speaks correctly**,
it just **only handles entry, never exit**.

**Instance**: a "single instance" supervisor script, launched by a scheduled task **every 5 minutes**,
using **the freshness of a heartbeat file** (`<180s` means "an instance already exists, exit") as its mutex.

- As long as the incumbent is **stuck for >180s** (blocked in a call, or waiting on something that
  never returns), the scheduled task **starts another one** -- the guard has just read "stuck" as "dead";
- and **once two coexist, neither ever exits**: they each refresh the heartbeat, so the guard
  now **correctly** blocks further instances -- **but nothing ever removes the ones already running**;
- so it reaches 2 after four days, 3 on the fifth. **Every one of them looks like "the guard working".**
- ⚠ What makes it genuinely dangerous: **these coexisting guards each perform the same
  side-effecting action** (restarting the same service) ⇒ **the coexistence itself becomes the new
  fault source** -- they fight over the same resource, and the symptom is "the service keeps dropping".

**⇒ Practice**:

① Make it the 4th mandatory question: "**who removes the ones that already got in?**"
   (the first three are in guideline 06).
② Do not use a **heuristic that misreads "stuck" as "dead"** -- **that manufactures the coexistence
   itself**. Use **ownership** (record the owner's identity; take over only once it is confirmed
   **genuinely absent**), not **freshness**.
   ⇒ Ownership **also preserves self-healing**: if the owner really died, its identity is gone ⇒ take over.
③ The reaper must itself be **feedable with a known-bad input** (guideline 10):
   **simulate an incumbent that is "stuck but still alive"** and check whether the guard wrongly takes over.
   That is exactly the case where "freshness heuristic" must go red and "ownership" must go green.
④ The reverse trap: **do not build the reaper as "kill anything that might still be alive"**.
   The reaper's criterion must be **existence**, not **responsiveness**.

**⚠️ Boundary with guideline 06**: 06 asks "is this criterion **always true**" (it **never speaks**);
this one asks "the criterion **speaks fine**, but it **only handles entry, never exit**".
Both present as "looks like it is working".

**⇒ A kindred shape: delegated *work* also needs a reclaim mechanism.**

"Admission is not cleanup" asks "**who cleans up the objects already inside**".
The same shape holds for **delegation**: for every piece of work you hand out,
**if it never comes back, who takes it over, and when?**

**Instance**: A repository-wide census was handed to an external executor. It died part-way through
for an **external reason** (quota / balance / network), producing **nothing** -- and all the ledger
recorded was one word: "**dispatched**".
⇒ From that moment the ledger **looked in-progress** while in fact **nobody was doing it**; and the
census existed precisely to answer "**a class that had never been surveyed by the system**"
⇒ that class **became an unowned open item again**.

⚠ The part most worth recording: at the time I had **deliberately** written "**I will not draw a
conclusion myself**" and handed the conclusion over (the **discipline itself was right**).
⇒ **Handing the right to conclude to an entity that may die is handing it to randomness.**

**⇒ How to act**:

① When dispatching, **write the takeover condition at the same time**: "if it has not reported by
   **when**, **who** takes over, with what **fallback**".
   (Same root as guideline 12, "predictions need an expiry": **a promise with no expiry is no promise**.)
② Dispatched work **belongs in the same ledger**, and **"dispatched" alone is not enough** --
   record the **expected artefact** and the **due moment**.
③ Prefer to **build the bounded version yourself** as the reclaim action: a dispatched
   "full census" usually has **a bounded version you can finish in ten minutes** --
   do that first, then wait for the additive part.
