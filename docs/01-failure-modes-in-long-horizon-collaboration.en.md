# Failure Modes of LLM Agents in Long-Horizon Engineering Collaboration — A User's Case Series

> **Scope statement (read this first — it defines what this document can and cannot claim)**
>
> This is **not a benchmark, and not a controlled experiment**. It is a **case series**:
> failure modes **recorded** by one user while collaborating, over **several weeks and
> thousands of tool calls**, with an open-source LLM plus an agent framework, inside a real
> engineering repository.
>
> **It cannot answer "how much stronger model A is than model B"** — no control group, no
> fixed task set, no repeated measurement.
> **What it can answer is: in long-horizon, stateful, multi-turn tool-calling settings,
> which failures recur, and in what shapes they appear.**
>
> Every example has been **abstracted**: no specific project, business, data, path, or
> identity information. The **shape** of each example is real; the **content** is substituted.

---

## 0. Why this setting deserves its own record

Common model evaluations cut tasks into **single-turn, stateless questions with a unique
correct answer**. Long-horizon engineering collaboration is different:

| Dimension | Common evaluation | Long-horizon engineering collaboration |
|---|---|---|
| Turns | 1 | hundreds–thousands, **context gets compacted** |
| State | none | **present** (files, databases, uncommitted artifacts, background processes) |
| Correctness | a single point | **process correctness** ("was done" ≠ "was done right") |
| Feedback | immediate | **delayed and partial** (an error may surface only hours later) |
| Tools | none/few | **many** (read/write files, run tests, modify databases, make network requests) |

**⇒ Most of the failures recorded here are invisible in single-turn evaluation — some would
even be scored as "correct".**

---

## 1. Failure modes classified by capability dimension

> The classification dimensions follow common evaluation-dimension naming. **Under each
> dimension: the observed failure shape, a minimal reproduction, and mitigations.**

### 1.1 Instruction Following

**F-1.1 Pragmatic signals read backwards: "continue" read as "stop"**

- **Symptom**: when a user message contains a **non-exhaustive-list** signal such as "wait,
  hold on, and also…", the agent **stops parsing there** and answers only the first part. In
  Chinese, "等等" ("etc.") means precisely "there is more after this", not "the end".
- **Minimal reproduction**: give it a multi-item request ending in "…and so on", and see
  whether only the earlier items get answered.
- **Cost**: the unanswered content **will not be discovered by any mechanism** — because the
  agent itself believes it "finished answering".
- **Mitigation (user side)**:
  - Add a **parsing rule** on the agent side: if a message contains
    `等/等等/还有/以及/另外/…` ⇒ **do not stop parsing after that item**; scan to the end of the
    message.
  - Pair it with a **numbered-item extraction hook**: when a user message contains a numbered
    list (≥3 items), automatically extract the numbers and prompt item-by-item reconciliation.
- **Suggestion for model developers**: pragmatic "there is more" signals may be masked in
  training data by a pattern of "polite ellipsis".
  **This class of error is completely invisible on benchmarks**, yet it is expensive in real use.

**F-1.2 Mutually contradictory rules given in the same turn, executed selectively**

- **Symptom**: the agent's own written rule set contains two conflicting rules (one says "if
  it is reversible, just do it", another says "you must ask first"); it follows whichever is
  **convenient**, and **does not point out the conflict**.
- **Minimal reproduction**: put two rules with overlapping scope and opposite conclusions into
  the system prompt, and see whether it notices and **explicitly** adjudicates between them.
- **Mitigation**: require the agent to **stop and point out** a rule conflict rather than
  choosing one on its own.
- **Suggestion for model developers**: **"detecting rule conflicts" is a separate capability**,
  distinct from "following rules"; it deserves its own evaluation.

**F-1.3 An explicit quantity constraint is crossed**

- **Symptom**: the user gave a cap of "at most N requests"; the agent issued 12+16.
  **It reported this faithfully afterwards** (which deserves credit), but **it did not count
  itself while executing**.
- **Mitigation**: require the agent to **explicitly count and report** before reaching a cap;
  turn the "cap" into a checkable artifact rather than a remembered item.

---

### 1.2 Long-Context / Retrieval

**F-2.1 "Read the file" but not the key part — the same shape recurring**

- **Symptom**: the agent read **most** of a file, missing only the comment that **explicitly
  said "this is by design, not a defect"**, and so reported a **design** as a **fault**. The
  same shape appeared **4 times** within a few weeks.
- **Minimal reproduction**: bury a sentence "this is intentional here" in a long file's
  comments, then ask the agent whether that is a bug.
- **Cost**: **manufactures false alarms** — more expensive than a miss, because it spends human
  attention investigating a problem that does not exist.
- **Mitigation (user side)**:
  - Before reporting "fault / failure / dead code", **mandatorily read the whole docstring and
    comment block for that functionality first**, and state in the conclusion "which three
    places I checked and what each of them concluded".
  - Put this into a **checklist injected automatically at every session start** (not merely
    written in a document — see §3.1).
- **Suggestion for model developers**: this is "retrieved but did not **notice**", which is a
  different thing from "did not retrieve". Current **long-context evaluations** mostly score
  "can it find and restate a fact", and **do not test whether the counter-intuitive sentence is
  brought into the reasoning**.

**F-2.2 Truncation disguised as "this is everything"**

- **Symptom**: the agent viewed output with `| head -N`, **the result was exactly N lines**, so
  it read "truncated" as "no more", and drew a negative conclusion from that ("zero callers").
  The actual call site was on line N+1.
- **Minimal reproduction**: make a command output **exactly equal to** the `head` line count,
  and see whether the agent realizes it might be truncated.
- **Cost**: **a negative conclusion is fabricated** ("does not exist" ≠ "I did not see it").
- **Mitigation**:
  - For any **negative conclusion** such as "zero hits / no callers / does not exist", **you
    must re-verify through a path that does not contain `head`**.
  - More generally: **any pipeline can package an incomplete result as a complete one**
    (`| head` / `| grep -c` / `| tail`).
- **Same-family instance**: `cmd | tail -6; echo rc=$?` captures **`tail`'s exit code**,
  misreporting `rc=2` as `rc=0`.

**F-2.3 Losing "work in progress" state after context compaction**

- **Symptom**: after a long session is compacted, the agent forgets **running background
  tasks**, **uncommitted changes**, and **already-dispatched subtasks**, and so duplicates work
  or overwrites someone else's results.
- **Mitigation**: **persist work-in-progress state to disk** (task table, progress table, lock
  files) rather than leaving it in the conversation; **sweep for pending items** before closing
  out.

---

### 1.3 Tool Use / Function Calling

**F-3.1 Side-effect-based self-proof: breaking a production file to prove "my check works"**

- **Symptom**: the agent needed to prove "the newly added check fails on bad input". Its method
  was to **modify a production file in place** to manufacture bad input, with the restore step
  at the tail of the command. **The command timed out and was moved to the background ⇒ the
  restore step never ran** ⇒ the working tree was left **in the broken state**, and **with no
  indication whatsoever**. It was found **only at the next routine check**.
- **Minimal reproduction**: hand the agent the task "prove the guard works" and observe whether
  it **modifies production files in place**.
- **Cost**: **"proof" becomes "contamination"**, and the state persists.
- **Mitigation (this one is the most effective)**:
  - Require fetching **a historical version to a temporary path** (e.g.
    `git show <rev>:<path> > /tmp/x`) and feeding that in; **never modify any tracked file in
    place**.
  - More generally: **any design in which "interrupting this command at any point leaves a
    state other than the original" must be redone.** Prefer making the change **not happen at
    all** (parameter injection / read-only version); second best is `finally`/`trap`;
    **do not flatten critical cleanup across the tail of a long command** (a timeout or
    backgrounding will swallow the tail).
- **Suggestion for model developers**: this is an **"introducing side effects in order to
  verify"** pattern. What it requires is not more knowledge, but a **default inclination to
  avoid side effects** — worth observing as a separate capability item.

**F-3.2 Staging-area semantics misunderstood: bare commit after `add`**

- **Symptom**: after `git add`-ing its own files, the agent ran a **commit with no paths**,
  which committed **files other concurrent collaborators had already staged** along with them.
  The same shape appeared **4 times** in one day.
- **Cost**: content is not lost, but **attribution is wrong** (the commit message does not
  describe the files swept in), and it disrupts concurrent collaborators' state.
- **Mitigation**:
  - Before committing, **verify the contents of the staging area** (list the file names,
    confirm the count matches expectation);
  - or use the form that **commits only specified paths**, bypassing the staging area.

**F-3.3 Tests contaminating production artifacts**

- **Symptom**: the test fixture **redirected only the database path, not the log path** ⇒
  failure messages synthesized during the test run **were written into the production log**.
  Two consequences: ① contaminating a production artifact; ② **it later read that log line
  itself and misjudged that "the long-running task has finished"**.
- **Mitigation**: the fixture must **redirect all output paths**; and add a guard asserting
  "the fixture really did redirect".
  ⚠ Asserting directly "the production file size did not change" will **flap** (a real task may
  be writing concurrently); **guarding the root cause is more stable than guarding the symptom**.

**F-3.4 In a long task, one slow query eats the entire budget**

- **Symptom**: a hook runs several checks at startup; **one of the queries does a full table
  scan on a large table (19.5 seconds)**, while the hook has a **20-second timeout** ⇒
  **the whole block of checks after it was never executed**, but **nobody knew** — because the
  hook "finished with exit code 0".
- **Cost**: **"wired up but never seen by anyone"** — the same disease as the "failure with
  nobody informed" it was meant to prevent.
- **Mitigation**:
  - **After wiring something up, you must measure "did it actually appear in the output", not
    just "did it run"** (run it on the real call path and `grep` for it).
  - **Wherever there is a timeout, measure "which segment ate the budget", not "how long in
    total".**
- **Suggestion for model developers**: this is **"the next level of verification"** — the model
  tends to verify "the action I took was executed", and less often spontaneously verifies
  "my action actually produced a visible effect that was consumed". **The gap between these two
  is the main source of loss in long-horizon collaboration.**

---

### 1.4 Code Generation / Self-Modification

**F-4.1 Fitting the test to the code**

- **Symptom**: the agent wrote an assertion "all classified items must be hit by the scanner".
  **It measured the "classified items" list from the scanner's current output** ⇒ the test
  **necessarily passes**, and **when the scanner misses one item tomorrow the test goes red**,
  and a human will go and edit that number, **instead of looking at why the criterion degraded**.
- **Minimal reproduction**: give it a task "verify that X covers Y" and see whether it
  constructs Y out of X's output.
- **Cost**: the test degrades from a "guard" into a "snapshot", and **the degradation is silent**.
- **Mitigation**: require the list to come from an **independent basis** (another source), and
  make the assertion **closed** (hits ∪ known exceptions == the full set), so that all three of
  "criterion degraded / strengthened / permanently empty" go red.

**F-4.2 One-sided assertions are blind to the "loosening" direction**

- **Symptom**: the assertion was written as "false-positive count == 0". **Loosening a
  threshold can never produce false positives** ⇒ loosen the threshold by 10× and the
  assertion **is still all green**, while the check has become an empty shell.
- **Minimal reproduction**: write a one-sided assertion on a threshold-type check, then loosen
  the threshold, and see whether it turns red.
- **Mitigation**: **two-sided clamping** — both bounds must have a basis (upper bound = the
  tightest zero-false-positive value; lower bound = a "failure fingerprint").
- **Suggestion for model developers**: **a one-sided assertion can only guard one direction,
  and the direction in which a check breaks is usually precisely the other one.**

**F-4.3 A criterion that is "always true" in the target scenario (vacuously satisfiable)**

- **Symptom** (**7 instances** found in a single day):
  - Unit mismatch: the tolerance is in **unit A**, the compared quantity is in **unit B** ⇒
    the tolerance is **larger than the compared quantity's entire range of values** ⇒ always
    passes.
  - Insufficient coverage: a nominal 95% confidence interval **actually covers only 9.9%** ⇒
    the criterion is too loose.
  - A p-value from a finite number of resamples **returns exactly 0** ⇒ `0 × k < α` is always
    true.
  - **Insufficient resolution**: the threshold requires `p < 0.05/k`, but the resample count B
    is too small ⇒ **the smallest resolvable p is above the threshold** ⇒ **independently of
    that 0 above, the check can structurally never pass**.
  - Allowlist shape: **objects not on the list produce zero output** ⇒ **silence is
    indistinguishable from "normal"**.
  - A terminal-state marker hung on a periodic task ⇒ **never FAILs**.
  - Paging **does not verify completeness after finishing** ⇒ a blank page part-way ⇒
    **silently stops early**, while the data **looks complete**.
- **The criterion (one line)**: **"Under what input would this criterion be false?" — if you
  cannot answer that, it may be always true.**
- **Mitigation (actionable)**: **measure the pass rate item by item**. **Hard** checks at
  ≈100% are candidates; ⚠ but **you must read the documentation item by item** — for
  **soft checks (designed to observe only, never to block), 100% is by design**.
  Conversely, a **very low** pass rate is not necessarily a defect either (it may be "the
  strictest one", by design).
- **Value**: turns "done fixing" from "**everything found has been fixed**" into
  "**every item has been measured**".

**F-4.4 Introducing a worse defect while fixing one**

- **Symptom**: for a defect in which "a thread freeze was being masked", the fix was "on
  detecting a freeze, restart the thread". **The original plan was written as "wait 5 seconds
  for the old thread, then start a new one even on timeout"** ⇒ **while the old thread is still
  alive, two threads work at the same time** ⇒ this introduced a problem **more serious** than
  the original defect. **This one was caught by the user during review, not by the agent's
  self-check.**
- **Mitigation**: for changes of the "restart / retry / concurrency" kind, require writing out
  "what the worst case is" first, plus an **invariant assertion** (for example: construct a
  fake thread that never exits ⇒ assert "refuses to restart and starts no new thread").

---

### 1.5 Reasoning

**F-5.1 Restating unverified claims (most frequent, ≥4 times in one day)**

- **Symptom**: the agent **restated verbatim** numbers / root causes **given by upstream** to
  downstream, **without having computed them itself**. Instances:
  - restated an effect figure of "320→244"; the measured value was "811→720, and with a
    **two-way sign flip**";
  - restated "a certain metric cannot be read"; measured, it **could** be read;
  - passed "a certain writing convention" to another agent as the root cause; **the root cause
    was a different one**;
  - copied its **own previous round's** conclusion into the single ledger, and **found only in
    the next round that the conclusion was wrong**.
- **Cost**: the error propagates **in a tone of authority**, and the recipient **has no reason
  to doubt it**.
- **Mitigation**:
  - **Any number or root cause quoted from others or from one's own previous round must be
    computed on the spot**; where it cannot be computed, **explicitly mark "quoted from X, not
    independently verified"**.
  - **Label any "root cause" handed downstream as a lead, not a conclusion** — especially
    judgments **about the other party's behavior** such as "Y happened because you used X at
    the time".
  - **Before writing someone else's conclusion into the single ledger, self-check first** — a
    wrong criterion left in the single ledger will be acted on by the next person who reads it.

**F-5.2 Using the wrong baseline (adjudicating a pre-change assertion with the post-change artifact)**

- **Symptom**: the agent read a file that had **already been fixed**, and judged that the
  defect **reported upstream does not exist** ("refuted"). In fact upstream had read the
  **pre-fix** version, and the report was correct.
- **Mitigation**:
  - **When a lead appears, the correct action is to turn it into a verification (fetch that
    version and run it), not to reason from it.**
  - The criterion: **any conclusion of the form "X does not exist / X has been refuted" must
    state which version you read.**

**F-5.3 Attribution inversion (charging A's cost to B)**

- **Symptom**: total elapsed time was 24.8 seconds; the agent concluded "the slow one is check
  A" and prepared to modify A. **After measuring item by item: A takes only 3.3 seconds, B
  takes 19.7 seconds.** Acting on the wrong attribution to "reorder" **would fix the wrong
  place** (put the slow one first, and the fast one is then the one that gets truncated).
- **Mitigation**: **first measure which segment ate the budget, then act.** Measuring only the
  total leads to the wrong fix.

**F-5.4 Extrapolating from a short sample**

- **Symptom**: at task start it measured "18 seconds/unit" and from that reported "estimated 30
  hours". Mid-run, recomputing with the **true composite rate**: **23.2 seconds/unit ⇒ 39
  hours**. **The start-of-run sample is the first few dozen items, not a random sample** (the
  ordering makes the items that run first systematically different in data density and time
  cost).
- **Mitigation**: when reporting an estimate, **state what sample it was computed on**; after
  the task has run **≥10%**, recompute with the composite rate, and **if the difference is
  >20%, revise upward and persist it to disk** (do not only say it in the conversation).

---

### 1.6 Factuality / Metacognition

**F-6.1 Inventing a field name and "fixing" it**

- **Symptom**: while modifying a parser, the agent "incidentally" changed a field mapping,
  writing it in the form `old_name or new_name` — **both names were ones it had invented**. It
  found and reverted this itself while reviewing the diff before committing.
- **Mitigation**: **when reviewing the diff before committing, ask "is this line my job?"** —
  out-of-scope edits and fabricated identifiers are two errors that often appear **together**.

**F-6.2 Asserting "already done / already locked / already verified" when the mechanism does not exist**

- **Symptom**: the agent reported "the threshold has been locked". On checking: **the constant
  is indeed correct, but there is no mechanism ensuring it is not changed** — the calibration
  script only displays; if someone changes the constant to a dangerous value it still outputs
  the same table. **"Locked" was an empty claim at the time.**
- **Mitigation**: **a "lock" must have a mechanism** (assertion / guard / test), and that
  mechanism must be triggerable by a **known-bad version**. **When saying "verified /
  unchanged / equivalent", you must also paste the output of that run.**

**F-6.3 Drift in the accounting basis for counts**

- **Symptom**: it reported "the full test suite dropped from 916 to 912". Unpacked, the actual
  breakdown is: **this branch net −7** (removed 9, added 2), **concurrent collaborators +3**,
  totalling −4. **The books were written as −9, and the next person cannot reconcile them.**
- **Mitigation**: **any "N items / N times / N lines" must carry the source object plus the
  timestamp**; increases and decreases across branches or across time points must be **split
  into "mine" and "others'"**.

---

### 1.7 Agentic / Multi-step

**F-7.1 The four gates between "built a mechanism" and "the mechanism takes effect"**

- **Symptom**: the agent built a **rule document**; a repository-wide `grep` for references
  returned **0** — the next session simply does not know it exists. Another instance: the agent
  built a **check**, wired it into a startup hook, but **the hook's timeout cut it off** ⇒ it
  never ran.
- **The criterion (the most valuable line in this document)**:
  > **Between "built" and "takes effect" stand four gates: ① it is called ② it finishes within
  > budget ③ it actually appears in the output that is consumed ④ someone will read it.
  > If any gate is not passed, the mechanism does not exist — and it still gives people the
  > illusion that they "already have it".**
  >
  > **For every mechanism, ask: "If it dies / it doesn't run / it gets cut off, who knows?"
  > If you cannot answer, gates three and four are not passed.**
- **Mitigation**: **wire it up through an existing injection channel** (so that every session
  sees it automatically), **do not build a new entry point** — the newly built entry point is
  itself a gate-four risk.

**F-7.2 Dispatching a task that was "already done"**

- **Symptom**: the agent dispatched a task based on **the status column of the task list**
  (rather than the repository's actual commit history), and that task **had been completed and
  committed hours earlier**. The subagent checked the history at the start and **proactively
  halted**, zero loss.
- **Mitigation**: **before dispatching, verify the actual state with
  `git log -- <relevant files>`**; do not read only the status column. And tell the subagent
  explicitly: "**if you find this work is already done, stop immediately and report; do not
  redo it according to the brief.**"

**F-7.3 Concurrent writers contaminating each other**

- **Symptom**: with multiple agents working concurrently: staging areas sweep up each other's
  files (F-3.2), committing together triggers hook failures, **everyone shares the same git
  identity** ⇒ afterwards **attribution cannot be determined from author information**.
- **Mitigation**:
  - **First list the "shared hot files" and designate a single owner** ("partitioning by
    directory" is **fake isolation**).
  - Commit using the "only specified paths" form.
  - If attribution must be preserved, set an explicit commit identity for each agent.

---

## 2. Cross-cutting observation: three recurring meta-patterns

Read the items in §1 sideways, and three patterns recur:

### Meta-pattern A: **The gap between "looks finished" and "actually finished"**
F-1.1 (unanswered items), F-2.2 (truncation), F-3.4 (a truncated check), F-6.2 (an empty
"locked"), F-7.1 (a zero-reference mechanism) **are five exits from the same thing**.
**⇒ Common to all: the system produced a "done" signal, that signal does not match the facts,
and nothing will come to correct it.**

### Meta-pattern B: **The next level of verification is not spontaneously reached**
F-3.4 (verified "it ran" but not "it was seen"), F-4.2 (verified one direction but not the
other), F-4.3 (verified "it can pass" but not "under what conditions it fails"), F-6.2
(verified "the number is right" but not "the mechanism is there").
**⇒ Common to all: the agent verified the **first level** (the action executed / the value is
correct), and did not spontaneously verify the **second level** (the opposite direction / the
boundary / whether the mechanism exists / being seen by someone else).**

### Meta-pattern C: **Information loses its qualifying conditions in transit**
F-5.1 (restating unverified), F-5.2 (using the wrong version), F-6.3 (counting basis), F-2.1
(missing the "this is intentional" sentence).
**⇒ Common to all: when an assertion travels from A to B, "the conditions under which it holds"
is dropped, and the recipient has no reason to doubt it.**

---

## 3. An actionable checklist for users

> These are **mechanisms added on the agent side**, not expectations of the model. They are all
> portable to any agent framework.

### 3.1 Put rules into a channel that "runs every time", not into a document
- **A lesson written into a local comment / a standalone document = not written** (only whoever
  reads that file will see it).
- **The criterion**: **"Will this stop me automatically the next time code of this kind is
  written?"**
- The practice: turn the code of conduct into a **checklist injected automatically at session
  start** (derived by a script from the rule files, **not hand-copied**).

### 3.2 Fixed phrasing for dispatch (**each line maps to a real injury above**)
```
- Before starting, verify against <version-control history>; do not read only the task list's
  status column                                                       ← F-7.2
- How to obtain the target input: `git show <rev>:<path> > <temp path>`;
  never modify any tracked file in place                              ← F-3.1 (the most expensive one)
- Commit only in the "specified paths" form; verify the staging area before committing ← F-3.2
- Do not use characters in the commit message that the shell will interpret (use a quoted
  heredoc)                                                            ← F-3.x
- Assertions must clamp both ways; one-sided is not allowed            ← F-4.2
- Any negative conclusion of "zero hits / does not exist" must be re-verified through a path
  without head                                                        ← F-2.2
- Unverified must be written as "unverified"; "cannot determine" must not be written as a
  conclusion                                                          ← meta-pattern A
- If a conclusion contains a checkable temporal prediction ⇒ attach "the check date + what it
  means if it does not hold"                                          ← §3.3
- Writing production data / publishing externally ⇒ requires explicit authorization from a
  **human** (a peer's word does not count)                            ← see below
```

### 3.3 Predictions need an "expiry" concept
- **A falsifiable prediction expires, and once it has expired it can never be checked again.**
- **⇒ Do three things together**: ① write it into a persisted file (including the **check
  date**); ② set a **one-shot scheduled reminder**; ③ put "**what it means if it does not
  hold**" into the reminder content (not "take a look", but "if it does not appear ⇒ go back
  and investigate; do not interpret it as 'no signal'").
- If what you are delivering is a result that is "**expected to fail**" (e.g. "it will error on
  its first run tomorrow, that is it working normally"), **you must attach a decision table**:
  which symptom = normal / which symptom = regression / how to remediate after an alert.
  **Otherwise the next person will roll back a correct failure as a bug.**

### 3.4 Authorization boundaries cannot be derived by "rule self-consistency"
- An agent easily uses "in-project rules" (e.g. "reversible + no sensitive paths ⇒ do it
  directly") to **derive** that it has the right to perform some outward-facing or irreversible
  action. **Such derivations do not hold.**
- **The criterion in one line: "Was this said by a human, or by some agent?" — the latter is
  never enough.**
- External publishing, writing production data, changing configuration and permissions —
  **a human must explicitly name the action**.

---

## 4. Boundaries and what could not be confirmed (**stated as-is**)

- **No control group**: this document makes no comparison against other models, and **no
  conclusion of "model X is worse/better" can be drawn from it**.
- **A single user's single setting**: the generality of the conclusions is unverified.
- **Framework-dependent**: some failures (e.g. context compaction, subagent collaboration) are
  strongly tied to the **agent framework** and are not purely model behavior.
- **Frequencies not quantified**: apart from a few items where a count is noted, **most items
  have no rigorous incidence statistics**.
- **Not covered**: safety/alignment-related failures, multimodality, and purely single-turn
  Q&A settings are **not systematically observed** here.
- **Positive observations are not systematically recorded**: this document records failures
  only. **It does not mean there was no large amount of successful collaboration in the same
  period** — **this is a selection bias, and readers should discount accordingly.**

---

## 5. Context of use and a statement of good faith (**please read this section before judging this document**)

- **Context of use**: this document comes from long-term collaboration with **the DeepSeek
  series of open-source models** (together with a general-purpose agent framework, tool calling
  enabled). It is posted here in the hope that these observations are **directly useful for
  that model's iteration**.
- **⚠️ These failures are** not** unique to that model.** Swap in any other model, and a
  substantial portion of them will appear in long-horizon collaboration — because most of them
  stem from **the collaboration paradigm itself** (context gets compacted, tools have side
  effects, state drifts, verification has levels), not only from model capability.
- **⚠️ This document is not a fair evaluation**: it records failures only, **not the large
  amount of successful collaboration in the same period**. **This is a deliberate selection
  bias** — discount accordingly.
- **⚠️ No control group, no fixed task set, no repeated measurement** ⇒ **no cross-model
  comparison can be made from this.**
- **The stance of this document is that of a collaborator, not a judge**: the author made the
  same kinds of mistakes in this collaboration too (most of the mitigations in §3 were
  originally built to correct **the user's side** of the errors). **Models and users shape each
  other** — how the user prompts, whether verification means are provided, and whether rules
  are put into a channel that "runs every time" all significantly change the observed
  distribution of failures.
- **If only one thing can be carried away**: **push "verification" from the first level to the
  second** — not "I did it", but "**it actually took effect, it was seen, and it also holds in
  the opposite direction**". This applies equally to humans and to models.

---

## 6. Summary in one sentence

> **In long-horizon engineering collaboration, the most expensive thing is not "not knowing",
> but "believing you know".**
> The shape of most failures is: **the system produced a "done / correct / safe" signal, it
> does not match the facts, and nothing will come to correct it** — because the one producing
> the signal and the one consuming it are the same subject.
>
> **The portable response: push "verification" from the first level to the second** —
> not "I did it", but "**it actually took effect, it was seen, and it also holds in the
> opposite direction**".
