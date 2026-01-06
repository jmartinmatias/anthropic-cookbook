"""
Agentic Orchestration Framework for EU Investment Funds Fine-Tuning

This package provides agentic routing and orchestration capabilities that leverage
the four-dimensional expertise framework:

1. Regulatory Knowledge (30%) - WHAT rules require
2. Operational Procedures (30%) - HOW your firm complies
3. Domain Expertise (25%) - WHY decisions are made
4. Industry Standards (15%) - WHAT everyone does

Key Components:
--------------
- RoutingEngine: Intelligent query classification and routing
- DimensionAgents: Four specialized agents (Regulatory, Operational, Domain, Industry)
- Orchestrator: Multi-agent coordination and workflow execution
- SynthesisAgent: Combines perspectives from multiple dimensions
- WorkflowEngine: Executes custom multi-step workflows

Usage:
------
    from finetuning.agentic import Orchestrator, RoutingEngine

    # Initialize orchestrator
    orchestrator = Orchestrator(api_key="your-api-key")

    # Route and execute query
    result = await orchestrator.process_query(
        "Should we invest in this high-yield bond fund?"
    )

    # Custom workflow
    workflow = orchestrator.create_workflow([
        ("regulatory", "check_compliance"),
        ("operational", "verify_procedures"),
        ("domain", "analyze_investment"),
        ("industry", "compare_to_peers")
    ])

    result = await workflow.execute(investment_proposal)

Agentic Patterns Supported:
---------------------------
1. Sequential Processing: Linear chain through dimensions
2. Intelligent Routing: Route to appropriate dimension expert
3. Parallel Evaluation: All agents evaluate simultaneously (fan-out/fan-in)
4. Iterative Refinement: Agents critique and improve outputs (evaluator-optimizer)
5. Dynamic Tool Orchestration: Agents decide which tools to call

Version: 1.0.0
Author: Anthropic Cookbook
"""

from .routing_engine import RoutingEngine, QueryType
from .dimension_agents import (
    RegulatoryAgent,
    OperationalAgent,
    DomainExpertAgent,
    IndustryAgent
)
from .orchestrator import Orchestrator, OrchestrationStrategy
from .synthesis_agent import SynthesisAgent, SynthesisResult
from .workflow_engine import WorkflowEngine, WorkflowStep

__version__ = "1.0.0"

__all__ = [
    # Core components
    "Orchestrator",
    "RoutingEngine",
    "SynthesisAgent",
    "WorkflowEngine",

    # Dimension agents
    "RegulatoryAgent",
    "OperationalAgent",
    "DomainExpertAgent",
    "IndustryAgent",

    # Enums and types
    "QueryType",
    "OrchestrationStrategy",
    "SynthesisResult",
    "WorkflowStep",
]
