# A mechanism must prove itself: feed it a known-bad sample and show that it really goes red

判据：Have I fed this check **a sample known to fail**? Did it really go red? **Paste the output of that run.**

**⇒ Why**: a check that has **never gone red** is indistinguishable from no check at all — and it is worse, because it **buys up attention**.

**Instance**: a guard's assertion "all classified items must be hit by the scanner", where **its list was measured from the scanner's current output** ⇒ the test **necessarily passes**, and when the scanner misses one item tomorrow the test goes red, and a human will go and edit that number, **instead of looking at why the criterion degraded**.
**⇒ Fitting the test to the code is the opposite of "proving itself".**

**⇒ Practice**:
① the "bad version" used as the known-bad input **must be obtained from a historical version into a temporary path** (see guideline 03), and **files must not be modified in place**;
② make the list come from an **independent basis**, and make the assertion **closed** (hits ∪ known exceptions == the full set), so that all three of "criterion degraded / strengthened / permanently empty" go red;
③ the guard's **output must be reconciled against an authoritative source**.
