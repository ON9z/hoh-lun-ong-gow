# Changelog

All notable changes to this repository are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/); the project uses `MAJOR.MINOR.PATCH`
with the single source of truth being `install/core.py: VERSION`.

---

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
