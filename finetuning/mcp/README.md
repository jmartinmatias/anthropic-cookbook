# EU Investment Funds Fine-tuning MCP Server

**Transform regulatory documents into fine-tuning training data directly from Claude!**

This Model Context Protocol (MCP) server enables Claude to generate high-quality fine-tuning training data from EU investment funds regulatory texts like UCITS, AIFMD, MiFID II, SFDR, and more.

## 🚀 What is This?

An MCP server that provides Claude with tools to:

- 📄 **Generate training data** from regulatory PDFs and documents
- ✅ **Validate** JSONL training files for AWS Bedrock compatibility
- 🎯 **Create specialized examples** for EU fund regulations
- 📊 **Analyze documents** to understand structure and content
- 🔗 **Combine datasets** from multiple sources
- 💰 **Estimate costs** for fine-tuning jobs
- 📚 **Get sample questions** for different regulation types

## 🎯 Why Use This MCP?

**Before MCP:**
```bash
# You had to run Python scripts manually
python generate_eu_funds_training_data.py --input doc.pdf --output training.jsonl
python validate.py --file training.jsonl
# ... multiple manual steps
```

**With MCP:**
```
You: "Generate training data from my UCITS directive PDF"
Claude: [Uses MCP tool] ✅ Generated 127 examples, validated and ready!

You: "Estimate the cost to fine-tune this"
Claude: [Uses MCP tool] 💰 Approximately $15 training + $200/mo PT

You: "Combine my UCITS, AIFMD, and SFDR training files"
Claude: [Uses MCP tool] ✅ Combined 450 examples into one file
```

**Much more natural and powerful!** 🎉

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Claude Desktop app (or Claude Code)
- Anthropic API key

### Quick Install

```bash
# 1. Navigate to the MCP directory
cd anthropic-cookbook/finetuning/mcp

# 2. Install dependencies
pip install -e .

# 3. Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Configure Claude Desktop

**Option 1: Automatic Configuration**

```bash
# Run the install script
python install.py
```

**Option 2: Manual Configuration**

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "eu-funds-finetuning": {
      "command": "python",
      "args": [
        "/absolute/path/to/anthropic-cookbook/finetuning/mcp/server.py"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/` with your actual path!

### Restart Claude Desktop

After configuring, restart Claude Desktop to load the MCP server.

## 🎮 Usage

Once installed, you can use natural language in Claude to access all features!

### Example Conversations

#### 1. Generate Training Data

```
You: I have a UCITS directive PDF at /docs/ucits.pdf.
     Generate training data with 20 examples per chunk.

Claude: I'll generate training data from your UCITS directive.
        [Uses generate_training_data tool]

        ✅ Generated 145 examples
        📁 Saved to: /docs/ucits_training.jsonl
        🔍 Validated: All examples valid!
```

#### 2. Analyze a Document First

```
You: Analyze my regulatory document at /docs/sfdr_regulation.pdf
     before generating training data.

Claude: [Uses analyze_document tool]

        📄 Found 89 articles across 12 chapters
        🔍 Detected: SFDR, Taxonomy Regulation
        📈 Estimated: ~180 examples can be generated
        💡 Recommend: 15 examples per chunk
```

#### 3. Validate Training Data

```
You: Validate my training file at /data/training.jsonl

Claude: [Uses validate_training_data tool]

        ✅ All 234 examples are valid!
        No errors or warnings.
        Ready for fine-tuning on Bedrock.
```

#### 4. Get Sample Questions

```
You: What kind of questions can I ask about UCITS?

Claude: [Uses get_sample_questions tool]

        Here are example UCITS questions by category:

        Definitional:
        - What is a UCITS fund?
        - What qualifies as a transferable security?

        Compliance:
        - What are the diversification requirements?
        - What are the eligible assets?

        [... more categories ...]
```

#### 5. Estimate Costs

```
You: Estimate the cost to fine-tune with my training file

Claude: [Uses estimate_training_cost tool]

        💰 Cost Breakdown:
        - Training (one-time): $12.50
        - Provisioned Throughput: ~$200/month
        - First month total: ~$212.50
        ⏱️ Training time: ~3.2 hours
```

#### 6. Combine Multiple Datasets

```
You: Combine my UCITS, AIFMD, and SFDR training files into one dataset

Claude: [Uses combine_datasets tool]

        ✅ Combined 3 files:
        - ucits.jsonl: 145 examples
        - aifmd.jsonl: 178 examples
        - sfdr.jsonl: 92 examples

        Total: 415 examples saved to combined_training.jsonl
```

#### 7. Create Specialized Examples

```
You: Give me the hand-crafted specialized examples

Claude: [Uses create_specialized_examples tool]

        ✅ Created 7 expert-quality examples covering:
        - UCITS fundamentals
        - AIFMD vs UCITS comparison
        - SFDR Article 8 & 9 classification
        - MiFID II client types
        - KIID requirements
        - Depositary duties
```

## 🔧 Available Tools

The MCP server provides 7 tools:

| Tool | Description | Use Case |
|------|-------------|----------|
| `generate_training_data` | Generate training examples from documents | Main data generation |
| `validate_training_data` | Validate JSONL for Bedrock | Quality check |
| `create_specialized_examples` | Get hand-crafted examples | Seed high-quality data |
| `analyze_document` | Analyze document structure | Pre-generation analysis |
| `combine_datasets` | Merge multiple JSONL files | Combine sources |
| `get_sample_questions` | See example questions | Understand coverage |
| `estimate_training_cost` | Calculate fine-tuning costs | Budget planning |

## 📚 Complete Workflow Example

Here's a full workflow using the MCP:

```
You: I want to create a fine-tuned model for EU fund regulations.
     I have three documents:
     - /docs/ucits.pdf
     - /docs/aifmd.pdf
     - /docs/sfdr.pdf

     Help me create the training data.

Claude: I'll help you create comprehensive training data! Let me:
        1. Analyze each document
        2. Generate training data
        3. Combine everything
        4. Validate the result
        5. Estimate costs

        [Analyzes all documents]

        📊 Analysis Complete:
        - UCITS: 127 articles, ~200 examples possible
        - AIFMD: 89 articles, ~150 examples possible
        - SFDR: 45 articles, ~100 examples possible

        [Generates training data from each]

        ✅ Generation Complete:
        - ucits_training.jsonl: 215 examples
        - aifmd_training.jsonl: 168 examples
        - sfdr_training.jsonl: 103 examples

        [Combines datasets]

        ✅ Combined: 486 total examples

        [Validates combined file]

        ✅ Validation: All examples valid!

        [Estimates cost]

        💰 Cost Estimate:
        - Training: ~$18 (one-time)
        - Provisioned Throughput: ~$200/month

        ⏱️ Training time: ~4 hours

        📁 Your training data is ready at:
        combined_eu_funds_training.jsonl

        Next steps:
        1. aws s3 cp combined_eu_funds_training.jsonl s3://your-bucket/
        2. Launch fine-tuning in Bedrock
        3. Deploy with Provisioned Throughput

You: Perfect! Now show me some sample questions it will be able to answer.

Claude: [Gets sample questions]

        Your fine-tuned model will be able to answer questions like:

        UCITS:
        - What are the diversification requirements?
        - What is the maximum leverage allowed?
        - What assets are eligible for UCITS investment?

        AIFMD:
        - What are the AUM thresholds for registration?
        - What reporting obligations apply to AIFMs?
        - What is the difference between EU and non-EU AIFMs?

        SFDR:
        - What is the difference between Article 8 and 9 funds?
        - What disclosure requirements apply?
        - What are Principal Adverse Impacts?

        [... and 40+ more examples ...]
```

## 🎯 Advanced Usage

### Custom System Prompts

```
You: Generate training data from /docs/ucits.pdf with a system prompt
     focused on compliance officers.

Claude: [Generates with custom prompt]

        Using system prompt:
        "You are a regulatory compliance officer specializing in EU
        investment funds. You provide practical, actionable guidance..."

        ✅ Generated 187 examples tailored for compliance use cases
```

### Batch Processing

```
You: Generate training data from all PDF files in /docs/regulations/

Claude: I'll process all regulatory documents in that directory.

        Found 5 PDFs:
        1. ucits_directive.pdf
        2. aifmd.pdf
        3. sfdr_regulation.pdf
        4. mifid_ii.pdf
        5. priips_regulation.pdf

        [Processes each file]

        ✅ Generated 5 training files with 847 total examples
        ✅ Combined into master_training.jsonl
        ✅ Validated: All examples valid
```

### Quality Control

```
You: Generate training data from /docs/ucits.pdf and validate it thoroughly.
     Only include specialized examples if they're high quality.

Claude: [Generates and validates]

        📊 Generation:
        - Auto-generated: 143 examples
        - Specialized: 7 expert examples
        - Total: 150 examples

        🔍 Quality Check:
        ✅ All examples valid
        ✅ No formatting errors
        ✅ Proper user/assistant alternation
        ✅ All have system prompts
        ⚠️ 2 examples flagged for manual review (complex multi-turn)

        🎯 Quality Score: 98.7%
```

## 🛠️ Troubleshooting

### MCP Server Not Appearing in Claude

1. **Check configuration:**
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Verify path is absolute:**
   ```json
   "args": ["/Users/yourname/anthropic-cookbook/finetuning/mcp/server.py"]
   // NOT: ["./server.py"] or ["~/cookbook/..."]
   ```

3. **Restart Claude Desktop**

4. **Check logs:**
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\Logs\mcp*.log`

### API Key Issues

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Or set it in the config file
"env": {
  "ANTHROPIC_API_KEY": "sk-ant-..."
}
```

### Python Dependencies Missing

```bash
# Reinstall with all dependencies
pip install -e ".[dev]"

# Or install individually
pip install mcp anthropic PyPDF2
```

### Permission Errors

```bash
# Make server executable
chmod +x server.py

# Check Python can be found
which python
# Use the full path in claude_desktop_config.json
```

## 📖 How It Works

### Architecture

```
Claude Desktop
    ↓
MCP Protocol (stdio)
    ↓
MCP Server (server.py)
    ↓
EUFundsTrainingDataGenerator (generate_eu_funds_training_data.py)
    ↓
Anthropic API (for generation)
    ↓
Training Data (JSONL files)
```

### Tool Execution Flow

1. **User asks Claude** to perform an action
2. **Claude decides** which MCP tool to use
3. **MCP server receives** the tool call
4. **Server executes** the appropriate function
5. **Results returned** to Claude
6. **Claude formats** the response for the user

### Example Tool Call

```python
# User: "Generate training data from ucits.pdf"

# Claude sends:
{
  "tool": "generate_training_data",
  "arguments": {
    "input_path": "/docs/ucits.pdf",
    "output_path": "/docs/ucits_training.jsonl",
    "examples_per_chunk": 15,
    "include_specialized": true
  }
}

# Server executes:
generator.generate_from_document(...)

# Returns:
{
  "content": "✅ Generated 145 examples\n📁 Saved to: ..."
}

# Claude formats and shows user
```

## 🎓 Tips & Best Practices

### 1. Start Small

```
You: Analyze the document first, then generate a small sample

Claude: Good approach! I'll:
        1. Analyze the document
        2. Generate 5 examples per chunk as a test
        3. You can review before generating the full dataset
```

### 2. Iterative Improvement

```
You: Generate initial training data, then let me review before combining

Claude: Smart! I'll generate separate files so you can:
        1. Review each regulation independently
        2. Remove any low-quality examples
        3. Combine only the approved datasets
```

### 3. Use Specialized Examples

```
You: Include the specialized examples - they're high quality

Claude: ✅ Including 7 hand-crafted examples covering core concepts.
        These will boost your training data quality!
```

### 4. Validate Often

```
You: Validate after each generation step

Claude: Good practice! I'll validate:
        ✅ After generating each file
        ✅ After combining datasets
        ✅ Before you upload to S3
```

## 🚀 What's Next?

After generating training data with this MCP:

1. **Upload to S3:**
   ```bash
   aws s3 cp training.jsonl s3://your-bucket/training/
   ```

2. **Fine-tune on Bedrock:**
   See the [main fine-tuning notebook](../finetuning_on_bedrock.ipynb)

3. **Deploy:**
   Set up Provisioned Throughput

4. **Use your fine-tuned model:**
   Query it with regulatory questions!

## 📚 Related Resources

- [Main Fine-tuning Notebook](../finetuning_on_bedrock.ipynb)
- [EU Funds Training Guide](../EU_FUNDS_TRAINING_README.md)
- [Quick Start Guide](../QUICK_START.md)
- [MCP Documentation](https://modelcontextprotocol.io)
- [Anthropic API Docs](https://docs.anthropic.com)
- [AWS Bedrock](https://aws.amazon.com/bedrock/)

## 🤝 Contributing

Found a bug or have a feature request?

- Open an issue on GitHub
- Submit a pull request
- Share your experience!

## 📝 License

MIT License - see parent cookbook repository

## 🙏 Acknowledgments

Built on:
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Anthropic Claude](https://www.anthropic.com)
- [AWS Bedrock](https://aws.amazon.com/bedrock/)

---

**Happy Fine-tuning! 🚀**

Transform your EU regulatory documents into expert AI models with just a conversation!
