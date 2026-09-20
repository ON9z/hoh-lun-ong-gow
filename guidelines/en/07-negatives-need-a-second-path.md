# A negative conclusion needs a second path (pipelines package the incomplete as complete)

判据：For any "zero hits / does not exist / no callers", have I **re-verified through a path that does not contain `head`**?

**Instance**: viewing output with `| head -10`, **the result was exactly 10 lines** ⇒ reading "truncated" as "no more" ⇒ reporting "zero callers". **The real call site was on line 11.**

**⇒ More generally**: **any pipeline can package an incomplete result as a complete one**:
- `| head -N` truncation;
- `| grep -c X` will also count `foo.X.py`;
- `cmd | tail -6; echo rc=$?` captures **`tail`'s exit code** (misreporting rc=2 as rc=0).

**⇒ Practice**: negative conclusion + a second path + state "which two paths you used".
**"I cannot see it" ≠ "it does not exist".**
