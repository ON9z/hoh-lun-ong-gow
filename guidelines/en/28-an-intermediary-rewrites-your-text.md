# An intermediary **rewrites your text** — if the string you must write contains a character **that means something to that intermediary**, ⛔ do not route it through that intermediary

判据：**Before I write a piece of text into a file 【through some intermediary】 — did I ask "**which characters does this intermediary give meaning to**"?**
⭐ Shape of the criterion: **"Does the text I am about to write contain a character that 【the intermediary itself interprets】?"**
⚠ Yes ⇒ **change the route**: use a write entry that **does not go through the intermediary** (an editor / the file API directly).

**⇒ Why**: **an intermediary is not transparent**. It has its own grammar, and **your text is merely its input**.
⇒ ⚠ **Whenever your text contains one of its metacharacters, it 【interprets】 it for you** —
⚠ and **the result looks almost identical to what you meant to write** ⇒ **you receive no error at all**,
⭐ until **downstream** (a compiler / parser / reader) breaks on a byte you never saw —
⚠ **and by then it is already on disk**.

⚠ **⚠ The worst tier is 【silent character loss】**: the interpretation is not "one extra character", it is **one character gone**
⇒ ⛔ **you cannot even see what changed** ⇒ **the two files look identical**.

**实例 (two forms, one family; ⚠ different intermediaries, same shape)**:

① **A backslash eaten by an escape processor** (recorded earlier): inside a **string literal**, writing `backslash + digit/letter`
   ⇒ ⭐ it is an **octal/escape sequence** ⇒ what really lands is **a different byte**
   (`backslash+4` → `0x04`; `backslash+b` → `0x08`) ⇒ ⚠ **a single NUL byte** is enough to make a text-search tool
   **treat the whole file as binary** ⇒ ⭐ **its behaviour was silently changed** (and the command reported no error).

② **A backslash folded by a shell heredoc** (new form, measured 2026-09-29):
   I wanted to append **source code containing backslash escapes** to a `.py` file, via
   `… <<'EOF'  <some Python>  EOF`. ⚠ **The `backslash backslash n` I wrote landed as 【a real newline】**
   ⇒ ⭐ **a syntax error**. ⚠ And **I repaired it twice through the same intermediary, and broke it the same way both times**
   ⇒ ⭐ **only 【changing the write entry】 (no shell, an editor writing the file directly) fixed it**.

⚠⚠ **What the two share**: **I kept asking "what am I writing", ⛔ never "what will it become"**.
⭐ And **the most expensive property of this family**: **on the second repair I used the same broken route**
⇒ ⚠ **retrying a broken write on the same intermediary yields another broken write.**

**⇒ 做法**:

① **When writing files**: if the content contains `backslash` · `$` · a backtick · `%` · `!` · quotes · control characters
   ⇒ ⭐ **use a write entry that 【does not pass through a shell】** (an editor / the file API directly).
② **When an intermediary is unavoidable**: ⭐ **use a form that 【does not interpret】** (quoted heredoc / a literal string),
   ⚠ and **read it back immediately**: measure **bytes and lines, ⛔ not "exit code 0"**.
   ⚠ **An exit code of 0 tells you nothing** — only that the intermediary itself did not complain.
③ **⚠ When repairing, change the route first**: **a second attempt on the same route is either the same bug or a variant of it.**
   ⭐ Criterion = **"is this write entry the same one I just failed with?"**
   ⚠ Yes ⇒ **change the route before discussing the fix**.

**⚠️ Boundaries with rules 7 / 22 / 25**:
- **7** (a negative conclusion must be re-checked through another channel) is about "**re-checking a 【denial】 already made**" — ⚠ that is the **conclusion side**;
- **22** (a delimiter in the content re-partitions the row) is about "**what the consumer of this line splits on**" —
  ⚠ that is the **read/split side**: **the row becomes more columns, and it still looks normal**;
- **25** (a truncated view) is about "**what I read was a slice**" — ⚠ that is the **read side**;
- **THIS rule** is about "**what I wrote got rewritten**" — ⚠ that is the **write side**,
  ⚠ and **it is harder to notice than 22 / 25**: **in 22 / 25 the thing is still there, I just did not see all of it;
  here the thing 【is no longer what you wrote】 — and 【the file looks right】.**

⚠ **Common thread**: they all treat "**the representation I hold is not my meaning**",
⚠ and **this one's criterion is the cheapest**: **one question — "does this intermediary use this character itself?"**
