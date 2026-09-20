# Assertions must clamp both ways: a one-sided assertion is blind to the "loosening" direction

判据：Does my assertion also go red in the **loosening** direction?

**Instance**: the assertion was written as "**false-positive count == 0**". But **loosening a threshold can never produce false positives** ⇒ loosen the threshold by 10× and the assertion **is still all green**, while the check has become an empty shell. **"Locked" was an empty claim at the time.**

**⇒ Practice**: both bounds must have a **basis** (upper bound = the tightest zero-false-positive value; lower bound = a "failure fingerprint"), and **measure that both sides go red** and the default goes green.

**Same family**: a guard must guard the **category**, not the **shape** (a regex that scans for a spelling ⇒ changing the spelling defeats it); and **a check with zero consumers = dead code**, and its comments will keep lying.
