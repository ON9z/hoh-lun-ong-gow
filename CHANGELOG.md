# Changelog

All notable changes to this repository are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the project uses `MAJOR.MINOR.PATCH`
with the single source of truth being `install/core.py: VERSION`.

---

## [1.3.6] — 2026-09-25

**Theme: four times in one day, the thing I "discovered" had already been written down — and three times my version was the weaker one.**

I spent a long session re-deriving what the repository already contained, because I searched for **one keyword**
instead of **listing the names of the domain first**. A single `ls` would have ended each of the four episodes
before it started. The most expensive part was not the wasted effort — it was that **my output was, three times
out of four, less precise than the artefact that already existed** (no line numbers, no provenance, no
"confirmed in use" check). Duplication costs one pass; **degradation costs the reader the better source**.

### Added

- **Guideline 24 — 进任何域之前，先列出它的名字 —— grep 只在你猜对了词时有效** · [`guidelines/24-list-the-domain-before-you-search.md`](guidelines/24-list-the-domain-before-you-search.md)
  Criterion: **before I conclude "this domain contains X / does not contain X" — have I listed the names of
  this domain?** Directory listing (`ls`) · or a single file's section skeleton (`grep -nE "^#{1,3} "`).
  Cannot produce the list ⇒ **my grep was a guess**, and I will read its empty result as "does not exist".
  ⚠ **The more expensive form**: you grep, you hit something *related*, and you conclude you found the
  authority — while the authority sits in another file and states it more precisely.
  Boundary with 7 (re-check a negative on a second path) · 19 (read the object's own declaration) ·
  23 (enumerate the scope of the criterion you wrote) — and the reason this one comes **first**: without the
  list you do not even know **which artefact to re-check or read**.
  ⚠ Instances are dated and kept as they happened: one of the four was caught by **a peer**, not by me.

### Changed

- **`hooks/pre-commit` checklist synced to 24** — the hand-maintained list is checked by
  `hook_checklist_problems()` against `guidelines/*.md` (bidirectional set equality). ⚠ The check only
  **prints**; silence is indistinguishable from a complete list (it is itself an instance of guideline 06).

## [1.3.5] — 2026-09-24

**Theme: you just proved the disease exists, and you fed the antidote to exactly one patient.**
A day of audit produced a criterion whose mechanism was fully understood — "checking only the count
misses all-NULL key columns, because SQLite's PRIMARY KEY permits NULL so the insert does not error".
It was added to the backfill script with a careful comment. **The smoke test inside that same script
still checked only the row count** — and reported success on 51,541 rows whose key column was NULL.

### Added

- **Guideline 23 — 你造了一条判据，但它该被用在哪几处，你枚举了吗** · [`guidelines/23-a-rule-you-wrote-must-name-where-it-applies.md`](guidelines/23-a-rule-you-wrote-must-name-where-it-applies.md)
  Criterion: **this check / guard / predicate I just wrote — how many places should it apply in?**
  Cannot answer ⇒ **a criterion that works in exactly one place, while looking like a general rule**.
  ⚠ The danger is not "I missed a spot" (guideline 17) — it is that you have **just personally demonstrated
  the failure exists**, and you fed the antidote to **exactly one patient**, so the next one is met with
  "I have a guard". Three instances, one day, one shape: the value-level predicate vs. its own smoke test ·
  a `*.0907bak` ignore rule facing three suffixes (and the first fix — and the verifying grep — missed one) ·
  a self-check added on one write path while sibling paths got none.
  Boundary with 13/17/18 spelled out. Criterion: **enumerate the scope at the moment of construction,
  and feed the criterion the scene where you found it.**

### Fixed

- **`selfcheck` [7] was too narrow, and the fix needed guideline 23 applied to itself** — the changelog
  guard asked only whether an entry exists, so this entry was written before the version bump was verified.

## [1.3.4] — 2026-09-24

**Theme: the consumer splits on a raw delimiter, so the *content* decides which cell is the status column.**
A ledger row flipped from "closed" to "open" because a note appended to it contained four raw pipe
characters — the "status cell" slid onto the new fragment. The row in question documented
*"this file's table structure is corrupted"*. **The defect was reproduced on the row that documents it.**

### Added

- **Guideline 22 — 内容里的分隔符会把这一行重新分栏 —— 而新的分栏看起来一样正常** · [`guidelines/22-a-delimiter-in-the-content-re-partitions-the-row.md`](guidelines/22-a-delimiter-in-the-content-re-partitions-the-row.md)
  A consumer that splits on a **raw delimiter** (Markdown `split("|")`, CSV `split(",")`) does not honour
  escaping — `\|` is still a delimiter to it. ⇒ **"which cell is the status column" is decided by the content.**
  Measured instance: appending prose containing 4 raw pipes to a ledger row moved the status boundary onto
  a fragment containing `⛔` ⇒ **the open-item count went 185 → 186**. Localised with **no guessing** by
  reverting each append **separately on a copy** and re-running the parser.
  ⚠ **The worse half**: after removing the pipes the row flipped back to "closed" — **by coincidence**
  (the last cell is a keyword-free fragment). **A verdict that "looks right" is more dangerous than one that errors.**
  Criterion: before writing into a structured row, ask "**does the delimiter occur in here?**",
  and when a structured consumer's count moves by ±1 for no reason, **suspect the delimiter before the semantics**.

### Fixed — a version that advanced while its own changelog did not

- **`selfcheck` [7]: CHANGELOG must contain an entry for the current `VERSION`.**
  ⚠ Measured: the `1.3.2` and `1.3.3` commits **never touched `CHANGELOG.md`**
  (`git show --stat` — neither file list contains it) ⇒ `VERSION` moved, the README version claims were
  updated, `selfcheck` stayed **green**, and the changelog's last entry stayed at `1.3.1` —
  i.e. the README sentence *"Current: v1.3.4"* pointed at a file with no `1.3.4` in it.
  **A lying artifact, produced by three green checks.**
  ⚠ Root cause is the same shape as the `v1.2.0`-had-no-tag incident that `[6]` was added for:
  **not "somebody forgot", but "nothing was asking the question"** — and the check added then covered
  the tag axis but **not the changelog axis**.
  Made **red** (same as `[5]`): there is **no legitimate window** — the entry belongs in the same commit
  as the version bump. Verified by feeding it the real defect: **`[7]` went red and named the stale head (`1.3.1`)**
  before the entry existed, and green after.

## [1.3.3] — 2026-09-24

### Added

- **Guideline 21 — 一个**看得见**的阈值会被优化掉** · [`guidelines/21-a-visible-threshold-gets-gamed.md`](guidelines/21-a-visible-threshold-gets-gamed.md)
  Criterion: **can the thing this threshold constrains *see* the threshold?**
  If it can ⇒ ⚠ **it is no longer a boundary, it is an optimization target** —
  and the more visible it is (a printed score, a line in a prompt, a hard cap quoted in the same context),
  the faster it gets optimized away. ⚠ Measured instance in this repo's own tooling: a **quota** whose
  remaining count is printed back to the very agent it constrains.

## [1.3.2] — 2026-09-24

### Added

- **Guideline 20 — 隐患被一个默认值挡着，看起来像不存在** · [`guidelines/20-a-guard-hidden-by-a-default.md`](guidelines/20-a-guard-hidden-by-a-default.md)
  Criterion: **this hazard is already in the code — so why has it never fired?**
  Separate ① **it doesn't exist** from ② **it exists, and every single time the same default blocks it**.
  Answering ① when the truth is ② ⇒ **you have recorded "a blocked hazard" as "no hazard"** —
  and the blocking default is protected by no criterion and measured by no instrument.
  Two measured instances: an impact-cost function whose only call site passes `skip_slippage=True`
  (so it never runs in production, and nobody has to answer where its coefficient came from);
  and an LLM client that falls back to **another provider's key** while keeping the original endpoint.

## [1.3.1] — 2026-09-23

**Theme: the measurement was right and the verdict was wrong.** A night of auditing a real
system produced a clean measurement — "the buy side has been at zero for twelve trading days" —
which was **about to be filed as a defect**. It was, in fact, **the system's own deliberate
closure**, and its module docstring says so in its first eight lines.

### Added

- **Guideline 19 — 先读它自己声明的规矩，再下断言 —— 而且要读在动手之前** · [`guidelines/19-read-the-subjects-own-declaration-first.md`](guidelines/19-read-the-subjects-own-declaration-first.md)
  A measurement answers "**what happened**"; the subject's own declaration answers
  "**is this intentional**". Without the second sentence the first is read as a bug.
  Measured instance: a gate had blocked **2,598 BUY signals (and 0 SELL)** since a given date,
  because the project had decided **short-horizon alpha was dead** — the module's docstring
  says so, names the surviving legitimate forms, and the execution ledger contains
  **exactly those forms**. **The sharpest part is not "I never read it"**: the code comment
  deciding that behaviour **had been read before the measurement** — read, and the "discovery"
  made anyway. ⇒ **The defect is in the ORDER of reading, not in the reading.**
  Criterion: before typing "defect", answer "**which lines are this object's self-declaration,
  and have I read them?**" Cannot answer ⇒ do not write it yet.

### Not added — a duplicate check was written and then deleted

- A `selfcheck` item comparing the **commit hook's printed checklist** against `guidelines/` was
  written, given a known-bad probe, and **it went red correctly**. It was then **removed**.
  **It was a duplicate**: `install/core.py: hook_checklist_problems()` (runs under index `[1]`)
  already compared the two **sets** in **both** directions, and its docstring already carried the
  exact portability argument the new item was "discovering"
  ("the hook installs into a **user's** repo, where there is no `guidelines/`").
  ⚠ **What found it was not a review — it was the red test.** Deleting the hook's entry to prove
  the new check would fire produced **three** failures, one of them the **older** check.
  ⇒ **This is Guideline 19 performed against this very commit**: the declaration sat at
  `core.py:258`, reasoning included, unread.
  ⇒ Net kept: **nothing**. The pre-existing check already covers it. The three places the count
  lives (`VERSION`/CHANGELOG, `README.md`, hook) each already have a watcher `[5]` / `[1]`.

### Changed

- README (all language sections) and `install/core.py: VERSION` → `1.3.1`.

---

## [1.3.0] — 2026-09-23

**Theme: the guard you wrote *because of* one incident, and the conclusion that loses its scope
when you repeat it.** Both new entries come from a single night of work, and both were found by
turning the same lens on the work itself.

### Added

- **Guideline 18 — 照你看见过的那一次失败造的守卫，只在那个方向上有效** · [`guidelines/18-a-guard-shaped-to-the-failure-you-saw.md`](guidelines/18-a-guard-shaped-to-the-failure-you-saw.md)
  When a failure appears, you hold **one sample**; the condition you extract hugs **that sample's
  shape** — its wording, its exception type, its trigger path. The guard stops the misstep you
  already took and is **blind to the other half of the same event**, while looking implemented
  every second. Measured instance: a "ban cooldown" matched two exact `RemoteDisconnected`
  strings — so a **timeout** in the same handler **never set the cooldown**, retried with blocking
  sleeps, and across a per-symbol call site (200+ per pass) cost up to **~60 minutes** —
  **the cooldown never once took effect**, having waited for a string that never appears.
  Criterion: is X the kind you **saw**, or the class you **defined**?

### Changed

- **Guideline 08** gained a kindred shape: **the boundary must travel with the claim.**
  Measured on the same night: the written artefact recorded the honest limit ("you **cannot**
  conclude this path is clean — the tool's recall is unknown"), and the **conversation** restated
  the same finding as "**this path is swept clean**". Not an inaccurate criterion — the **same
  criterion spoken at two strengths**, because compression removes the scope first.
  Criterion: *before restating a conclusion, ask what qualifiers you attached last time.*
- **Guideline 17** gained the other kind of "only part of it": **the same shape at multiple *call
  sites*.** Measured: one fix shape ("no unbounded network call on the tick thread") appeared
  **four times in the same file**; the fixing was **pushed along by incidents**, so four sites took
  **four rounds**, two of them a full night apart. Criterion: after fixing one site, **write the
  shape as a searchable sentence and go search**; extract a shared unit; turn "a new site appeared"
  into a criterion that goes red; and **delete the registry entry once fixed** (otherwise the
  allow-list becomes a list of what once existed — Guideline 13's family).
- README and the pre-commit checklist updated to 18; `VERSION` → `1.3.0`.

---

## [1.2.0] — 2026-09-23

**Theme: a fix is an action with consequences — and the consequences are the part nobody records.**
All three new entries, plus two folded extensions, come from one night of work in which
every change was made deliberately, verified, and *still* produced a second-order effect that
nothing was watching for.

### Added

- **Guideline 15 — 修好一个故障，会移除一条依赖这个故障的隐性路径** · [`guidelines/15-a-fix-removes-what-depended-on-the-bug.md`](guidelines/15-a-fix-removes-what-depended-on-the-bug.md)
  A long-running fault **grows its own ecosystem**: other mechanisms adapt to it, route around it,
  or ride on top of it — adaptations that live in no design document. Fix the fault and those
  adaptations vanish with it, unwarned, because **the path you dismantled was never written down**.
  Measured instance: a keeper restarted a hanging service roughly 1–5 times a day, 28 days running,
  **never a zero day** — and "restart" had quietly become the deployment mechanism for unrelated
  changes. Fixing the hang would have removed it, and no dashboard measured the thing that stopped.

- **Guideline 16 — 代理量当锚点会双向错：能直接量，就别用代理** · [`guidelines/16-a-proxy-anchor-can-be-wrong-in-both-directions.md`](guidelines/16-a-proxy-anchor-can-be-wrong-in-both-directions.md)
  A proxy is chosen because it correlates with the truth — and that correlation is exactly what
  hides the part it misses. A proxy does not fail by being "a bit off"; it fails by **lying in both
  directions**. Measured instance: "newest commit time" used as the anchor for "is the running
  process on old code?" — **false green** with uncommitted edits, **false red** when deploy preceded
  commit, both hit on the same day. The fix is not a better threshold; it is a **direct measurement**
  (newest source-file mtime), correct in both directions.

- **Guideline 17 — 半个修复比没有修复更误导** · [`guidelines/17-half-a-fix-is-worse-than-none.md`](guidelines/17-half-a-fix-is-worse-than-none.md)
  A criterion usually acts in **more than one layer** ("what counts as a hit" / "how it propagates").
  Fixing only one layer does not remove the noise — it **changes its form**, and the new form
  **looks more like a conclusion**. Measured instance: an exclusion set applied at the "hit" layer but
  not the "propagation" layer turned 2776 obviously-noisy hits into 152 "high-specificity candidates"
  that were **mostly still false** — i.e. **a trusted list**, which is exactly the one a human reads line by line.

### Changed

- **Guideline 09** gained two kindred shapes: **a lazily-printed log string is not a liveness probe**
  (a string inside a lazy initialiser only appears on first use — so "0 hits" gets misread as
  "the new code never ran"), and **a label is not behaviour** (`Enabled=True` plus a name that
  promises a daily run, on a one-shot trigger that already expired, means it will never run again —
  read the scheduler, not the label).
- **Guideline 13** gained a kindred shape: **delegated *work* also needs a reclaim mechanism**.
  A dispatched task that dies from an external cause leaves a ledger that says "dispatched" and
  **looks in-progress while nobody is doing it**. The sharpest part: handing the right to conclude
  to an entity that may die is handing it to randomness — so a dispatch must record **who takes
  over, by when, with what fallback**.
- README and the pre-commit checklist updated to 17; `VERSION` → `1.2.0`.

---

## [1.1.0] — 2026-09-21

**Theme: two failure modes that both present as "the mechanism looks like it is working".**
Both entries come from a single day of real work; both were expensive precisely because
nothing ever went red.

### Added

- **Guideline 13 — 准入 ≠ 清理 (admission is not cleanup)** · [`guidelines/13-admission-is-not-cleanup.md`](guidelines/13-admission-is-not-cleanup.md)
  A guard of the "single instance / dedupe / cap" kind only ever answers *"should I let this one in
  right now?"*. It can stop **new** arrivals but has **no authority over the ones already inside** —
  so its failure mode is not "it missed one", it is **monotone accumulation**, and it looks healthy
  the entire time.
  Measured: a scheduled task launched a "single instance" supervisor every 5 minutes; the mutex was
  **heartbeat freshness** (`<180s` ⇒ exit). The moment the incumbent **stalled >180s**, a second one
  started — and **once two coexisted, neither ever exited** (each refreshed the heartbeat, so the
  guard then correctly blocked further ones, but nothing removed the ones already running).
  4 days → 2 instances; day 5 → 3. And because each instance performed the same side-effecting action,
  **the coexistence itself became the new fault source**.
  ⇒ New mandatory question: **"who removes the ones that already got in?"** Use **ownership**, not a
  **freshness heuristic that misreads "stuck" as "dead"** — that heuristic *manufactures* the very
  coexistence it is meant to prevent.

- **Guideline 14 — 改了文件 ≠ 行为变了 (edited is not loaded)** · [`guidelines/14-edited-is-not-loaded.md`](guidelines/14-edited-is-not-loaded.md)
  "I edited the file" is **an action I took**; "behaviour changed" is **a property of the system**.
  Between them sits **a load moment**, and that moment is not inside my field of view.
  Measured: I added failure-scene capture to a supervisor script and treated the file's mtime as proof.
  The script **had already been started 41 seconds earlier** and reads itself **by byte offset**.
  A failure later that day left **no snapshot** — and my reading was "no snapshot ⇒ no failure happened".
  Wrong: the log recorded one. The real conclusion was "**the running copy is still the old content**".
  ⇒ Verify **from the running side** (version / load time / one observable new behaviour), never from
  the filesystem. And **"I see no output" has two readings** — check which one before choosing.

### Changed

- **Guideline 06** gained a second and third medium of the "allowlist shape" instance:
  the list need not be **objects** — it can be **wording**. A check whose *rule text* says "any
  assertion of the 'stuck process' kind must first do X" while its **hand-maintained trigger word
  list contains none of that family's phrasings** leaves **that entire family unguarded**, while the
  rule reads as though it were guarded. ⇒ Ask: **do the "rule" and the "trigger condition" come from
  the same enumeration?**
- **Guideline 10** gained the shape that is hardest to see in yourself: **when you fix a vacuously
  satisfiable check, you very easily build another vacuously satisfiable one.** Measured: the
  replacement criterion was "the report contains the string `py-spy`" — refuted immediately by
  "I did not run py-spy" and "py-spy is not installed". ⇒ Two required moves: **turn the ruler you
  just used onto your own artifact**, and **write the criterion against the measured shape of real
  evidence** (run the tool first, look at its actual output) rather than against a guess.
- `README.md`: "12 guidelines" → "14 guidelines" in all three languages (EN / 简体 / 繁體).
- `hooks/pre-commit`: the pre-push checklist now lists all 14 guidelines.

### Fixed

- **`hooks/pre-commit`'s guideline checklist was hand-maintained and silently drifted.** The list
  cannot be derived (the hook is installed into *consumer* repos, where `guidelines/` does not
  exist), so it must be carried inside the hook — which means it *will* drift, and since it **only
  prints**, the drift is indistinguishable from the list being complete.
  ⇒ Added `hook_checklist_problems()` to the installer, asserted from `selfcheck`:
  **the numbers in the checklist must equal the numbers in `guidelines/*.md`**, both directions,
  **with two feed cases** (a list missing one entry must report; a complete list must not).
  This check caught its own first real drift on the day it was written.

### Verification

- `install/core.py selfcheck` → **exit 0**, all sections green (14 条 × 2 languages; hook checklist
  in sync; the new feed cases pass; the installed git hook is byte-identical to `hooks/pre-commit`).
- `install/core.py status` → `claude`, `cursor`, `generic` all **已装（与 guidelines 一致）**.
- `AGENTS.md` regenerated by `sync` and now reads `BEGIN v1.1.0`.

### Notes

- `install/core.py` contains a **historical** docstring (`guidelines_dir()`) that says
  "24 files on disk, `load_guidelines()` returns only 12". That sentence records the state at the
  time of the bug it describes and is **deliberately not updated** — rewriting it would falsify history.
  Version numbers elsewhere are derived, not duplicated.

---

## [1.0.0] — 2026-09-20

First public release: the failure-mode catalogue (`docs/01`), the mechanism-building practices
(`docs/02`), portable design across agents (`docs/03`), 12 guidelines, and an installer that can be
installed and removed cleanly.
