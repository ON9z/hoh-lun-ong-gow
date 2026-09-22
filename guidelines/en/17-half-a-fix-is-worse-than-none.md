# Half a fix is worse than no fix

判据：Before changing a criterion or adding a filter, ask
"**how many places does this logic act in? How many did I change?**"
Changing only one ⇒ you have very likely traded **visible noise** for **invisible contamination**.

**⇒ Why**: A criterion usually has **more than one layer of action**:
"**what counts as a hit**" is one layer; "**what it is matched against / how it propagates**" is another.
Fix only the first, and the noise **does not disappear** -- it **changes form**. And the new form
usually **looks more like a conclusion**, because it has already been through one filter.

⇒ The genuinely dangerous part: **you are trading "I removed thousands of false positives" for
"I can no longer see at a glance that it is wrong".**

**Instance**: A static census tool decides "does this function body make a network call?" **by name**,
and suppresses false positives from builtin method names with **one exclusion set**. The first version
applied that exclusion set only at the "**hit**" layer, and **not** at the "**propagation**" layer of
the same logic ("who calls a function that makes network calls") -- so the `get` of a dict lookup
**propagated** false positives to **every function that ever called `.get()`**:

| | Hits | How it reads |
|---|---|---|
| Before the partial fix | 2776 | overwhelmingly dict lookups ⇒ **obviously noise at a glance**; nobody would trust it |
| After changing only one layer | 152 "high-specificity candidates" | **most of them still false** ⇒ and **a short list is exactly the one a human reads line by line** |

⇒ **It is now more dangerous than before the fix** -- because it is now **a trusted list**.

**⇒ How to act**:

① Before touching it, **enumerate the layers this criterion acts in** (common ones:
   **hit** / **propagate** / **dedupe** / **sort** / **truncate** -- each is a layer).
   Ask of each layer: "**should the exclusion apply here too?**"
② **An exclusion must be printed** (the excluded **names** and the **count**) --
   otherwise "improving precision" degrades into "**silently seeing less**".
   A silent allow-list means you do not know what you are not looking at.
③ Immediately **re-run the same input afterwards**: how much did the count drop? And
   **did those drop out because they were excluded, or because they were hidden?**

**⚠️ Boundary with Guideline 13**: 13 is "a guard that only admits, never cleans up ⇒ objects
**accumulate**". This one is "**a criterion has several layers of action and you changed one**" --
the former piles up; the latter **swaps the list you intend to read for a more trustworthy-looking one**.

**⚠️ Boundary with Guideline 05**: 05 is "assertions must be two-sided". This one is "**a fix must
cover every layer it acts on**" -- you can verify every assertion in both directions and **still
add the filter at only one layer**.
