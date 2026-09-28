# "Fresh" is not a reason to keep a guard — "still reachable" is

判据：**Before I argue 【it cannot be deleted】 because "this guard has a real, recent incident behind it" —**
**did I ask "**can that incident still happen today**"?** ⚠ Cannot answer ⇒ **I have taken "it was right to add" for "it is right to keep"**.

**⇒ Why**: **an incident provenance proves the PAST, ⛔ not REACHABILITY.**
A guard **was added because of a real incident** — and that incident **may long since be unreachable**:
the write entry that produced it was removed / narrowed / made read-only, or the object it checks **became generated** (hand-edits are inert anyway).
⇒ ⚠ **And "the provenance is recent" makes me feel the hole is still dangerous** ⇒
⇒ **so the machinery only grows**: every guard has a provenance, **not one may be removed** — ⚠ and that **is the engine of machinery bloat**.

⚠ **The other half is just as wrong**: I also may **not** delete a guard because "it looks duplicated"
— ⚠ **I must first inject the real sample and see whether it is still caught by another guard**.

**实例 (single-operator single-machine automated system, 2026-09-29)**:
The user ruled "**should there be this many guards (I think there is a defect), streamline it**". ⭐ After measuring the 12 guards I wrote:

> (M1) ⭐ **deleting a guard is unsafe here** — because **all 12 have real incident provenance, and it is recent** ⇒ ⚠ removing any one may reopen a hole I just paid for ✓

⚠ That is **wrong reasoning**, and **an external re-check overturned it on the spot**:

> "**All of them have an incident provenance**" only proves the guard **was right to add**, ⛔ **not that it cannot go now**.
> ⭐ **"Fresh" is not a reason to keep it; "still reachable" is.**
> Deletion criteria (**any one suffices**): ① **Unreachable** (the write entry that produced the incident is gone / narrowed / read-only)
> ② **Unrepresentable** (the target is now generated, hand-edits are inert ⇒ the guard only needs to check idempotence and hash)
> ③ **Superseded** (**the same** historical sample, injected, is still caught by **another retained** guard)
> ④ **Regression-refuted** (the historical sample cannot be injected, or is caught once injected)

⭐ In other words: **I used one dimension ("provenance"), while deleting a guard needs a different one ("reachability")** —
⚠ the two **look cognate** (both are about that incident), **but one is a proxy for the other**.

**⇒ 做法**:

① **Before deleting any guard**, ask the four questions above (①–④) of **each** of its incidents.
   ⚠ **If you cannot answer any one of them, keep it.**
② **Do ③ first**: ⭐ it is **the cheapest and the hardest** — inject the historical incident sample **once**
   and see **how many** guards turn red. **≥ 2 ⇒ there is redundancy to remove** (⚠ but first confirm those two do not each have other duties).
③ **Use "fresh provenance" for ordering, ⛔ never for a verdict**:
   recent provenance says "this class of incident **did** happen" ⇒ ⭐ it is **input to prioritising ①–④**, ⛔ not evidence that "it cannot be deleted".
④ **⚠ Guard the other direction too**: ⛔ do not delete because something "looks duplicated" —
   ⚠ **duplication must be measured via ③**, ⛔ never inferred from reading the code.

**⚠️ Boundaries with rules 13 / 26**:
- **13** (admission ≠ cleanup) says "a **guard** admits but never reclaims ⇒ **the objects it governs** accumulate" — ⚠ that is accumulation of **data**;
- **26** (mechanism self-service rate) says "**every guard is fine while the whole output flows back into the machinery**" — ⚠ that is where the **budget** goes;
- **THIS rule** says "**should this one guard stay**" — ⚠ that is **admission/exit of a guard**,
  ⚠ and **it is upstream of 26**: ⭐ **only if guards can be removed can the machinery avoid growing fat**.

⚠ **Common thread**: they all treat "**using local evidence for a whole-level verdict**",
⚠ and **this one is the most insidious**: **the evidence I used was true** (each provenance is checkable, freshness is measurable),
⭐ **it just did not answer the question I asked** — ⚠ **"why it was added" ≠ "whether it is still needed".**
