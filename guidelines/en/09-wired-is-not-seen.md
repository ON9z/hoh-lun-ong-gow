# Wired up ≠ in effect: measure "did it actually appear in the output?"

判据：Am I measuring "**it ran**", or "**it actually appeared in the output that is consumed**"?

**⇒ The four gates**: between "built" and "takes effect" stand — **① it is called ② it finishes within budget ③ it actually appears in the output that is consumed ④ someone will read it.**
**If any gate is not passed, the mechanism does not exist — and it still gives people the illusion that they "already have it".**

**Instances**:
- after a **rule document** was built, a repository-wide `grep` for references returned **0** ⇒ the next session **simply does not know it exists**;
- a **check** was wired into a startup hook, but the hook has a **20-second timeout**, and one query inside that check takes **19.5 seconds** ⇒ **the whole block of checks after it was never executed**, and the hook's exit code was 0 ⇒ **nobody knew**.

**⇒ Acceptance criterion**: **for every mechanism ask "if it dies / it doesn't run / it gets cut off, who knows?" If you cannot answer, gates three and four are not passed.**
**⇒ Practice**: hook into an **existing channel that is certain to run** (session start / pre-commit hook / scheduled task); **do not build a new entry point** — a newly built entry point is itself a gate-four risk.
