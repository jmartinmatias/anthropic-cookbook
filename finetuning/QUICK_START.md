# Quick Start: EU Funds Fine-tuning

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
pip install anthropic PyPDF2 boto3
export ANTHROPIC_API_KEY='your-key-here'
```

### 2. Generate Training Data
```bash
# Using the sample file
python generate_eu_funds_training_data.py \
    --input sample_ucits_text.txt \
    --output my_training_data.jsonl

# Or run the examples
python example_usage.py
```

### 3. Validate
```bash
python generate_eu_funds_training_data.py \
    --output my_training_data.jsonl \
    --validate-only
```

### 4. Upload to S3
```bash
aws s3 cp my_training_data.jsonl s3://your-bucket/training/
```

### 5. Fine-tune in Bedrock
```python
import boto3

bedrock = boto3.client('bedrock')
bedrock.create_model_customization_job(
    customizationType="FINE_TUNING",
    jobName="eu-funds-expert",
    customModelName="claude-haiku-eu-funds",
    roleArn="arn:aws:iam::ACCOUNT:role/BedrockRole",
    baseModelIdentifier="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0:200k",
    hyperParameters={"epochCount": "5", "batchSize": "8"},
    trainingDataConfig={"s3Uri": "s3://your-bucket/training/my_training_data.jsonl"},
    outputDataConfig={"s3Uri": "s3://your-bucket/results/"}
)
```

## 📖 Common Use Cases

### Use Your Own Regulatory Documents
```bash
# PDF document
python generate_eu_funds_training_data.py \
    --input /path/to/UCITS_Directive.pdf \
    --output ucits_training.jsonl \
    --examples-per-chunk 20

# Text document
python generate_eu_funds_training_data.py \
    --input /path/to/AIFMD.txt \
    --output aifmd_training.jsonl
```

### Custom System Prompt
```bash
python generate_eu_funds_training_data.py \
    --input regulations.txt \
    --output training.jsonl \
    --system-prompt "You are a fund compliance officer providing practical regulatory guidance."
```

### Combine Multiple Sources
```bash
# Generate from each regulation
python generate_eu_funds_training_data.py --input ucits.txt --output ucits.jsonl
python generate_eu_funds_training_data.py --input aifmd.txt --output aifmd.jsonl
python generate_eu_funds_training_data.py --input sfdr.txt --output sfdr.jsonl

# Combine all
cat ucits.jsonl aifmd.jsonl sfdr.jsonl > complete_training.jsonl
```

## 📋 Command Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--input` | Path to regulatory document | `--input ucits.pdf` |
| `--output` | Output JSONL file | `--output training.jsonl` |
| `--examples-per-chunk` | Examples per chunk (default: 15) | `--examples-per-chunk 25` |
| `--system-prompt` | Custom system message | `--system-prompt "Expert..."` |
| `--no-specialized` | Skip hand-crafted examples | `--no-specialized` |
| `--validate-only` | Just validate existing file | `--validate-only` |
| `--api-key` | API key (or use env var) | `--api-key sk-...` |

## 🎯 Recommended Settings

| Use Case | Examples/Chunk | Total Examples | Epochs |
|----------|----------------|----------------|--------|
| **Quick Test** | 10 | 50-100 | 3 |
| **Basic Model** | 15 | 200-300 | 5 |
| **Production** | 20 | 500-1000 | 5-7 |
| **Comprehensive** | 25 | 1000+ | 7-10 |

## 💡 Pro Tips

1. **Start Small**: Test with 50-100 examples first
2. **Quality > Quantity**: Review samples before fine-tuning
3. **Diverse Sources**: Mix different regulations for broader knowledge
4. **Update Regularly**: Regulations change - keep data current
5. **Validate Always**: Check format before uploading

## ⚠️ Common Issues

**Problem**: "Could not read document"
- **Fix**: Ensure PDF is text-based (not scanned image)

**Problem**: "Too few examples generated"
- **Fix**: Increase `--examples-per-chunk` or check document content

**Problem**: "Validation errors"
- **Fix**: Run `--validate-only` to see details

**Problem**: "API timeout"
- **Fix**: Reduce `--examples-per-chunk` to process smaller batches

## 📁 Files Included

- `generate_eu_funds_training_data.py` - Main generator script
- `example_usage.py` - Usage examples
- `sample_ucits_text.txt` - Sample regulatory text
- `EU_FUNDS_TRAINING_README.md` - Detailed documentation
- `QUICK_START.md` - This file

## 🔗 Resources

- Full guide: [EU_FUNDS_TRAINING_README.md](EU_FUNDS_TRAINING_README.md)
- Fine-tuning notebook: [finetuning_on_bedrock.ipynb](finetuning_on_bedrock.ipynb)
- Anthropic docs: https://docs.anthropic.com
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/

## 🆘 Need Help?

1. Check the detailed README: `EU_FUNDS_TRAINING_README.md`
2. Run examples: `python example_usage.py`
3. Validate your data: `--validate-only` flag
4. Review the main fine-tuning notebook
