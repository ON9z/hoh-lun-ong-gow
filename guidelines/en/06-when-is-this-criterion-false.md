# Can a criterion be always true? Ask "under what input would this criterion be false?"

判据：**Under what input would this check fail to hold?** If you cannot answer ⇒ it may be **always true**.

**Instances (7 in one day, in varied shapes)**:
- **Unit mismatch**: the tolerance is in unit A, the compared quantity is in unit B ⇒ the tolerance is **larger than the compared quantity's entire range of values** ⇒ always passes (pass rate 99.91%);
- **Insufficient coverage**: a nominal 95% confidence interval **actually covers only 9.9%**;
- **Finite resampling returns 0**: `p = (deltas<=0).mean()` **returns exactly 0** when everything is positive ⇒ `0 × k < α` is always true;
- **Insufficient resolution**: the threshold requires `p < 0.05/k`, but the resample count B is too small ⇒ **the smallest resolvable p is above the threshold** ⇒ **it can structurally never pass**;
- **Allowlist shape**: objects not on the list **produce zero output** ⇒ **silence is indistinguishable from "normal"**;
  ⚠ **The same shape has a second medium: the list need not be "objects" — it can be "wording".**
  A check's **rule text** says "any assertion of the 'process stuck / not working' kind must first do X",
  while its **trigger word list** is **hand-maintained** and contains **none of that family's phrasings**
  (stuck / frozen / hung / unresponsive / spinning / `hang` / `frozen` — **all nine miss**) ⇒
  **that entire family of assertions has zero guard**, while the rule reads as though it were guarded.
  ⇒ **Criterion: do the "rule" and the "trigger condition" come from the same enumeration?** Maintaining
  them separately ⇒ the rule points at a class the trigger condition **cannot reach**.
  ⇒ The same day produced a **third** medium: **the wording of the evidence criterion** —
  "the report contains the tool name `py-spy`" is satisfied by "**I did not run py-spy**" and by
  "**py-spy is not installed**" (see guideline 10). **A criterion satisfiable by one sentence = no criterion.**
- **A terminal-state marker hung on a periodic task** ⇒ **never FAILs**;
- **Paging does not verify completeness** ⇒ a blank page part-way ⇒ **silently stops early**, while the data **looks complete**.

**⇒ The actionable version: measure the pass rate item by item.** **Hard** checks at ≈100% are candidates;
⚠ but **you must read the documentation item by item** — for **soft checks designed to "observe only, never block", 100% is by design**.
Conversely, a **very low** pass rate is not necessarily a defect either (it may be "the strictest one", by design).
**⇒ The value: turns "done fixing" from "everything found has been fixed" into "every item has been measured".**
