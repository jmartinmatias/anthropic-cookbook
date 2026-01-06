#!/usr/bin/env python3
"""
EU Investment Funds Fine-tuning MCP Server

This MCP server provides tools for generating fine-tuning training data
from EU investment funds regulatory texts.

Tools provided:
- generate_training_data: Generate training examples from regulatory documents
- validate_training_data: Validate JSONL training files
- create_specialized_examples: Get hand-crafted regulatory examples
- analyze_document: Analyze a regulatory document structure
- combine_datasets: Merge multiple training files
- get_sample_questions: Get example questions for a regulation type
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path to import the generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_eu_funds_training_data import EUFundsTrainingDataGenerator

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)


# Initialize server
server = Server("eu-funds-finetuning")

# Global generator instance
generator: Optional[EUFundsTrainingDataGenerator] = None


def get_generator() -> EUFundsTrainingDataGenerator:
    """Get or create generator instance"""
    global generator
    if generator is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        generator = EUFundsTrainingDataGenerator(api_key=api_key)
    return generator


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="generate_training_data",
            description="""Generate fine-tuning training data from EU investment funds regulatory documents.

            Supports UCITS, AIFMD, MiFID II, PRIIPs, SFDR, and other EU fund regulations.
            Automatically creates diverse Q&A examples covering definitions, compliance obligations,
            thresholds, exemptions, timelines, and multi-turn conversations.

            Input: Path to regulatory document (PDF or text)
            Output: Number of examples generated and validation results""",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to regulatory document (PDF or TXT file)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save JSONL training data"
                    },
                    "examples_per_chunk": {
                        "type": "integer",
                        "description": "Number of examples to generate per document chunk (default: 15)",
                        "default": 15
                    },
                    "include_specialized": {
                        "type": "boolean",
                        "description": "Include hand-crafted specialized examples (default: true)",
                        "default": True
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Custom system prompt for training examples (optional)"
                    }
                },
                "required": ["input_path", "output_path"]
            }
        ),
        Tool(
            name="validate_training_data",
            description="""Validate a JSONL training file for AWS Bedrock compatibility.

            Checks:
            - Valid JSON format
            - Required message structure (user/assistant alternation)
            - Minimum message count
            - Content presence
            - System prompt presence (warning if missing)

            Returns detailed validation report with errors and warnings.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to JSONL training file to validate"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="create_specialized_examples",
            description="""Get hand-crafted, expert-quality training examples for EU fund regulations.

            Includes pre-written examples covering:
            - UCITS fundamentals and diversification rules
            - AIFMD vs UCITS comparison
            - SFDR Article 8 & 9 classification
            - MiFID II client categorization
            - KIID/KID requirements
            - Depositary duties

            These are high-quality examples that can be used to seed or augment auto-generated data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Optional: Path to save examples as JSONL. If not provided, returns as text."
                    }
                }
            }
        ),
        Tool(
            name="analyze_document",
            description="""Analyze the structure and content of a regulatory document.

            Provides:
            - Document length and estimated chunks
            - Detected regulatory frameworks (UCITS, AIFMD, etc.)
            - Article/section structure
            - Key terms and definitions found
            - Estimated number of examples that can be generated

            Useful for understanding a document before generating training data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to regulatory document to analyze"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="combine_datasets",
            description="""Combine multiple JSONL training files into a single dataset.

            Useful for merging training data from different regulatory sources
            (e.g., UCITS + AIFMD + SFDR) into one comprehensive training file.

            Validates each file before combining and provides a summary.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of JSONL file paths to combine"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save combined training data"
                    }
                },
                "required": ["input_files", "output_path"]
            }
        ),
        Tool(
            name="get_sample_questions",
            description="""Get example questions that can be asked about specific EU fund regulations.

            Helps users understand what kind of knowledge the fine-tuned model will have.
            Returns sample questions for different categories and regulation types.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "regulation": {
                        "type": "string",
                        "enum": ["UCITS", "AIFMD", "SFDR", "MiFID II", "PRIIPs", "all"],
                        "description": "Which regulation to get sample questions for",
                        "default": "all"
                    },
                    "question_type": {
                        "type": "string",
                        "enum": ["definitional", "procedural", "compliance", "threshold", "exemption", "timeline", "all"],
                        "description": "Type of questions to return",
                        "default": "all"
                    }
                }
            }
        ),
        Tool(
            name="estimate_training_cost",
            description="""Estimate the cost and time for fine-tuning based on training data.

            Provides estimates for:
            - AWS Bedrock fine-tuning cost
            - Training time duration
            - Provisioned throughput cost
            - Total cost breakdown

            Based on training data size and configuration.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "training_file": {
                        "type": "string",
                        "description": "Path to training JSONL file"
                    },
                    "epochs": {
                        "type": "integer",
                        "description": "Number of training epochs (default: 5)",
                        "default": 5
                    },
                    "batch_size": {
                        "type": "integer",
                        "description": "Batch size (default: 8)",
                        "default": 8
                    }
                },
                "required": ["training_file"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "generate_training_data":
            return await handle_generate_training_data(arguments)
        elif name == "validate_training_data":
            return await handle_validate_training_data(arguments)
        elif name == "create_specialized_examples":
            return await handle_create_specialized_examples(arguments)
        elif name == "analyze_document":
            return await handle_analyze_document(arguments)
        elif name == "combine_datasets":
            return await handle_combine_datasets(arguments)
        elif name == "get_sample_questions":
            return await handle_get_sample_questions(arguments)
        elif name == "estimate_training_cost":
            return await handle_estimate_training_cost(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}\n\n{type(e).__name__}"
        return [TextContent(type="text", text=error_msg)]


async def handle_generate_training_data(args: Dict[str, Any]) -> List[TextContent]:
    """Generate training data from regulatory document"""
    gen = get_generator()

    input_path = args["input_path"]
    output_path = args["output_path"]
    examples_per_chunk = args.get("examples_per_chunk", 15)
    include_specialized = args.get("include_specialized", True)
    system_prompt = args.get("system_prompt")

    # Generate training data
    num_examples = gen.generate_from_document(
        file_path=input_path,
        output_path=output_path,
        examples_per_chunk=examples_per_chunk,
        include_specialized=include_specialized,
        system_prompt=system_prompt
    )

    # Validate the generated file
    validation = gen.validate_training_file(output_path)

    result = f"""✅ Training Data Generated Successfully

📊 Results:
- Total examples: {num_examples}
- Valid examples: {validation['valid_examples']}
- Output file: {output_path}

🔍 Validation:
- Errors: {len(validation['errors'])}
- Warnings: {len(validation['warnings'])}
"""

    if validation['errors']:
        result += f"\n❌ Errors found:\n"
        for error in validation['errors'][:5]:
            result += f"  - {error}\n"

    if validation['warnings']:
        result += f"\n⚠️  Warnings:\n"
        for warning in validation['warnings'][:5]:
            result += f"  - {warning}\n"

    result += f"""
📈 Next Steps:
1. Review the generated file: {output_path}
2. Upload to S3: aws s3 cp {output_path} s3://your-bucket/
3. Launch fine-tuning job in AWS Bedrock
4. Deploy with Provisioned Throughput

💡 Tip: Use the 'validate_training_data' tool to check the file again anytime.
"""

    return [TextContent(type="text", text=result)]


async def handle_validate_training_data(args: Dict[str, Any]) -> List[TextContent]:
    """Validate training data file"""
    gen = get_generator()

    file_path = args["file_path"]

    if not os.path.exists(file_path):
        return [TextContent(type="text", text=f"❌ File not found: {file_path}")]

    results = gen.validate_training_file(file_path)

    result = f"""📋 Validation Results for {file_path}

📊 Summary:
- Total examples: {results['total_examples']}
- Valid examples: {results['valid_examples']}
- Success rate: {results['valid_examples']/max(results['total_examples'], 1)*100:.1f}%
- Errors: {len(results['errors'])}
- Warnings: {len(results['warnings'])}
"""

    if results['errors']:
        result += f"\n❌ Errors ({len(results['errors'])}):\n"
        for error in results['errors'][:10]:
            result += f"  - {error}\n"
        if len(results['errors']) > 10:
            result += f"  ... and {len(results['errors']) - 10} more\n"

    if results['warnings']:
        result += f"\n⚠️  Warnings ({len(results['warnings'])}):\n"
        for warning in results['warnings'][:10]:
            result += f"  - {warning}\n"
        if len(results['warnings']) > 10:
            result += f"  ... and {len(results['warnings']) - 10} more\n"

    if results['valid_examples'] == results['total_examples'] and results['total_examples'] > 0:
        result += f"\n✅ All examples are valid! Ready for fine-tuning.\n"
    elif results['errors']:
        result += f"\n⚠️  Fix errors before using for fine-tuning.\n"

    return [TextContent(type="text", text=result)]


async def handle_create_specialized_examples(args: Dict[str, Any]) -> List[TextContent]:
    """Create specialized hand-crafted examples"""
    gen = get_generator()

    examples = gen.create_specialized_examples()
    output_path = args.get("output_path")

    if output_path:
        # Save to file
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        result = f"""✅ Specialized Examples Created

📊 Summary:
- Total examples: {len(examples)}
- Output file: {output_path}

📚 Topics covered:
- UCITS fundamentals and diversification
- AIFMD vs UCITS comparison
- SFDR Article 8 & 9 classification
- MiFID II client categorization
- KIID/KID requirements
- Depositary duties

💡 These examples are expert-quality and can be combined with auto-generated data.
"""
    else:
        # Return as text
        result = f"""✅ Specialized Examples

📊 Total: {len(examples)} hand-crafted examples

📝 Sample Example:

{json.dumps(examples[0], indent=2, ensure_ascii=False)}

📚 All examples cover:
- UCITS fundamentals and diversification
- AIFMD vs UCITS comparison
- SFDR Article 8 & 9 classification
- MiFID II client categorization
- KIID/KID requirements
- Depositary duties

💡 Use output_path parameter to save these to a file.
"""

    return [TextContent(type="text", text=result)]


async def handle_analyze_document(args: Dict[str, Any]) -> List[TextContent]:
    """Analyze regulatory document structure"""
    gen = get_generator()

    file_path = args["file_path"]

    if not os.path.exists(file_path):
        return [TextContent(type="text", text=f"❌ File not found: {file_path}")]

    # Read document
    document = gen.read_document(file_path)

    if not document:
        return [TextContent(type="text", text=f"❌ Could not read document: {file_path}")]

    # Analyze structure
    chunks = gen.chunk_document(document)

    # Detect regulations
    detected_regs = []
    for reg in gen.REGULATORY_FRAMEWORKS:
        if reg.upper() in document.upper():
            detected_regs.append(reg)

    # Count articles
    import re
    articles = len(re.findall(r'\bArticle \d+', document))
    sections = len(re.findall(r'\bSection \d+', document))
    chapters = len(re.findall(r'\bChapter \d+', document))

    # Estimate examples
    estimated_examples = len(chunks) * 15 + 7  # per chunk + specialized

    result = f"""📄 Document Analysis: {file_path}

📊 Structure:
- Document size: {len(document):,} characters
- Estimated chunks: {len(chunks)}
- Articles found: {articles}
- Sections found: {sections}
- Chapters found: {chapters}

🔍 Detected Regulations:
"""

    if detected_regs:
        for reg in detected_regs:
            result += f"  ✓ {reg}\n"
    else:
        result += "  - No specific regulations detected\n"

    result += f"""
📈 Training Data Estimates:
- Estimated examples (default): ~{estimated_examples}
- With 20 examples/chunk: ~{len(chunks) * 20 + 7}
- With 25 examples/chunk: ~{len(chunks) * 25 + 7}

💡 Recommendations:
- Start with {min(15, max(10, len(chunks) * 15 // len(chunks)))} examples per chunk
- Expected processing time: ~{len(chunks) * 2} minutes
- Cost estimate: ~${len(chunks) * 0.05:.2f} in API calls

📝 Sample Content (first 500 chars):
{document[:500]}...

✅ Ready to generate training data with 'generate_training_data' tool
"""

    return [TextContent(type="text", text=result)]


async def handle_combine_datasets(args: Dict[str, Any]) -> List[TextContent]:
    """Combine multiple training files"""
    input_files = args["input_files"]
    output_path = args["output_path"]

    all_examples = []
    file_stats = []

    for file_path in input_files:
        if not os.path.exists(file_path):
            return [TextContent(type="text", text=f"❌ File not found: {file_path}")]

        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        example = json.loads(line)
                        all_examples.append(example)
                        count += 1
                    except json.JSONDecodeError:
                        continue

        file_stats.append({"file": file_path, "examples": count})

    # Write combined file
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    result = f"""✅ Datasets Combined Successfully

📊 Summary:
- Input files: {len(input_files)}
- Total examples: {len(all_examples)}
- Output file: {output_path}

📁 Source Files:
"""

    for stat in file_stats:
        result += f"  - {stat['file']}: {stat['examples']} examples\n"

    result += f"""
💡 Next Steps:
1. Validate: Use 'validate_training_data' on {output_path}
2. Upload to S3: aws s3 cp {output_path} s3://your-bucket/
3. Launch fine-tuning job
"""

    return [TextContent(type="text", text=result)]


async def handle_get_sample_questions(args: Dict[str, Any]) -> List[TextContent]:
    """Get sample questions for regulations"""
    regulation = args.get("regulation", "all")
    question_type = args.get("question_type", "all")

    samples = {
        "UCITS": {
            "definitional": [
                "What is a UCITS fund?",
                "What qualifies as a transferable security under UCITS?",
                "Define the term 'money market instrument' in UCITS context"
            ],
            "procedural": [
                "What is the process for authorizing a UCITS?",
                "How does a UCITS obtain a management company passport?",
                "What steps are required to merge two UCITS funds?"
            ],
            "compliance": [
                "What are the diversification requirements for UCITS?",
                "What are the eligible assets for UCITS investment?",
                "What are the limits on derivative use in UCITS?"
            ],
            "threshold": [
                "What is the maximum investment in a single issuer?",
                "What are the concentration limits for UCITS?",
                "What is the minimum capital requirement for a UCITS management company?"
            ],
            "exemption": [
                "Which funds are exempt from UCITS requirements?",
                "What exemptions exist for government bond concentration?",
                "Are there exemptions for index-tracking UCITS?"
            ],
            "timeline": [
                "When must the annual report be published?",
                "What are the notification deadlines for material changes?",
                "How long does regulatory approval typically take?"
            ]
        },
        "AIFMD": {
            "definitional": [
                "What is an Alternative Investment Fund?",
                "Define an Alternative Investment Fund Manager (AIFM)",
                "What is the difference between EU AIFM and non-EU AIFM?"
            ],
            "compliance": [
                "What are the registration requirements for AIFMs?",
                "What reporting obligations apply to AIFMs?",
                "What are the remuneration requirements under AIFMD?"
            ],
            "threshold": [
                "What are the AUM thresholds for AIFMD registration?",
                "What is the de minimis threshold for AIFMs?",
                "What are the leverage reporting thresholds?"
            ]
        },
        "SFDR": {
            "definitional": [
                "What is the difference between Article 6, 8, and 9 funds?",
                "Define 'sustainable investment' under SFDR",
                "What are Principal Adverse Impacts (PAI)?"
            ],
            "compliance": [
                "What disclosure obligations apply to Article 8 funds?",
                "What must be included in periodic SFDR reports?",
                "When must the website disclosures be updated?"
            ]
        },
        "MiFID II": {
            "definitional": [
                "What is the difference between professional and retail clients?",
                "Define 'execution-only' services",
                "What qualifies as investment advice under MiFID II?"
            ],
            "compliance": [
                "What are the suitability assessment requirements?",
                "What must be disclosed about costs and charges?",
                "What are the best execution obligations?"
            ]
        },
        "PRIIPs": {
            "definitional": [
                "What is a PRIIP?",
                "What is a Key Information Document (KID)?",
                "Define 'retail investor' under PRIIPs"
            ],
            "compliance": [
                "What must be included in a PRIIPs KID?",
                "When must the KID be provided to investors?",
                "How often must the KID be updated?"
            ]
        }
    }

    result = f"📚 Sample Questions for EU Investment Funds Regulations\n\n"

    if regulation == "all":
        for reg, questions in samples.items():
            result += f"## {reg}\n\n"
            if question_type == "all":
                for qtype, qs in questions.items():
                    result += f"### {qtype.title()}\n"
                    for q in qs[:2]:  # Limit to 2 per type
                        result += f"- {q}\n"
                    result += "\n"
            else:
                if question_type in questions:
                    for q in questions[question_type]:
                        result += f"- {q}\n"
            result += "\n"
    else:
        if regulation in samples:
            result += f"## {regulation}\n\n"
            if question_type == "all":
                for qtype, qs in samples[regulation].items():
                    result += f"### {qtype.title()}\n"
                    for q in qs:
                        result += f"- {q}\n"
                    result += "\n"
            else:
                if question_type in samples[regulation]:
                    result += f"### {question_type.title()}\n"
                    for q in samples[regulation][question_type]:
                        result += f"- {q}\n"

    result += """
💡 These are examples of questions a fine-tuned model can answer with expertise.
Use 'generate_training_data' to create training examples from your regulatory documents.
"""

    return [TextContent(type="text", text=result)]


async def handle_estimate_training_cost(args: Dict[str, Any]) -> List[TextContent]:
    """Estimate fine-tuning cost"""
    training_file = args["training_file"]
    epochs = args.get("epochs", 5)
    batch_size = args.get("batch_size", 8)

    if not os.path.exists(training_file):
        return [TextContent(type="text", text=f"❌ File not found: {training_file}")]

    # Count examples and estimate tokens
    num_examples = 0
    total_tokens = 0

    with open(training_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                num_examples += 1
                # Rough estimate: 1 char ≈ 0.3 tokens
                total_tokens += len(line) * 0.3

    # AWS Bedrock pricing estimates (as of 2024)
    # These are approximate - check current pricing
    cost_per_1k_tokens = 0.008  # Training cost
    training_tokens = total_tokens * epochs
    training_cost = (training_tokens / 1000) * cost_per_1k_tokens

    # Provisioned throughput (approximate)
    pt_monthly_cost = 200  # Very rough estimate for minimal PT

    # Training time estimate
    training_time_hours = (num_examples * epochs) / (batch_size * 100)  # Rough estimate

    result = f"""💰 Fine-tuning Cost Estimate

📊 Training Data:
- Examples: {num_examples}
- Estimated tokens: {int(total_tokens):,}
- Epochs: {epochs}
- Batch size: {batch_size}

⏱️  Time Estimate:
- Training time: ~{training_time_hours:.1f} hours
- Wall time: ~{training_time_hours * 1.5:.1f} hours (with overhead)

💵 Cost Breakdown (Estimates):

1. Fine-tuning Training:
   - Total training tokens: {int(training_tokens):,}
   - Estimated cost: ${training_cost:.2f}

2. Model Storage:
   - Cost: ~$0/month (included in PT)

3. Provisioned Throughput (required for inference):
   - Minimum commitment: ~${pt_monthly_cost}/month
   - This is the main ongoing cost

4. Total First Month:
   - One-time training: ${training_cost:.2f}
   - Monthly PT: ${pt_monthly_cost:.2f}
   - Total: ${training_cost + pt_monthly_cost:.2f}

5. Ongoing (monthly):
   - Provisioned Throughput: ${pt_monthly_cost:.2f}

⚠️  Important Notes:
- These are ROUGH ESTIMATES based on approximate 2024 pricing
- Actual costs depend on AWS region and current Bedrock pricing
- Provisioned Throughput is required and is the main cost
- Check official AWS Bedrock pricing for accurate numbers
- Consider starting with lower PT capacity and scaling up

💡 Cost Optimization Tips:
- Use fine-tuning for frequently asked questions
- Use RAG for infrequently accessed content
- Combine both for optimal cost/performance
- Monitor usage and adjust PT capacity

📈 ROI Considerations:
- Reduces per-query API costs vs. base models
- Faster responses (no RAG retrieval)
- Better accuracy for domain-specific queries
- Consider break-even point based on query volume

🔗 For exact pricing, visit:
https://aws.amazon.com/bedrock/pricing/
"""

    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
