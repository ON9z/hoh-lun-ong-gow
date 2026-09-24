# You **wrote a criterion** — did you enumerate **where it applies**?

判据：**This check / guard / predicate I just wrote — how many places should it apply in? How many did I put it in?**

If you cannot answer ⇒ ⚠ **what you built is a criterion that works in exactly one place, while looking like a general rule.**

**⇒ Why**: when you write a criterion you are **staring at one specific failure** ⇒ so you naturally install it **there**.
⚠ But **the shape of the criterion** ("values must be checked" · "suffixes must be covered" · "the missing ones must be filled")
**is inherently general** — ⚠ so **the reader (including future-you) will read it as a general rule**,
⛔ while it in fact covers one place.

⚠ The danger is not "I missed a spot" (that is guideline 17). It is that
**① you have just personally demonstrated the failure exists**, and
**② you fed the antidote to exactly one patient** ⇒ ⚠ **when the next one arrives, you will say "I have a guard."**

**Instances (one shape, one day, three times)**:

① **I had just measured** that "checking only the count misses all-NULL key columns"
   (⚠ with a full mechanism: SQLite's `PRIMARY KEY` permits NULL ⇒ the insert does not error),
   **so I added a value-level self-check to the backfill script** —
   ⚠ while **the smoke test inside that same script still only checked the row count** ("240 rows written").
   ⇒ ⚠ **I built the criterion, wrote the comment, and then used it somewhere else.**

② **A backup-ignore rule**: `.gitignore` had `*.0907bak` (one suffix).
   ⚠ The working tree actually contained **three different suffixes**, and **one had already been committed**.
   ⇒ ⚠ Fixing it, my first version wrote `*.bak_*` (underscore) — ⚠ **which misses the hyphenated one**;
   ⚠ even **the grep I used to verify** (`\.bak$` or `\.bak_`) **missed the same one**.

③ **A value-level self-check** was added at the backfill's write site ✔ —
   ⚠ while **other tables / other write paths in the same batch** got none.

**⇒ Practice**:

① **The moment the criterion is written, enumerate its scope:**
   write down "the classes of object this criterion must cover" — ⚠ cannot ⇒ it is not finished.
   ⚠ **Count them class by class** (⛔ not "I think there are a few more").

② ⚠ **Feed it the scene where you found it, one more time** —
   ⚠ if you found the failure at A and installed the guard at B, ⚠ **the failure at A must be caught by it.**

③ ⚠ **Put the scope into the criterion's own name or comment** —
   "value-level self-check (⚠ covers: **every** write path in this script)" is far safer than "value-level self-check".

**⚠️ Boundary with guidelines 13 / 17 / 18**:
- **17** is "**one piece of logic, N places, I changed 1**" — ⚠ that is a **fix**;
- **18** is "**the guard's shape was grown from the one failure you saw**" — ⚠ that is a **shape**;
- **this one** is "**at the moment of construction the scope was empty**" —
  ⚠ not a wrong fix, not a wrong shape, **a thing that only ever covered one place from birth**.

⚠ **What the three share**: **the failure happens outside the criterion's reach,
and the criterion cannot see its own boundary.**
