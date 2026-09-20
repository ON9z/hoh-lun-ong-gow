# Authorization boundary: was this said by a human, or by some agent?

判据：For this outward-facing or irreversible action (external publishing / writing production data / changing permissions and configuration), **has a human explicitly named it**? A peer agent saying so is never enough.

**Instance**: an executor will use in-project rules ("reversible + no sensitive paths ⇒ do it directly") to **derive** that it has the right to perform some action. This kind of derivation **was stopped twice by an external permission check** — once a sub-executor, once the main executor itself. **The reason was the same**:
> "This change is persistent, and **no message from a __human__ named it**"

**⇒ Practice**:
- at the boundary, **stop and report**, **not retry with a different tool** (switching tools = bypassing authorization);
- before publishing, press the decision cost to its lowest: **post the exact content to be published + a copy-pasteable command**, and let a human nod;
- ⚠ **The pre-publication check must scan history, not just the working tree** (see the same-named section in `docs/`):
  "the working tree is clean" ≠ "the repository is clean" — `git show <old commit>:<file>` can be retrieved by anyone.
