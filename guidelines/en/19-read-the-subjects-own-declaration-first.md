# Read the subject's **own declaration** before you judge it — and read it **before** you measure

判据：Before you write down "**defect / finding / something is wrong here**", have you read
**the constraint this object declares about itself** — its file header, its top-of-module
docstring, the message text hung on its hook, the comment on its own table column, what the
script prints about itself? And: **at which step did you read it?**
If the answer is "**last**", then every measurement before it was a bet.

**Instance (2026-09-23, one night, nearly filed "working as designed" as a defect)**:

- I measured that "**the buy side has been at zero for 12 trading days**"
  (`pre_gate_signals` BUY=0 day after day, while SELL ran 5-553/day without pause),
  and was **already writing it up in defect format**.
- Meanwhile lines **1-8** of `factor_graveyard.py` (the module docstring) literally say:
  > "**short-horizon alpha is dead; this is the explicit closure that admits short-horizon
  > trading should not be done.** Retained: risk-control SELL (always allowed) + panic-timing
  > BUY (runs on the execution rail, bypassing this gate).
  > **The legitimate short-horizon forms are IPO subscription / reverse repo / panic timing
  > (structural operations), not momentum / pattern / anomaly alpha.**"
- Cross-check: the execution ledger contains **exactly IPO + reverse repo**, matching the
  forms it names, **word for word**.

**⇒ Why this deserves its own entry**: **the measurement can be entirely correct while the
conclusion is entirely wrong.** A measurement answers "**what happened**"; the docstring answers
"**is this intentional**". **Without the second sentence, the first gets read as a bug.**

**⚠⚠ And the sharpest part is not "I did not read it"**: the code comment that decides this
behaviour (`dead factors block BUY only; SELL is always let through`) **I had read before I
measured** — read it, and **still went and "discovered" that the buy side disappeared.**
⇒ **The problem is not whether you read, but in what ORDER you read.** Measuring first and
reading the self-declaration last means betting one reading against four queries.

**⇒ How to act**: put "read its own declaration" **before** the measurement. The cost is usually
one `sed -n '1,40p'`.
**⇒ Criterion (runnable)**: **before typing the word "defect", answer —
"which LINES are this object's self-declaration? Have I read them?"**
Cannot answer ⇒ **do not write it yet; go read.**

**⇒ Kindred shapes**: taking someone's **status label** as fact
(`Enabled=True` does not answer "will it ever move"); taking a **table name** as semantics
(a table called `pre_gate_signals` is, for BUY, actually **post-gate** — the gate sits 200 lines
before the persist call); taking "**it appeared in a log**" as "**production is running it**"
(that may have been a self-test). All three share one shape: **using an object's name / label /
existence in place of its self-declaration / behaviour.**

**⚠️ Boundary with Guideline 01**: 01 is "measure **which part** is the cause before you
change it" — it governs **changing**. This one governs **judging**: the measurement may be
perfect and the verdict still wrong, because nobody asked the object whether it meant to.

**⚠️ Boundary with Guideline 08**: 08 is "do not write 'unverifiable' as a conclusion"
(a **strength-of-wording** rule). This one is a **sequencing** rule: the information existed,
was already read once, and was consulted **after** the work instead of before it.

---

## ⚠⚠ On the night this guideline was written, it landed on itself first

In the **same session** that produced this entry, I built a **new `selfcheck` item** to guard
against the commit hook's checklist drifting. It was written, given a known-bad probe, and the
probe **went red correctly**. It looked entirely sound.

Then it turned out to be a **duplicate**. `install/core.py: hook_checklist_problems()`
(line 258, running under the pre-existing item `[1]`) **already compared the same two sets in
both directions**, and its docstring already stated the rationale more completely than mine --
including the portability argument I had "rediscovered"
("the hook installs into a **user's** repo, where there is **no `guidelines/`**").

**⇒ What found it was not my review -- it was the probe.** To prove the new check would fire,
I deleted entry 19 from the hook; **three** items went red, and one of them was the **older** check.

⇒ Exactly what this guideline says: **the subject's own declaration was sitting at line 258 and I
had not read it.**
⇒ Corollary: **before building a check, grep for whether something already checks it** --
otherwise you get a duplicate guard that "looks like it is working" every second, and whose
existence makes everyone **assume nobody was watching before**.
