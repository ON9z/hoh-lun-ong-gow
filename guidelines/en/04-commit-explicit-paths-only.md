# Commit explicit paths only: a bare commit after `add` sweeps up other people's staged files

判据：Before committing, have I verified **the staging area's file names and count**?

**Instance**: **4 times** in one day — A ran `git add` on its own files and then committed **without paths**, sweeping up B's files that were **staged but not yet committed**. Content is not lost, but **attribution is wrong** (the commit message does not describe the files swept in), and it disrupts concurrent collaborators' state.

**⇒ Practice**: use the "commit only specified paths" form; or print the staging area listing before committing and **count it**.
**⇒ Additional requirement in a concurrent setting**: set an **explicit commit identity** for each subagent — otherwise afterwards **attribution cannot be determined from author information**, and the main agent's "no-defect confirmation" is invalidated by this.

**⚠️ A *different* shape that this guideline does NOT catch (different mechanism — **do not merge the counts**)**

I staged **explicitly named paths**, and believed I was fully compliant with this guideline.
**But `git add <path>` takes the whole file, not "my hunks".**
Another executor was editing **the same file** at that moment => **its change went into my commit,
and my commit message said nothing about it.**

> **=> Path-level granularity != hunk-level granularity.** This guideline addresses "sweeping up other *paths*";
> it does **not** address "someone else's hunks inside the same file" -- and the two share a **symptom**
> (the commit message does not describe what was swept in), so self-checking only
> "did I name the path?" **can never surface the latter**.

**=> Practice (run these three before committing)**:
1. `git status --porcelain` -- who is writing **right now** (not several minutes ago)
2. `git diff --stat <the paths I named>` -- are those changes **mine**
3. A shared hot file with a concurrent writer => **stage by hunk**, or **wait for them to land**

⚠ **One more, related**: `git status` can also read a **stale** state.
I acted on a reading that said "the teammate's fix is not yet committed" -- it **had been committed**
(inside **my** commit). **=> Bind a reading to its timestamp; re-read before acting.**
