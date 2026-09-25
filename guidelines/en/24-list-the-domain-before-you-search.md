# List the **names** of a domain before you search it — grep only answers when you **guessed the word**

判据：**Before I conclude "this contains X / does not contain X" — have I listed the names of this domain?**
Directory listing (`ls`) · or, for a single file, its **section skeleton** (`grep -nE "^#{1,3} " <file>`).
**Cannot produce the list ⇒ my grep was a guess**, and its **empty result** will be read by me as "it does not exist".

**⇒ Why**: **grep tests for a STRING, ⛔ not for EXISTENCE.**
It answers only when **you happen to guess the one word the author used** — ⚠ and **naming is arbitrary**:
the same concept can be `NOVELTY_HARD` / 「新颖性闸」 / `redundancy`,
it can live in a **section heading** with no mention in any sentence,
⚠ or in **a directory you did not search**.

⚠ And **"I grepped and got nothing" looks exactly like "it does not exist" on screen** —
⇒ so **a failed search gets written down as a conclusion**.

⚠ **The more expensive form**: **you grep, you hit something RELATED, and you conclude you found the authority** —
⚠ while the authority sits in **another file**, and **states it more precisely**
(with line numbers, with provenance, with a "confirmed in use" check).

**Instances (one day, four times)**:

① **A structural defect already registered**: I measured that "**an entire class of conclusions is forced into one state bucket**",
   ⚠ **while the ledger had recorded it verbatim five days earlier**, including a suggested fix.
   ⇒ ⚠ **A peer stopped me before I wrote it up as a new discovery** — ⛔ I did not find it myself.

② **A threshold that already existed**: I proposed "**first compute the correlation between a candidate and existing objects**"
   as the first ruler — ⚠ **while the code already had `NOVELTY_HARD = 0.95` / `NOVELTY_GRAY = 0.80`**,
   with a comment reading "old-factor clone, reject outright".

③ **A design document that already said it better**: I wrote up a "criterion chain / five gates" explanation —
   ⚠ **while a design doc already had that section**, and **said more than I did**:
   "**explicitly print the most similar existing factor next to the verdict (|r|=0.87)**",
   "**default leans reject**", "**corresponds to a known upstream defect: generating many highly correlated redundant factors**".

④ **An index page that already existed**: I proposed "**collect the existing artefacts into one index page**" —
   ⚠ **while the repository already had** a "**constant → line number → confirmed in use**" audit table —
   ⭐ **that IS the index page**.

⚠ **In ②③④ my output was WEAKER than what already existed** ⇒ ⭐ **this is not duplicated work, it is OUTPUT DEGRADATION** —
   **duplication saves a pass; degradation is a net loss** (the reader meets the worse version first).

**⇒ Practice**:

① **Entering any domain (code / docs / memory / scripts), list the names first**:
   `ls <dir>`; for a single file, list its **section skeleton** `grep -nE "^#{1,3} " <file>`. ⚠ **Only then** grep keywords.

② **Before concluding "there is no X here", produce the LIST for that domain** —
   ⚠ **the list itself is the evidence**; ⛔ "I grepped X and got no hit" is not.

③ ⚠ **Once you have a candidate, ask "is this the authority for the domain?"** —
   ⚠ if a **more systematic** artefact sits next to it (with line numbers, provenance, a "confirmed in use" check),
   **read that one first**.

**⚠️ Boundary with guidelines 7 / 19 / 23**:
- **7** is "**a negative conclusion needs a second path for verification**" — ⚠ that is **re-checking a negative already made**;
- **19** is "**read the object's own declaration**" — ⚠ that is **a single object**, and it cures "**I read, but I read the wrong object**";
- **23** is "**enumerate the scope of the criterion you wrote**" — ⚠ that is **your output**;
- **this one** is "**before you judge, did you pull up the names of the domain**" — ⚠ that is the **input side**,
  ⚠ and **it happens BEFORE 7 and 19**: **without the list you do not even know which artefact to re-check or read.**

⚠ **What they share**: **all of them treat "my judgement rests on a surface I do not fully hold"**,
⚠ and **this one is the cheapest** — the price is usually one `ls`.
