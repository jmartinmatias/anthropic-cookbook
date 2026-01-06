#!/usr/bin/env python3
"""
Agentic MCP Server - The Ultimate Fine-Tuning Toolkit with Agentic Capabilities

This MCP server combines ALL capabilities:
- Four-dimensional expertise (Regulatory, Operational, Domain, Industry)
- Agentic routing and orchestration
- Multi-agent workflows
- Intelligent synthesis

Use this for conversational access to the complete fine-tuning toolkit
with advanced agentic features.
"""

import os
import sys
import asyncio
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agentic components
from agentic.orchestrator import Orchestrator, OrchestrationStrategy
from agentic.routing_engine import RoutingEngine
from agentic.synthesis_agent import SynthesisAgent, SynthesisMode
from agentic.workflow_engine import WorkflowEngine

# Import dimension modules
try:
    from generate_eu_funds_training_data import EUFundsTrainingDataGenerator
    from operational_procedures import OperationalProcedureParser, OperationalTrainingGenerator
    from domain_expertise import DomainExpertiseParser, DomainExpertiseGenerator
    from industry_standards import IndustryStandardsParser, IndustryStandardsGenerator
except ImportError as e:
    print(f"Warning: Could not import dimension modules: {e}")

# Initialize server
server = Server("eu-funds-agentic-finetuning")

# Global instances (initialized on first use)
orchestrator = None
router = None
synthesizer = None
workflow_engine = None


def get_api_key() -> str:
    """Get Anthropic API key from environment"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return api_key


def init_agentic_components():
    """Initialize agentic components (lazy initialization)"""
    global orchestrator, router, synthesizer, workflow_engine

    api_key = get_api_key()

    if orchestrator is None:
        orchestrator = Orchestrator(api_key, use_ml_routing=True)
    if router is None:
        router = RoutingEngine(api_key, use_ml_routing=True)
    if synthesizer is None:
        synthesizer = SynthesisAgent(api_key)
    if workflow_engine is None:
        workflow_engine = WorkflowEngine(api_key)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available tools"""
    return [
        # ============================================================
        # AGENTIC ROUTING & ORCHESTRATION TOOLS
        # ============================================================
        types.Tool(
            name="route_query",
            description="""Intelligently route a query to appropriate dimension expert(s).

Uses ML-based intent detection to determine which dimension(s) should handle the query:
- Regulatory: Legal compliance, regulations
- Operational: Procedures, how-to
- Domain: Investment strategy, expert judgment
- Industry: Market practices, what peers do

Returns routing decision with confidence and reasoning.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "User query to route"
                    }
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="orchestrate_query",
            description="""Process a query using multi-agent orchestration.

Strategies:
- dynamic: Automatically choose best strategy (default)
- routing: Single agent handles query
- sequential: Process through dimensions in order
- parallel: All dimensions evaluate simultaneously
- iterative: Agents refine each other's outputs

Returns comprehensive answer combining multiple expert perspectives.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to process"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["dynamic", "routing", "sequential", "parallel", "iterative"],
                        "description": "Orchestration strategy (default: dynamic)"
                    }
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="synthesize_perspectives",
            description="""Synthesize multiple dimension perspectives into cohesive answer.

Synthesis Modes:
- comprehensive: Show all perspectives (default)
- consensus: Highlight agreements
- decision: Make clear recommendation
- risk_focused: Emphasize risks
- actionable: Focus on next steps

Use this when you have responses from multiple dimensions and want intelligent synthesis.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Original query"
                    },
                    "regulatory_answer": {
                        "type": "string",
                        "description": "Answer from regulatory expert (optional)"
                    },
                    "operational_answer": {
                        "type": "string",
                        "description": "Answer from operational expert (optional)"
                    },
                    "domain_answer": {
                        "type": "string",
                        "description": "Answer from domain expert (optional)"
                    },
                    "industry_answer": {
                        "type": "string",
                        "description": "Answer from industry expert (optional)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["comprehensive", "consensus", "decision", "risk_focused", "actionable"],
                        "description": "Synthesis mode (default: comprehensive)"
                    }
                },
                "required": ["query"]
            }
        ),

        types.Tool(
            name="execute_workflow",
            description="""Execute a pre-built multi-agent workflow.

Available Templates:
- investment_evaluation: Complete investment analysis (regulatory → operational → domain → industry)
- compliance_review: Compliance-focused review (regulatory → operational)
- strategy_assessment: Strategy evaluation (parallel: regulatory/domain/industry → operational)

Workflows combine multiple agents in specific patterns with conditional logic.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "enum": ["investment_evaluation", "compliance_review", "strategy_assessment"],
                        "description": "Workflow template to execute"
                    },
                    "context": {
                        "type": "object",
                        "description": "Context variables (e.g., {investment_description: '...'})",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["template", "context"]
            }
        ),

        # ============================================================
        # TRAINING DATA GENERATION TOOLS (All 4 Dimensions)
        # ============================================================
        types.Tool(
            name="generate_complete_training_dataset",
            description="""Generate a COMPLETE training dataset combining all four dimensions.

This is the ONE-COMMAND solution for creating comprehensive fine-tuning data.

Distribution:
- 30% Regulatory (UCITS, AIFMD, SFDR, etc.)
- 30% Operational (SOPs, workflows)
- 25% Domain Expertise (strategies, judgment)
- 15% Industry Standards (market practices)

Creates a model that knows WHAT rules require, HOW to comply, WHY decisions are made, and WHAT everyone does.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "regulatory_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to regulatory documents (PDF, TXT)"
                    },
                    "operational_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to SOPs and procedure documents"
                    },
                    "domain_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to investment strategy documents"
                    },
                    "industry_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to industry standards documents"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for combined JSONL file"
                    },
                    "total_examples": {
                        "type": "integer",
                        "description": "Total number of examples to generate (default: 1000)",
                        "default": 1000
                    }
                },
                "required": ["output_path"]
            }
        ),

        types.Tool(
            name="generate_regulatory_training_data",
            description="""Generate training data from EU regulatory documents (Dimension 1: WHAT).

Focuses on regulations: UCITS, AIFMD, SFDR, MiFID II, PRIIPs, etc.
Creates Q&A about compliance requirements, eligible assets, limits, reporting, etc.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to regulatory document (PDF or TXT)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for JSONL file"
                    },
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of examples per chunk (default: 15)",
                        "default": 15
                    }
                },
                "required": ["file_path", "output_path"]
            }
        ),

        types.Tool(
            name="generate_operational_training_data",
            description="""Generate training data from SOPs and procedures (Dimension 2: HOW).

Extracts workflows, steps, roles, timing from operational documents.
Creates how-to questions, responsibility questions, timing questions, scenarios, compliance checks.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to SOP/procedure document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for JSONL file"
                    },
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of examples to generate (default: 20)",
                        "default": 20
                    }
                },
                "required": ["file_path", "output_path"]
            }
        ),

        types.Tool(
            name="generate_domain_training_data",
            description="""Generate training data from domain expertise documents (Dimension 3: WHY).

Processes investment strategies, risk frameworks, best practices.
Creates questions about investment rationale, risk assessment, strategy selection, implementation, concepts, best practices.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to strategy/expertise document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for JSONL file"
                    },
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of examples to generate (default: 20)",
                        "default": 20
                    }
                },
                "required": ["file_path", "output_path"]
            }
        ),

        types.Tool(
            name="generate_industry_training_data",
            description="""Generate training data from industry standards documents (Dimension 4: WHAT EVERYONE DOES).

Processes market conventions, settlement practices, pricing standards, documentation norms.
Creates questions about market practices, geographic differences, standard timelines, peer comparisons, convention applications.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to industry standards document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Output path for JSONL file"
                    },
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of examples to generate (default: 20)",
                        "default": 20
                    }
                },
                "required": ["file_path", "output_path"]
            }
        ),

        types.Tool(
            name="validate_training_data",
            description="""Validate JSONL training data for AWS Bedrock compatibility.

Checks:
- Valid JSONL format
- Required fields (system, messages)
- Message structure
- No empty messages
- Returns validation report with errors""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to JSONL file to validate"
                    }
                },
                "required": ["file_path"]
            }
        ),

        types.Tool(
            name="estimate_training_cost",
            description="""Estimate AWS Bedrock fine-tuning cost.

Provides cost estimate based on:
- Number of training examples
- Number of epochs
- Claude model (Haiku, Sonnet)

Returns estimated cost and training time.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_examples": {
                        "type": "integer",
                        "description": "Number of training examples"
                    },
                    "num_epochs": {
                        "type": "integer",
                        "description": "Number of training epochs (default: 3)",
                        "default": 3
                    },
                    "model": {
                        "type": "string",
                        "enum": ["haiku", "sonnet"],
                        "description": "Claude model (default: haiku)",
                        "default": "haiku"
                    }
                },
                "required": ["num_examples"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        # Initialize agentic components
        init_agentic_components()

        # ============================================================
        # AGENTIC TOOLS
        # ============================================================
        if name == "route_query":
            query = arguments["query"]
            decision = router.route_query(query)
            explanation = router.explain_routing(decision)
            return [types.TextContent(type="text", text=explanation)]

        elif name == "orchestrate_query":
            query = arguments["query"]
            strategy_name = arguments.get("strategy", "dynamic")
            strategy = OrchestrationStrategy(strategy_name)

            result = await orchestrator.process_query(query, strategy)

            output = orchestrator.explain_orchestration(result)
            output += "\n\n" + "="*70 + "\n"
            output += "FINAL ANSWER:\n"
            output += "="*70 + "\n"
            output += result.final_answer

            return [types.TextContent(type="text", text=output)]

        elif name == "synthesize_perspectives":
            from agentic.dimension_agents import AgentResponse

            query = arguments["query"]
            mode_name = arguments.get("mode", "comprehensive")
            mode = SynthesisMode(mode_name)

            # Build agent responses from provided answers
            agent_responses = {}

            if "regulatory_answer" in arguments:
                agent_responses["regulatory"] = AgentResponse(
                    dimension="regulatory",
                    answer=arguments["regulatory_answer"],
                    confidence=0.8,
                    sources=[],
                    warnings=[],
                    follow_up_questions=[],
                    requires_other_dimensions=[]
                )

            if "operational_answer" in arguments:
                agent_responses["operational"] = AgentResponse(
                    dimension="operational",
                    answer=arguments["operational_answer"],
                    confidence=0.8,
                    sources=[],
                    warnings=[],
                    follow_up_questions=[],
                    requires_other_dimensions=[]
                )

            if "domain_answer" in arguments:
                agent_responses["domain"] = AgentResponse(
                    dimension="domain",
                    answer=arguments["domain_answer"],
                    confidence=0.8,
                    sources=[],
                    warnings=[],
                    follow_up_questions=[],
                    requires_other_dimensions=[]
                )

            if "industry_answer" in arguments:
                agent_responses["industry"] = AgentResponse(
                    dimension="industry",
                    answer=arguments["industry_answer"],
                    confidence=0.8,
                    sources=[],
                    warnings=[],
                    follow_up_questions=[],
                    requires_other_dimensions=[]
                )

            result = synthesizer.synthesize(query, agent_responses, mode)
            output = synthesizer.format_synthesis(result)

            return [types.TextContent(type="text", text=output)]

        elif name == "execute_workflow":
            template = arguments["template"]
            context = arguments["context"]

            result = await workflow_engine.execute_template(template, context)

            output = f"""
Workflow Execution Report
=========================

Template: {result.workflow_name}
Status: {result.status}
Processing Time: {result.total_time_ms:.0f}ms

Steps Executed ({len(result.steps_executed)}):
{chr(10).join(f"  ✓ {step}" for step in result.steps_executed)}
"""

            if result.steps_failed:
                output += f"\n\nSteps Failed ({len(result.steps_failed)}):\n"
                output += "\n".join(f"  ✗ {step}" for step in result.steps_failed)

            if result.steps_skipped:
                output += f"\n\nSteps Skipped ({len(result.steps_skipped)}):\n"
                output += "\n".join(f"  ⊘ {step}" for step in result.steps_skipped)

            output += "\n\n" + "="*70 + "\n"
            output += "FINAL OUTPUT:\n"
            output += "="*70 + "\n"
            output += str(result.final_output)

            return [types.TextContent(type="text", text=output)]

        # ============================================================
        # TRAINING DATA GENERATION TOOLS
        # ============================================================
        elif name == "generate_complete_training_dataset":
            # This would combine all four dimensions
            reg_files = arguments.get("regulatory_files", [])
            ops_files = arguments.get("operational_files", [])
            dom_files = arguments.get("domain_files", [])
            ind_files = arguments.get("industry_files", [])
            output_path = arguments["output_path"]
            total_examples = arguments.get("total_examples", 1000)

            # Calculate distribution
            reg_count = int(total_examples * 0.30)
            ops_count = int(total_examples * 0.30)
            dom_count = int(total_examples * 0.25)
            ind_count = int(total_examples * 0.15)

            report = f"""
Complete Training Dataset Generation
====================================

Target Distribution:
  • Regulatory: {reg_count} examples (30%)
  • Operational: {ops_count} examples (30%)
  • Domain: {dom_count} examples (25%)
  • Industry: {ind_count} examples (15%)

Total: {total_examples} examples

Input Files:
  • Regulatory: {len(reg_files)} files
  • Operational: {len(ops_files)} files
  • Domain: {len(dom_files)} files
  • Industry: {len(ind_files)} files

Output: {output_path}

Status: Would generate complete dataset (implementation requires actual file processing)

NOTE: This tool demonstrates the structure. Full implementation would:
1. Process each dimension's files
2. Generate examples according to distribution
3. Combine into single JSONL file
4. Validate final output
"""
            return [types.TextContent(type="text", text=report)]

        elif name == "generate_regulatory_training_data":
            file_path = arguments["file_path"]
            output_path = arguments["output_path"]
            num_examples = arguments.get("num_examples", 15)

            generator = EUFundsTrainingDataGenerator(api_key=get_api_key())
            count = generator.generate_from_document(
                file_path=file_path,
                output_path=output_path,
                examples_per_chunk=num_examples
            )

            return [types.TextContent(
                type="text",
                text=f"✓ Generated {count} regulatory training examples\nOutput: {output_path}"
            )]

        elif name == "generate_operational_training_data":
            file_path = arguments["file_path"]
            output_path = arguments["output_path"]
            num_examples = arguments.get("num_examples", 20)

            with open(file_path, 'r') as f:
                content = f.read()

            parser = OperationalProcedureParser()
            generator = OperationalTrainingGenerator(api_key=get_api_key())

            procedure = parser.parse_procedure(content, os.path.basename(file_path))
            examples = generator.generate_from_procedure(procedure, num_examples)

            # Write to JSONL
            import json
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps(example) + '\n')

            return [types.TextContent(
                type="text",
                text=f"✓ Generated {len(examples)} operational training examples\nOutput: {output_path}"
            )]

        elif name == "generate_domain_training_data":
            file_path = arguments["file_path"]
            output_path = arguments["output_path"]
            num_examples = arguments.get("num_examples", 20)

            with open(file_path, 'r') as f:
                content = f.read()

            parser = DomainExpertiseParser()
            generator = DomainExpertiseGenerator(api_key=get_api_key())

            doc = parser.parse_domain_document(content, os.path.basename(file_path))
            examples = generator.generate_from_domain_doc(doc, num_examples)

            # Write to JSONL
            import json
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps(example) + '\n')

            return [types.TextContent(
                type="text",
                text=f"✓ Generated {len(examples)} domain expertise training examples\nOutput: {output_path}"
            )]

        elif name == "generate_industry_training_data":
            file_path = arguments["file_path"]
            output_path = arguments["output_path"]
            num_examples = arguments.get("num_examples", 20)

            with open(file_path, 'r') as f:
                content = f.read()

            parser = IndustryStandardsParser()
            generator = IndustryStandardsGenerator(api_key=get_api_key())

            standards = parser.parse_standards_document(content, os.path.basename(file_path))
            examples = generator.generate_from_standards(standards, num_examples)

            # Write to JSONL
            import json
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps(example) + '\n')

            return [types.TextContent(
                type="text",
                text=f"✓ Generated {len(examples)} industry standards training examples\nOutput: {output_path}"
            )]

        elif name == "validate_training_data":
            file_path = arguments["file_path"]

            generator = EUFundsTrainingDataGenerator(api_key=get_api_key())
            is_valid, errors = generator.validate_training_file(file_path)

            if is_valid:
                return [types.TextContent(
                    type="text",
                    text=f"✓ Training data is valid!\nFile: {file_path}"
                )]
            else:
                error_text = f"✗ Validation failed!\n\nErrors:\n" + "\n".join(f"  • {e}" for e in errors)
                return [types.TextContent(type="text", text=error_text)]

        elif name == "estimate_training_cost":
            num_examples = arguments["num_examples"]
            num_epochs = arguments.get("num_epochs", 3)
            model = arguments.get("model", "haiku")

            # Rough cost estimates (update with actual Bedrock pricing)
            cost_per_1k_examples = 1.0 if model == "haiku" else 3.0
            estimated_cost = (num_examples / 1000) * cost_per_1k_examples * num_epochs

            # Training time estimate (rough)
            hours_per_epoch = (num_examples / 1000) * 0.5
            total_hours = hours_per_epoch * num_epochs

            report = f"""
Training Cost Estimate
=====================

Configuration:
  • Examples: {num_examples:,}
  • Epochs: {num_epochs}
  • Model: Claude 3 {model.title()}

Estimated Cost: ${estimated_cost:.2f}
Estimated Time: {total_hours:.1f} hours

NOTE: These are rough estimates. Actual costs depend on:
- AWS Bedrock pricing in your region
- Model version
- Training complexity
"""
            return [types.TextContent(type="text", text=report)]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        import traceback
        error_msg = f"Error executing {name}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return [types.TextContent(type="text", text=error_msg)]


async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eu-funds-agentic-finetuning",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
