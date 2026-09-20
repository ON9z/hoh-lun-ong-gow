# A mechanism must prove itself: feed it a known-bad sample and show that it really goes red

判据：Have I fed this check **a sample known to fail**? Did it really go red? **Paste the output of that run.**

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
