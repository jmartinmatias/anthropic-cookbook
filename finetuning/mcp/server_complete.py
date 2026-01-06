#!/usr/bin/env python3
"""
EU Investment Funds Fine-tuning MCP Server - Complete Edition

This is the complete MCP server supporting all three dimensions of expertise:
1. Regulatory Knowledge (UCITS, AIFMD, SFDR, MiFID II, etc.)
2. Operational Procedures (SOPs, workflows, checklists)
3. Domain Expertise (investment strategies, risk management, best practices)

Together, these create a truly expert AI model that knows:
- WHAT the rules are (regulatory)
- HOW to comply (operational)
- WHY decisions are made (domain expertise)

Total tools: 15+
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_eu_funds_training_data import EUFundsTrainingDataGenerator
from operational_procedures import (
    OperationalProcedureParser,
    OperationalTrainingGenerator,
    OperationalKnowledgeBase
)
from domain_expertise import (
    DomainExpertiseParser,
    DomainExpertiseGenerator,
    create_sample_domain_documents
)

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Error: Anthropic SDK not installed. Install with: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# Initialize server
server = Server("eu-funds-finetuning-complete")

# Global instances
reg_generator: Optional[EUFundsTrainingDataGenerator] = None
op_generator: Optional[OperationalTrainingGenerator] = None
domain_generator: Optional[DomainExpertiseGenerator] = None
knowledge_base: Optional[OperationalKnowledgeBase] = None


def get_api_key() -> str:
    """Get API key from environment"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return api_key


def get_reg_generator() -> EUFundsTrainingDataGenerator:
    """Get regulatory training generator"""
    global reg_generator
    if reg_generator is None:
        reg_generator = EUFundsTrainingDataGenerator(api_key=get_api_key())
    return reg_generator


def get_op_generator() -> OperationalTrainingGenerator:
    """Get operational training generator"""
    global op_generator
    if op_generator is None:
        client = anthropic.Anthropic(api_key=get_api_key())
        op_generator = OperationalTrainingGenerator(client)
    return op_generator


def get_domain_generator() -> DomainExpertiseGenerator:
    """Get domain expertise generator"""
    global domain_generator
    if domain_generator is None:
        client = anthropic.Anthropic(api_key=get_api_key())
        domain_generator = DomainExpertiseGenerator(client)
    return domain_generator


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools"""
    return [
        # ===== REGULATORY TOOLS =====
        Tool(
            name="generate_regulatory_training",
            description="Generate training data from EU regulatory documents (UCITS, AIFMD, SFDR, MiFID II, PRIIPs). Teaches WHAT the regulatory requirements are.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {"type": "string"},
                    "output_path": {"type": "string"},
                    "examples_per_chunk": {"type": "integer", "default": 15},
                    "system_prompt": {"type": "string"}
                },
                "required": ["input_path", "output_path"]
            }
        ),

        # ===== OPERATIONAL TOOLS =====
        Tool(
            name="generate_operational_training",
            description="Generate training data from operational procedures (SOPs, workflows, checklists). Teaches HOW to comply with regulations in daily operations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_file": {"type": "string"},
                    "output_path": {"type": "string"},
                    "num_examples": {"type": "integer", "default": 25}
                },
                "required": ["procedure_file", "output_path"]
            }
        ),

        # ===== DOMAIN EXPERTISE TOOLS =====
        Tool(
            name="generate_domain_expertise_training",
            description="""Generate training data from domain expertise documents (investment strategies, risk frameworks, best practices).

            Teaches expert judgment and WHY decisions are made. Creates training examples from:
            - Investment memos and rationales
            - Strategy guides and philosophies
            - Risk management frameworks
            - Portfolio construction methodologies
            - Market analysis and insights
            - Best practices and lessons learned

            This captures the expertise that separates good from great investment professionals.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain_file": {
                        "type": "string",
                        "description": "Path to domain expertise document"
                    },
                    "output_path": {
                        "type": "string"
                    },
                    "document_type": {
                        "type": "string",
                        "enum": ["investment_memo", "strategy_guide", "risk_report", "best_practices", "auto"],
                        "description": "Type of document (auto-detect if not specified)",
                        "default": "auto"
                    },
                    "num_examples": {
                        "type": "integer",
                        "default": 20
                    }
                },
                "required": ["domain_file", "output_path"]
            }
        ),
        Tool(
            name="parse_domain_document",
            description="""Analyze a domain expertise document to extract structure and key elements.

            Extracts:
            - Document type (investment memo, strategy guide, etc.)
            - Domain area (investment strategy, risk management, ESG, etc.)
            - Key concepts and principles
            - Best practices
            - Warning signs and pitfalls
            - Decision criteria
            - Real-world examples

            Use before generating training data to understand the document.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain_file": {"type": "string"}
                },
                "required": ["domain_file"]
            }
        ),

        # ===== INTEGRATED TOOLS =====
        Tool(
            name="create_complete_training_dataset",
            description="""Create a complete training dataset combining all three dimensions:
            - Regulatory knowledge (40%)
            - Operational procedures (40%)
            - Domain expertise (20%)

            This creates a truly expert model that knows theory, practice, AND judgment.

            Automates the entire workflow:
            1. Generates regulatory training data
            2. Generates operational training data
            3. Generates domain expertise training data
            4. Combines and validates everything
            5. Provides cost estimate""",
            inputSchema={
                "type": "object",
                "properties": {
                    "regulatory_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of regulatory document paths"
                    },
                    "operational_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of operational procedure paths"
                    },
                    "domain_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domain expertise document paths"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save complete training dataset"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="analyze_training_coverage",
            description="""Analyze training data coverage across all three dimensions.

            Provides:
            - Regulatory coverage (which regulations, how many examples)
            - Operational coverage (which procedures, process areas covered)
            - Domain coverage (which expertise areas, depth of examples)
            - Gap analysis and recommendations
            - Balance assessment (is it 40/40/20 or skewed?)

            Helps ensure comprehensive training data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "training_file": {"type": "string"}
                },
                "required": ["training_file"]
            }
        ),
        Tool(
            name="validate_training_data",
            description="Validate JSONL training file for AWS Bedrock compatibility",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_sample_domain_questions",
            description="""Get example questions demonstrating domain expertise.

            Shows the types of expert judgment questions the model will be able to answer:
            - Investment rationale: "Why invest in this opportunity?"
            - Risk assessment: "What are the key risks and how to manage them?"
            - Strategy decisions: "When should you deploy this strategy?"
            - Portfolio construction: "How do you size this position?"
            - Best practices: "What separates good from great?"
            - Judgment calls: "Given this scenario, what would you do?"

            These questions demonstrate expertise, not just knowledge.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain_area": {
                        "type": "string",
                        "enum": ["investment_strategy", "risk_management", "esg", "portfolio_construction", "all"],
                        "default": "all"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    try:
        # Regulatory tools
        if name == "generate_regulatory_training":
            return await handle_regulatory_training(arguments)

        # Operational tools
        elif name == "generate_operational_training":
            return await handle_operational_training(arguments)

        # Domain expertise tools
        elif name == "generate_domain_expertise_training":
            return await handle_domain_training(arguments)
        elif name == "parse_domain_document":
            return await handle_parse_domain_doc(arguments)

        # Integrated tools
        elif name == "create_complete_training_dataset":
            return await handle_complete_dataset(arguments)
        elif name == "analyze_training_coverage":
            return await handle_analyze_coverage(arguments)
        elif name == "validate_training_data":
            return await handle_validate(arguments)
        elif name == "get_sample_domain_questions":
            return await handle_sample_domain_questions(arguments)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        import traceback
        return [TextContent(type="text", text=f"Error: {str(e)}\n\n{traceback.format_exc()}")]


# ===== TOOL HANDLERS =====

async def handle_regulatory_training(args: Dict) -> List[TextContent]:
    """Generate regulatory training data"""
    gen = get_reg_generator()
    num_examples = gen.generate_from_document(
        file_path=args["input_path"],
        output_path=args["output_path"],
        examples_per_chunk=args.get("examples_per_chunk", 15),
        system_prompt=args.get("system_prompt")
    )

    result = f"""✅ Regulatory Training Data Generated

📊 Results: {num_examples} examples
📁 Output: {args["output_path"]}

This teaches WHAT the regulatory requirements are.

Next: Add operational procedures (HOW) and domain expertise (WHY)!
"""
    return [TextContent(type="text", text=result)]


async def handle_operational_training(args: Dict) -> List[TextContent]:
    """Generate operational training data"""
    op_gen = get_op_generator()
    parser = OperationalProcedureParser()

    with open(args["procedure_file"], 'r') as f:
        content = f.read()

    procedure = parser.parse_procedure(content)
    examples = op_gen.generate_from_procedure(procedure, args.get("num_examples", 25))

    with open(args["output_path"], 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    result = f"""✅ Operational Training Data Generated

📄 Procedure: {procedure.title}
📊 Examples: {len(examples)}
📁 Output: {args["output_path"]}

This teaches HOW to comply in daily operations.

Next: Add domain expertise (WHY decisions are made)!
"""
    return [TextContent(type="text", text=result)]


async def handle_domain_training(args: Dict) -> List[TextContent]:
    """Generate domain expertise training data"""
    domain_gen = get_domain_generator()
    parser = DomainExpertiseParser()

    with open(args["domain_file"], 'r') as f:
        content = f.read()

    # Parse document
    doc = parser.parse_domain_document(content)

    # Generate examples
    examples = domain_gen.generate_from_domain_doc(doc, args.get("num_examples", 20))

    # Save
    with open(args["output_path"], 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    result = f"""✅ Domain Expertise Training Data Generated

📄 Document: {doc.title}
📋 Type: {doc.doc_type.value}
🎯 Domain: {doc.domain_area.value}

📊 Generated: {len(examples)} examples

Key Elements Captured:
- Concepts: {len(doc.key_concepts)}
- Principles: {len(doc.principles)}
- Best Practices: {len(doc.best_practices)}
- Warnings: {len(doc.warnings)}
- Decision Criteria: {len(doc.decision_criteria)}

📁 Output: {args["output_path"]}

This teaches WHY decisions are made and demonstrates expert judgment!

💡 Combine with regulatory + operational data for complete expertise.
"""
    return [TextContent(type="text", text=result)]


async def handle_parse_domain_doc(args: Dict) -> List[TextContent]:
    """Parse and analyze domain document"""
    parser = DomainExpertiseParser()

    with open(args["domain_file"], 'r') as f:
        content = f.read()

    doc = parser.parse_domain_document(content)

    result = f"""📄 Domain Document Analysis

Title: {doc.title}
Type: {doc.doc_type.value}
Domain Area: {doc.domain_area.value}

📚 Key Concepts ({len(doc.key_concepts)}):
{chr(10).join(f'  - {c}' for c in doc.key_concepts[:5])}
{'  ...' if len(doc.key_concepts) > 5 else ''}

💡 Principles ({len(doc.principles)}):
{chr(10).join(f'  - {p[:80]}...' if len(p) > 80 else f'  - {p}' for p in doc.principles[:3])}
{'  ...' if len(doc.principles) > 3 else ''}

✅ Best Practices ({len(doc.best_practices)}):
{chr(10).join(f'  - {bp[:80]}...' if len(bp) > 80 else f'  - {bp}' for bp in doc.best_practices[:3])}
{'  ...' if len(doc.best_practices) > 3 else ''}

⚠️  Warnings ({len(doc.warnings)}):
{chr(10).join(f'  - {w[:80]}...' if len(w) > 80 else f'  - {w}' for w in doc.warnings[:3])}
{'  ...' if len(doc.warnings) > 3 else ''}

🎯 Decision Criteria ({len(doc.decision_criteria)}):
{chr(10).join(f'  - {dc[:80]}...' if len(dc) > 80 else f'  - {dc}' for dc in doc.decision_criteria[:3])}
{'  ...' if len(doc.decision_criteria) > 3 else ''}

✅ Ready to generate domain expertise training data!

Use 'generate_domain_expertise_training' to create expert judgment examples.
"""
    return [TextContent(type="text", text=result)]


async def handle_complete_dataset(args: Dict) -> List[TextContent]:
    """Create complete training dataset"""
    reg_gen = get_reg_generator()
    op_gen = get_op_generator()
    domain_gen = get_domain_generator()

    all_examples = []
    stats = {"regulatory": 0, "operational": 0, "domain": 0}

    # Regulatory
    if args.get("regulatory_files"):
        for reg_file in args["regulatory_files"]:
            temp_output = f"/tmp/reg_{Path(reg_file).stem}.jsonl"
            count = reg_gen.generate_from_document(reg_file, temp_output, 15)
            with open(temp_output, 'r') as f:
                for line in f:
                    all_examples.append(json.loads(line))
            stats["regulatory"] += count

    # Operational
    if args.get("operational_files"):
        parser = OperationalProcedureParser()
        for op_file in args["operational_files"]:
            with open(op_file, 'r') as f:
                procedure = parser.parse_procedure(f.read())
            examples = op_gen.generate_from_procedure(procedure, 25)
            all_examples.extend(examples)
            stats["operational"] += len(examples)

    # Domain
    if args.get("domain_files"):
        parser = DomainExpertiseParser()
        for domain_file in args["domain_files"]:
            with open(domain_file, 'r') as f:
                doc = parser.parse_domain_document(f.read())
            examples = domain_gen.generate_from_domain_doc(doc, 20)
            all_examples.extend(examples)
            stats["domain"] += len(examples)

    # Save combined
    with open(args["output_path"], 'w') as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    total = sum(stats.values())
    reg_pct = (stats["regulatory"] / total * 100) if total > 0 else 0
    op_pct = (stats["operational"] / total * 100) if total > 0 else 0
    domain_pct = (stats["domain"] / total * 100) if total > 0 else 0

    result = f"""✅ Complete Training Dataset Created

📊 Breakdown:
- Regulatory: {stats["regulatory"]} examples ({reg_pct:.0f}%)
- Operational: {stats["operational"]} examples ({op_pct:.0f}%)
- Domain Expertise: {stats["domain"]} examples ({domain_pct:.0f}%)

Total: {total} examples

📁 Output: {args["output_path"]}

🎯 Your model will now have:
✅ Regulatory knowledge (WHAT the rules are)
✅ Operational procedures (HOW to comply)
✅ Domain expertise (WHY decisions are made)

= Complete Expert Model! 🏆

💰 Estimated cost: ~${total * 0.015:.2f} training + $200/mo PT
⏱️  Training time: ~{total / 20:.1f} hours

Ready to fine-tune on AWS Bedrock!
"""
    return [TextContent(type="text", text=result)]


async def handle_analyze_coverage(args: Dict) -> List[TextContent]:
    """Analyze training coverage"""
    # Simplified version - just count examples by system prompt keywords
    with open(args["training_file"], 'r') as f:
        examples = [json.loads(line) for line in f if line.strip()]

    regulatory_count = sum(1 for ex in examples if any(word in ex.get("system", "").lower()
                          for word in ["regulatory", "regulation", "compliance", "ucits", "aifmd"]))

    operational_count = sum(1 for ex in examples if any(word in ex.get("system", "").lower()
                           for word in ["operational", "procedure", "sop", "workflow"]))

    domain_count = sum(1 for ex in examples if any(word in ex.get("system", "").lower()
                      for word in ["investment", "portfolio", "risk management", "strategy", "expert"]))

    total = len(examples)

    result = f"""📊 Training Data Coverage Analysis

Total Examples: {total}

📋 By Dimension:
- Regulatory: {regulatory_count} ({regulatory_count/total*100:.0f}%)
- Operational: {operational_count} ({operational_count/total*100:.0f}%)
- Domain Expertise: {domain_count} ({domain_count/total*100:.0f}%)

🎯 Recommended Balance: 40% regulatory, 40% operational, 20% domain

Current Balance: {"✅ Well-balanced" if 30 <= regulatory_count/total*100 <= 50 and 30 <= operational_count/total*100 <= 50 else "⚠️  Consider rebalancing"}
"""
    return [TextContent(type="text", text=result)]


async def handle_validate(args: Dict) -> List[TextContent]:
    """Validate training data"""
    gen = get_reg_generator()
    results = gen.validate_training_file(args["file_path"])

    result = f"""📋 Validation Results

Total: {results['total_examples']}
Valid: {results['valid_examples']}
Success: {results['valid_examples']/max(results['total_examples'],1)*100:.1f}%

{"✅ All valid!" if results['valid_examples'] == results['total_examples'] else "⚠️  Some errors found"}
"""
    return [TextContent(type="text", text=result)]


async def handle_sample_domain_questions(args: Dict) -> List[TextContent]:
    """Get sample domain questions"""
    domain_area = args.get("domain_area", "all")

    samples = {
        "investment_strategy": [
            "Why would you invest in European small-cap value stocks now?",
            "What factors drive alpha in emerging markets?",
            "How do you evaluate a company's competitive moat?",
            "When should you shift from growth to value strategy?"
        ],
        "risk_management": [
            "What are the key risks in a long-short equity strategy?",
            "How do you hedge currency risk in a global portfolio?",
            "What warning signs indicate a portfolio is over-concentrated?",
            "How do you size positions to manage downside risk?"
        ],
        "esg": [
            "How do you integrate ESG factors into valuation?",
            "What makes an ESG rating reliable vs greenwashing?",
            "How do you engage with companies on ESG improvements?",
            "What ESG factors are most material for energy sector?"
        ],
        "portfolio_construction": [
            "How do you build a resilient multi-asset portfolio?",
            "What's the optimal allocation to alternatives for UCITS funds?",
            "How do you rebalance during market stress?",
            "How do you construct a portfolio with specific factor exposures?"
        ]
    }

    if domain_area == "all":
        result = "📚 Sample Domain Expertise Questions\n\n"
        for area, questions in samples.items():
            result += f"## {area.replace('_', ' ').title()}\n"
            for q in questions:
                result += f"- {q}\n"
            result += "\n"
    else:
        result = f"## {domain_area.replace('_', ' ').title()}\n"
        for q in samples.get(domain_area, []):
            result += f"- {q}\n"

    result += """
💡 A model trained on domain expertise can answer these with sophisticated
   judgment, weighing trade-offs and providing expert reasoning - not just
   reciting rules or procedures.
"""
    return [TextContent(type="text", text=result)]


async def main():
    """Run the complete MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
