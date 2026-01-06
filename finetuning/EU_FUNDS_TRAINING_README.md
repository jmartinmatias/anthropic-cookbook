# Generating Training Data for EU Investment Funds Regulations

This guide shows you how to generate fine-tuning training data from EU investment funds regulatory texts using Claude.

## 🎯 Overview

The `generate_eu_funds_training_data.py` script automatically creates high-quality training examples from regulatory documents such as:

- **UCITS Directive** (2009/65/EC)
- **AIFMD** (Alternative Investment Fund Managers Directive)
- **MiFID II** (Markets in Financial Instruments Directive)
- **PRIIPs Regulation** (Packaged Retail Investment Products)
- **SFDR** (Sustainable Finance Disclosure Regulation)
- **Taxonomy Regulation**
- **Prospectus Regulation**
- And other EU fund regulations

## 📋 Prerequisites

```bash
# Install required packages
pip install anthropic PyPDF2

# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Generate training data from a regulatory document
python generate_eu_funds_training_data.py \
    --input /path/to/UCITS_Directive.pdf \
    --output ucits_training_data.jsonl
```

### 2. With Custom Options

```bash
# More examples per chunk, custom system prompt
python generate_eu_funds_training_data.py \
    --input regulations.txt \
    --output training.jsonl \
    --examples-per-chunk 25 \
    --system-prompt "You are a UCITS compliance expert providing regulatory guidance."
```

### 3. Validate Existing Training File

```bash
# Check if your training file is properly formatted
python generate_eu_funds_training_data.py \
    --output training.jsonl \
    --validate-only
```

## 📖 What It Generates

The script creates diverse training examples covering:

### Question Types

1. **Definitions**
   - "What is a UCITS fund?"
   - "Define alternative investment fund under AIFMD"

2. **Procedural Requirements**
   - "What are the authorization requirements for an AIFM?"
   - "How does a UCITS obtain regulatory approval?"

3. **Compliance Obligations**
   - "What are the disclosure obligations under SFDR Article 8?"
   - "What reporting requirements apply to AIFMs?"

4. **Thresholds & Limits**
   - "What are the leverage limits for UCITS?"
   - "What are the concentration limits under Article 52?"

5. **Exemptions**
   - "Which entities are exempt from AIFMD?"
   - "What funds qualify for the de minimis exemption?"

6. **Timelines & Deadlines**
   - "When must the annual report be published?"
   - "What are the notification deadlines for material changes?"

7. **Multi-turn Conversations**
   - Follow-up questions and clarifications
   - Comparative analysis

### Example Output Format

```json
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
```

## 🎨 Features

### Hand-Crafted Specialized Examples

The script includes pre-written, high-quality examples covering:

- UCITS fundamentals and diversification rules
- AIFMD vs UCITS comparison
- SFDR Article 8 & 9 classification
- MiFID II client categorization
- KIID/KID requirements
- Depositary duties

Disable with `--no-specialized` flag if you want only auto-generated examples.

### Intelligent Document Chunking

- Automatically splits large documents
- Preserves article/section boundaries
- Handles PDF and text formats

### Validation

- Ensures proper JSONL format
- Validates message structure
- Checks user/assistant alternation
- Reports errors and warnings

## 📚 Complete Workflow Example

### Step 1: Prepare Your Documents

```bash
# Example: Download UCITS Directive text
# Place in a directory like:
# /documents/regulations/ucits_directive.txt
```

### Step 2: Generate Training Data

```bash
python generate_eu_funds_training_data.py \
    --input /documents/regulations/ucits_directive.txt \
    --output datasets/ucits_training.jsonl \
    --examples-per-chunk 20
```

Output:
```
Reading document: /documents/regulations/ucits_directive.txt
Document length: 125000 characters
Split into 2 chunks
Added 7 specialized examples

Processing chunk 1/2...
Generated 18 examples from chunk 1

Processing chunk 2/2...
Generated 19 examples from chunk 2

✅ Successfully generated 44 training examples
📁 Saved to: datasets/ucits_training.jsonl

🔍 Validating generated file...
Valid examples: 44/44

✅ Training data generation complete!
```

### Step 3: Validate

```bash
python generate_eu_funds_training_data.py \
    --output datasets/ucits_training.jsonl \
    --validate-only
```

### Step 4: Review Sample Examples

```bash
# View first 3 examples
head -n 3 datasets/ucits_training.jsonl | python -m json.tool
```

### Step 5: Upload to S3

```bash
aws s3 cp datasets/ucits_training.jsonl s3://your-bedrock-bucket/training/
```

### Step 6: Launch Fine-tuning (see main notebook)

```python
import boto3

bedrock = boto3.client('bedrock')

bedrock.create_model_customization_job(
    customizationType="FINE_TUNING",
    jobName="eu-funds-regulations-expert",
    customModelName="claude-haiku-eu-funds",
    roleArn="arn:aws:iam::YOUR_ACCOUNT:role/BedrockRole",
    baseModelIdentifier="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0:200k",
    hyperParameters={
        "epochCount": "5",
        "batchSize": "8",
        "learningRateMultiplier": "1.0"
    },
    trainingDataConfig={"s3Uri": "s3://your-bedrock-bucket/training/ucits_training.jsonl"},
    outputDataConfig={"s3Uri": "s3://your-bedrock-bucket/results/"}
)
```

## 💡 Best Practices

### 1. Source Document Quality

- Use official regulatory texts (EUR-Lex, ESMA, national regulators)
- Ensure documents are up-to-date with latest amendments
- Include relevant technical standards and guidelines

### 2. Training Data Size

- **Minimum**: 50-100 examples
- **Recommended**: 200-500 examples for good coverage
- **Large datasets**: 1000+ for comprehensive regulatory knowledge

### 3. Diverse Coverage

Generate data from multiple regulatory frameworks:
```bash
# Generate from multiple sources
python generate_eu_funds_training_data.py --input ucits.txt --output data1.jsonl
python generate_eu_funds_training_data.py --input aifmd.txt --output data2.jsonl
python generate_eu_funds_training_data.py --input sfdr.txt --output data3.jsonl

# Combine
cat data1.jsonl data2.jsonl data3.jsonl > combined_training.jsonl
```

### 4. System Prompts

Customize system prompts based on your use case:

**For compliance advisors:**
```bash
--system-prompt "You are a regulatory compliance advisor for investment fund managers. You provide accurate, practical guidance on EU fund regulations."
```

**For fund documentation:**
```bash
--system-prompt "You are an expert in investment fund documentation. You help draft regulatory disclosures and investor documents in compliance with EU rules."
```

**For regulatory reporting:**
```bash
--system-prompt "You are an expert in regulatory reporting for investment funds. You help prepare accurate regulatory filings and reports."
```

### 5. Quality Review

Always manually review a sample of generated examples:

```python
import json

# Review random samples
with open('training.jsonl', 'r') as f:
    examples = [json.loads(line) for line in f]

import random
sample = random.sample(examples, 10)

for ex in sample:
    print(f"Q: {ex['messages'][0]['content']}")
    print(f"A: {ex['messages'][1]['content'][:200]}...")
    print("-" * 80)
```

## 🔧 Advanced Usage

### Custom Question Types

Modify the `QUESTION_TYPES` dictionary in the script:

```python
QUESTION_TYPES = {
    "risk_management": "What risk management requirements apply to {scenario}?",
    "cross_border": "What are the cross-border requirements for {activity}?",
    "delegation": "What are the rules for delegating {function}?",
    # Add your own types
}
```

### Processing Multiple Files

```bash
#!/bin/bash
# process_all_regulations.sh

for file in regulations/*.pdf; do
    basename=$(basename "$file" .pdf)
    echo "Processing $basename..."
    python generate_eu_funds_training_data.py \
        --input "$file" \
        --output "datasets/${basename}_training.jsonl" \
        --examples-per-chunk 15
done

# Combine all outputs
cat datasets/*_training.jsonl > datasets/all_regulations_training.jsonl
```

### Fine-tuning Multiple Models

```python
# Strategy: Create specialized models for different regulations

# Model 1: UCITS specialist
# Train on: UCITS directive + Level 2 regulations + ESMA guidelines

# Model 2: AIFMD specialist
# Train on: AIFMD + Level 2 regs + reporting technical standards

# Model 3: Sustainability specialist
# Train on: SFDR + Taxonomy + RTS disclosures
```

## 📊 Expected Results

After fine-tuning on 300-500 examples, your model should be able to:

✅ Accurately cite specific articles and directives
✅ Explain complex regulatory concepts clearly
✅ Distinguish between similar regulatory frameworks
✅ Provide practical compliance guidance
✅ Handle multi-jurisdictional questions
✅ Reference relevant deadlines and thresholds
✅ Explain exemptions and special cases

## ⚠️ Important Notes

### Legal Disclaimer

- This tool generates training data for educational/operational purposes
- Always verify regulatory interpretations with qualified legal counsel
- Regulations change frequently - keep training data updated
- Fine-tuned models should complement, not replace, expert legal advice

### Data Privacy

- Do not include confidential client information in training data
- Use only public regulatory texts and generic examples
- Sanitize any proprietary internal procedures

### Model Limitations

- Fine-tuning improves domain knowledge but doesn't guarantee accuracy
- Always validate model outputs for regulatory compliance
- Keep a human-in-the-loop for final regulatory decisions

## 🆘 Troubleshooting

### Issue: "Could not parse line as JSON"

**Solution:** The model sometimes adds explanatory text. The script handles this automatically, but if you see many warnings:
- Reduce `examples_per_chunk`
- Manually review and clean the output

### Issue: "Too few examples generated"

**Solution:**
- Ensure input document has sufficient content
- Increase `examples_per_chunk`
- Check document formatting (PDF extraction quality)

### Issue: Validation errors

**Solution:**
```bash
# Get detailed validation report
python generate_eu_funds_training_data.py \
    --output training.jsonl \
    --validate-only
```

## 📞 Support

- Review the [main fine-tuning notebook](finetuning_on_bedrock.ipynb)
- Check [Anthropic documentation](https://docs.anthropic.com)
- AWS Bedrock [fine-tuning guide](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization.html)

## 🚀 Next Steps

1. ✅ Generate training data from your regulatory documents
2. ✅ Validate the output format
3. ✅ Upload to S3
4. ✅ Launch fine-tuning job in Bedrock
5. ✅ Deploy with Provisioned Throughput
6. ✅ Test with real-world regulatory queries
7. ✅ Iterate and improve based on results
