# Write unverified as unverified: "cannot determine" must not be written as a conclusion

判据：Is this sentence **measured**, **restated**, or **inferred**? Have I labelled which? And: **what did I check this number (or claim) against?**

**Instance**: facing a question that static reading of the code cannot settle, the easiest failure is — **cannot determine ⇒ so give a conclusion that sounds certain**. **The strength of the wording must equal the strength of the evidence.**

**⇒ Practice**: **declare the ceiling up front** (far more useful than a guessed answer):
> "If the trace was not persisted to disk, I will say plainly that **it takes one real run to settle**, rather than give you a guessed answer."

**⚠️ A companion finding**: an observation field that is **not persisted** = the question **is undecidable at the static level** ⇒ say that sentence first, then give candidates.

**Same family**: when reporting "N times / every X minutes / all / widespread", **where do those numbers come from**? Derived by multiplication ⇒ forbidden; a single measurement ⇒ needs multiple samples; sample < 10% of the whole ⇒ you may only say "the N I have measured".

**⚠️ The more useful half: an exit gate lowers the error rate better than making the criterion more accurate.**

**Measured (2026-09-21, after both sides had the gate installed)**: the number of broken criteria in one
day **did not fall** (a regex missing `re.M`, a backslash in an f-string, a `grep` whose wording did not
match the source, a criterion carried across domains... a dozen-plus across two parties).
**But the false signals that actually got reported fell sharply** — because **the gate at the exit**
changed from "**measure a number, report it**" to "**get a second method to agree before saying anything**".

**=> Criterion**:
> **"What did I check this number against?" — if you cannot answer, it does not count.**
> (The same ruler as "if you cannot say *when* it should come to mind, it is not a behavioural rule" --
> it measures two different things.)

**⚠️ Why this matters**: **making a criterion more accurate is a capability problem — slow and
unreliable. Adding a gate at the exit is a process problem: install it and it works immediately,
and it does not require the criteria to improve first.**
**=> Do not wait for the criteria to get better; install the gate.**
