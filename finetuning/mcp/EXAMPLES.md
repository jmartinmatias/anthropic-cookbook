# MCP Server Usage Examples

Real-world examples of using the EU Funds Fine-tuning MCP server with Claude.

## 🚀 Quick Examples

### Example 1: Basic Training Data Generation

**You:**
```
I have a UCITS directive PDF at /Users/me/docs/ucits_directive.pdf
Generate training data from it
```

**Claude:**
```
I'll generate training data from your UCITS directive PDF.

[Uses generate_training_data tool]

✅ Training Data Generated Successfully

📊 Results:
- Total examples: 127
- Valid examples: 127
- Output file: /Users/me/docs/ucits_directive_training.jsonl

🔍 Validation:
- Errors: 0
- Warnings: 0

📈 Next Steps:
1. Review the generated file
2. Upload to S3: aws s3 cp /Users/me/docs/ucits_directive_training.jsonl s3://your-bucket/
3. Launch fine-tuning job in AWS Bedrock
```

---

### Example 2: Analyze Before Generating

**You:**
```
Before I generate training data, analyze my document at /docs/sfdr_regulation.pdf
Tell me what to expect
```

**Claude:**
```
I'll analyze the SFDR regulation document for you.

[Uses analyze_document tool]

📄 Document Analysis: /docs/sfdr_regulation.pdf

📊 Structure:
- Document size: 89,234 characters
- Estimated chunks: 2
- Articles found: 45
- Sections found: 8
- Chapters found: 5

🔍 Detected Regulations:
  ✓ SFDR
  ✓ Taxonomy Regulation

📈 Training Data Estimates:
- Estimated examples (default): ~37
- With 20 examples/chunk: ~47
- With 25 examples/chunk: ~57

💡 Recommendations:
- Start with 15 examples per chunk
- Expected processing time: ~4 minutes
- Cost estimate: ~$0.10 in API calls

✅ Ready to generate training data with 'generate_training_data' tool
```

**You:**
```
Great! Generate with 20 examples per chunk
```

---

### Example 3: Complete Workflow for Multiple Documents

**You:**
```
I want to create a comprehensive training dataset for EU fund regulations.
I have three documents:

1. /docs/ucits_directive.pdf
2. /docs/aifmd.pdf
3. /docs/sfdr_regulation.pdf

Can you:
1. Analyze all three
2. Generate training data from each
3. Combine them
4. Validate the combined file
5. Estimate the fine-tuning cost
```

**Claude:**
```
I'll create a comprehensive training dataset from your three regulatory documents.
Let me work through this step by step.

[Step 1: Analyzing documents]

Analyzing UCITS directive...
Analyzing AIFMD...
Analyzing SFDR regulation...

📊 Analysis Summary:

UCITS Directive:
- 127 articles, 2 chunks
- Estimated: ~37 examples (15/chunk) or ~47 (20/chunk)

AIFMD:
- 89 articles, 2 chunks
- Estimated: ~37 examples (15/chunk) or ~47 (20/chunk)

SFDR:
- 45 articles, 1 chunk
- Estimated: ~22 examples (15/chunk) or ~27 (20/chunk)

Total estimated: ~96-121 examples

[Step 2: Generating training data]

Generating from UCITS directive (20 examples/chunk)...
✅ Generated 52 examples → ucits_training.jsonl

Generating from AIFMD (20 examples/chunk)...
✅ Generated 48 examples → aifmd_training.jsonl

Generating from SFDR (20 examples/chunk)...
✅ Generated 31 examples → sfdr_training.jsonl

[Step 3: Combining datasets]

Combining all training files...
✅ Combined 131 total examples → combined_eu_funds_training.jsonl

📁 Source Files:
  - ucits_training.jsonl: 52 examples
  - aifmd_training.jsonl: 48 examples
  - sfdr_training.jsonl: 31 examples

[Step 4: Validating combined file]

📋 Validation Results for combined_eu_funds_training.jsonl

📊 Summary:
- Total examples: 131
- Valid examples: 131
- Success rate: 100.0%
- Errors: 0
- Warnings: 0

✅ All examples are valid! Ready for fine-tuning.

[Step 5: Estimating costs]

💰 Fine-tuning Cost Estimate

📊 Training Data:
- Examples: 131
- Estimated tokens: 45,230
- Epochs: 5 (default)
- Batch size: 8 (default)

⏱️  Time Estimate:
- Training time: ~2.2 hours
- Wall time: ~3.3 hours (with overhead)

💵 Cost Breakdown (Estimates):

1. Fine-tuning Training:
   - Total training tokens: 226,150
   - Estimated cost: $1.81

2. Provisioned Throughput (required for inference):
   - Minimum commitment: ~$200/month
   - This is the main ongoing cost

3. Total First Month:
   - One-time training: $1.81
   - Monthly PT: $200.00
   - Total: $201.81

4. Ongoing (monthly):
   - Provisioned Throughput: $200.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Summary:

✅ Created comprehensive training dataset
📁 File: combined_eu_funds_training.jsonl
📊 Examples: 131 (all valid)
💰 Estimated cost: ~$1.81 training + $200/mo PT
⏱️  Training time: ~2-3 hours

📈 Next Steps:
1. aws s3 cp combined_eu_funds_training.jsonl s3://your-bucket/training/
2. Launch fine-tuning job in AWS Bedrock (see notebook)
3. Deploy with Provisioned Throughput
4. Test with regulatory queries!
```

---

### Example 4: Get Specialized Examples

**You:**
```
Show me the pre-written specialized examples for EU funds
```

**Claude:**
```
I'll get the hand-crafted specialized examples.

[Uses create_specialized_examples tool]

✅ Specialized Examples

📊 Total: 7 hand-crafted examples

📚 Topics covered:
- UCITS fundamentals and diversification
- AIFMD vs UCITS comparison
- SFDR Article 8 & 9 classification
- MiFID II client categorization
- KIID/KID requirements
- Depositary duties

📝 Sample Example:

{
  "system": "You are an expert in EU investment funds regulation, specializing in UCITS compliance.",
  "messages": [
    {
      "role": "user",
      "content": "What are the diversification requirements for UCITS?"
    },
    {
      "role": "assistant",
      "content": "Under Article 52 of the UCITS Directive, the key diversification requirements are:\n\n1. Maximum 10% of assets in securities from a single issuer\n2. Maximum 20% if the issuer is a credit institution with special supervision\n3. Maximum 5% in unlisted securities\n4. The 10% limit can be raised to 25% for covered bonds and certain other instruments\n5. The aggregate of positions exceeding 5% cannot exceed 40% of assets\n\nThese rules ensure appropriate risk spreading and investor protection."
    }
  ]
}

💡 These are expert-quality examples that cover the most important regulatory concepts.
   They can be used alone or combined with auto-generated examples.
```

**You:**
```
Save those to a file at /docs/specialized_examples.jsonl
```

---

### Example 5: Validate Existing File

**You:**
```
I have a training file at /docs/my_training.jsonl that I created manually.
Can you validate it for me?
```

**Claude:**
```
I'll validate your training file.

[Uses validate_training_data tool]

📋 Validation Results for /docs/my_training.jsonl

📊 Summary:
- Total examples: 45
- Valid examples: 43
- Success rate: 95.6%
- Errors: 2
- Warnings: 3

❌ Errors (2):
  - Line 23: First message must be from user
  - Line 38: Messages must alternate between user and assistant

⚠️  Warnings (3):
  - Line 5: No system prompt
  - Line 12: No system prompt
  - Line 34: No system prompt

⚠️  Fix errors before using for fine-tuning.

Would you like me to help fix these issues?
```

---

### Example 6: Sample Questions

**You:**
```
What kind of UCITS questions can a fine-tuned model answer?
```

**Claude:**
```
[Uses get_sample_questions tool with regulation="UCITS"]

📚 Sample Questions for UCITS

## Definitional
- What is a UCITS fund?
- What qualifies as a transferable security under UCITS?
- Define the term 'money market instrument' in UCITS context

## Procedural
- What is the process for authorizing a UCITS?
- How does a UCITS obtain a management company passport?
- What steps are required to merge two UCITS funds?

## Compliance
- What are the diversification requirements for UCITS?
- What are the eligible assets for UCITS investment?
- What are the limits on derivative use in UCITS?

## Threshold
- What is the maximum investment in a single issuer?
- What are the concentration limits for UCITS?
- What is the minimum capital requirement for a UCITS management company?

## Exemption
- Which funds are exempt from UCITS requirements?
- What exemptions exist for government bond concentration?
- Are there exemptions for index-tracking UCITS?

## Timeline
- When must the annual report be published?
- What are the notification deadlines for material changes?
- How long does regulatory approval typically take?

💡 A fine-tuned model can answer all these questions (and more) with regulatory citations.
```

---

### Example 7: Cost Estimation

**You:**
```
I have a training file with 500 examples.
Estimate the cost to fine-tune with 7 epochs instead of 5.
```

**Claude:**
```
[Uses estimate_training_cost tool]

💰 Fine-tuning Cost Estimate

📊 Training Data:
- Examples: 500
- Estimated tokens: 173,000
- Epochs: 7
- Batch size: 8

⏱️  Time Estimate:
- Training time: ~8.3 hours
- Wall time: ~12.5 hours (with overhead)

💵 Cost Breakdown (Estimates):

1. Fine-tuning Training:
   - Total training tokens: 1,211,000
   - Estimated cost: $9.69

2. Provisioned Throughput (required for inference):
   - Minimum commitment: ~$200/month

3. Total First Month:
   - One-time training: $9.69
   - Monthly PT: $200.00
   - Total: $209.69

4. Ongoing (monthly):
   - Provisioned Throughput: $200.00

💡 With 500 examples and 7 epochs, you're looking at a robust training run.
   This should produce excellent results for domain-specific queries!

⚠️  Remember: These are estimates. Check AWS Bedrock pricing for exact costs.
```

---

### Example 8: Custom System Prompt

**You:**
```
Generate training data from /docs/ucits.pdf with a system prompt
that focuses on helping compliance officers with practical guidance
```

**Claude:**
```
I'll generate training data with a custom system prompt tailored for compliance officers.

[Uses generate_training_data with custom system_prompt]

Using system prompt:
"You are a senior regulatory compliance officer specializing in EU investment funds.
You provide practical, actionable guidance to fund managers on compliance with UCITS
and related regulations. Your advice is accurate, cites specific regulatory provisions,
and considers real-world implementation challenges."

✅ Training Data Generated Successfully

📊 Results:
- Total examples: 89
- Valid examples: 89
- Output file: /docs/ucits_compliance_training.jsonl

🎯 All examples are now framed from a compliance officer's perspective,
   focusing on practical implementation rather than academic definitions.
```

---

### Example 9: Combine Multiple Files

**You:**
```
Combine these three training files into one:
- /training/ucits.jsonl
- /training/aifmd.jsonl
- /training/sfdr.jsonl

Save the combined file to /training/complete_training.jsonl
```

**Claude:**
```
[Uses combine_datasets tool]

✅ Datasets Combined Successfully

📊 Summary:
- Input files: 3
- Total examples: 243
- Output file: /training/complete_training.jsonl

📁 Source Files:
  - /training/ucits.jsonl: 89 examples
  - /training/aifmd.jsonl: 92 examples
  - /training/sfdr.jsonl: 62 examples

💡 Next Steps:
1. Validate: The combined file has been created
2. Upload to S3: aws s3 cp /training/complete_training.jsonl s3://your-bucket/
3. Launch fine-tuning job

Your comprehensive EU funds training dataset is ready!
```

---

## 🎯 Advanced Patterns

### Pattern 1: Quality-First Approach

```
You: Let's create high-quality training data. Here's my approach:

1. First analyze the document
2. Generate a small sample (5 examples/chunk)
3. Let me review the sample
4. If good, generate the full dataset
5. Add specialized examples
6. Validate everything
7. Estimate costs

Start with /docs/ucits.pdf

Claude: [Executes each step, providing results for review at each stage]
```

### Pattern 2: Iterative Improvement

```
You: Generate initial training data from /docs/ucits.pdf.
     After I review it, I'll tell you what to adjust.

Claude: [Generates initial dataset]

You: The examples are good but too academic.
     Regenerate with a system prompt that's more practical
     and focuses on day-to-day compliance questions.

Claude: [Regenerates with adjusted system prompt]

You: Perfect! Now combine with the specialized examples.

Claude: [Combines datasets]
```

### Pattern 3: Multi-Regulation Dataset

```
You: Build a comprehensive EU funds expert model:

Regulations to cover:
- UCITS (/docs/ucits.pdf) - 20 examples/chunk
- AIFMD (/docs/aifmd.pdf) - 20 examples/chunk
- SFDR (/docs/sfdr.pdf) - 25 examples/chunk (more detail needed)
- MiFID II (/docs/mifid.pdf) - 15 examples/chunk
- PRIIPs (/docs/priips.pdf) - 15 examples/chunk

Include specialized examples.
Validate everything.
Give me a cost estimate.

Claude: [Processes all regulations, combines, validates, estimates]
```

---

## 💡 Tips for Best Results

### Tip 1: Start with Analysis
Always analyze documents first to understand what you're working with.

### Tip 2: Use Specialized Examples
The hand-crafted examples are high quality - include them!

### Tip 3: Validate Often
Validate after each generation and after combining files.

### Tip 4: Custom System Prompts
Tailor system prompts to your specific use case (compliance, documentation, advisory, etc.)

### Tip 5: Iterate
Generate small samples first, review, then scale up.

---

## 🚀 Ready to Try?

Install the MCP server and start generating training data with natural language!

See [README.md](README.md) for installation instructions.
