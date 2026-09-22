# A proxy used as an anchor can be **wrong in both directions**: measure directly when you can

判据：Before using some quantity X to decide "did event Y happen?", ask
"**is X correct in both directions of Y?**"
If you cannot answer, X is a **proxy** -- and a proxy does not fail by being "a bit off";
it fails by **lying to you in both directions**.

**⇒ Why**: A proxy is always chosen because it is **correlated** with the truth, and that
correlation is exactly what hides **the part it misses**.
Worse: **a proxy's two directions are rarely checked together**. You usually hit one direction,
then "fix" it using the same reasoning -- which **freezes the other direction in place**.

**Instance (one anchor, both directions fooled, on the same day)**:
Using "**the newest commit time**" as the anchor to decide "is the running process on old code?".

| Situation | What the proxy reads | The truth |
|---|---|---|
| Working tree has **uncommitted** edits, process started after them | commit is older than process start ⇒ **"fresh" (false green)** | the edits were **never loaded** |
| **Deployed first, committed after** | commit is newer than process start ⇒ **"old code" (false red)** | it is running exactly that revision |

⇒ **The fix is not "tune the threshold", it is to switch to a direct measurement**:
anchor on "**the modification time of the newest source file**".
It answers **"when did the code on disk last change?"** -- **correct in both directions**.

**⇒ How to act**:

① **Prefer the direct measurement; use a proxy only as a fallback** -- even when the direct one
   is "cruder" (file timestamps vs version-control metadata).
② If you must use a proxy, **feed it one known sample per direction** (Guideline 10):
   "truth moved but the proxy did not" **and** "the proxy moved but the truth did not" --
   both must be able to flip.
③ Having chosen an anchor, ask **which way its error leans**. In the example above the cost of
   mtime is a **false red** (`checkout`/`touch` rewrites timestamps without changing content) --
   **that is the safe direction**: **someone looks at a false red; nobody ever looks at a false green.**

**⚠️ Boundary with Guideline 05**: 05 is "an **assertion** must be two-sided" (the assertion you
wrote must also go red in the loosening direction). This one is "**choosing the anchor / criterion**"
-- an assertion can be written perfectly and **still be wrong in both directions if the anchor is wrong**.

**⚠️ Boundary with Guideline 06**: 06 asks "under what input is this criterion false?" (aimed at
**always-true** criteria). This one asks "what does this proxy read, in **each direction** of the
truth?" An always-true criterion **never speaks**; a two-sided-wrong proxy **speaks in both
directions, and is wrong in both**.
