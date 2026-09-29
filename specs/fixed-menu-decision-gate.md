# Spec: Fixed-Menu Decision Gate for AI Trading Bots

Source: "I Gave 3 AI Trading Bots $1,000 (Jev)" — Creator Magic, 18 min, published 25 Sep 2026.
https://youtu.be/8ijN8LGljKg

Timestamps ([m:ss]) refer to moments in the video. Where a fact is not from the video it is marked *(inference)*.

---

## 1. Candidates

1. **Fixed-menu decision + risk layer** — the model returns one choice from a fixed menu with probabilities; a separate risk layer turns it into market orders. [6:50]
2. **Trade-only, IP-bound, sub-account API keys** — a practice: isolate each bot's funds, forbid withdrawals at the key, bind keys to the server IP. [2:40]
3. **One-click paper-trading deploy** — open-source Node/TypeScript service, Docker Compose, Hostinger VPS, paper trading by default. [15:40]
4. **Read-only live dashboard** — React page streaming decisions, orders, P/L, fees and AI cost per bot. [13:00]
5. **AI cost accounting next to P/L** — track the decision engine's spend as a first-class number beside profit and fees. [1:00], [13:00]

## 2. Choose

| Candidate | Value | Effort (5 = least) | Video support | Novelty | Total |
|---|---|---|---|---|---|
| 1. Fixed-menu decision + risk layer | 5 | 4 | 4 | 4 | **17** |
| 2. Trade-only, IP-bound sub-account keys | 4 | 5 | 5 | 2 | 16 |
| 3. One-click paper-trading deploy | 3 | 2 | 5 | 2 | 12 |
| 4. Read-only live dashboard | 3 | 3 | 4 | 2 | 12 |
| 5. AI cost accounting beside P/L | 3 | 4 | 3 | 3 | 13 |

**Winner: the fixed-menu decision + risk layer.** It is the one piece of the video that makes a language model safe to put in a loop with real money: the model never emits a free-form order, only a pick from a menu the operator wrote, and a deterministic layer decides whether and how that pick becomes a trade. Candidate 2 is nearly as strong and cheaper, but it is already standard exchange hygiene; the gate is the part most builders skip and most need.

## 3. Spec

### Title
**Fixed-Menu Decision Gate** — a constrained-action layer between an AI decision engine and an exchange.

### Pitch
The model chooses from a fixed menu with probabilities, and a deterministic risk layer decides what, if anything, hits the exchange. [6:50]

### Problem
- **Who:** builders wiring a language model to an exchange account, as the video does for Bizzy, Breezy and Boozy. [0:00]
- **What it costs today:** a free-form model output can produce malformed, oversized or unintended orders. The video names the worst case as someone using the key to "make really bad trading decisions on my behalf". [2:40] Withdrawal-free keys limit theft but not bad trades. *(inference)* Without a gate, every prompt injection or model mistake is a live order.

### Outcome
Once shipped:
- Every order placed traces back to exactly one menu choice, one probability vector and one risk-layer verdict.
- No order can reach the exchange that the risk layer did not approve.
- The service runs in paper-trading mode by default, so the gate can be observed for free before any real funds are used. [15:40]

### Users and scenarios
1. **Solo builder, paper trading.** Clones the open-source repo, runs it in dry-run mode, and watches the dashboard show each decision and whether the gate approved it. [15:40], [13:00]
2. **Operator with three funded sub-accounts.** Each bot has its own strategy text and position; the gate applies per-bot limits so one bot's bad run cannot spend another's funds. [1:40], [6:50]
3. **Reviewer after a losing day.** Reads the decision log to see which menu choices the model made, with what probabilities, and which the risk layer rejected and why. [13:00]

### Requirements

**Must**
- M1. Every 60 seconds, pull market metrics from the exchange and build a small token snapshot. [6:50]
- M2. Send the snapshot plus the bot's strategy text and current position to the decision engine. [6:50]
- M3. The decision engine returns exactly one choice from a fixed menu, with probabilities. [6:50]
- M4. A risk layer sits between the returned choice and any market order. [6:50]
- M5. Orders are market orders. [6:50]
- M6. Paper trading (dry run) is the default mode; live trading requires an explicit switch. [15:40]
- M7. The risk layer rejects any response that is not a valid menu item. *(inference)* The menu is only a constraint if off-menu answers are dropped.
- M8. Every decision, risk verdict and order is logged and available to a read-only dashboard, alongside P/L, fees and decision-engine cost. [13:00]

**Should**
- S1. Per-bot isolation: one sub-account, one API key, one strategy per bot. [1:40], [6:50]
- S2. API keys are trade-only, with withdrawals disabled, and bound to the server IP. [2:40]
- S3. Record decision-engine cost per bot so it appears next to P/L. [13:00]
- S4. Risk-layer rules are configuration, not prompt text, so a prompt injection cannot loosen them. *(inference)*

**Could**
- C1. Use the returned probabilities as a confidence threshold: below a configurable floor, the gate treats the choice as "hold". *(inference)* The video says probabilities are returned but not how they are used.
- C2. Support the exchange's full 537 tradable assets in the menu or snapshot. [7:00]
- C3. One-click Docker Compose deploy to a VPS. [15:40]

### Acceptance criteria
- **Given** a valid snapshot, **when** the decision engine returns a choice on the menu, **then** the risk layer either emits one market order or a logged rejection with a reason, and never more than one order per cycle.
- **Given** a decision-engine response that is not on the menu, **when** the risk layer receives it, **then** no order is placed and the rejection is logged.
- **Given** the service is started with no explicit live flag, **when** a choice is approved, **then** the order is recorded as a paper trade and no exchange order endpoint is called.
- **Given** a bot's API key, **when** any withdrawal call is attempted with it, **then** the exchange refuses it. [2:40]
- **Given** the dashboard is open, **when** a cycle completes, **then** the decision, probabilities, risk verdict, order and cost appear without a page reload. [13:00]
- **Given** 100 demo-mode calls, **when** they run end to end, **then** all 100 return successfully with the latency the video reports as low. [15:40]

### Non-goals
- Choosing or tuning a trading strategy. The strategy text is an input.
- Predicting whether the bots profit. The video promises results in 30 days and reports none yet. [0:00]
- Withdrawals, transfers between sub-accounts, or any funds movement.
- Limit orders or order types beyond market orders. [6:50]
- Replacing the exchange's own risk controls.

### Design notes
**Approach implied by the video.** A Node/TypeScript service, built with Claude Code, loops every 60 seconds: exchange metrics → small token snapshot → decision engine with strategy text and position → one menu choice with probabilities → risk layer → market order. [5:00], [6:50] Dockerized and deployed to a Hostinger KVM2 VPS running 24/7. [15:40] A React dashboard reads the same event stream. [13:00]

**Alternative: let the model emit structured orders directly, validated by a schema.** Cheaper to build and more expressive, since the model can set size and asset freely. Trade-off: the surface area for a bad or injected output grows with expressiveness, and every new field is a new thing the validator must bound. *(inference)* The fixed menu keeps the action space enumerable and auditable, at the cost of flexibility.

### Risks and unknowns
- **Risk layer is unspecified.** The video says a risk layer exists but not what it checks. [6:50] Position limits, cooldowns and drawdown stops are all inference.
- **Decision rate is asserted, not shown.** "300 trading decisions in one single minute" [0:40] sits beside a 60-second snapshot cycle [6:50]. The summary does not reconcile them.
- **Cost figures are estimates.** $5/day at [0:40], $3/day and $150 total at ~[7:00]. None are measured over the 30-day run.
- **Funding figures conflict.** $1,000 per bot in the intro [0:00] versus 333 USDC transferred to each sub-account [1:40].
- **Security claim is scoped.** Trade-only keys stop withdrawals but not losses from bad trades, which the speaker acknowledges. [2:40]
- **"Jev" is ambiguous** in the source material: it is used for both the decision engine and the narrator.
- **No profitability evidence.** The experiment had just started at publication.

### Metrics
| Metric | Target |
|---|---|
| Orders placed without a matching approved decision record | 0 |
| Off-menu responses that reach the exchange | 0 |
| Cycles completing end to end in demo mode | 100 of 100 [15:40] |
| Decision-engine cost per bot per day | ≤ $3, as the video estimates [7:00] |
| Uptime of the loop on the VPS over 30 days | ≥ 99% *(inference)* |

### First milestone
One day of work:
1. A loop that builds a snapshot from a mocked exchange feed every 60 seconds.
2. A decision-engine call that returns one of a hardcoded menu (for example: buy, sell, hold) with probabilities.
3. A risk layer with two rules: reject off-menu answers, and reject any order above a fixed size.
4. Paper-trading mode only, writing every decision and verdict to a JSON log.
5. Run 100 demo cycles and confirm every one logged and none produced a live order.

### Open questions
- What exactly is on the fixed menu? Buy/sell/hold, sized options, per-asset choices?
- What checks does the risk layer perform, and what are its limits?
- How are the returned probabilities used, if at all?
- How do 300 decisions per minute relate to the 60-second snapshot cycle?
- Which exchange is used? The video says only that it is compliant and supports sub-accounts and an API. [1:40]
- How is "position" represented in the prompt, and does it include open P/L?
- What happens on decision-engine timeout or error within a cycle?
- Is the risk layer part of the open-source code, and how is it configured?
- Was the per-bot amount $1,000 or 333 USDC?
