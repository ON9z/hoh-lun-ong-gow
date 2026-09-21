# Editing a file is not the same as changing behaviour: **the running copy may still be the old one**

判据：Before you say "I changed it, it is fixed" -- **the thing that is currently running, which copy of the content is it using?** Did you **restart it**, or did you **assume it hot-reloads**? And -- did you check that **from the running process itself**, or **from the filesystem** (mtime, `git diff`)?

**⇒ Why**: "editing the file" is **an action I took**; "behaviour changed" is **a property of the system**.
Between them sits **a load moment**, and that moment **is not inside my field of view**.
For long-running processes, cached configuration, and **scripts being interpreted line by line as they
execute**, the former **does not imply** the latter.

**⇒ And "it did not take effect" usually looks like "silent, no output" -- identical to "the event
never happened".** ⇒ Until you have independent evidence, **both readings are still on the table**.

**Instance**:

- I added "capture an on-the-spot snapshot before acting on a failure" to a **supervisor script**,
  looked at the file's mtime, and considered it done.
- **41 seconds earlier**, that script **had already been started** -- and it reads its own file
  in segments, **by byte offset**.
- Later that day a failure really did occur: **no snapshot was left behind**.
- My reading at the time was: "**no snapshot ⇒ no failure happened tonight**". **Wrong** -- the log
  plainly recorded that it had.
  ⇒ The real conclusion was "**the running copy is still the old content**".
- ⇒ Only after I **restarted** it and confirmed the new load moment did that new logic actually take effect.

**⇒ Practice**:

① After editing **any file a long-running process uses** (a script / a config / **an imported module**),
   you must answer two questions explicitly: **does it need a restart? did you restart it?**
   If you cannot answer, the job is not finished.
② **Verify from the running side** that it has the new content: a version string / a load timestamp /
   **one observable new behaviour**. **Do not verify from the filesystem** -- a file's mtime
   **proves nothing** about what any process has read.
③ ⚠ "**I see no output**" has two readings: "the event did not happen" and "it happened, but I did not
   record it". ⇒ **First go look for independent evidence that it happened** (logs, the other side's
   records, side effects), and only then pick one. **Do not default to the reading that comforts you.**
④ This is guideline "edited = fixed" along the **time** axis; along the **space** axis the same shape
   is guideline 09 (wired ≠ appears in the consumed output). Both demand: **take your evidence from the
   consuming end, not from the end where you did the work.**
