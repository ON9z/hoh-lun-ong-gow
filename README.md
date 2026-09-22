**language/语言：** [English](#english) · [简体中文](#zh-cn) · [繁體中文](#zh-tw)

---

<a id="english"></a>
# Failure modes and mechanism-building in agent collaboration


**In plain terms**: if you let an AI work for a long time -- not one question and one answer, but
dozens or hundreds of turns, where it edits files, runs commands and leaves side effects behind --
you will hit problems that **simply do not show up in single-turn evaluation**:

- it says "I verified it", **but never actually ran anything**;
- it adds a check, and that check **can never fail**;
- it thinks it is done, **having changed half of it**;
- three things all show green, and that green **proves something about a different file**.

**This repository is a record of those problems, plus a set of practices we worked out in response.**

**Three things it can do for you:**

| What you want | What to use |
|---|---|
| **Recognise** these failures | `docs/01`: failure modes classified by capability dimension; each has symptom / minimal reproduction / mitigation |
| **Prevent** them | `docs/02` + `install/`: 18 guidelines plus an installer that can be installed and removed cleanly, putting them where the AI **reads them every session** |
| **Make them surface** | `docs/03` + `hooks/`: a commit hook / sentinels / a leak scan, so that "did not do it" and "did it wrong" both become visible |

**When this is useful**: you are building an agent, or you have worked with an AI over a long horizon
and hit "it said it was done, and the result was wrong".
**When it is not**: you only ask an AI one or two questions; or what you want is a **model benchmark
comparison** (there is none here -- see "Boundaries" below).

**No specific project, business, data or identity information appears in this repository** -- every
example has been abstracted.

---

## Contents

| File | Contents |
|---|---|
| [`docs/01-failure-modes-in-long-horizon-collaboration.en.md`](docs/01-failure-modes-in-long-horizon-collaboration.en.md) | **Failure modes classified by capability dimension**: instruction following / long-context retrieval / tool use / code generation and self-modification / reasoning / factuality and metacognition / multi-step and agentic collaboration. Each entry has: symptom · minimal reproduction · mitigation · suggestion for model developers |
| [`docs/02-mechanisms-for-ai-assisted-engineering.en.md`](docs/02-mechanisms-for-ai-assisted-engineering.en.md) | **A set of practices for turning "criticism and lessons" into mechanisms**: the four-gates criterion / automatic guideline injection / a dictionary of error types / a checklist-reconciliation hook / a dispatch template / **criteria and counterexamples for using subagents and teams** / prediction expiry / authorization boundaries / a single source of truth / mechanism self-proof |
| [`docs/03-portable-mechanism-design.en.md`](docs/03-portable-mechanism-design.en.md) | **Making mechanisms work across agents**: the host capability matrix / **the five-layer design L0–L4** / why the **commit hook** is the broadest common ground across agents / capability probing / per-layer self-proof / privacy (the diagnostic bundle carries structure, not content) |
| [`CHANGELOG.md`](CHANGELOG.md) | **What changed, version by version** — each entry states the failure mode in its own words, the measurement behind it, and how it was verified. Current: `v1.1.0`. |

---

## Why it is worth reading (if you are building agents or doing long-term AI collaboration)

Common evaluations cut tasks into **single-turn, stateless questions with a unique correct
answer**. The real properties of long-term collaboration are different:

| Dimension | Common evaluation | Long-horizon engineering collaboration |
|---|---|---|
| Turns | 1 | hundreds–thousands, **context gets compacted** |
| State | none | **present** (files, databases, uncommitted artifacts, background processes) |
| Correctness | a single point | **process correctness** ("was done" ≠ "was done right") |
| Feedback | immediate | **delayed and partial** |
| Tools | none / few | **many, and with side effects** |

**⇒ Most of the failures recorded here are invisible in single-turn evaluation — some would even
be scored as "correct".**

---

## Three things you can take away immediately

**1. The four gates** (from two real counterexamples in one measurement)
> **Between "built" and "takes effect" stand four gates: ① it is called ② it finishes within
> budget ③ it actually appears in the output that is consumed ④ someone will read it.**
> **If any gate is not passed, the mechanism does not exist — and it still gives people the
> illusion that they "already have it".**
>
> **Acceptance criterion: "If it dies / it doesn't run / it gets cut off, who knows?" If you
> cannot answer, gates three and four are not passed.**

**2. Push verification from the first level to the second**
> Not "I did it", but "**it actually took effect, it was seen, and it also holds in the opposite
> direction**".
> Measured: **7 checks that "a criterion can be vacuously satisfied"** were found in a single day
> (unit mismatch / insufficient coverage / finite resampling returning 0 / resolution
> insufficient to reach the threshold / allowlist shape / a terminal-state marker hung on a
> periodic task / paging without completeness verification).
> **The criterion: "Under what input would this criterion be false?" — if you cannot answer
> that, it may be always true.**

**3. When you require an action, you must also give the "permitted way to implement it"**
> A task brief said only "you must verify with a known-bad version that your check fails",
> **without saying "how to obtain it"**
> ⇒ the executor **modified a production file in place** to manufacture the bad version, the
> command timed out and was moved to the background ⇒ **the restore step never ran**
> ⇒ the working tree was left **in the broken state** with no indication.

---

## Install (**executable, not just documentation**)

This repository ships an installer that puts the 12 engineering guidelines into your agent's
configuration, **idempotently and with exact uninstall**.

```bash
sh    install/install.sh    install --agent claude            # dry-run first; see what it would change
sh    install/install.sh    install --agent claude --apply    # actually write
powershell -File install/install.ps1 status                   # Windows
install\install.cmd status                                     # cmd.exe
```
`--agent` accepts `claude` / `codex` / `cursor` / `generic` (the last one just needs a directory).

**⇒ After installing, run `install/core.py selfcheck` first** — the installer **must be verified
too**; it will tell you which layers did or did not get installed.
`install/core.py report` generates a diagnostic bundle that is **structure-only and
content-free**, for pasting into an issue.

### Three decisions to make from the start

| Decision | How to make it |
|---|---|
| **agent teams policy** | `--teams=always` (spawn subagents/teammates yourself when needed) / **`ask` (the default: ask you first, every time)** / `never` (do not spawn). **If omitted, your previous choice is kept** — upgrading will not reset your setting. |
| **Which layers to install** | The installer **probes** how far up your host is supported (see `docs/03`), **installs only what it can, and faithfully reports which layer did not get installed**. |
| **Commit hook** | Installed by default (it only writes into `.git/hooks/`, local and reversible). It is **the only layer that does not depend on the host and can genuinely say "no"**. |

## Prerequisites and **what it does not depend on**

**There is only one prerequisite: `git`** (used for the L2 commit hook). Python 3.8+ is needed
only by the installer, and **nothing here goes online**.

**Explicitly not depended on** (this column matters more than the one above):

- ⛔ **Not dependent on any particular vendor or model** — these observations come from
  long-term collaboration, and **they still apply if you change model or change agent**;
- ⛔ **No API key, no paid service, no network access**;
- ⛔ **Not dependent on skill packages such as superpowers** — the mechanisms here are **plain
  text plus a git hook**, usable by any agent that can read a file at the project root (plain
  API calls have a corresponding layer too — see the capability matrix in `docs/03`);
- ⛔ **You are not required to hand your workflow over to it** — uninstalling is one command,
  and the original text is restored exactly (`selfcheck` includes idempotence and restore
  cases).

## Feedback

**Problems, counterexamples, and "this criterion of yours does not hold in my setting"** are all
welcome:

- **Bug / cannot install**: use [a new issue](../../issues/new?template=bug_report.yml),
  **and please paste the output of `install/core.py report`** (it contains only structure and
  hashes: version, OS, which layers are installed, the target's path and whether it is writable,
  the block's length and hash).
  **⚠ Do not paste the contents of your configuration file** — it may contain other people's
  private content.
- **Adding or changing a guideline**: use [a guideline proposal](../../issues/new?template=guideline_proposal.yml).
  **A guideline must carry a `判据：` line** (one executable, falsifiable sentence) — a guideline
  without one is marked not-actionable by `selfcheck`.
- **Pre-publication self-check**: `python tools/leak_scan.py` — it scans the **working tree +
  the entire commit history + commit messages**, three media.
  **"The working tree is clean" ≠ "the repository is clean".**

---

## Boundaries (**discount accordingly**)

- **No control group, no fixed task set, no repeated measurement** ⇒ **no cross-model comparison
  can be made from this.**
- **Only failures are recorded; the large amount of successful collaboration from the same
  period is not** ⇒ **a deliberate selection bias.**
- **A single user's single setting**; generality is unverified.
- **Some failures are strongly tied to the agent framework** (context compaction, subagent
  collaboration) and are not purely model behavior.

### ⚠️ What to know before using it (**disclaimer**)

- **The installer will change your agent configuration files** (`~/.claude/CLAUDE.md`,
  `AGENTS.md` and the like). It **defaults to dry-run** (nothing is written without `--apply`),
  it is **idempotent**, and it is **exactly uninstallable** (`selfcheck` includes restore cases),
  **but it does change your files** — **review the diff first, back up yourself, and use at your
  own risk** (the `AS IS` clause of `LICENSE` applies).
- **This repository is one user's personal record of observations. It is not official material
  from any vendor, and it does not represent any vendor's position.**
- **The commit hook will block commits** (that is its design purpose). It has two escape
  hatches: `--no-verify` and `AGENT_LESSONS_STRICT=0`.

---

## License

See [`LICENSE`](LICENSE).

---

<a id="zh-cn"></a>
# Agent 协作的失效模式与机制建设


**简单来说**：如果你让 AI 长时间干活 —— 不是一问一答，而是几十上百轮，它会改文件、跑命令、留下副作用 ——
你会碰到一些**单轮评测里根本不会出现**的毛病：

- 它说「我验证过了」，**其实没跑**；
- 它加了一个检查，而那个检查**永远不会报错**；
- 它以为改完了，**只改了一半**；
- 三样东西都显示绿灯，而那个绿**证明的是别的文件**。

**这个仓库是这些毛病的记录，以及我们试出来的一套应对办法。**

**它能帮你做的三件事：**

| 你想 | 用什么 |
|---|---|
| **认出**这些毛病 | `docs/01`：按能力维度分类的失效模式，每条含现象 / 最小复现 / 缓解 |
| **防住**它们 | `docs/02` + `install/`：18 条准则，加一个可装可卸的安装器，把准则放到 AI **每次都会读到**的地方 |
| **让它自己露出来** | `docs/03` + `hooks/`：提交钩子 / 哨兵 / 泄漏扫描，让「没做」和「做错了」都瞒不住 |

**什么时候用得上**：你在做 Agent，或者你已经和 AI 长期协作过，并且遇到过「它说『已经做完了』，结果不对」。
**什么时候用不上**：你只用 AI 问一两个问题；或者你要的是**模型跑分对比**（这里没有，见下面的「边界」）。

**仓库里不含任何具体项目、业务、数据或身份信息** —— 所有例子都抽象化过。

---

## 目录

| 文件 | 内容 |
|---|---|
| [`docs/01-failure-modes-in-long-horizon-collaboration.md`](docs/01-failure-modes-in-long-horizon-collaboration.md) | **按能力维度分类的失效模式**：指令遵循 / 长上下文检索 / 工具使用 / 代码生成与自我修改 / 推理 / 事实性与自我评估 / 多步与代理协作。每条含：现象 · 最小复现 · 缓解 · 对模型方的建议 |
| [`docs/02-mechanisms-for-ai-assisted-engineering.md`](docs/02-mechanisms-for-ai-assisted-engineering.md) | **把"批评教训"变成机制的一套做法**：四道门判据 / 准则自动注入 / 错误类型字典 / 清单对账钩子 / 派工模板 / **子 Agent 与团队的使用判据与反例** / 预测到期 / 授权边界 / 单一事实源 / 机制自证 |
| [`docs/03-portable-mechanism-design.md`](docs/03-portable-mechanism-design.md) | **让机制跨 Agent 生效**：宿主能力矩阵 / **五层设计 L0–L4** / 为什么**提交钩子**是跨 Agent 的最大公约数 / 能力探测 / 逐层自证 / 隐私（诊断包只含结构不含内容） |
| [`CHANGELOG.md`](CHANGELOG.md) | **逐版本的变更记录** —— 每条用自己的话讲清失效模式、背后的实测、以及它如何被验证。当前 `v1.1.0`。 |

---

## 为什么值得看（如果你在做 Agent 或做长期 AI 协作）

常见评测把任务切成**单轮、无状态、有唯一正确答案**的题。而长期协作的真实特点是：

| 维度 | 常见评测 | 长程工程协作 |
|---|---|---|
| 回合数 | 1 | 数百~数千，**上下文会被压缩** |
| 状态 | 无 | **有**（文件、数据库、未提交产物、后台进程） |
| 正确性 | 单点 | **过程正确性**（"做过了" ≠ "做对了"） |
| 反馈 | 立刻 | **延迟且部分** |
| 工具 | 无 / 少量 | **大量，且带副作用** |

**⇒ 本文记录的失效，绝大多数在单轮评测里看不见，甚至会被判为"正确"。**

---

## 三条可以立刻带走的

**1. 四道门**（来自一次实测的两个反例）
> **「建了」与「生效」之间隔着四道门：①被调用 ②在预算内跑完 ③真正出现在被消费的输出里 ④有人会读它。**
> **任一未过，机制等于不存在 —— 而它还会给人"已经有了"的错觉。**
>
> **验收判据：「它死了 / 它没跑 / 它被截了，谁知道？」答不出来，就是没过第三、四道门。**

**2. 把验证从第一层推到第二层**
> 不是"我做了"，而是"**它真的生效了、被看见了、且在反方向上也成立**"。
> 实测一天内发现 **7 个"判据可被空满足"**的检查（量纲不匹配 / 覆盖率不足 / 有限次重采样返回 0 /
> 分辨率不足以达到阈值 / 白名单形状 / 终态标记挂在周期任务上 / 翻页不校验完整性）。
> **判据：「这个判据在什么输入下会为假？」—— 答不出来，它可能恒真。**

**3. 要求一个动作，必须同时给出"允许的实现方式"**
> 一份任务书只写「必须拿已知坏版本验证你的检查会失败」，**没写"怎么拿"**
> ⇒ 执行方**原地修改了生产文件**制造坏版本，命令超时被移到后台 ⇒ **还原那一步没跑到**
> ⇒ 工作区留在**被改坏的状态**且无提示。

---

## 安装（**可执行，不只是文档**）

本仓库带一个安装器，把 18 条工程准则装进你的 Agent 配置，并**幂等、可精确卸载**。

```bash
sh    install/install.sh    install --agent claude            # 先 dry-run，看它要改什么
sh    install/install.sh    install --agent claude --apply    # 真的写
powershell -File install/install.ps1 status                   # Windows
install\install.cmd status                                     # cmd.exe
```
`--agent` 支持 `claude` / `codex` / `cursor` / `generic`（后者只需给一个目录）。

**⇒ 装完先跑 `install/core.py selfcheck`** —— 安装器**自己也要被验**，它会告诉你每一层装没装上。
`install/core.py report` 生成**只含结构、不含内容**的诊断包，用于贴 issue。

### 三条你一开始就要做的决定

| 决定 | 怎么定 |
|---|---|
| **agent teams 策略** | `--teams=always`（需要就自己开分身）/ **`ask`（默认：每次先问你）** / `never`（不开）。**不给则沿用上次的选择**，升级不会把你的设置重置。 |
| **装哪几层** | 安装器**探测**你的宿主支持到第几层（见 `docs/03`），**只装能装的，并如实报告哪层没装上**。 |
| **提交钩子** | 默认装（它只写进 `.git/hooks/`，本地、可逆）。它是**唯一不依赖宿主、又能真的说"不"**的一层。 |

## 前置与**不依赖**

**前置只有一条：`git`**（用于 L2 提交钩子）。Python 3.8+ 仅安装器需要，**全程不联网**。

**明确不依赖**（这一栏比上面那栏重要）：

- ⛔ **不依赖任何特定厂商或模型** —— 这些观察来自长期协作，**换模型/换 Agent 依然适用**；
- ⛔ **不需要 API key、不需要付费服务、不需要联网**；
- ⛔ **不依赖 superpowers 之类的技能包** —— 本仓库的机制是**纯文本 + git 钩子**，
  任何能读项目根文件的 Agent 都用得上（纯 API 调用也有对应层，见 `docs/03` 的能力矩阵）；
- ⛔ **不要求你把工作流交给它** —— 卸载一条命令，原文精确还原（`selfcheck` 里有幂等与还原用例）。

## 反馈

**问题、反例、以及"你这条判据在我这里不成立"**，都欢迎：

- **Bug / 装不上**：用 [新 issue](../../issues/new?template=bug_report.yml)，
  **请贴 `install/core.py report` 的输出**（它只含结构与哈希：版本、系统、装了哪层、目标的路径与是否可写、块的长度与哈希）。
  **⚠ 不要贴配置文件内容** —— 那里面可能有别人的私密内容。
- **新增/修改一条准则**：用 [准则提案](../../issues/new?template=guideline_proposal.yml)。
  **准则必须带「判据：」行**（一句可执行、可证伪的话）—— 没有判据的准则会被 `selfcheck` 标为不可执行。
- **发布前自检**：`python tools/leak_scan.py` —— 它扫**工作区 + 全历史提交 + 提交信息**，
  三类介质。**「工作区干净」≠「仓库干净」。**

---

## 边界（**请据此打折**）

- **无对照组、无固定任务集、无重复测量** ⇒ **不能据此做模型间比较。**
- **只记录失效，不记录同期大量成功的协作** ⇒ **明确的选择偏差。**
- **单一使用者的单一场景**，普适性未验证。
- **部分失效与 Agent 框架强相关**（上下文压缩、子 Agent 协作），不完全是模型行为。

### ⚠️ 使用前请知道的（**免责**）

- **安装器会改动你的 agent 配置文件**（`~/.claude/CLAUDE.md`、`AGENTS.md` 之类）。
  它**默认 dry-run**（不加 `--apply` 不写任何东西）、**幂等**、**可精确卸载**（`selfcheck` 里有还原用例），
  **但它改的是你的文件** —— **请先看 diff、自行备份、自担风险**（`LICENSE` 的 `AS IS` 条款适用）。
- **本仓库是使用者个人的观察记录，不是任何厂商的官方材料，也不代表任何厂商的立场。**
- **提交钩子会阻断提交**（这是它的设计目的）。它有 `--no-verify` 与 `AGENT_LESSONS_STRICT=0` 两个逃生口。

---

## 许可

见 [`LICENSE`](LICENSE)。

---

<a id="zh-tw"></a>
# Agent 協作的失效模式與機制建設


**簡單來說**：如果你讓 AI 長時間幹活 —— 不是一問一答，而是幾十上百輪，它會改檔案、跑指令、留下副作用 ——
你會碰到一些**單輪評測裡根本不會出現**的毛病：

- 它說「我驗證過了」，**其實沒跑**；
- 它加了一個檢查，而那個檢查**永遠不會報錯**；
- 它以為改完了，**只改了一半**；
- 三樣東西都顯示綠燈，而那個綠**證明的是別的檔案**。

**這個倉庫是這些毛病的記錄，以及我們試出來的一套應對辦法。**

**它能幫你做的三件事：**

| 你想 | 用什麼 |
|---|---|
| **認出**這些毛病 | `docs/01`：按能力維度分類的失效模式，每條含現象 / 最小重現 / 緩解 |
| **防住**它們 | `docs/02` + `install/`：14 條準則，加一個可裝可卸的安裝器，把準則放到 AI **每次都會讀到**的地方 |
| **讓它自己露出來** | `docs/03` + `hooks/`：提交鉤子 / 哨兵 / 洩漏掃描，讓「沒做」和「做錯了」都瞞不住 |

**什麼時候用得上**：你在做 Agent，或者你已經和 AI 長期協作過，並且遇到過「它說『已經做完了』，結果不對」。
**什麼時候用不上**：你只用 AI 問一兩個問題；或者你要的是**模型跑分對比**（這裡沒有，見下面的「邊界」）。

**倉庫裡不含任何具體專案、業務、資料或身分資訊** —— 所有例子都抽象化過。

---

## 目錄

| 檔案 | 內容 |
|---|---|
| [`docs/01-failure-modes-in-long-horizon-collaboration.md`](docs/01-failure-modes-in-long-horizon-collaboration.md) | **按能力維度分類的失效模式**：指令遵循 / 長上下文檢索 / 工具使用 / 程式碼生成與自我修改 / 推理 / 事實性與自我評估 / 多步與代理協作。每條含：現象 · 最小重現 · 緩解 · 對模型方的建議 |
| [`docs/02-mechanisms-for-ai-assisted-engineering.md`](docs/02-mechanisms-for-ai-assisted-engineering.md) | **把「批評教訓」變成機制的一套做法**：四道門判據 / 準則自動注入 / 錯誤類型字典 / 清單對帳鉤子 / 派工模板 / **子 Agent 與團隊的使用判據與反例** / 預測到期 / 授權邊界 / 單一事實源 / 機制自證 |
| [`docs/03-portable-mechanism-design.md`](docs/03-portable-mechanism-design.md) | **讓機制跨 Agent 生效**：宿主能力矩陣 / **五層設計 L0–L4** / 為什麼**提交鉤子**是跨 Agent 的最大公約數 / 能力偵測 / 逐層自證 / 隱私（診斷包只含結構不含內容） |
| [`CHANGELOG.md`](CHANGELOG.md) | **逐版本的變更記錄** —— 每條用自己的話講清失效模式、背後的實測、以及它如何被驗證。目前 `v1.1.0`。 |

---

## 為什麼值得看（如果你在做 Agent 或做長期 AI 協作）

常見評測把任務切成**單輪、無狀態、有唯一正確答案**的題。而長期協作的真實特點是：

| 維度 | 常見評測 | 長程工程協作 |
|---|---|---|
| 回合數 | 1 | 數百~數千，**上下文會被壓縮** |
| 狀態 | 無 | **有**（檔案、資料庫、未提交產物、背景處理程序） |
| 正確性 | 單點 | **過程正確性**（「做過了」 ≠ 「做對了」） |
| 回饋 | 立刻 | **延遲且部分** |
| 工具 | 無 / 少量 | **大量，且帶副作用** |

**⇒ 本文記錄的失效，絕大多數在單輪評測裡看不見，甚至會被判為「正確」。**

---

## 三條可以立刻帶走的

**1. 四道門**（來自一次實測的兩個反例）
> **「建了」與「生效」之間隔著四道門：①被呼叫 ②在預算內跑完 ③真正出現在被消費的輸出裡 ④有人會讀它。**
> **任一未過，機制等於不存在 —— 而它還會給人「已經有了」的錯覺。**
>
> **驗收判據：「它死了 / 它沒跑 / 它被截了，誰知道？」答不出來，就是沒過第三、四道門。**

**2. 把驗證從第一層推到第二層**
> 不是「我做了」，而是「**它真的生效了、被看見了、且在反方向上也成立**」。
> 實測一天內發現 **7 個「判據可被空滿足」**的檢查（因次不匹配 / 覆蓋率不足 / 有限次重取樣傳回 0 /
> 解析度不足以達到閾值 / 允許清單形狀 / 終態標記掛在週期任務上 / 翻頁不驗證完整性）。
> **判據：「這個判據在什麼輸入下會為假？」—— 答不出來，它可能恆真。**

**3. 要求一個動作，必須同時給出「允許的實作方式」**
> 一份任務書只寫「必須拿已知壞版本驗證你的檢查會失敗」，**沒寫「怎麼拿」**
> ⇒ 執行方**原地修改了生產檔案**製造壞版本，指令逾時被移到背景 ⇒ **還原那一步沒跑到**
> ⇒ 工作區留在**被改壞的狀態**且無提示。

---

## 安裝（**可執行，不只是文件**）

本倉庫帶一個安裝器，把 14 條工程準則裝進你的 Agent 設定，並**冪等、可精確解除安裝**。

```bash
sh    install/install.sh    install --agent claude            # 先 dry-run，看它要改什麼
sh    install/install.sh    install --agent claude --apply    # 真的寫
powershell -File install/install.ps1 status                   # Windows
install\install.cmd status                                     # cmd.exe
```
`--agent` 支援 `claude` / `codex` / `cursor` / `generic`（後者只需給一個目錄）。

**⇒ 裝完先跑 `install/core.py selfcheck`** —— 安裝器**自己也要被驗**，它會告訴你每一層裝沒裝上。
`install/core.py report` 生成**只含結構、不含內容**的診斷包，用於貼 issue。

### 三條你一開始就要做的決定

| 決定 | 怎麼定 |
|---|---|
| **agent teams 策略** | `--teams=always`（需要就自己開分身）/ **`ask`（預設：每次先問你）** / `never`（不開）。**不給則沿用上次的選擇**，升級不會把你的設定重設。 |
| **裝哪幾層** | 安裝器**偵測**你的宿主支援到第幾層（見 `docs/03`），**只裝能裝的，並如實報告哪層沒裝上**。 |
| **提交鉤子** | 預設裝（它只寫進 `.git/hooks/`，本機、可逆）。它是**唯一不依賴宿主、又能真的說「不」**的一層。 |

## 前置與**不依賴**

**前置只有一條：`git`**（用於 L2 提交鉤子）。Python 3.8+ 僅安裝器需要，**全程不連網**。

**明確不依賴**（這一欄比上面那欄重要）：

- ⛔ **不依賴任何特定廠商或模型** —— 這些觀察來自長期協作，**換模型/換 Agent 依然適用**；
- ⛔ **不需要 API key、不需要付費服務、不需要連網**；
- ⛔ **不依賴 superpowers 之類的技能套件** —— 本倉庫的機制是**純文字 + git 鉤子**，
  任何能讀專案根目錄檔案的 Agent 都用得上（純 API 呼叫也有對應層，見 `docs/03` 的能力矩陣）；
- ⛔ **不要求你把工作流程交給它** —— 解除安裝一行指令，原文精確還原（`selfcheck` 裡有冪等與還原測試案例）。

## 回饋

**問題、反例、以及「你這條判據在我這裡不成立」**，都歡迎：

- **Bug / 裝不上**：用 [新 issue](../../issues/new?template=bug_report.yml)，
  **請貼上 `install/core.py report` 的輸出**（它只含結構與雜湊：版本、系統、裝了哪層、目標的路徑與是否可寫、區塊的長度與雜湊）。
  **⚠ 不要貼設定檔內容** —— 那裡面可能有別人的私密內容。
- **新增/修改一條準則**：用 [準則提案](../../issues/new?template=guideline_proposal.yml)。
  **準則必須帶「判据：」行**（一句可執行、可證偽的話）—— 沒有判據的準則會被 `selfcheck` 標為不可執行。
- **發布前自檢**：`python tools/leak_scan.py` —— 它掃**工作區 + 全歷史提交 + 提交資訊**，
  三類介質。**「工作區乾淨」≠「倉庫乾淨」。**

---

## 邊界（**請據此打折**）

- **無對照組、無固定任務集、無重複測量** ⇒ **不能據此做模型間比較。**
- **只記錄失效，不記錄同期大量成功的協作** ⇒ **明確的選擇偏差。**
- **單一使用者的單一情境**，通用性未驗證。
- **部分失效與 Agent 框架強相關**（上下文壓縮、子 Agent 協作），不完全是模型行為。

### ⚠️ 使用前請知道的（**免責**）

- **安裝器會改動你的 agent 設定檔**（`~/.claude/CLAUDE.md`、`AGENTS.md` 之類）。
  它**預設 dry-run**（不加 `--apply` 不寫任何東西）、**冪等**、**可精確解除安裝**（`selfcheck` 裡有還原測試案例），
  **但它改的是你的檔案** —— **請先看 diff、自行備份、自負風險**（`LICENSE` 的 `AS IS` 條款適用）。
- **本倉庫是使用者個人的觀察記錄，不是任何廠商的官方材料，也不代表任何廠商的立場。**
- **提交鉤子會阻擋提交**（這是它的設計目的）。它有 `--no-verify` 與 `AGENT_LESSONS_STRICT=0` 兩個逃生出口。

---

## 授權

見 [`LICENSE`](LICENSE)。

---
