# A guard shaped to **the failure you happened to see** only works in that one direction

判据：Whenever you write a guard / breaker / cooldown / fallback of the form
"**if X happens, do Y**", ask: "**is X the kind I have *seen*, or the class I have *defined*?**"
If you cannot answer, you have built a **one-sided guard** -- it stops the exact misstep you
already took, is **blind to the other half of the same event**, and **looks like it is working
every second**.

**⇒ Why**: the first time a failure appears, you hold **one sample**.
The condition you extract from it **unconsciously hugs the shape of that one sample** --
its **wording**, its **exception type**, its **trigger path**. Those are features of
"**that one occurrence**", not of the class.

**Instance (measured, 2026-09-23)**: a market-data fetcher carries a "ban cooldown": on a hit it
pushes the cooldown 120 seconds out and stops fetching.

```python
except Exception as e:
    if "Remote end closed" in str(e) or "RemoteDisconnected" in str(e):
        self._cooldown_until = time.time() + 120 ; break     # only these two strings cool down
    if attempt < 2:
        time.sleep(1 + attempt)                              # backoff
```

- The guard **was built from the one occurrence observed** (peer closed the connection) --
  and for that shape it is **fully effective**.
- But a **timeout** enters the same `except`, **does not match** those two strings
  ⇒ **no cooldown, retries as usual** ⇒ each retry sleeps again
  ⇒ a single call costs up to **3 x timeout + 3 seconds of blocking sleep**.
- And the call site is **per symbol** (200+ in one pass) ⇒ worst case **~60 minutes**.
- ⇒ **And the cooldown never once took effect** -- it was waiting for a string that never appears.

⚠ The cost is hidden because it presents as "**the guard is implemented**": the cooldown exists,
no log line complains, and anyone reading that line sees a defence that looks complete.

**⇒ How to act**:

① Before writing the condition, ask "**how many shapes does this class of failure have?**"
   List the **seen** and the **unseen** separately.
② When unsure, write it as "**anything other than success counts**" (default-deny) --
   **not** as "the kind I saw".
③ Give the guard **a probe from the other side** (Guideline 10): **feed it a failure you have
   never seen** and watch whether it stays silent. Feeding it only "the kind you saw" proves
   the **fixture**, not the guard.
④ **Stateful** guards (cooldown / breaker / backoff budget) are the most dangerous: if the state
   never gets set, **every call pays the full price again** -- and "it was never set" is itself
   **not an error**.

**⚠️ Boundary with Guideline 05**: 05 is "**test assertions** must be two-sided" (the assertion
I wrote must also go red in the loosening direction). This one is "**defensive guards in
production are built from the one sample observed**" -- assertions are **designed**; guards are
**pushed into existence by an incident**, and their condition hugs that incident's shape.
Both share one question: **"what does it do in the other direction?"**

**⚠️ Boundary with Guideline 06**: 06 asks "under what input is this criterion false?"
(aimed at **always-true** criteria). This one asks "**how many shapes of this class does this
criterion cover?**" An always-true criterion **never speaks**; a one-sided guard **speaks,
speaks correctly, and is then silent forever outside the one case**.
