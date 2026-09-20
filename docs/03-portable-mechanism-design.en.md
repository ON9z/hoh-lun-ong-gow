# Making mechanisms work across agents: layering and capability detection

> **Problem**: a mechanism depends on **the host's capabilities**. And agent capabilities differ
> enormously between vendors — some support session-level hooks, some only read one file at the
> project root, and **a plain API call has no hooks at all**.
> **⇒ Making a mechanism into a single shape necessarily makes it take effect for only one class
> of host.**
>
> **This document gives a layered design: split the mechanism into 5 layers, install as many
> layers as the host's capabilities permit, and make every layer independently verifiable.**
>
> ⚠ Following this repository's stance: **there is no control group; this is an engineering
> practice, not a benchmark conclusion.**

---

## 1. First, see the differences clearly: the host capability matrix

| Host form | Does it read a file at the project root? | Supports session hooks? | Supports commit hooks? | Can be scheduled externally? |
|---|---|---|---|---|
| CLI agent with hooks | ✅ (something like `AGENTS.md` / `CLAUDE.md`) | ✅ | ✅ | ✅ |
| CLI agent without hooks | ✅ | ❌ | ✅ | ✅ |
| IDE-embedded agent | partial | ❌ | ✅ | partial |
| **Plain API call** (you write the loop yourself) | ❌ (nobody reads it on its behalf) | ❌ | ✅ | ✅ |
| Manual operation (yourself) | — | — | ✅ | ✅ |

**⇒ This table is the source of the entire problem.** Any mechanism "hooked onto a hook" has
**zero coverage of "plain API calls" and "CLI agents without hooks"** — and those two classes are
the majority of actual users.

---

## 2. The solution: five layers, progressing by capability

| Layer | Depends on | Covers whom | Strength | When it fails |
|---|---|---|---|---|
| **L0 text layer** | nothing | **everyone** (including plain API and manual) | **weakest** (relies on the model's or the human's conscientiousness) | silent |
| **L1 project-file layer** | the host reads a file at the project root | most CLI agents | medium | silent |
| **L2 commit-hook layer** | the project uses git | **nearly all** (see §3) | **strong (machine-enforced)** | **blocks the commit** |
| **L3 session-hook layer** | the host supports session-level hooks | a minority of CLI agents | strong | injects a reminder |
| **L4 external-scheduling layer** | there is a scheduled task / CI | **everyone** | strong (but **lagging**) | alerts |

**Core principle:**
> **Do not ask "which form is best"; ask "how far up does this host support", and then install
> the highest layer it can reach.**
> **Every layer must be able to take effect independently** — a missing layer is not the same as
> having no effect.

---

## 3. ⭐ Why **L2 (the commit hook) is the broadest common ground across agents**

- **Code written by any agent has to be committed eventually.** The session hook and the project
  file only *advise*; **the commit hook says *no***.
- **It does not depend on the host**: it depends only on "this project is a git repository".
- **It works for "plain API calls" too** — because whoever finally commits the code is also a
  human or a script, going through the same path.
- **The cost**: it is **after the fact** (it runs at the moment of committing); it cannot prevent
  the mistake from happening, only prevent the mistake from **landing in the repository**.
  **⇒ But for "irreversible contamination", after-the-fact blocking is already a decisive layer.**

**⇒ Conclusion: put the hardest checks in L2. L0/L1/L3 are responsible for "making fewer
mistakes"; L2 is responsible for "not letting them land in the repository".**

**⚠️ One boundary that must be admitted**: **L2 can only govern "actions that go through git".**
Writing to a production database, making an outbound request, changing configuration — **these
do not go through git** ⇒ **L2 cannot reach them** ⇒
**this class of "outward-facing / irreversible" action can only rely on L0/L1 rules plus human
authorization** (see guideline 11).

---

## 4. Capability detection: how the installer chooses layers

The installer **does not assume** host capabilities; it **probes** them, then **installs only
what it can**, and reports the result faithfully.

```
Probe order (every step may fail; on failure, degrade — never exit with an error):
  ① Host identity         infer the vendor from environment variables / known config directories
  ② L1's target file      what is the project-level / user-level config file path for this host,
                          and does it exist
  ③ L3's hook capability  does this host have a hook config that can be written to; **do not
                          guess — look it up in the known list**
  ④ L2's availability     is the current directory (or the given directory) a git repository
  ⑤ L4's availability     is there a scheduled task that can be registered (this layer is
                          **not installed by default**, only suggested)
```

**⇒ The output must be a table of "what was installed / what was not / why"**, not a vague
"installation succeeded".

> **The criterion: "If it dies / it doesn't run / it gets cut off, who knows?"**
> The installer **must answer this question itself** — `status` must be able to say **whether
> each layer is currently alive or dead**.

---

## 5. How each layer "proves itself" (**the four gates made concrete**)

Following the four gates from `02-mechanisms-for-ai-assisted-engineering.md` §0 — **① it is
called ② it finishes within budget ③ it actually appears in the output that is consumed
④ someone will read it** — here is an executable verification method, layer by layer:

| Layer | How to verify "it really took effect" (not "it was installed") |
|---|---|
| **L0** | **Cannot be machine-verified** ⇒ **must be labelled as-is**: this layer relies on conscientiousness; a tool cannot guarantee it for you. ⚠ Do not pretend it works. |
| **L1** | Trigger it once on the host's **real read path** and confirm it can be read (for example, open a new session and see whether it mentions that file). |
| **L2** | **Deliberately make one violating commit** and confirm it is **really blocked**. ⚠ **Not blocked = this layer does not exist**. |
| **L3** | Trigger one real event and **`grep` for that injection in the output** — ⚠ a real counterexample was measured in this project: it was wired into the hook, but **the hook's timeout cut the whole block off** ⇒ it never executed. |
| **L4** | Check **whether it really ran last time** (read its output, not the scheduler's "completed" marker). |

**⇒ One general criterion**: **for each layer ask "what evidence says it is in effect right
now?" — if you cannot answer, label it "unverified", not "installed".**

### 5.1 ⚠️ A measured case: **"the whole hook silently vanished" is harder to notice than "a section was truncated"**

The table above is about a layer not taking effect. **Here is a sharper piece of evidence**
(taken from the host's own execution metadata):

```
Per-run records of one session-level check (20 s timeout):
  09-19T05:19   durationMs= 7 516   stdout=4579 bytes   all content present ✅
  09-19T14:18   durationMs=17 637   stdout=4678 bytes   all content present ✅
  09-20T06:23   durationMs=20 146   exitCode=None  **stdout=0 bytes**   **nothing appeared at all** ❌
```

**⇒ It was not "the second half got cut off" — the entire hook was killed by its timeout and
produced no output at all.**
**⇒ Everything it was supposed to inject** (the pending-items block, three meta-critiques, two
sentinels) **never reached the context — not one character.**
**⇒ And `stdout=0` looks exactly like "nothing to report" inside the session.**

**This is the strongest illustration of the criterion in §5**:
> **"It died / it did not run / it got cut — who would know?" — in that moment, the answer was
> that nobody would.**

**⇒ Which yields a portable design rule** (this repository now follows it):

> **An injection-type mechanism must emit one line even when it has nothing to report —
> "check ran, no anomalies."**
> **"Empty output" has to be distinguishable** — otherwise it simultaneously means
> "everything is fine" and "I never ran", and those two require **opposite** responses.

**⚠ One more number, and it is the one that matters**: that hook's **timeout is 20 000 ms** --
**it exceeded its own timeout by 146 milliseconds.** This is not "the budget was set too tight,
so it fails now and then". It was **hugging the line**: 7 516 -> 17 637 -> a thin crossing,
**and after that it was never seen again.**
**⇒ The criterion: if a mechanism's runtime distribution sits close to its own budget, it is not
"occasionally failing" -- it is already on the way to failing.** And when it fails, the output
(empty) **looks exactly like everything being fine.**

**⚠ Alongside it**: this layer **must be able to report when it last succeeded**.
Reporting only "no anomalies right now" is not enough — that is indistinguishable from
"the last success was three days ago".

---

## 6. Privacy: the diagnostic bundle carries structure, not content

When a user reports a problem, the easiest thing to do is "paste your config file here".
**That is wrong** — **that file may contain other people's private content** (prompts, internal
paths, project information).

**⇒ Design rules for the diagnostic bundle:**
```
✅ May include: version number / OS and Python version / **which layers are installed** /
          the target's **path** and **whether it is writable**
          / whether the block exists / the block's **length and hash** (for judging "whether it
          matches the released version")
          / **self-check results** per layer (pass/fail)
⛔ Never include: **any content** of the file / the **values** of environment variables /
          username / hostname / the project's file list
```
**⇒ The criterion**: **if a field would let a third party infer "who this person is / what
project they are working on", it should not go into the diagnostic bundle.**

---

## 7. The boundaries of this layered design (**stated as-is**)

- **L0 is fundamentally unguaranteeable** — it relies on the model's or the human's
  conscientiousness. **Any claim that "with L0 installed you are safe" is false.**
- **L2 can only govern git** — writing to a database, making requests, changing configuration:
  **actions that do not go through git are out of its reach**.
- **L3's coverage is inherently narrow** — hosts that support session hooks are a minority,
  **and the hook semantics are not standardized across vendors**.
- **Capability detection will expire** — hosts' hook capabilities **change**. ⇒ The detection
  checklist must be **configurable**, and `status` must faithfully report "which version of the
  checklist I detected against".
- **No control group** — the layering here is a **design**, not a "measured to be more
  effective" conclusion.

---

## 8. In one sentence

> **The portability of a mechanism does not come from "a stronger mechanism"; it comes from
> "layering by host capability, and faithfully reporting which layer did not get installed".**
>
> **And the layer that most deserves to be made hard is the commit hook — because it is the only
> layer that is "independent of the host and can genuinely say no".**
