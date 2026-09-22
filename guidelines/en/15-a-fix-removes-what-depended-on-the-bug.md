# Fixing a fault removes a hidden path that **depended on that fault**

判据：Before fixing a long-standing fault, ask "**is anything depending on this fault?**"
If you cannot answer, then fixing it will **quietly dismantle a path you assumed did not exist but
that was in fact doing work** -- and **nothing will warn you**, because the path you dismantled
**was never written down**.

**⇒ Why**: A fault that keeps happening **grows its own ecosystem**.
Other mechanisms **adapt to it, route around it, or ride on top of it** -- and those adaptations
are **in no design document**. They are the product of "this is how we have always done it".
**⇒ When the fault disappears, the adaptations disappear with it, and nobody knew they existed.**

**Instance**: A long-running service occasionally hangs. An external keeper checks **every 60
seconds** and kills-and-restarts it when it hangs. On the surface: one fault plus one safety net.

The truth: **"restart" had been doing duty as the deployment mechanism for something entirely
unrelated**. Code changes were never deployed deliberately, because **a hang would force a restart
a few times a day anyway**, and the changes went live as a side effect.
Measured: 28 days, **at least one restart every single day, never a zero day**.

**⇒ Then someone fixes the hang at the root.** The hang stops, so the restarts stop --
**and the path "changes go live via a restart" stops with them.**
The consequence is not "changes go live a bit later". It is "**changes silently never go live**",
while every dashboard stays green, because **no dashboard was measuring this**.

**⇒ How to act**:

① **Before the fix, measure the fault's frequency**, and ask **who consumes that frequency**.
   "Checks every 60 seconds" is the design; "**actually fires 1-5 times a day**" is the fact --
   the fact is the half that was being depended on.
② **After the fix, watch the old consumer.** It shows up as "**something stopped happening**".
   This class of regression has **no error, no log line, no metric** -- it can only be found by
   **knowing in advance what to look for**.
③ The hidden path usually looks like "**something that necessarily happens every so often**".
   ⇒ **Go and count that "necessarily".** If something in a healthy system fires on a guaranteed
   cadence, assume **someone depends on it** first, and make them disprove it.

**⚠️ Boundary with Guideline 13**: 13 is "a guard that only admits, never cleans up ⇒ objects
**accumulate**". This one is "**the thing you fixed had dependents** ⇒ a path is **severed**".
Both look like "changed one place, something else broke" -- but one accumulates, the other
**quietly stops happening**.
