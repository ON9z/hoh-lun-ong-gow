# Measure before changing: before acting, measure "which segment / which variable" is the main cause

判据：Before I change anything, have I measured **which segment** is the main cause? Or did I measure only the total?

**Instance**: a 24.8-second pipeline timed out. I concluded "the slow one is check A" and prepared to change A. Measuring item by item revealed that A takes only 3.3 seconds and B takes 19.7 seconds. **Acting on the wrong attribution to "reorder" would fix the wrong place** (put the slow one first, and the fast one is then the one that gets truncated).

**Same family**: extrapolating a long task from a small sample's rate (18s/unit at the start ⇒ reported as 30 hours; measured 23.2s/unit ⇒ 39 hours).
**A short sample is not a random sample** — the ordering makes the items that run first systematically different in time cost.

**⇒ Practice**: when reporting an estimate, state what sample it was computed on; after ≥10% has run, recompute with the composite rate, and if the difference is >20%, revise upward and persist it to disk.
