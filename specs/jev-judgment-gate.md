# Spec: Jev Judgment Gate for Claude Code

Source: "7 Jev Repos That 10x Claude Code (Free)" — AI Edge, 16 min, published 25 Sep 2026.
https://youtu.be/q35Yy_JY5Bw

**Citation note.** The source summary contains no timestamps, so citations below point to the summary section they come from (for example [Topic 2], [Takeaway 5]) rather than [m:ss]. Nothing here is attributed to a moment the source does not give. Items marked *(inference)* are mine, not the video's.

---

## 1. Candidates

1. **Jev MCP judgment gate** — a tool Claude calls for fast verify / screen / decide calls that return a confidence score, so cheap judgments happen before expensive inference. [Topic 2], [Actionable 3]
2. **Split-model practice** — Jev for probabilistic, binary-outcome decisions; Claude for planning and strategic thinking. [Takeaway 4], [What to avoid]
3. **Computer Use fast-click** — Aaron's tool that clicks in 0.3 s instead of 5 s by reducing the need for screenshots. [Topic 2]
4. **Shapeshift** — real-time UI generation from text input. [Topic 2]
5. **Jev Voice Browser** — voice-controlled browsing with real-time response ("Go to wikipedia.com. Bang."). [Topic 2]

Also mentioned but not scored: an Ad Blocker the summary itself calls less practical, and JevMeter, a "BS" score over live data. [Topic 2], [Resources]

## 2. Choose

| Candidate | Value | Effort (5 = least) | Video support | Novelty | Total |
|---|---|---|---|---|---|
| 1. Jev MCP judgment gate | 5 | 4 | 4 | 3 | **16** |
| 2. Split-model practice | 3 | 5 | 5 | 2 | 15 |
| 3. Computer Use fast-click | 3 | 3 | 4 | 3 | 13 |
| 4. Shapeshift UI generation | 3 | 3 | 4 | 3 | 13 |
| 5. Jev Voice Browser | 2 | 3 | 4 | 3 | 12 |

**Winner: the Jev MCP judgment gate.** It is the concrete form of the video's core principle, since adopting "Jev decides, Claude thinks" changes nothing measurable until a tool routes the cheap decisions somewhere. The split-model practice scores close but its value only lands through the gate, so the two are folded together here.

## 3. Spec

### Title
**Jev Judgment Gate** — an MCP tool that lets Claude Code delegate verify / screen / decide calls to Jev and get back a choice with a confidence score.

### Pitch
Claude keeps the planning; Jev takes the split-second yes/no calls at a fraction of the latency and cost. [Takeaway 4], [Takeaway 5]

### Problem
- **Who:** developers and founders running high-volume, repetitive judgments inside Claude Code or Codex workflows, such as screening candidates or verifying pricing structures. [Takeaway 5]
- **What it costs today:** each judgment is a full LLM inference. The video puts Opus 5.5 at 5.2 s per command against Jev's 0.13 s, and Jev at 155 times cheaper per decision. [Takeaway 1], [Takeaway 5]
- *(inference)* At thousands of items, latency and spend dominate the task, and the LLM's reasoning is wasted on questions with a binary answer.

### Outcome
Once shipped:
- Claude Code can call a `judge`-style tool that returns one choice from a small set plus a confidence score, in well under a second per call. [Topic 2], [Takeaway 1]
- Simple verify / screen / decide tasks no longer consume Claude inference. [Actionable 3]
- Every gate decision is logged with its confidence, so the operator can audit what was screened out before it reached Claude. *(inference)*

### Users and scenarios
1. **Founder screening candidates.** Feeds a batch of applications through the gate with a rule set; Jev returns pass/fail with confidence, and only the passes go to Claude for a written assessment. [Takeaway 5]
2. **Developer verifying pricing structures.** Asks Claude to check a pricing page; Claude calls the gate to verify each claim quickly, then reasons only over the flagged ones. [Takeaway 5], [Actionable 3]
3. **Automation builder.** Uses the gate inside a workflow where each step is a probabilistic decision with predefined rules, as the video shows for a trading bot. [Takeaway 2]

### Requirements

**Must**
- M1. Expose Jev to Claude as an MCP tool for judgment calls: verify, screen, decide. [Topic 2], [Actionable 3]
- M2. Each call returns a choice and a confidence score. [TL;DR], [Topic 2]
- M3. Calls target probabilistic, binary-outcome tasks; the tool is not used for planning or inference. [Takeaway 4], [What to avoid]
- M4. Installable into an existing Claude Code or Codex setup via the provided prompt. [Actionable 1], [TL;DR]
- M5. Per-call latency and cost are recorded so the speed and cost claims can be checked locally. *(inference)*

**Should**
- S1. A confidence threshold below which the gate returns "uncertain" and Claude handles the item itself. *(inference)* The video reports confidence scores but does not say how they are used.
- S2. Batch mode: many items, one rule set, one call per item, results streamed back. *(inference)* Needed for the screening scenario to save real time.
- S3. Ship with example rule sets for the three demoed uses: screening, verifying claims, workflow decisions. [Takeaway 5], [Takeaway 2]

**Could**
- C1. Route gate results into the Computer Use or Voice Browser tools for fast follow-up actions. [Topic 2]
- C2. A JevMeter-style "BS" score as one preset judgment type. [Resources]

### Acceptance criteria
- **Given** Claude Code with the gate installed, **when** Claude calls it with an item and a rule set, **then** it receives exactly one choice from the allowed set and a confidence score in [0, 1].
- **Given** 100 items in a batch, **when** the gate processes them, **then** median per-item latency is under 1 s and each result is logged with confidence and cost. [Takeaway 1] sets the 0.13 s claim; the 1 s bound is *(inference)* to leave margin.
- **Given** a result below the confidence threshold, **when** it is returned, **then** it is marked uncertain and Claude, not Jev, produces the final answer. *(inference)*
- **Given** a request that asks for a plan or multi-step reasoning, **when** it is sent to the gate, **then** the gate refuses it and tells Claude to handle it directly. [What to avoid]
- **Given** the install prompt, **when** a user runs it in a fresh Claude Code setup, **then** the tool appears in Claude's tool list without manual config edits. [Actionable 1]

### Non-goals
- Replacing Claude or Codex for reasoning, planning or writing. [Takeaway 4]
- Open-ended generation of any kind. [What to avoid]
- The other repos in the video (Shapeshift, Voice Browser, Computer Use, Ad Blocker). They are separate deliverables.
- Validating Jev's model quality. This spec measures speed and cost; accuracy is an open question below.

### Design notes
**Approach implied by the video.** Jev sits beside Claude as an MCP server. Claude decides when a sub-task is a judgment call and hands it over; Jev returns a choice with probabilities; Claude carries on with the strategic work. Content can be screened or verified before it enters the LLM at all. [Topic 2], [Actionable 3], [Takeaway 4]

**Alternative: prompt-level routing without a tool.** Ask Claude to answer yes/no questions in a terse mode and skip the second model. Trade-off: no new dependency and no install step, but every judgment still pays full Claude latency and price, which is exactly the cost the video is trying to remove. *(inference)*

### Risks and unknowns
- **Speed and cost figures are not reconciled.** The TL;DR says 40–200x faster and 119–155x cheaper; the takeaways say 14–40x faster and 155x cheaper; the one concrete pair (0.13 s vs 5.2 s) is 40x. None are shown as a controlled benchmark.
- **"$0.042 vs $5.25 per token"** is stated as per-token pricing. *(inference)* Those magnitudes look like per-million-token figures; the unit needs confirming.
- **Accuracy is never measured.** The video shows speed, not how often Jev's judgments are right. A fast wrong screen is worse than a slow right one.
- **"MCP" is expanded as "Model Checkpoint"** in the summary. In common usage MCP means Model Context Protocol. Which one the video means affects how the tool is installed.
- **Install path is a community prompt**, not a documented package. What the prompt does to a user's setup is unknown.
- **Jev's provenance** (who builds it, how it is hosted, what data it sees) is not covered.
- **Summary verdict is "Maybe"** and it flags that some tools are impractical. The source is not strongly confident in its own material.

### Metrics
| Metric | Target |
|---|---|
| Median gate latency per call | < 1 s; video claims 0.13 s [Takeaway 1] |
| Cost per gate decision vs the same call to Opus | ≥ 100x cheaper; video claims 155x [Takeaway 5] |
| Share of screening items that never reach Claude | ≥ 50% on the candidate-screening scenario *(inference)* |
| Agreement between gate verdict and a Claude verdict on a held-out sample | ≥ 95% *(inference)*; needed before trusting the gate |
| Install success from the prompt on a fresh setup | 10 of 10 attempts *(inference)* |

### First milestone
One day of work:
1. Install the Jev MCP tool into one Claude Code setup using the provided prompt. [Actionable 1]
2. Write one rule set for a single judgment: "does this text make a pricing claim, yes or no". [Takeaway 5]
3. Run 100 items through the gate and 100 through Opus 5.5 directly; log latency, cost and answer for each.
4. Report the measured speed and cost ratios against the video's 40x and 155x claims, and the agreement rate between the two.
5. Decide go / no-go on S1 and S2 from those numbers.

### Open questions
- What input does the Jev MCP tool accept, and what does a response look like beyond "choice plus confidence"?
- Is MCP here Model Context Protocol or something the video calls Model Checkpoint?
- How accurate is Jev on the demoed tasks, and against what baseline?
- What are the actual pricing units behind "$0.042 vs $5.25"?
- What does the community install prompt change in a Claude Code or Codex setup?
- Who operates Jev, where does it run, and what happens to submitted content?
- How are the "predefined rules" for a decision expressed?
- Does Jev return a probability over all options or only a confidence for the chosen one?
- Where do the seven repos live, and under what licenses?
