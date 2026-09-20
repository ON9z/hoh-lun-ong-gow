# Revert to a historical version; never edit a tracked file in place

判据：**If this command were interrupted at an arbitrary point, would the state left behind be the original state?** If not ⇒ the design is not finished.

**Instance (the most expensive one)**: to prove that "the newly added check fails on bad input", the subagent **edited a tracked production file in place**, and restored it at the tail of the command. **The command timed out and was moved to the background ⇒ the restore step never ran** ⇒ the working tree was left **in the broken state**, with no indication whatsoever. **It was found only at the next routine check.**

**⇒ Practice (in priority order)**:
① **make the change not happen at all** — fetch a historical version to a temporary path (`git show <rev>:<path> > /tmp/x`) and load from the temporary path;
② `finally` / `trap`;
③ ⛔ **do not flatten critical cleanup across the tail of a long command** (a timeout or backgrounding will swallow the tail).
