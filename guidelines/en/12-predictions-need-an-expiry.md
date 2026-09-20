# A prediction needs an expiry date: persist it + a scheduled reminder + "what it means if it does not hold"

判据：Have I written down this prediction's **check date** and its **check method** (which command / which query)? Have I written down **what it means if it does not hold**?

**⇒ Why**: **a falsifiable prediction expires, and once expired it can never be checked again.**

**⇒ Do three things together**:
① write it into a persisted file, including the **check date** and the **check method**;
② set a **one-shot scheduled reminder** (automatically recalled on the due date);
③ put "**what it means if it does not hold**" into the reminder content —
   ✗ "take a look at the result" ✓ "if it does not appear ⇒ the fix did not take effect ⇒ go back and investigate, **do not explain it away as 'no signal'**".

**⇒ The stronger form**: when delivering a result that is "**expected to fail**", **a decision table is mandatory** (which symptom = normal / which symptom = regression / how to remediate after an alert).
> **Without this table, the next person will roll back a "correct failure" as a bug.**
