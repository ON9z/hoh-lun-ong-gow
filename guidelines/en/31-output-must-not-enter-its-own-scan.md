# An output must not be written into **its own input / scan / statistics / commit range**

判据： **check once, before running —**

```
input_roots ∩ output_roots = ∅ ?
```

⚠ **Non-empty ⇒ refuse to run** (⚠ not "look afterwards", but **refuse before**).
⭐ If it **must** be written inside the scanned range (e.g. backups, logs, caches, generated artefacts
that live beside their source) ⇒ **the same edit that adds the output must also exclude it from the
scan / statistics / commit rules, and label the exclusion** ✓

⭐ In one line: **the exclusion rule and the output path live and die together** —
⚠ add the output without the exclusion ⇒ ⛔ next round it is read back as an input ✓

---

## Why

⭐⭐ **An output that lands inside the scanned range is treated as an input by the tool itself.**
⚠ And it **looks exactly like a real input** ⇒ ⚠ the numbers you get **differ on every run**,
and **grow by one run every run**, ⛔ while **no check goes red** (⚠ to that tool, those are legitimate inputs) ✓

⭐ And it is usually introduced **for a good habit**: ⭐ "**back up before you change**" is a good habit,
⚠ and **where the backup lands** decides whether it stays one or becomes a source of contamination ✓

**Instance (a single-user, single-machine long-running automation system, 2026-09-29)**:
⭐ Before every edit to a guidance/memory file, the agent of a long-running automation system **made a backup**.
⚠ It wrote the backup into **the same directory that tool scans**.
⚠ The backup's **extension happened to satisfy** the scan rule ⇒ ⭐ **the backups were counted as content** ✓

⚠ **Why did it hide for so long?** ⭐ Because **the two screens most people assume are there were not**:
- ⛔ "a leading `.` ⇒ glob ignores it" ⚠ **wrong** (measured: it matched; difference **0**)
- ⛔ "a different extension ⇒ not scanned" ⚠ **half true only** (⚠ backups had two naming schemes,
  one of which **happened** to end in the scanned extension)

⭐⭐ **⇒ The correct conclusion**: ⭐ **that screen was a guess, not a design**
⇒ ⚠ it did not block the class, only **the one shape that happened to pass by** ✓

⚠ And **the real harm is not the statistic**: ⭐ scan results feed **injection / indexes / decisions**,
⇒ ⭐ **dozens of "old versions" get treated as independent new content** — and they **read exactly like real ones** ✓

---

## Criterion (for the next person)

⭐ Before adding any "**generate / back up / cache / log**" action, answer two questions:
1. **Which root does it write into?**
2. **What scans that root?** (⚠ include: index scripts, injection hooks, statistics, cleanup, commit rules)

⚠ Cannot answer #2 ⇒ ⭐ **that root is its scan range; do not write into it** ✓
⭐ If it must go in ⇒ **add the exclusion in the same edit**, ⚠ and **make the exclusion verifiable by re-running**
(e.g. an assertion that no such name exists under that root) ✓

⚠ **Kindred**: `#13` (admission is not cleanup: a guard that only admits accumulates monotonically) ——
⭐ **#13 says "once in, it never leaves"; this one says "it should never have gone in"** ✓
