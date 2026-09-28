# Seeing a slice is not seeing the whole — no **truncated view** can support a claim that "it is X" or "there is no X"

判据：**Before I write "this code is / is not X" or "there is no X here" — did I read the WHOLE object, or a WINDOW of it?**
**A window** = `head` · `tail` · `grep -A/-B/-C` · `sed -n 'a,bp'` · paginated reads (`offset`/`limit`) · anything that shows "only the first N lines".
**If you cannot say "I read all of it" ⇒ your claim rests on the part you did not see** — ⚠ and **that part may contain exactly the thing you are looking for**.

**⇒ Why**: **A window exists to save time, ⛔ not to stand for the whole.**
It necessarily drops things at its boundary — ⚠ and **the dropped stretch may be precisely what you are after right now**:
a fix, an existing rule, a check that already solved the problem.
⚠ And **"not in the window" and "not in the object" look identical on screen** ⇒
⇒ so **one truncated read becomes a conclusion about the whole**.

⚠ **The more expensive form**: **you then go and change something that was never broken** —
⚠ because "I did not see that fix" reads as "that fix is not there",
⇒ and **acting on it damages what was right, with no signal telling you it was right**.

**实例 (same night, twice; ⚠ and I had written a rule about the FIRST one an hour earlier)**:

① **A guard I judged "did not fire"**: to verify a new check I ran
   `… 2>&1 | grep -E "…|FAIL|…" | head -14` ⇒ ⚠ **my FAIL was not among those 14 lines** ⇒
   I wrote down "**the guard did not fire**" and went reading source to find out why.
   ⭐ The truth: **it fired** — calling its decision function directly showed the `FAIL`
   sitting at **line 81 of the full output**, long since cut off by `head -14`.

② **A piece of code I judged "broken"**: to read one function's implementation I ran
   `grep -n "def <name>" -A 30` ⇒ ⚠ **`-A 30` cut off at line 230** ⇒
   I wrote down "**this function's boundary rule is broken (a real defect)**" and drafted a whole fix.
   ⭐ The truth: **that code was correct, and had been fixed long before** — the fix sat at
   **lines 231–251**, i.e. inside the 21 lines I never read. ⚠ The comment on that fix was **one I had written myself, earlier**.
   ⇒ ⭐ **I nearly changed something that was already right.**

⚠ **What the two share**: **the mechanism changed its skin** (`| head` → `grep -A 30`),
⚠ **and I did not recognize it** — ⭐ because I had recorded the first one as the **concrete** fact
   "`head` eats lines", ⛔ rather than as the **category** "any read that gives me only a slice cannot support a claim about the whole".
⇒ ⭐ **Write the criterion as a CATEGORY: ⛔ not "be careful with tool Y", but "this CLASS of action cannot support that CLASS of conclusion".**

**⇒ 做法**:

① **To claim a shape ⇒ read all of it**: the whole function / the whole file / the whole output.
   ⚠ When you must read in segments, **measure the total first** (`wc -l`, `grep -c`), then check
   **"the number of lines I read == the range I declared"** (reading `218–260` should yield 43 lines).
② **To decide whether a check fired ⇒ look at ITS OWN return value, or the FULL output**:
   redirect the output **to a file and read that**, or call its decision function directly.
   ⛔ `grep … | head` both drops matches **and** returns the exit code of the pipe's last stage ⇒ untrustworthy in both directions.
③ **⚠ "Take a quick `head` to look for leads" is allowed** — ⭐ what breaks is **not the reading, it is the CLAIM**.
   ✅ "I took a quick look" is fine; ⛔ "I looked, so I know" is not.

**⚠️ Boundaries with rules 7 / 19 / 24**:
- **7** is "**a negative conclusion must be re-checked through another channel**" — ⚠ that re-checks a denial already made;
- **19** is "**read the object's own declared rules**" — ⚠ it treats "**you read, but read the wrong object**";
- **24** is "**list the domain's names before judging**" — ⚠ that is the **input side** (where to search);
- **THIS rule** is "**I did read — ⛔ but I read a slice**" — ⚠ that is the **read side**,
  ⚠ and **it comes after 7 and 19**: only once you have read does re-checking or citing make sense.

**⚠️ Relation to rule 16**: **16** says "**a proxy used as an anchor errs in both directions**" —
⚠ "a window" is exactly **a proxy for the whole, and it lies both ways**:
❌ nothing in the window ⇒ you say "it does not exist"; ❌ something in the window ⇒ you say "it is like this" (while further along it may not be).

⚠ **Common thread**: they all treat "**my judgement rests on a surface I do not fully hold**",
⚠ and **this one is the cheapest and the easiest to commit**: the cost is usually one `wc -l`, or **deleting that `head`**.
