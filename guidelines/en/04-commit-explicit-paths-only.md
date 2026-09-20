# Commit explicit paths only: a bare commit after `add` sweeps up other people's staged files

判据：Before committing, have I verified **the staging area's file names and count**?

**Instance**: **4 times** in one day — A ran `git add` on its own files and then committed **without paths**, sweeping up B's files that were **staged but not yet committed**. Content is not lost, but **attribution is wrong** (the commit message does not describe the files swept in), and it disrupts concurrent collaborators' state.

**⇒ Practice**: use the "commit only specified paths" form; or print the staging area listing before committing and **count it**.
**⇒ Additional requirement in a concurrent setting**: set an **explicit commit identity** for each executor — otherwise afterwards **attribution cannot be determined from author information**, and the main executor's "no-defect confirmation" is invalidated by this.
