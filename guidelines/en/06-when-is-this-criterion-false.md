# Can a criterion be always true? Ask "under what input would this criterion be false?"

判据：**Under what input would this check fail to hold?** If you cannot answer ⇒ it may be **always true**.

**Instances (7 in one day, in varied shapes)**:
- **Unit mismatch**: the tolerance is in unit A, the compared quantity is in unit B ⇒ the tolerance is **larger than the compared quantity's entire range of values** ⇒ always passes (pass rate 99.91%);
- **Insufficient coverage**: a nominal 95% confidence interval **actually covers only 9.9%**;
- **Finite resampling returns 0**: `p = (deltas<=0).mean()` **returns exactly 0** when everything is positive ⇒ `0 × k < α` is always true;
- **Insufficient resolution**: the threshold requires `p < 0.05/k`, but the resample count B is too small ⇒ **the smallest resolvable p is above the threshold** ⇒ **it can structurally never pass**;
- **Allowlist shape**: objects not on the list **produce zero output** ⇒ **silence is indistinguishable from "normal"**;
- **A terminal-state marker hung on a periodic task** ⇒ **never FAILs**;
- **Paging does not verify completeness** ⇒ a blank page part-way ⇒ **silently stops early**, while the data **looks complete**.

**⇒ The actionable version: measure the pass rate item by item.** **Hard** checks at ≈100% are candidates;
⚠ but **you must read the documentation item by item** — for **soft checks designed to "observe only, never block", 100% is by design**.
Conversely, a **very low** pass rate is not necessarily a defect either (it may be "the strictest one", by design).
**⇒ The value: turns "done fixing" from "everything found has been fixed" into "every item has been measured".**
