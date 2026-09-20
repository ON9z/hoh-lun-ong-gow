# Failure modes and mechanism-building in agent collaboration

Three sets of **field observations** from **long-term engineering collaboration** between one user
and an AI agent (weeks, thousands of tool calls).

**They are not benchmarks; they are a case series.** They contain no specific project, business,
data, or identity information.

---

## Contents

| File | Contents |
|---|---|
| [`docs/01-failure-modes-in-long-horizon-collaboration.en.md`](docs/01-failure-modes-in-long-horizon-collaboration.en.md) | **Failure modes classified by capability dimension**: instruction following / long-context retrieval / tool use / code generation and self-modification / reasoning / factuality and metacognition / multi-step and agentic collaboration. Each entry has: symptom · minimal reproduction · mitigation · suggestion for model developers |
| [`docs/02-mechanisms-for-ai-assisted-engineering.en.md`](docs/02-mechanisms-for-ai-assisted-engineering.en.md) | **A set of practices for turning "criticism and lessons" into mechanisms**: the four-gates criterion / automatic guideline injection / a dictionary of error types / a checklist-reconciliation hook / a dispatch template / **criteria and counterexamples for using subagents and teams** / prediction expiry / authorization boundaries / a single source of truth / mechanism self-proof |
| [`docs/03-portable-mechanism-design.en.md`](docs/03-portable-mechanism-design.en.md) | **Making mechanisms work across agents**: the host capability matrix / **the five-layer design L0–L4** / why the **commit hook** is the broadest common ground across agents / capability probing / per-layer self-proof / privacy (the diagnostic bundle carries structure, not content) |

---

## Why it is worth reading (if you are building agents or doing long-term AI collaboration)

Common evaluations cut tasks into **single-turn, stateless questions with a unique correct
answer**. The real properties of long-term collaboration are different:

| Dimension | Common evaluation | Long-horizon engineering collaboration |
|---|---|---|
| Turns | 1 | hundreds–thousands, **context gets compacted** |
| State | none | **present** (files, databases, uncommitted artifacts, background processes) |
| Correctness | a single point | **process correctness** ("was done" ≠ "was done right") |
| Feedback | immediate | **delayed and partial** |
| Tools | none / few | **many, and with side effects** |

**⇒ Most of the failures recorded here are invisible in single-turn evaluation — some would even
be scored as "correct".**

---

## Three things you can take away immediately

**1. The four gates** (from two real counterexamples in one measurement)
> **Between "built" and "takes effect" stand four gates: ① it is called ② it finishes within
> budget ③ it actually appears in the output that is consumed ④ someone will read it.**
> **If any gate is not passed, the mechanism does not exist — and it still gives people the
> illusion that they "already have it".**
>
> **Acceptance criterion: "If it dies / it doesn't run / it gets cut off, who knows?" If you
> cannot answer, gates three and four are not passed.**

**2. Push verification from the first level to the second**
> Not "I did it", but "**it actually took effect, it was seen, and it also holds in the opposite
> direction**".
> Measured: **7 checks that "a criterion can be vacuously satisfied"** were found in a single day
> (unit mismatch / insufficient coverage / finite resampling returning 0 / resolution
> insufficient to reach the threshold / allowlist shape / a terminal-state marker hung on a
> periodic task / paging without completeness verification).
> **The criterion: "Under what input would this criterion be false?" — if you cannot answer
> that, it may be always true.**

**3. When you require an action, you must also give the "permitted way to implement it"**
> A task brief said only "you must verify with a known-bad version that your check fails",
> **without saying "how to obtain it"**
> ⇒ the executor **modified a production file in place** to manufacture the bad version, the
> command timed out and was moved to the background ⇒ **the restore step never ran**
> ⇒ the working tree was left **in the broken state** with no indication.

---

## Install (**executable, not just documentation**)

This repository ships an installer that puts the 12 engineering guidelines into your agent's
configuration, **idempotently and with exact uninstall**.

```bash
sh    install/install.sh    install --agent claude            # dry-run first; see what it would change
sh    install/install.sh    install --agent claude --apply    # actually write
powershell -File install/install.ps1 status                   # Windows
install\install.cmd status                                     # cmd.exe
```
`--agent` accepts `claude` / `codex` / `cursor` / `generic` (the last one just needs a directory).

**⇒ After installing, run `install/core.py selfcheck` first** — the installer **must be verified
too**; it will tell you which layers did or did not get installed.
`install/core.py report` generates a diagnostic bundle that is **structure-only and
content-free**, for pasting into an issue.

### Three decisions to make from the start

| Decision | How to make it |
|---|---|
| **agent teams policy** | `--teams=always` (spawn subagents/teammates yourself when needed) / **`ask` (the default: ask you first, every time)** / `never` (do not spawn). **If omitted, your previous choice is kept** — upgrading will not reset your setting. |
| **Which layers to install** | The installer **probes** how far up your host is supported (see `docs/03`), **installs only what it can, and faithfully reports which layer did not get installed**. |
| **Commit hook** | Installed by default (it only writes into `.git/hooks/`, local and reversible). It is **the only layer that does not depend on the host and can genuinely say "no"**. |

## Prerequisites and **what it does not depend on**

**There is only one prerequisite: `git`** (used for the L2 commit hook). Python 3.8+ is needed
only by the installer, and **nothing here goes online**.

**Explicitly not depended on** (this column matters more than the one above):

- ⛔ **Not dependent on any particular vendor or model** — these observations come from
  long-term collaboration, and **they still apply if you change model or change agent**;
- ⛔ **No API key, no paid service, no network access**;
- ⛔ **Not dependent on skill packages such as superpowers** — the mechanisms here are **plain
  text plus a git hook**, usable by any agent that can read a file at the project root (plain
  API calls have a corresponding layer too — see the capability matrix in `docs/03`);
- ⛔ **You are not required to hand your workflow over to it** — uninstalling is one command,
  and the original text is restored exactly (`selfcheck` includes idempotence and restore
  cases).

## Feedback

**Problems, counterexamples, and "this criterion of yours does not hold in my setting"** are all
welcome:

- **Bug / cannot install**: use [a new issue](../../issues/new?template=bug_report.yml),
  **and please paste the output of `install/core.py report`** (it contains only structure and
  hashes: version, OS, which layers are installed, the target's path and whether it is writable,
  the block's length and hash).
  **⚠ Do not paste the contents of your configuration file** — it may contain other people's
  private content.
- **Adding or changing a guideline**: use [a guideline proposal](../../issues/new?template=guideline_proposal.yml).
  **A guideline must carry a `判据：` line** (one executable, falsifiable sentence) — a guideline
  without one is marked not-actionable by `selfcheck`.
- **Pre-publication self-check**: `python tools/leak_scan.py` — it scans the **working tree +
  the entire commit history + commit messages**, three media.
  **"The working tree is clean" ≠ "the repository is clean".**

---

## Boundaries (**discount accordingly**)

- **No control group, no fixed task set, no repeated measurement** ⇒ **no cross-model comparison
  can be made from this.**
- **Only failures are recorded; the large amount of successful collaboration from the same
  period is not** ⇒ **a deliberate selection bias.**
- **A single user's single setting**; generality is unverified.
- **Some failures are strongly tied to the agent framework** (context compaction, subagent
  collaboration) and are not purely model behavior.

### ⚠️ What to know before using it (**disclaimer**)

- **The installer will change your agent configuration files** (`~/.claude/CLAUDE.md`,
  `AGENTS.md` and the like). It **defaults to dry-run** (nothing is written without `--apply`),
  it is **idempotent**, and it is **exactly uninstallable** (`selfcheck` includes restore cases),
  **but it does change your files** — **review the diff first, back up yourself, and use at your
  own risk** (the `AS IS` clause of `LICENSE` applies).
- **This repository is one user's personal record of observations. It is not official material
  from any vendor, and it does not represent any vendor's position.**
- **The commit hook will block commits** (that is its design purpose). It has two escape
  hatches: `--no-verify` and `AGENT_LESSONS_STRICT=0`.

---

## License

See [`LICENSE`](LICENSE).
