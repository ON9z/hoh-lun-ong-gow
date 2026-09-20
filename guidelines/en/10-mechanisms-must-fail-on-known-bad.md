# A mechanism must prove itself: feed it a known-bad sample and show that it really goes red

判据：Have I fed this check **a sample known to fail**? Did it really go red? **Paste the output of that run.** And: **does it also go red when its entry condition does not hold? — "did not run" is not "passed".**

**⇒ Why**: a check that has **never gone red** is indistinguishable from no check at all — and it is worse, because it **buys up attention**.

**Instance**: a guard's assertion "all classified items must be hit by the scanner", where **its list was measured from the scanner's current output** ⇒ the test **necessarily passes**, and when the scanner misses one item tomorrow the test goes red, and a human will go and edit that number, **instead of looking at why the criterion degraded**.
**⇒ Fitting the test to the code is the opposite of "proving itself".**

**⇒ Practice**:
① the "bad version" used as the known-bad input **must be obtained from a historical version into a temporary path** (see guideline 03), and **files must not be modified in place**;
② make the list come from an **independent basis**, and make the assertion **closed** (hits ∪ known exceptions == the full set), so that all three of "criterion degraded / strengthened / permanently empty" go red;
③ the guard's **output must be reconciled against an authoritative source**.

**⚠️ One more (an even more upstream form of this guideline): if the verifier itself crashes, that is "unverified" -- NOT "passed".**

**Measured**: I wrote a script to check a count claim. The script **never ran at all** because of a syntax error, so it produced **no output** -- and I **did not notice the output was missing**, and committed the claim anyway. **=> The claim shipped in a public artifact, never once checked.**

**=> Criterion**: **for any "claim + verifier" pair, a verifier that produced nothing == the claim is unverified.**
**Missing output, an error, a non-zero exit -- all three must stop the claim**, not let the process continue.
**⚠ The most dangerous case is "no output"** -- it looks like "it ran fine".

**=> Self-check**: after running a verifier, ask
**"Where is its output? Is what I am looking at written by it, or what I assumed it would write?"**

**⚠ One step earlier: when a guard's precondition fails inside an `if`, there is not even "no output".**

**Measured (the third instance of one shape)**:
```python
if tool.exists() and anchors_present:      # <- no else
    try:   ...run the check...
    except Exception as e: print("[!!] could not run"); bad += 1
```
**=> Tool deleted or renamed => the whole `if` body is skipped => nothing printed, counted as 0 =>
the caller reports "everything passed".**
And **the comment above it said** "tool missing/broken => report it, **do not silently treat it as
passing**" -- **the comment described a behaviour the code did not have.**

**=> Criterion**: **a guard whose entry condition does not hold is in the same state as a guard that
failed -- both must go red.**
```python
if not precondition:  report_red(); bad += 1
else:                 try: … except: report_red(); bad += 1
```

**⚠ Same family (all measured)**:
- a health check wrapped in `if X is not None:` => **when the guarded object does not exist the
  check never engages, i.e. zero self-healing**;
- the previous guard's `if not path.exists(): return {}` => **when the file is absent it silently
  returns "no problem"**;
- this one.

**=> What they share**: **writing "did not check" as "check passed"** -- and the two produce
**identical output**.
