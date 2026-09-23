# A **delimiter** inside the content **re-partitions** the row — and the new partition looks just as normal

判据：**What does the consumer of this row split on?** — then ask: **can that delimiter appear inside the *content*?**

⚠ If it can ⇒ **"which cell is the status column" is decided by the *content*, not by the schema** —
⇒ **writing a single character into a row can change somebody else's status,**
**with no error and no warning.**

**⇒ Why**: a consumer that splits on a raw delimiter (a Markdown table's `split("|")`, a CSV's `split(",")`,
a log line split on spaces) **does not honour escaping** — you write `\|` believing it is "escaped",
and it sees a delimiter. ⇒ **structural boundaries drift with the content**,
and **the drifted result looks entirely normal.**

**⇒ Two hazards (the second is worse)**:

① **One of your writes changes someone else's verdict** — that row's "status cell" slides right
   onto the fragment you wrote, and its ✅/❗ is decided by **whether your prose happens to contain a keyword**.
② ⚠ **The reverse too**: after you remove the delimiter, the row may **coincidentally** look healthy again —
   ⚠ **by coincidence**: the last cell is a keyword-free fragment ⇒ **it looks like it is working every second,
   while it does not mean "this is actually done"**. ⇒ **A verdict that "looks right" is far more dangerous
   than one that errors.**

**Instance (measured, 2026-09-24)**:

A project's **master ledger** is parsed by a state machine into an "open items" list, where
`_cells = line.strip("|").split("|")` — **a raw split**.
⚠ Therefore **the "status column" = the text after the row's *last raw pipe*.**

Appending a note to one row, my prose contained **4 raw pipes** (a shell snippet)
⇒ **the row split into more cells ⇒ the status cell shifted right** ⇒ the new last cell happened to
contain `⛔` (one of `OPEN_MARKS`) ⇒ ⚠ **the row flipped from "closed" to "open":
the ledger's open count went `185 → 186`.**

⚠⚠ **And that row records exactly the defect "this file's table structure is corrupted"** —
**I reproduced that defect on the very row that documents it.**
⚠ How it was localised (**no guessing**): revert each of the two appends **separately on a copy**,
re-run the parser ⇒ reverting that one gives 186→**185**, reverting the other stays at 186 ⇒ **that row**.
⚠ After removing the pipes the row "went back to closed" — **and that time it was coincidence** (hazard ②).

**⇒ What to do**:

① **Before writing into a structured row, ask "does the delimiter occur in here?"** —
   if it does, use an equivalent form that **does not contain it** (`chr(124)`, prose, or a code block).
   ⛔ "But I escaped it with a backslash" **does not count**: a raw-splitting consumer cannot see escapes.

② **When a structured consumer's count moves by ±1 for no reason, suspect the delimiter before the semantics.**
   ⚠ Because "the semantics changed" sends you to edit the content, while the real cause is in the
   **formatting layer** — editing the content only makes it messier.

③ **Rows that already contain a delimiter (legacy) ⇒ their status cell is already a fragment** ⇒
   ⛔ **do not trust their ✅/❗**; find independent evidence before assigning work from them.
   ⚠ This is also the **real root cause** of "table structure corrupted" defects:
   **not "somebody forgot to add a row", but "the row already carries a delimiter"** —
   ⇒ any "add rows line by line" repair will **break while repairing**.

**⚠️ Boundary against guidelines 06 / 16 / 18**:
- **06** is about a **vacuously true criterion** (empty satisfaction);
- **16** is about a **proxy anchor wrong in both directions**;
- **18** is about a **guard that only blocks the failure you happened to see**;
- **this one** is about **"the structural boundary is decided by the content"** —
  ⚠ it produces no error; it **silently changes who is who**.

⚠ **What the four share**: **the failure does not report itself, and it looks like it is working** ⇒
⇒ **whenever something "looks like it is working", ask: is this "right" *computed*, or *coincidental*?**
