# Operational Procedures Extension Guide

**Extend your fine-tuning from regulatory theory to operational practice!**

## 🎯 What This Does

The operational procedures extension allows you to generate training data from your **actual fund operations**:

- ✅ **SOPs** (Standard Operating Procedures)
- ✅ **Workflows** (Process flows)
- ✅ **Checklists** (Compliance checklists)
- ✅ **Decision Trees** (Escalation procedures)
- ✅ **Process Guides** (How-to documents)

### Why This Matters

**Regulatory training alone:**
```
User: "What are the UCITS diversification requirements?"
Model: "Article 52 states maximum 10% in single issuer..."  ✅ Knows the regulation
```

**Regulatory + Operational training:**
```
User: "How do I calculate the NAV for a UCITS fund?"
Model: "Here's the step-by-step NAV calculation procedure:
       1. Obtain closing prices from approved vendors
       2. Verify against the approved source list
       3. Calculate holdings value...
       This ensures compliance with UCITS Article 85..."  ✅ Knows HOW to do it
```

**The model becomes an operational expert, not just a regulatory encyclopedia!**

---

## 🚀 Quick Start

### Option 1: Use Extended MCP Server

```bash
# Install
cd finetuning/mcp
pip install -e .

# Configure Claude Desktop to use server_extended.py instead of server.py
# Edit claude_desktop_config.json:
{
  "mcpServers": {
    "eu-funds-finetuning": {
      "command": "python",
      "args": ["/path/to/anthropic-cookbook/finetuning/mcp/server_extended.py"]
    }
  }
}

# Restart Claude Desktop
```

### Option 2: Use Python Directly

```python
from operational_procedures import (
    OperationalProcedureParser,
    OperationalTrainingGenerator
)
import anthropic

# Parse a procedure
parser = OperationalProcedureParser()
with open('nav_calculation.txt', 'r') as f:
    content = f.read()

procedure = parser.parse_procedure(content)

# Generate training data
client = anthropic.Anthropic(api_key="your-key")
generator = OperationalTrainingGenerator(client)

examples = generator.generate_from_procedure(procedure, num_examples=30)

# Save
import json
with open('nav_training.jsonl', 'w') as f:
    for example in examples:
        f.write(json.dumps(example) + '\n')
```

---

## 📖 Using the MCP Tools

### Tool 1: Generate from Procedures

**What it does:** Converts operational procedures into training data

**Example conversation:**
```
You: I have a NAV calculation SOP at /procedures/nav_calculation.txt
     Generate training data from it

Claude: [Uses generate_from_procedures tool]

        ✅ Operational Training Data Generated

        📄 Procedure: NAV Calculation Procedure
        📋 Type: Standard Operating Procedure

        📊 Generated: 25 examples
        - How-to questions: ~5 ("How do I calculate NAV?")
        - Role questions: ~5 ("Who is responsible for NAV approval?")
        - Scenario questions: ~5 ("What if prices are unavailable?")
        - Compliance questions: ~5 ("How does this ensure UCITS compliance?")

        📁 Output: nav_training.jsonl

        This teaches the model HOW NAV calculation works in practice!
```

### Tool 2: Parse Procedure

**What it does:** Analyzes procedure structure before generating training data

**Example conversation:**
```
You: Analyze my trade settlement procedure at /procedures/trade_settlement.txt

Claude: [Uses parse_procedure tool]

        📄 Procedure Analysis

        Title: Trade Settlement Monitoring Workflow
        Type: Workflow

        📋 Structure:
        - Steps identified: 9
        - Roles mentioned: 3 (Middle Office, Trading Desk, Custodian)
        - Related regulations: 1 (MiFID II)
        - Triggers: 1 (T+1 after trade execution)
        - Control points: 2

        📝 Sample Steps:
          1. Receive trade confirmations from counterparties
          2. Match trade details against internal records
          3. Identify any breaks or discrepancies

        ✅ Ready to generate training data!
```

### Tool 3: Cross-Procedure Scenarios

**What it does:** Creates training examples involving multiple procedures

**Example conversation:**
```
You: Create scenarios combining these procedures:
     - /procedures/nav_calculation.txt
     - /procedures/error_correction.txt
     - /procedures/escalation.txt

Claude: [Uses generate_cross_procedure_scenarios tool]

        ✅ Cross-Procedure Scenarios Generated

        📊 Input:
        - Procedures combined: 3
        - Scenarios generated: 15

        Examples created:
        - "A NAV error was detected. Walk me through the correction process."
        - "What happens when the NAV error exceeds the materiality threshold?"
        - "How do we communicate NAV corrections to investors?"

        These scenarios teach how procedures work together!

        📁 Output: cross_procedure_scenarios.jsonl
```

### Tool 4: Link Procedures to Regulations

**What it does:** Creates training data bridging regulations and operations

**Example conversation:**
```
You: Link my NAV procedure to the UCITS directive requirements

Claude: [Uses link_procedures_to_regulations tool]

        Creates examples like:
        - Q: "How does the NAV calculation procedure ensure compliance
             with UCITS Article 85?"
          A: "The procedure implements Article 85 requirements through:
             1. Daily valuation using latest available prices
             2. Four-eyes approval process
             3. NAV movement threshold monitoring
             Each step directly addresses Article 85 obligations..."

        This bridges regulatory theory with operational practice!
```

### Tool 5: Analyze Coverage

**What it does:** Identifies gaps in operational procedure documentation

**Example conversation:**
```
You: Analyze coverage of my procedures directory /procedures/

Claude: [Uses analyze_procedure_coverage tool]

        📊 Operational Procedure Coverage Analysis

        📋 Overall: 12 procedures documented

        📜 Coverage by Regulation:
        ✅ UCITS: 5 procedures
        ⚠️  AIFMD: 2 procedures
        ❌ SFDR: 0 procedures
        ✅ MiFID II: 3 procedures

        💡 Recommendations:
        - Add SFDR-related operational procedures
        - Document AIFMD reporting workflows
        - Create compliance checklists

        This helps ensure comprehensive training coverage!
```

---

## 📚 Complete Workflow Examples

### Workflow 1: Single Procedure

**Goal:** Train model on NAV calculation

```
1. You: "Analyze my NAV procedure at /procedures/nav_calc.txt"
   Claude: [Shows structure, 15 steps, 4 roles, links to UCITS Article 85]

2. You: "Generate 30 training examples from it"
   Claude: [Creates 30 examples covering how-to, roles, scenarios]

3. You: "Validate the output"
   Claude: [All 30 examples valid, ready for fine-tuning]

4. You: "Combine with my UCITS regulatory training data"
   Claude: [Merges regulatory + operational knowledge]
```

**Result:** Model knows both UCITS Article 85 AND how to calculate NAV in practice!

---

### Workflow 2: Multiple Procedures

**Goal:** Comprehensive operational training

```
You: I want to train my model on fund operations. I have procedures for:
     - NAV calculation (/procedures/nav.txt)
     - Trade settlement (/procedures/settlement.txt)
     - Investor onboarding (/procedures/onboarding.txt)
     - Error correction (/procedures/errors.txt)
     - Escalation (/procedures/escalation.txt)

     Generate comprehensive training data including cross-procedure scenarios.

Claude: I'll create a complete operational training dataset!

        [Step 1: Parse all procedures]
        ✅ Analyzed 5 procedures

        [Step 2: Generate from each procedure]
        ✅ NAV: 25 examples
        ✅ Settlement: 22 examples
        ✅ Onboarding: 28 examples
        ✅ Errors: 20 examples
        ✅ Escalation: 18 examples

        [Step 3: Generate cross-procedure scenarios]
        ✅ Created 20 multi-procedure scenarios like:
           - "NAV error detected during settlement - what's the process?"
           - "New investor onboarding with unusual risk profile - how to handle?"

        [Step 4: Combine everything]
        ✅ Total: 133 operational training examples

        📁 Output: comprehensive_ops_training.jsonl

        Next: Combine with your regulatory training data for complete coverage!
```

---

### Workflow 3: Regulatory + Operational Combined

**Goal:** Model that knows both theory and practice

```
You: Create a complete training dataset combining:

     Regulatory knowledge:
     - UCITS directive (/regs/ucits.pdf)
     - AIFMD (/regs/aifmd.pdf)
     - SFDR (/regs/sfdr.pdf)

     Operational procedures:
     - All procedures in /procedures/ directory

     Link procedures to regulations where applicable.

Claude: I'll create a comprehensive regulatory + operational dataset!

        [Regulatory Training Data]
        ✅ UCITS: 145 examples
        ✅ AIFMD: 128 examples
        ✅ SFDR: 89 examples
        → Total regulatory: 362 examples

        [Operational Training Data]
        ✅ Analyzed 12 procedures
        ✅ Generated 145 operational examples
        ✅ Created 25 cross-procedure scenarios
        → Total operational: 170 examples

        [Linkage Training Data]
        ✅ Created 40 examples linking procedures to regulations
        Examples:
        - "How does NAV procedure implement UCITS Article 85?"
        - "Which procedures ensure SFDR Article 8 compliance?"

        [Complete Dataset]
        📊 Total: 572 examples
        📁 Output: complete_fund_training.jsonl

        ✅ Validated: All examples valid

        💰 Estimated cost: ~$8 training + $200/mo PT
        ⏱️  Training time: ~5 hours

        Your model will now understand:
        ✅ Regulatory requirements (UCITS, AIFMD, SFDR)
        ✅ Operational procedures (HOW to comply)
        ✅ How regulations and operations connect

        Ready to fine-tune a complete fund management expert!
```

---

## 🎯 Real-World Use Cases

### Use Case 1: Onboarding Junior Staff

**Before (without operational training):**
```
Junior: "How do I calculate NAV?"
Model: "NAV is calculated per UCITS Article 85..." [unhelpful regulatory answer]
```

**After (with operational training):**
```
Junior: "How do I calculate NAV?"
Model: "Follow these steps:
       1. Open the fund accounting system
       2. Obtain closing prices from Bloomberg/Refinitiv
       3. Verify prices are from approved sources (check vendor list)
       4. Calculate total holdings value
       5. Add accrued income and receivables
       6. Subtract all liabilities
       7. Divide by outstanding shares
       8. Compare to prior day - flag if movement > 5%
       9. Get Controller approval
       10. Publish to distribution channels

       This implements UCITS Article 85 valuation requirements."
```

**The model becomes a virtual trainer!**

---

### Use Case 2: Exception Handling

**Training data includes scenarios like:**

```json
{
  "system": "You are an expert in fund operations and compliance procedures.",
  "messages": [
    {
      "role": "user",
      "content": "I'm calculating NAV but prices are unavailable for one security that represents 3% of the fund. What should I do?"
    },
    {
      "role": "assistant",
      "content": "Here's the procedure for missing prices:\n\n1. Check if the security trades on multiple exchanges - use alternate exchange price if available\n\n2. If no alternate price available:\n   - Use most recent available price with appropriate aging disclosure\n   - Document the pricing source and reason\n   - Flag for review by Fund Controller\n\n3. If position > 5% of fund:\n   - Escalate to CIO immediately\n   - May require NAV publication delay\n   - Consider if material enough for investor notification\n\n4. For 3% position (your case):\n   - Use last available price\n   - Document in NAV calculation notes\n   - Inform Controller\n   - Monitor for price availability next day\n\n5. Update the pricing exception log\n\nThis ensures compliance with UCITS valuation rules while maintaining operational continuity."
    }
  ]
}
```

---

### Use Case 3: Compliance Audits

**Model can answer:**
- "Show me the controls in our NAV procedure that ensure Article 85 compliance"
- "What procedures do we have for SFDR Article 8 disclosure?"
- "How do we demonstrate MiFID II best execution in our trade workflow?"

**Answers reference actual procedures + regulatory requirements**

---

## 📝 Procedure Document Format

### What the Parser Recognizes

The parser automatically extracts:

```
Title: [Detected from first line or "Title:" field]

Type: SOP | Workflow | Checklist | Decision Tree
(Auto-detected from keywords or specified)

Responsible: [Role/Person]
Role: [Alternative keyword]
Owner: [Alternative keyword]

Regulation: [Regulatory reference]
Compliance: [Alternative keyword]
Article XX: [Auto-detected]

Trigger: [What initiates this procedure]
When: [Alternative keyword]
Upon: [Alternative keyword]

Steps:
1. Step one
2. Step two
[Also recognizes: A., ►, •, - formats]

Control: [Control point]
Checkpoint: [Alternative keyword]
Verify: [Alternative keyword]

Output: [Deliverable]
Result: [Alternative keyword]
```

### Example Procedure Format

```text
NAV Calculation Procedure

Type: Standard Operating Procedure
Regulation: UCITS Directive Article 85

Responsible: Fund Accountant
Review: Fund Controller

Trigger: Daily, at market close

Steps:
1. Obtain closing prices from pricing vendors (Bloomberg, Refinitiv)
2. Verify price sources against approved vendor list
   Control: Price Source Validation
3. Calculate fund holdings value using latest prices
4. Add accrued income and receivables
5. Subtract liabilities and accrued expenses
6. Divide net asset value by outstanding shares
7. Review NAV movement vs. prior day
   Control: NAV Movement Check - escalate if > 5% unexplained
8. Obtain Controller approval
9. Publish NAV to distribution channels

Output: Daily NAV per share
Timeline: Must publish by 9 AM T+1

Escalation: NAV errors > 0.5% escalate to CIO
```

**The parser extracts:**
- Title: "NAV Calculation Procedure"
- Type: SOP
- 9 steps
- 2 roles (Fund Accountant, Fund Controller)
- 1 regulation (UCITS Article 85)
- 1 trigger (Daily at market close)
- 2 controls
- 1 escalation rule

---

## 🎨 Types of Questions Generated

### 1. How-To Questions (Procedural)

```
Q: "How do I calculate the NAV for a UCITS fund?"
A: [Full step-by-step procedure]

Q: "What is the process for investor onboarding?"
A: [Complete workflow with checkpoints]
```

### 2. Role/Responsibility Questions

```
Q: "Who is responsible for NAV approval?"
A: "The Fund Controller is responsible for final NAV approval..."

Q: "What is the role of Middle Office in trade settlement?"
A: "Middle Office is responsible for: 1) Trade confirmation matching..."
```

### 3. Timing/Trigger Questions

```
Q: "When should the NAV calculation procedure be initiated?"
A: "Daily at market close, typically 4:00 PM EST..."

Q: "What triggers the escalation procedure?"
A: "Escalation is triggered when: 1) NAV error exceeds 0.5%..."
```

### 4. Scenario Questions (What-If)

```
Q: "What should I do if trade settlement fails?"
A: "If a trade fails to settle, follow these steps..."

Q: "A pricing vendor is unavailable. How do I proceed with NAV calculation?"
A: "When the primary pricing vendor is unavailable..."
```

### 5. Compliance Linkage Questions

```
Q: "How does the NAV procedure ensure UCITS Article 85 compliance?"
A: "The procedure implements Article 85 through: 1) Daily valuation..."

Q: "What controls demonstrate MiFID II compliance in our trading workflow?"
A: "MiFID II compliance is demonstrated through the following controls..."
```

---

## 💡 Best Practices

### 1. Start with Core Procedures

Priority order:
1. NAV calculation (critical daily operation)
2. Trade execution and settlement
3. Investor onboarding/redemption
4. Error correction
5. Compliance checks/checklists

### 2. Link to Regulations

Always specify related regulations in your procedures:
```
Regulation: UCITS Article 85
Compliance: MiFID II Article 27
Reference: SFDR Article 8
```

This enables the "link_procedures_to_regulations" tool to work effectively.

### 3. Include Controls and Checkpoints

Specify control points:
```
Control: Four-eyes approval required
Checkpoint: Verify against approved vendor list
Review: NAV movement > 5% requires CIO approval
```

These become part of compliance-focused training examples.

### 4. Document Exceptions

Include exception handling:
```
If [condition]:
  - Do [action]
  - Escalate to [role]
  - Document in [system]
```

This creates valuable scenario-based training data.

### 5. Use Consistent Formatting

Consistent formatting helps the parser:
- Number steps clearly (1., 2., 3.)
- Use consistent role labels (Responsible:, Owner:)
- Specify regulations explicitly (Regulation:, Article:)

---

## 🔄 Integration with Regulatory Training

### Combined Training Strategy

```
Regulatory Training (40%):
- UCITS directive
- AIFMD
- SFDR
- MiFID II
→ Teaches WHAT the rules are

Operational Training (40%):
- NAV calculation
- Trade workflows
- Investor services
- Compliance checks
→ Teaches HOW to comply

Linkage Training (20%):
- Procedure-to-regulation mapping
- Cross-procedure scenarios
- End-to-end workflows
→ Teaches WHY and WHEN

= Complete Expert Model
```

### Example Combined Conversation

```
User: "How should I handle a NAV error?"

Model: "For NAV error handling:

       [OPERATIONAL]
       1. Immediately halt NAV publication
       2. Quantify the error (recalculate with correct data)
       3. Determine impact on historical NAVs
       4. If error > 0.5%, escalate to CIO
       5. If error > 1%, escalate to Board

       [REGULATORY]
       This procedure ensures compliance with:
       - UCITS Article 85 (accurate valuation)
       - Article 78 (investor disclosure requirements)
       - Material errors may require investor notification

       [PRACTICAL]
       For errors < 0.5%: Correct in next NAV
       For errors > 0.5%: May require NAV restatement and investor notice
       For errors > 1%: Regulatory notification required

       Would you like me to walk through the specific steps for your situation?"
```

**The model seamlessly combines operational procedure, regulatory requirements, and practical guidance!**

---

## 📊 Sample Training Data Output

### Example 1: Single Procedure

**Input:** NAV Calculation SOP

**Output:** 25 examples

```json
{"system": "You are an expert in fund operations.", "messages": [{"role": "user", "content": "How do I calculate NAV?"}, {"role": "assistant", "content": "To calculate NAV:\n1. Obtain closing prices...\n2. Verify prices...\n[full procedure]\nThis ensures UCITS Article 85 compliance."}]}

{"system": "You are an expert in fund operations.", "messages": [{"role": "user", "content": "Who approves the NAV?"}, {"role": "assistant", "content": "The Fund Controller is responsible for final NAV approval after reviewing...[details]"}]}

{"system": "You are an expert in fund operations.", "messages": [{"role": "user", "content": "What if prices are unavailable?"}, {"role": "assistant", "content": "If closing prices are unavailable:\n1. Check alternate exchanges...\n2. Use last available price with disclosure...\n[full exception handling]"}]}
```

### Example 2: Cross-Procedure Scenario

**Input:** NAV Calculation + Error Correction + Escalation procedures

**Output:** 15 examples

```json
{"system": "You are an expert in fund operations with deep knowledge of operational procedures.", "messages": [{"role": "user", "content": "We discovered a NAV error from 3 days ago that affected 50 investors. Walk me through what we need to do."}, {"role": "assistant", "content": "For a historical NAV error affecting 50 investors:\n\n[NAV ERROR CORRECTION]\n1. Quantify the error (recalculate correct NAVs)\n2. Determine if material (> 0.5% threshold)\n3. Calculate impact on each affected investor\n\n[ESCALATION]\n4. Escalate to CIO immediately\n5. Notify Board if error > 1%\n6. Prepare incident report\n\n[INVESTOR NOTIFICATION]\n7. Draft investor notification letter\n8. Calculate compensation if applicable\n9. Coordinate with Legal/Compliance\n\n[REGULATORY]\n10. Determine if regulatory notification required\n11. File incident report with regulator if material\n12. Document root cause analysis\n\n[REMEDIATION]\n13. Process compensation payments\n14. Update systems to prevent recurrence\n15. Review and update procedures\n\nThis process ensures compliance with UCITS Article 85 and investor protection requirements."}]}
```

---

## 🚀 Getting Started Checklist

- [ ] Identify your 5-10 most critical operational procedures
- [ ] Ensure procedures document: steps, roles, regulations, controls
- [ ] Format procedures consistently (numbered steps, clear structure)
- [ ] Install extended MCP server OR use Python directly
- [ ] Generate training data from each procedure
- [ ] Create cross-procedure scenarios
- [ ] Combine with regulatory training data
- [ ] Validate combined dataset
- [ ] Fine-tune on Bedrock
- [ ] Test with realistic operational questions

---

## 📞 Troubleshooting

### Parser Not Extracting Steps

**Issue:** Steps not detected

**Fix:** Use numbered format:
```
Steps:
1. First step
2. Second step
3. Third step
```

Not: "First, do this. Then, do that."

### Missing Regulatory Links

**Issue:** Regulation not detected

**Fix:** Use explicit labels:
```
Regulation: UCITS Article 85
Compliance: MiFID II Article 27
```

Not: "This follows UCITS rules"

### Too Few Examples Generated

**Issue:** Only 5-10 examples created

**Fix:**
- Increase `num_examples` parameter
- Ensure procedure has sufficient detail (10+ steps)
- Add more roles, controls, scenarios to source procedure

---

## 🎓 Next Steps

1. **Generate your first operational training data:**
   ```
   Use: generate_from_procedures
   Input: Your NAV calculation procedure
   Output: 25 operational training examples
   ```

2. **Combine with regulatory data:**
   ```
   Combine: Regulatory examples + Operational examples
   Result: Model that knows both theory and practice
   ```

3. **Test the fine-tuned model:**
   ```
   Ask: "How do I handle a NAV error?"
   Get: Step-by-step operational procedure + regulatory context
   ```

4. **Iterate and improve:**
   ```
   Add more procedures → More comprehensive operational knowledge
   Create cross-procedure scenarios → Better real-world understanding
   Link to regulations → Stronger compliance guidance
   ```

---

**Transform your model from a regulatory encyclopedia into an operational expert!** 🚀

The combination of regulatory knowledge + operational procedures creates a truly useful fund management AI assistant.
