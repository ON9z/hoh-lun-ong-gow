# Wired up ≠ in effect: measure "did it actually appear in the output?"

判据：Am I measuring "**it ran**", or "**it actually appeared in the output that is consumed**"?

**⇒ The four gates**: between "built" and "takes effect" stand — **① it is called ② it finishes within budget ③ it actually appears in the output that is consumed ④ someone will read it.**
**If any gate is not passed, the mechanism does not exist — and it still gives people the illusion that they "already have it".**

**Instances**:
- after a **rule document** was built, a repository-wide `grep` for references returned **0** ⇒ the next session **simply does not know it exists**;
- a **check** was wired into a startup hook, but the hook has a **20-second timeout**, and one query inside that check takes **19.5 seconds** ⇒ **the whole block of checks after it was never executed**, and the hook's exit code was 0 ⇒ **nobody knew**.

**⇒ Acceptance criterion**: **for every mechanism ask "if it dies / it doesn't run / it gets cut off, who knows?" If you cannot answer, gates three and four are not passed.**
**⇒ Practice**: hook into an **existing channel that is certain to run** (session start / pre-commit hook / scheduled task); **do not build a new entry point** — a newly built entry point is itself a gate-four risk.

**⇒ Two kindred failure shapes (same family: mistaking "the object exists" for "the event happens")**

**① A lazily-printed string is not a liveness probe.**
A log string **existing in the code** does not mean it **will appear** -- if it sits inside a
**lazy initialiser** (the print comes after `if self._started: return`), it is printed only
**the first time the thing is actually used**.
⇒ Using "is this line in the log?" to decide "did the new code run?" **necessarily returns 0 hits
before first use** -- and 0 hits gets read as "**the new code never executed**".
⇒ Criterion: before adopting a string as a liveness probe, **read the condition under which it is printed**.

**② A label is not behaviour.**
`Enabled=True`, a task name like `*_0800_restart`, a status column that says "running" --
**these are labels**. A label answers "how is this thing configured"; it does **not** answer
"**will it actually move**".
⇒ Instance: a scheduled task with `Enabled=True` whose name promises "restart daily at 08:00",
but with a **one-shot trigger that has already expired** (`Next` empty, `StartBoundary` a fixed
moment in the past) ⇒ **it will never run again**. The thing its name promised has never happened once.
⇒ Criterion: to decide "will it move", read **what the scheduler itself says**
(next fire time / last result code / trigger type) -- **not the label**.
⚠ Especially `Enabled`: between "enabled" and "will run" sits **an entire trigger**.
