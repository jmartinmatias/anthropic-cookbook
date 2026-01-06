"""
Orchestrator - Multi-Agent Coordination and Workflow Execution

This module coordinates multiple dimension agents to handle complex queries
that require expertise from multiple dimensions.

Orchestration Strategies:
1. Sequential: Process through dimensions in order
2. Parallel: All dimensions evaluate simultaneously
3. Routing: Single dimension handles query
4. Iterative: Agents refine each other's outputs
5. Dynamic: Orchestrator decides strategy based on query
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .routing_engine import RoutingEngine, RoutingDecision, DimensionType
from .dimension_agents import (
    RegulatoryAgent,
    OperationalAgent,
    DomainExpertAgent,
    IndustryAgent,
    AgentResponse,
    AgentRole
)


class OrchestrationStrategy(Enum):
    """Strategy for coordinating multiple agents"""
    SEQUENTIAL = "sequential"        # Linear chain through dimensions
    PARALLEL = "parallel"            # Fan-out/fan-in simultaneous evaluation
    ROUTING = "routing"              # Single agent handles query
    ITERATIVE = "iterative"          # Agents refine each other's outputs
    DYNAMIC = "dynamic"              # Orchestrator chooses best strategy


@dataclass
class OrchestrationResult:
    """Result of orchestrated multi-agent processing"""
    query: str
    strategy_used: OrchestrationStrategy
    routing_decision: RoutingDecision
    agent_responses: Dict[str, AgentResponse]
    final_answer: str
    confidence: float
    processing_order: List[str]
    total_time_ms: float


class Orchestrator:
    """
    Orchestrates multiple dimension agents to answer complex queries

    The orchestrator:
    1. Routes query to appropriate agent(s)
    2. Coordinates multi-agent workflows
    3. Synthesizes responses
    4. Manages iterative refinement
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        use_ml_routing: bool = True
    ):
        """
        Initialize orchestrator

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            use_ml_routing: Whether to use ML-based routing (more accurate)
        """
        self.api_key = api_key
        self.model = model

        # Initialize routing engine
        self.router = RoutingEngine(api_key=api_key, use_ml_routing=use_ml_routing)

        # Initialize dimension agents
        self.agents = {
            "regulatory": RegulatoryAgent(api_key, model),
            "operational": OperationalAgent(api_key, model),
            "domain": DomainExpertAgent(api_key, model),
            "industry": IndustryAgent(api_key, model),
        }

    async def process_query(
        self,
        query: str,
        strategy: OrchestrationStrategy = OrchestrationStrategy.DYNAMIC,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Process query using specified orchestration strategy

        Args:
            query: User query
            strategy: Orchestration strategy to use
            context: Additional context

        Returns:
            OrchestrationResult with complete processing details
        """
        import time
        start_time = time.time()

        # Route query
        routing_decision = self.router.route_query(query)

        # Choose strategy if dynamic
        if strategy == OrchestrationStrategy.DYNAMIC:
            strategy = self._choose_strategy(routing_decision)

        # Execute based on strategy
        if strategy == OrchestrationStrategy.ROUTING:
            result = await self._execute_routing(query, routing_decision, context)
        elif strategy == OrchestrationStrategy.SEQUENTIAL:
            result = await self._execute_sequential(query, routing_decision, context)
        elif strategy == OrchestrationStrategy.PARALLEL:
            result = await self._execute_parallel(query, routing_decision, context)
        elif strategy == OrchestrationStrategy.ITERATIVE:
            result = await self._execute_iterative(query, routing_decision, context)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        end_time = time.time()
        result.total_time_ms = (end_time - start_time) * 1000

        return result

    def _choose_strategy(self, routing_decision: RoutingDecision) -> OrchestrationStrategy:
        """
        Dynamically choose best orchestration strategy

        Args:
            routing_decision: Routing decision from routing engine

        Returns:
            Best orchestration strategy for this query
        """
        # Use router's suggestion if available
        if routing_decision.suggested_strategy == "routing_only":
            return OrchestrationStrategy.ROUTING
        elif routing_decision.suggested_strategy == "sequential":
            return OrchestrationStrategy.SEQUENTIAL
        elif routing_decision.suggested_strategy == "parallel":
            return OrchestrationStrategy.PARALLEL

        # Fallback logic
        if len(routing_decision.dimensions) == 1:
            return OrchestrationStrategy.ROUTING
        elif len(routing_decision.dimensions) <= 2:
            return OrchestrationStrategy.PARALLEL
        else:
            return OrchestrationStrategy.SEQUENTIAL

    async def _execute_routing(
        self,
        query: str,
        routing_decision: RoutingDecision,
        context: Optional[Dict] = None
    ) -> OrchestrationResult:
        """Execute routing strategy (single agent)"""
        # Get primary dimension
        dimension = routing_decision.dimensions[0].value

        # Get agent response
        agent = self.agents[dimension]
        response = agent.answer_query(query, context, AgentRole.PRIMARY)

        return OrchestrationResult(
            query=query,
            strategy_used=OrchestrationStrategy.ROUTING,
            routing_decision=routing_decision,
            agent_responses={dimension: response},
            final_answer=response.answer,
            confidence=response.confidence,
            processing_order=[dimension],
            total_time_ms=0  # Will be set by caller
        )

    async def _execute_sequential(
        self,
        query: str,
        routing_decision: RoutingDecision,
        context: Optional[Dict] = None
    ) -> OrchestrationResult:
        """
        Execute sequential strategy (linear chain)

        Order: Regulatory → Operational → Domain → Industry
        Each agent sees previous agents' outputs
        """
        agent_responses = {}
        processing_order = []

        # Process in standard order
        dimension_order = ["regulatory", "operational", "domain", "industry"]
        relevant_dims = [d.value for d in routing_decision.dimensions]

        accumulated_context = context or {}

        for dimension in dimension_order:
            if dimension not in relevant_dims:
                continue

            processing_order.append(dimension)

            # Add previous responses to context
            if agent_responses:
                accumulated_context["previous_responses"] = agent_responses

            # Get agent response
            agent = self.agents[dimension]
            response = agent.answer_query(query, accumulated_context, AgentRole.CONTRIBUTOR)
            agent_responses[dimension] = response

        # Synthesize final answer
        final_answer = self._synthesize_sequential(query, agent_responses, processing_order)

        # Average confidence
        avg_confidence = sum(r.confidence for r in agent_responses.values()) / len(agent_responses)

        return OrchestrationResult(
            query=query,
            strategy_used=OrchestrationStrategy.SEQUENTIAL,
            routing_decision=routing_decision,
            agent_responses=agent_responses,
            final_answer=final_answer,
            confidence=avg_confidence,
            processing_order=processing_order,
            total_time_ms=0
        )

    async def _execute_parallel(
        self,
        query: str,
        routing_decision: RoutingDecision,
        context: Optional[Dict] = None
    ) -> OrchestrationResult:
        """
        Execute parallel strategy (fan-out/fan-in)

        All relevant dimensions evaluate simultaneously,
        then results are synthesized.
        """
        relevant_dims = [d.value for d in routing_decision.dimensions]

        # Execute all agents in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(relevant_dims)) as executor:
            futures = {}
            for dimension in relevant_dims:
                agent = self.agents[dimension]
                future = executor.submit(agent.answer_query, query, context, AgentRole.CONTRIBUTOR)
                futures[dimension] = future

            # Collect results
            agent_responses = {}
            for dimension, future in futures.items():
                agent_responses[dimension] = future.result()

        # Synthesize final answer
        final_answer = self._synthesize_parallel(query, agent_responses)

        # Average confidence
        avg_confidence = sum(r.confidence for r in agent_responses.values()) / len(agent_responses)

        return OrchestrationResult(
            query=query,
            strategy_used=OrchestrationStrategy.PARALLEL,
            routing_decision=routing_decision,
            agent_responses=agent_responses,
            final_answer=final_answer,
            confidence=avg_confidence,
            processing_order=list(relevant_dims),
            total_time_ms=0
        )

    async def _execute_iterative(
        self,
        query: str,
        routing_decision: RoutingDecision,
        context: Optional[Dict] = None,
        max_iterations: int = 3
    ) -> OrchestrationResult:
        """
        Execute iterative strategy (evaluator-optimizer)

        Agents critique and refine each other's outputs.

        Flow:
        1. Domain agent proposes answer
        2. Regulatory agent reviews for compliance
        3. Domain agent refines based on feedback
        4. Operational agent checks feasibility
        5. Industry agent validates against norms
        """
        agent_responses = {}
        processing_order = []
        iteration_history = []

        # Iteration 1: Domain expert drafts initial answer
        domain_agent = self.agents["domain"]
        domain_response = domain_agent.answer_query(query, context, AgentRole.PRIMARY)
        agent_responses["domain_v1"] = domain_response
        processing_order.append("domain (draft)")
        iteration_history.append(("domain", "draft", domain_response.answer))

        current_answer = domain_response.answer

        # Iteration 2: Regulatory review
        if "regulatory" in [d.value for d in routing_decision.dimensions]:
            reg_agent = self.agents["regulatory"]
            review_context = {"answer_to_review": current_answer}
            reg_response = reg_agent.answer_query(query, review_context, AgentRole.REVIEWER)
            agent_responses["regulatory_review"] = reg_response
            processing_order.append("regulatory (review)")
            iteration_history.append(("regulatory", "review", reg_response.answer))

            # Refine based on regulatory feedback
            refinement_context = {
                "original_answer": current_answer,
                "regulatory_feedback": reg_response.answer
            }
            domain_refined = domain_agent.answer_query(
                f"Refine this answer based on regulatory feedback:\n\nOriginal: {current_answer}\n\nFeedback: {reg_response.answer}",
                refinement_context,
                AgentRole.PRIMARY
            )
            agent_responses["domain_v2"] = domain_refined
            processing_order.append("domain (refined)")
            iteration_history.append(("domain", "refined", domain_refined.answer))
            current_answer = domain_refined.answer

        # Iteration 3: Operational feasibility check
        if "operational" in [d.value for d in routing_decision.dimensions]:
            ops_agent = self.agents["operational"]
            ops_context = {"answer_to_review": current_answer}
            ops_response = ops_agent.answer_query(query, ops_context, AgentRole.REVIEWER)
            agent_responses["operational_review"] = ops_response
            processing_order.append("operational (review)")
            iteration_history.append(("operational", "review", ops_response.answer))

        # Final: Industry validation
        if "industry" in [d.value for d in routing_decision.dimensions]:
            industry_agent = self.agents["industry"]
            industry_response = industry_agent.answer_query(query, {"answer_to_review": current_answer}, AgentRole.REVIEWER)
            agent_responses["industry_review"] = industry_response
            processing_order.append("industry (review)")
            iteration_history.append(("industry", "review", industry_response.answer))

        # Synthesize final answer
        final_answer = self._synthesize_iterative(query, agent_responses, iteration_history)

        # Use last domain version confidence
        confidence = agent_responses.get("domain_v2", agent_responses["domain_v1"]).confidence

        return OrchestrationResult(
            query=query,
            strategy_used=OrchestrationStrategy.ITERATIVE,
            routing_decision=routing_decision,
            agent_responses=agent_responses,
            final_answer=final_answer,
            confidence=confidence,
            processing_order=processing_order,
            total_time_ms=0
        )

    def _synthesize_sequential(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse],
        processing_order: List[str]
    ) -> str:
        """Synthesize sequential agent responses into final answer"""
        synthesis = f"# Complete Answer: {query}\n\n"

        for dimension in processing_order:
            response = agent_responses[dimension]
            synthesis += f"## {dimension.upper()} Perspective\n\n"
            synthesis += f"{response.answer}\n\n"

            if response.warnings:
                synthesis += "⚠️ **Warnings:**\n"
                for warning in response.warnings:
                    synthesis += f"- {warning}\n"
                synthesis += "\n"

        return synthesis.strip()

    def _synthesize_parallel(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse]
    ) -> str:
        """Synthesize parallel agent responses into final answer"""
        synthesis = f"# Multi-Dimensional Analysis: {query}\n\n"

        # Group by dimension type
        dimension_order = ["regulatory", "operational", "domain", "industry"]

        for dimension in dimension_order:
            if dimension not in agent_responses:
                continue

            response = agent_responses[dimension]

            # Use emoji indicators
            emoji = {
                "regulatory": "⚖️",
                "operational": "⚙️",
                "domain": "🎯",
                "industry": "🌐"
            }

            synthesis += f"## {emoji[dimension]} {dimension.upper()}\n\n"
            synthesis += f"{response.answer}\n\n"

            if response.warnings:
                synthesis += "**⚠️ Warnings:**\n"
                for warning in response.warnings:
                    synthesis += f"- {warning}\n"
                synthesis += "\n"

        # Add synthesis conclusion
        synthesis += "## 🎯 Synthesis\n\n"
        synthesis += "Considering all perspectives:\n"

        # Check for conflicts
        warnings = [w for r in agent_responses.values() for w in r.warnings]
        if warnings:
            synthesis += "\n**Key Considerations:**\n"
            for warning in warnings[:5]:  # Top 5 warnings
                synthesis += f"- {warning}\n"

        return synthesis.strip()

    def _synthesize_iterative(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse],
        iteration_history: List[tuple]
    ) -> str:
        """Synthesize iterative refinement process into final answer"""
        synthesis = f"# Refined Answer (Iterative Process): {query}\n\n"

        # Show the refinement process
        synthesis += "## 🔄 Refinement Process\n\n"

        for i, (dimension, stage, answer_snippet) in enumerate(iteration_history, 1):
            synthesis += f"**{i}. {dimension.upper()} ({stage}):**\n"
            # Show first 200 chars of each iteration
            snippet = answer_snippet[:200] + "..." if len(answer_snippet) > 200 else answer_snippet
            synthesis += f"{snippet}\n\n"

        # Final refined answer
        synthesis += "## ✅ Final Refined Answer\n\n"

        # Get the last domain version
        final_response = agent_responses.get("domain_v2") or agent_responses.get("domain_v1")
        synthesis += final_response.answer + "\n\n"

        # Show all review feedback
        synthesis += "## 📋 Review Feedback\n\n"

        if "regulatory_review" in agent_responses:
            synthesis += "**⚖️ Regulatory Review:**\n"
            synthesis += agent_responses["regulatory_review"].answer + "\n\n"

        if "operational_review" in agent_responses:
            synthesis += "**⚙️ Operational Review:**\n"
            synthesis += agent_responses["operational_review"].answer + "\n\n"

        if "industry_review" in agent_responses:
            synthesis += "**🌐 Industry Review:**\n"
            synthesis += agent_responses["industry_review"].answer + "\n\n"

        return synthesis.strip()

    def explain_orchestration(self, result: OrchestrationResult) -> str:
        """
        Generate human-readable explanation of orchestration process

        Args:
            result: OrchestrationResult to explain

        Returns:
            Human-readable explanation
        """
        explanation = f"""
🎭 Orchestration Report
======================

Query: "{result.query}"

Strategy: {result.strategy_used.value.replace('_', ' ').title()}
Confidence: {result.confidence:.0%}
Processing Time: {result.total_time_ms:.0f}ms

Routing Decision:
{self.router.explain_routing(result.routing_decision)}

Processing Order:
{chr(10).join(f"  {i+1}. {dim}" for i, dim in enumerate(result.processing_order))}

Agents Involved: {len(result.agent_responses)}
"""
        return explanation.strip()


# Example usage
if __name__ == "__main__":
    import os
    import asyncio

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)

    async def main():
        # Initialize orchestrator
        orchestrator = Orchestrator(api_key, use_ml_routing=False)

        # Test queries
        test_queries = [
            "Is this investment allowed under UCITS?",
            "Should we invest 15% in emerging market bonds?",
            "Evaluate this new ESG screening methodology",
        ]

        for query in test_queries:
            print("\n" + "=" * 70)
            print(f"Query: {query}")
            print("=" * 70)

            # Process with dynamic strategy
            result = await orchestrator.process_query(query)

            print(orchestrator.explain_orchestration(result))
            print("\n" + "-" * 70)
            print("FINAL ANSWER:")
            print("-" * 70)
            print(result.final_answer)

    asyncio.run(main())
