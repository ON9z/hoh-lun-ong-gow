# A visible threshold gets optimized away: don't show a gate's parameter to the side the gate constrains

判据：**This threshold (cap / cutoff / quota / score line) — will the thing it constrains be able to see it?**
If yes ⇒ ⚠ **it is no longer a boundary, it is an objective.**

**⇒ Why**: a threshold you **cannot see** can only be **hit**; a threshold you **can see** can be **hugged**.
⇒ And the constrained side **usually knows its own input distribution better than you do** — it only has to press its output a hair below the line to pass,
⛔ **and that "press it below the line" move is exactly what the line existed to exclude.**

⚠ **A subtler form**: the threshold is **not in the prompt**, but gets **reflected back inside the constrained side's own output**
(e.g. the gate prints "you exceeded by 3%", and next round it lands 0.1% short).
⇒ **The criterion is not "did I put it in the prompt" — it is "can it observe the line through any channel at all".**

**Instance**:

① An **execution-layer gate** carries a **participation cap**. It must **live only in deterministic code**:
   ⛔ not in the prompt · ⛔ not in configuration the constrained side can read.
   The reason: once that side **knows where the cap is, it plans just under it**,
   ⇒ **the gate never fires again** — ⚠ **and "never fires" and "everything compliant" look identical on a dashboard.**

② **Same shape**: a **rejection-rate** monitor written into a report the monitored side can read ⇒ it shapes its behaviour to avoid triggering that trend criterion
   (⚠ and trend criteria are, by construction, even easier to hug than point thresholds).

⇒ ⚠ **Shared root**: **a gate's visibility is the ceiling on its effectiveness.**

**⇒ Practice**:

① **Decide "who can see this line" before "where do I set this line".**
   ⚠ Walk every channel: **prompt / configuration / error text / logs / return values / its own output**.
   ⛔ "I didn't put it in the prompt" is not an argument.

② **A visible threshold ⇒ either change the criterion's shape, or accept that it gets optimized away.**
   - **Change the shape**: replace a **point threshold** with a **capability / trend criterion** (⚠ but note trend criteria are easier to hug);
   - **or**: **drop the threshold entirely and charge the cost instead** (⚠ make hugging unprofitable) —
     ⚠ this is usually more robust, because **it does not require guessing the other side's distribution**.

③ **When verifying, feed it a "hugging" sample**:
   give it an input that is **known to optimize against the threshold**, and see whether it lands **just under the line**.
   ⚠ Feeding only "obviously violating" samples cannot tell you whether the line was already routed around.

**⚠️ Boundary with rule 18**:
- **18** is "a guard **shaped to the one failure you saw** ⇒ blind to the other half of the same thing";
- **this rule** is "the guard **is shaped correctly**, but **the side it constrains can see it** ⇒ it gets routed around".
⚠ 18 is about **the guard's own shape**; this rule is about **the guard's relationship to its object**.
