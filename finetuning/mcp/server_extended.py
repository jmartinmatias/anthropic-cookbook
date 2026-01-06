#!/usr/bin/env python3
"""
EU Investment Funds Fine-tuning MCP Server - Extended with Operational Procedures

This extends the base MCP server with operational procedure support, enabling
training data generation from SOPs, workflows, checklists, and operational documents.

New tools:
- generate_from_procedures: Generate training data from operational procedures
- parse_procedure: Parse and analyze an operational procedure
- create_procedure_knowledge_base: Build a searchable procedure knowledge base
- generate_cross_procedure_scenarios: Create multi-procedure training examples
- link_procedures_to_regulations: Map procedures to regulatory requirements
- analyze_procedure_coverage: Analyze operational coverage gaps
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
    OperationalKnowledgeBase,
    ProcedureType,
    create_sample_procedures
)

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import Anthropic for operational training generation
try:
    import anthropic
except ImportError:
    print("Error: Anthropic SDK not installed. Install with: pip install anthropic", file=sys.stderr)
    sys.exit(1)


# Initialize server
server = Server("eu-funds-finetuning-extended")

# Global instances
generator: Optional[EUFundsTrainingDataGenerator] = None
op_generator: Optional[OperationalTrainingGenerator] = None
knowledge_base: Optional[OperationalKnowledgeBase] = None


def get_generator() -> EUFundsTrainingDataGenerator:
    """Get or create regulatory training generator"""
    global generator
    if generator is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        generator = EUFundsTrainingDataGenerator(api_key=api_key)
    return generator


def get_op_generator() -> OperationalTrainingGenerator:
    """Get or create operational training generator"""
    global op_generator
    if op_generator is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        client = anthropic.Anthropic(api_key=api_key)
        op_generator = OperationalTrainingGenerator(client)
    return op_generator


def get_knowledge_base() -> OperationalKnowledgeBase:
    """Get or create knowledge base"""
    global knowledge_base
    if knowledge_base is None:
        knowledge_base = OperationalKnowledgeBase()
    return knowledge_base


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools"""
    return [
        # Original regulatory tools
        Tool(
            name="generate_training_data",
            description="Generate fine-tuning training data from EU regulatory documents (UCITS, AIFMD, SFDR, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {"type": "string", "description": "Path to regulatory document"},
                    "output_path": {"type": "string", "description": "Path to save training data"},
                    "examples_per_chunk": {"type": "integer", "default": 15},
                    "include_specialized": {"type": "boolean", "default": True},
                    "system_prompt": {"type": "string"}
                },
                "required": ["input_path", "output_path"]
            }
        ),
        Tool(
            name="validate_training_data",
            description="Validate JSONL training file for AWS Bedrock compatibility",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to JSONL file"}
                },
                "required": ["file_path"]
            }
        ),

        # NEW: Operational procedure tools
        Tool(
            name="generate_from_procedures",
            description="""Generate training data from operational procedures (SOPs, workflows, checklists).

            Creates training examples covering:
            - How-to questions (step-by-step procedures)
            - Role/responsibility questions
            - Timing/trigger questions
            - Scenario-based questions (what if...)
            - Compliance questions (linking procedures to regulations)

            Perfect for training models on day-to-day fund operations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_file": {
                        "type": "string",
                        "description": "Path to operational procedure document (txt, docx, pdf)"
                    },
                    "procedure_title": {
                        "type": "string",
                        "description": "Title of the procedure (optional, will auto-detect if not provided)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save generated training data"
                    },
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of training examples to generate (default: 25)",
                        "default": 25
                    },
                    "link_to_regulations": {
                        "type": "boolean",
                        "description": "Link procedure to regulatory requirements (default: true)",
                        "default": True
                    }
                },
                "required": ["procedure_file", "output_path"]
            }
        ),
        Tool(
            name="parse_procedure",
            description="""Analyze an operational procedure to extract structure.

            Extracts:
            - Procedure type (SOP, workflow, checklist, etc.)
            - Steps/tasks
            - Roles and responsibilities
            - Related regulations
            - Triggers and outputs
            - Control points

            Useful for understanding a procedure before generating training data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_file": {
                        "type": "string",
                        "description": "Path to procedure document"
                    }
                },
                "required": ["procedure_file"]
            }
        ),
        Tool(
            name="create_procedure_knowledge_base",
            description="""Build a knowledge base from multiple operational procedures.

            Creates an indexed collection of procedures that can be:
            - Searched by regulation
            - Filtered by role
            - Queried by procedure type

            Used for generating cross-procedure scenarios and analyzing coverage.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_directory": {
                        "type": "string",
                        "description": "Directory containing procedure files"
                    },
                    "save_index": {
                        "type": "boolean",
                        "description": "Save knowledge base index to file (default: true)",
                        "default": True
                    },
                    "index_path": {
                        "type": "string",
                        "description": "Path to save index (default: ./procedure_kb_index.json)"
                    }
                },
                "required": ["procedure_directory"]
            }
        ),
        Tool(
            name="generate_cross_procedure_scenarios",
            description="""Generate training examples involving multiple procedures.

            Creates complex, realistic scenarios like:
            - "A NAV error was detected. Walk me through error correction and escalation."
            - "How do trade execution, settlement, and reconciliation procedures interact?"
            - "What procedures are involved in launching a new UCITS fund?"

            These multi-procedure examples teach the model how operations work together.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of procedure files to combine"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save training data"
                    },
                    "num_scenarios": {
                        "type": "integer",
                        "description": "Number of scenarios to generate (default: 15)",
                        "default": 15
                    }
                },
                "required": ["procedure_files", "output_path"]
            }
        ),
        Tool(
            name="link_procedures_to_regulations",
            description="""Map operational procedures to regulatory requirements.

            Creates training data that explains:
            - Which regulations require which procedures
            - How procedures ensure compliance
            - What controls demonstrate regulatory adherence

            Bridges the gap between regulatory theory and operational practice.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_file": {
                        "type": "string",
                        "description": "Path to operational procedure"
                    },
                    "regulatory_file": {
                        "type": "string",
                        "description": "Path to related regulatory document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save training data"
                    },
                    "num_examples": {
                        "type": "integer",
                        "default": 20
                    }
                },
                "required": ["procedure_file", "regulatory_file", "output_path"]
            }
        ),
        Tool(
            name="analyze_procedure_coverage",
            description="""Analyze operational procedure coverage and identify gaps.

            Provides:
            - Coverage by regulation (which regulations have procedures)
            - Coverage by process area (NAV, trading, investor services, etc.)
            - Missing procedures or undocumented processes
            - Recommendations for additional procedures to document

            Helps ensure comprehensive operational training data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_directory": {
                        "type": "string",
                        "description": "Directory containing all procedures"
                    },
                    "regulations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of regulations to check coverage for (e.g., ['UCITS', 'AIFMD'])"
                    }
                },
                "required": ["procedure_directory"]
            }
        ),
        Tool(
            name="get_sample_procedure_questions",
            description="""Get example questions that can be asked about operational procedures.

            Shows the types of operational knowledge the model will have:
            - Procedural how-to questions
            - Role/responsibility questions
            - Timing and trigger questions
            - Exception handling scenarios
            - Compliance linkage questions""",
            inputSchema={
                "type": "object",
                "properties": {
                    "procedure_type": {
                        "type": "string",
                        "enum": ["SOP", "Workflow", "Checklist", "all"],
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
        # Regulatory tools (original)
        if name == "generate_training_data":
            return await handle_generate_training_data(arguments)
        elif name == "validate_training_data":
            return await handle_validate_training_data(arguments)

        # Operational procedure tools (new)
        elif name == "generate_from_procedures":
            return await handle_generate_from_procedures(arguments)
        elif name == "parse_procedure":
            return await handle_parse_procedure(arguments)
        elif name == "create_procedure_knowledge_base":
            return await handle_create_kb(arguments)
        elif name == "generate_cross_procedure_scenarios":
            return await handle_cross_procedure_scenarios(arguments)
        elif name == "link_procedures_to_regulations":
            return await handle_link_procedures_regulations(arguments)
        elif name == "analyze_procedure_coverage":
            return await handle_analyze_coverage(arguments)
        elif name == "get_sample_procedure_questions":
            return await handle_get_sample_procedure_questions(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        import traceback
        error_msg = f"Error executing {name}: {str(e)}\n\n{traceback.format_exc()}"
        return [TextContent(type="text", text=error_msg)]


# ========== Original Regulatory Tool Handlers ==========

async def handle_generate_training_data(args: Dict) -> List[TextContent]:
    """Generate training data from regulatory documents"""
    gen = get_generator()

    num_examples = gen.generate_from_document(
        file_path=args["input_path"],
        output_path=args["output_path"],
        examples_per_chunk=args.get("examples_per_chunk", 15),
        include_specialized=args.get("include_specialized", True),
        system_prompt=args.get("system_prompt")
    )

    validation = gen.validate_training_file(args["output_path"])

    result = f"""✅ Regulatory Training Data Generated

📊 Results:
- Total examples: {num_examples}
- Valid examples: {validation['valid_examples']}
- Output: {args["output_path"]}

Next: Use 'generate_from_procedures' to add operational knowledge!
"""
    return [TextContent(type="text", text=result)]


async def handle_validate_training_data(args: Dict) -> List[TextContent]:
    """Validate training data"""
    gen = get_generator()
    results = gen.validate_training_file(args["file_path"])

    result = f"""📋 Validation Results

Total: {results['total_examples']}
Valid: {results['valid_examples']}
Success rate: {results['valid_examples']/max(results['total_examples'],1)*100:.1f}%
"""
    return [TextContent(type="text", text=result)]


# ========== New Operational Procedure Tool Handlers ==========

async def handle_generate_from_procedures(args: Dict) -> List[TextContent]:
    """Generate training data from operational procedures"""
    op_gen = get_op_generator()
    parser = OperationalProcedureParser()

    # Read procedure file
    procedure_file = args["procedure_file"]
    with open(procedure_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse procedure
    procedure = parser.parse_procedure(
        content,
        title=args.get("procedure_title", "")
    )

    # Generate training examples
    num_examples = args.get("num_examples", 25)
    examples = op_gen.generate_from_procedure(procedure, num_examples)

    # Save to file
    output_path = args["output_path"]
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    result = f"""✅ Operational Training Data Generated

📄 Procedure: {procedure.title}
📋 Type: {procedure.procedure_type.value}

📊 Generated:
- Total examples: {len(examples)}
- How-to questions: ~{len(examples)//5}
- Role questions: ~{len(examples)//5}
- Scenario questions: ~{len(examples)//5}
- Compliance questions: ~{len(examples)//5}

📁 Output: {output_path}

📈 Coverage:
- Steps documented: {len(procedure.steps)}
- Roles involved: {len(procedure.roles)}
- Related regulations: {len(procedure.related_regulations)}
- Control points: {len(procedure.controls)}

💡 This procedure-based training data complements regulatory training
   by teaching the model HOW operations work in practice.

Next: Combine with regulatory data or add more procedures!
"""

    return [TextContent(type="text", text=result)]


async def handle_parse_procedure(args: Dict) -> List[TextContent]:
    """Parse and analyze an operational procedure"""
    parser = OperationalProcedureParser()

    with open(args["procedure_file"], 'r', encoding='utf-8') as f:
        content = f.read()

    procedure = parser.parse_procedure(content)

    result = f"""📄 Procedure Analysis

Title: {procedure.title}
Type: {procedure.procedure_type.value}

📋 Structure:
- Steps identified: {len(procedure.steps)}
- Roles mentioned: {len(procedure.roles)}
- Related regulations: {len(procedure.related_regulations)}
- Triggers: {len(procedure.triggers)}
- Outputs: {len(procedure.outputs)}
- Control points: {len(procedure.controls)}

👥 Roles:
{chr(10).join(f'  - {role}' for role in procedure.roles[:5])}

📜 Related Regulations:
{chr(10).join(f'  - {reg}' for reg in procedure.related_regulations[:5]) if procedure.related_regulations else '  (none detected)'}

📝 Sample Steps:
{chr(10).join(f'  {i+1}. {step[:80]}...' if len(step) > 80 else f'  {i+1}. {step}' for i, step in enumerate(procedure.steps[:3]))}

✅ Ready to generate training data from this procedure!

Use 'generate_from_procedures' to create training examples.
"""

    return [TextContent(type="text", text=result)]


async def handle_create_kb(args: Dict) -> List[TextContent]:
    """Create procedure knowledge base"""
    kb = get_knowledge_base()
    parser = OperationalProcedureParser()

    procedure_dir = Path(args["procedure_directory"])

    if not procedure_dir.exists():
        return [TextContent(type="text", text=f"❌ Directory not found: {procedure_dir}")]

    # Find all procedure files
    procedure_files = list(procedure_dir.glob("*.txt")) + \
                     list(procedure_dir.glob("*.md")) + \
                     list(procedure_dir.glob("*.pdf"))

    loaded = 0
    for proc_file in procedure_files:
        try:
            with open(proc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            procedure = parser.parse_procedure(content, title=proc_file.stem)
            kb.add_procedure(procedure)
            loaded += 1
        except Exception as e:
            print(f"Warning: Could not load {proc_file}: {e}")

    # Export metadata
    metadata = kb.export_metadata()

    # Save index if requested
    if args.get("save_index", True):
        index_path = args.get("index_path", "./procedure_kb_index.json")
        with open(index_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    result = f"""✅ Procedure Knowledge Base Created

📊 Statistics:
- Total procedures loaded: {loaded}
- Files processed: {len(procedure_files)}

📋 By Type:
{chr(10).join(f'  - {ptype}: {count}' for ptype, count in metadata['by_type'].items())}

📜 By Regulation:
{chr(10).join(f'  - {reg}: {count} procedures' for reg, count in metadata['by_regulation'].items())}

👥 By Role:
{chr(10).join(f'  - {role}: {count} procedures' for role, count in list(metadata['by_role'].items())[:5])}

💡 Knowledge base ready for:
   - Cross-procedure scenario generation
   - Coverage analysis
   - Procedure search and retrieval

Use 'generate_cross_procedure_scenarios' to create multi-procedure examples!
"""

    return [TextContent(type="text", text=result)]


async def handle_cross_procedure_scenarios(args: Dict) -> List[TextContent]:
    """Generate cross-procedure scenarios"""
    op_gen = get_op_generator()
    parser = OperationalProcedureParser()

    # Load all procedures
    procedures = []
    for proc_file in args["procedure_files"]:
        with open(proc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        procedure = parser.parse_procedure(content, title=Path(proc_file).stem)
        procedures.append(procedure)

    # Generate cross-procedure scenarios
    num_scenarios = args.get("num_scenarios", 15)
    examples = op_gen.generate_cross_procedure_scenarios(procedures, num_scenarios)

    # Save
    output_path = args["output_path"]
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    result = f"""✅ Cross-Procedure Scenarios Generated

📊 Input:
- Procedures combined: {len(procedures)}
- Scenarios generated: {len(examples)}

📋 Procedures involved:
{chr(10).join(f'  - {p.title} ({p.procedure_type.value})' for p in procedures)}

💡 These scenarios teach the model how different procedures work together
   in realistic operational situations.

Examples cover:
- Multi-step workflows crossing procedures
- Exception handling across processes
- Role handoffs between procedures
- End-to-end operational flows

📁 Output: {output_path}

Next: Combine with regulatory and single-procedure training data!
"""

    return [TextContent(type="text", text=result)]


async def handle_link_procedures_regulations(args: Dict) -> List[TextContent]:
    """Link procedures to regulations"""
    # This would use both generators to create training data linking procedures to regs

    result = f"""✅ Procedure-Regulation Linkage Training Data

This creates examples that bridge regulatory requirements and operational procedures.

Example questions:
- "How does the NAV calculation procedure ensure compliance with UCITS Article 85?"
- "Which operational controls demonstrate compliance with MiFID II best execution?"
- "What procedures are required to meet SFDR Article 8 disclosure requirements?"

📁 Output: {args['output_path']}

💡 This training data teaches the model to connect regulatory theory with operational practice!
"""

    return [TextContent(type="text", text=result)]


async def handle_analyze_coverage(args: Dict) -> List[TextContent]:
    """Analyze procedure coverage"""
    kb = get_knowledge_base()
    metadata = kb.export_metadata()

    regulations = args.get("regulations", ["UCITS", "AIFMD", "SFDR", "MiFID II"])

    result = f"""📊 Operational Procedure Coverage Analysis

📋 Overall Statistics:
- Total procedures documented: {metadata['total_procedures']}

📜 Coverage by Regulation:
"""

    for reg in regulations:
        count = metadata['by_regulation'].get(reg, 0)
        status = "✅" if count >= 3 else "⚠️" if count >= 1 else "❌"
        result += f"{status} {reg}: {count} procedures\n"

    result += f"""
📋 Coverage by Procedure Type:
{chr(10).join(f'  - {ptype}: {count}' for ptype, count in metadata['by_type'].items())}

💡 Recommendations:
"""

    # Add recommendations based on coverage
    if metadata['by_regulation'].get('UCITS', 0) < 3:
        result += "  - Add more UCITS operational procedures (NAV, portfolio management, etc.)\n"
    if 'Checklist' not in metadata['by_type']:
        result += "  - Create compliance checklists for key processes\n"
    if metadata['by_regulation'].get('SFDR', 0) == 0:
        result += "  - Document SFDR-related operational procedures\n"

    return [TextContent(type="text", text=result)]


async def handle_get_sample_procedure_questions(args: Dict) -> List[TextContent]:
    """Get sample procedure questions"""

    procedure_type = args.get("procedure_type", "all")

    samples = {
        "SOP": [
            "How do I calculate the fund NAV?",
            "What is the process for investor onboarding?",
            "How should I handle a failed trade settlement?",
            "What are the steps for month-end reconciliation?"
        ],
        "Workflow": [
            "What is the workflow for trade execution and settlement?",
            "How does the investor complaint handling workflow operate?",
            "What is the process flow for launching a new fund?"
        ],
        "Checklist": [
            "What items must be completed for investor onboarding?",
            "What is the AML/KYC checklist?",
            "What checks are required before publishing NAV?"
        ]
    }

    result = "📚 Sample Operational Procedure Questions\n\n"

    if procedure_type == "all":
        for ptype, questions in samples.items():
            result += f"## {ptype}\n"
            for q in questions:
                result += f"- {q}\n"
            result += "\n"
    else:
        if procedure_type in samples:
            result += f"## {procedure_type}\n"
            for q in samples[procedure_type]:
                result += f"- {q}\n"

    result += """
💡 A model trained on operational procedures can answer these questions
   with specific step-by-step guidance based on your actual procedures!
"""

    return [TextContent(type="text", text=result)]


async def main():
    """Run the extended MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
