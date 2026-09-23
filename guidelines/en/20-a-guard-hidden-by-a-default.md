# A hazard hidden by a **default value**: it looks like it doesn't exist

判据：**This hazard is already in the code — so why has it never fired?** —
⚠ **separate two answers**: ① **it doesn't exist** (that path truly is gone); ② **it exists, but every single time the same default value blocks it**.

Answering ① when the truth is ② ⇒ **you have written down "a blocked hazard" as "no hazard"** —
⚠ **and the default that blocks it is not protected by any criterion, and no instrument measures it.**

**⇒ Why**: a default value is the **cheapest** possible block — one parameter change, no deletion, no explanation, no review.
So it **stays there for a long time**, and **"nothing has ever gone wrong" gets read as "there is no problem"**.
⇒ **the two look identical** (no alert, no error, no log); **only flipping that default once can tell them apart.**

**Instance (two, same shape)**:

① An **impact-cost** function reads `min(quantity / avg_daily_volume * 0.02, 0.02)`.
   Its only call site sits inside `if not skip_slippage:`, and **every production call site passes `skip_slippage=True`**
   ⇒ ⚠ **it never runs in production**.
   ⇒ So the fact that "this coefficient has no source, and differs from another site by ~100×" **is a question nobody has to answer** —
   **it wasn't solved, it was bypassed.**

② A **multi-provider LLM client**, when one provider can't get its own key, would take **another provider's key**,
   while **the endpoint stayed the original provider's** ⇒ ⚠ **the credential would be sent to a different vendor**.
   ⇒ That code **has been deleted**, but **the reason lives only in a comment**, and **the reason it hasn't detonated** is that
   the routing function **happens** to short-circuit that provider — **the comment itself says "the fuse is one line".**

⇒ ⚠ **What the two share**: **the hazard is real, the trigger path is open, and what blocks it is a default value that was never treated as a criterion.**

**⇒ Practice**:

① **Ask "why hasn't it fired" — and give a falsifiable answer.**
   ⛔ "It hasn't fired" is not an answer. Name **the exact line that blocks it**.
   Can't ⇒ **you do not actually know whether it is dead or alive.**

② **Treat that block as a first-class thing**: it is **not** "configuration", it is **an implicit safety boundary**.
   ⇒ Give it **a criterion** (e.g. changing it obliges you to handle the paths it was blocking).
   ⚠ Otherwise, **the moment it is flipped, every hazard it was blocking takes effect at once** — **with no alert.**

③ **Test "after flipping it"**: feed a known-firing sample with the default turned off,
   ⚠ **and see whether it really misbehaves** — that single step proves two things at once: **the hazard exists**, and **the block works**.
   ⛔ Skip it, and **you may be guarding a boundary that quietly stopped existing.**

**⚠️ Boundary with rules 09 / 13 / 14**:
- **09** is "**you thought it took effect; it didn't**" (false-positive direction);
- **14** is "**you edited the file, but what's running is the old copy**";
- **13** is "admission without cleanup ⇒ **objects accumulate**";
- **this rule** is "**you thought it didn't exist; it exists, blocked by a default**" (**false-negative direction**).

⚠ All four **present as "nothing happened"** — ⇒ **whenever nothing is happening, ask: is it truly absent, or is it blocked?**
