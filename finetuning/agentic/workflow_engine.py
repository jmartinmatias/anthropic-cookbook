"""
Workflow Engine - Custom Multi-Step Agent Workflows

This module provides a framework for defining and executing custom multi-step
workflows that combine dimension agents in specific patterns.

Key Features:
- Define workflows as sequences of steps
- Conditional branching based on agent outputs
- Parallel execution of independent steps
- State management across steps
- Pre-built workflow templates
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .dimension_agents import (
    RegulatoryAgent,
    OperationalAgent,
    DomainExpertAgent,
    IndustryAgent,
    AgentResponse
)


class StepType(Enum):
    """Type of workflow step"""
    AGENT_QUERY = "agent_query"              # Query a dimension agent
    CONDITIONAL = "conditional"              # Conditional branch
    PARALLEL = "parallel"                    # Execute steps in parallel
    SYNTHESIS = "synthesis"                  # Synthesize results
    VALIDATION = "validation"                # Validate output
    TRANSFORM = "transform"                  # Transform data


class StepStatus(Enum):
    """Status of workflow step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """
    A single step in a workflow

    Steps can query agents, perform conditional logic, execute in parallel, etc.
    """
    name: str
    step_type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[Callable] = None
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    workflow_name: str
    status: str  # "completed", "failed", "partial"
    steps_executed: List[str]
    steps_failed: List[str]
    steps_skipped: List[str]
    final_output: Any
    step_results: Dict[str, Any]
    total_time_ms: float


class WorkflowEngine:
    """
    Executes custom multi-step agent workflows

    Workflows are defined as directed acyclic graphs (DAGs) of steps.
    The engine handles:
    - Dependency resolution
    - Parallel execution
    - Conditional branching
    - State management
    - Error handling
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize workflow engine

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model

        # Initialize agents
        self.agents = {
            "regulatory": RegulatoryAgent(api_key, model),
            "operational": OperationalAgent(api_key, model),
            "domain": DomainExpertAgent(api_key, model),
            "industry": IndustryAgent(api_key, model),
        }

        # Workflow templates
        self.templates = self._load_templates()

    async def execute_workflow(
        self,
        steps: List[WorkflowStep],
        initial_context: Dict[str, Any],
        workflow_name: str = "custom"
    ) -> WorkflowResult:
        """
        Execute a workflow

        Args:
            steps: List of workflow steps
            initial_context: Initial context/state
            workflow_name: Name of workflow

        Returns:
            WorkflowResult with execution details
        """
        import time
        start_time = time.time()

        context = initial_context.copy()
        step_results = {}
        steps_executed = []
        steps_failed = []
        steps_skipped = []

        # Build dependency graph
        step_map = {step.name: step for step in steps}

        # Execute steps in dependency order
        for step in self._topological_sort(steps):
            # Check dependencies
            dependencies_met = all(
                dep in steps_executed or dep in steps_skipped
                for dep in step.depends_on
            )

            if not dependencies_met:
                step.status = StepStatus.FAILED
                step.error = "Dependencies not met"
                steps_failed.append(step.name)
                continue

            # Check condition
            if step.condition and not step.condition(context):
                step.status = StepStatus.SKIPPED
                steps_skipped.append(step.name)
                continue

            # Execute step
            step.status = StepStatus.IN_PROGRESS

            try:
                result = await self._execute_step(step, context, step_results)
                step.result = result
                step.status = StepStatus.COMPLETED
                step_results[step.name] = result
                steps_executed.append(step.name)

                # Update context
                context[f"step_{step.name}_result"] = result

            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                steps_failed.append(step.name)

        # Determine final status
        if steps_failed:
            status = "failed" if len(steps_failed) > len(steps_executed) else "partial"
        else:
            status = "completed"

        # Get final output (last step's result or specified output step)
        final_output = step_results.get(steps[-1].name) if steps else None

        end_time = time.time()

        return WorkflowResult(
            workflow_name=workflow_name,
            status=status,
            steps_executed=steps_executed,
            steps_failed=steps_failed,
            steps_skipped=steps_skipped,
            final_output=final_output,
            step_results=step_results,
            total_time_ms=(end_time - start_time) * 1000
        )

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        step_results: Dict[str, Any]
    ) -> Any:
        """Execute a single workflow step"""
        if step.step_type == StepType.AGENT_QUERY:
            return await self._execute_agent_query(step, context)

        elif step.step_type == StepType.PARALLEL:
            return await self._execute_parallel(step, context, step_results)

        elif step.step_type == StepType.SYNTHESIS:
            return await self._execute_synthesis(step, context, step_results)

        elif step.step_type == StepType.VALIDATION:
            return await self._execute_validation(step, context)

        elif step.step_type == StepType.TRANSFORM:
            return await self._execute_transform(step, context)

        else:
            raise ValueError(f"Unknown step type: {step.step_type}")

    async def _execute_agent_query(self, step: WorkflowStep, context: Dict) -> AgentResponse:
        """Execute agent query step"""
        dimension = step.config.get("dimension")
        query = step.config.get("query")

        if not dimension or not query:
            raise ValueError("Agent query step requires 'dimension' and 'query'")

        # Substitute context variables in query
        query = query.format(**context)

        agent = self.agents[dimension]
        response = agent.answer_query(query, context)

        return response

    async def _execute_parallel(
        self,
        step: WorkflowStep,
        context: Dict,
        step_results: Dict
    ) -> Dict[str, AgentResponse]:
        """Execute parallel agent queries"""
        dimensions = step.config.get("dimensions", [])
        query = step.config.get("query")

        if not dimensions or not query:
            raise ValueError("Parallel step requires 'dimensions' and 'query'")

        # Substitute context variables
        query = query.format(**context)

        # Execute in parallel
        with ThreadPoolExecutor(max_workers=len(dimensions)) as executor:
            futures = {}
            for dimension in dimensions:
                agent = self.agents[dimension]
                future = executor.submit(agent.answer_query, query, context)
                futures[dimension] = future

            # Collect results
            results = {}
            for dimension, future in futures.items():
                results[dimension] = future.result()

        return results

    async def _execute_synthesis(
        self,
        step: WorkflowStep,
        context: Dict,
        step_results: Dict
    ) -> str:
        """Synthesize results from multiple steps"""
        source_steps = step.config.get("source_steps", [])

        if not source_steps:
            raise ValueError("Synthesis step requires 'source_steps'")

        # Collect agent responses
        agent_responses = {}
        for source_step in source_steps:
            result = step_results.get(source_step)
            if isinstance(result, AgentResponse):
                # Single agent response
                agent_responses[source_step] = result
            elif isinstance(result, dict):
                # Multiple agent responses (from parallel step)
                agent_responses.update(result)

        # Simple synthesis (concatenate)
        synthesis = "# Synthesized Results\n\n"
        for name, response in agent_responses.items():
            synthesis += f"## {name}\n{response.answer}\n\n"

        return synthesis

    async def _execute_validation(self, step: WorkflowStep, context: Dict) -> bool:
        """Execute validation step"""
        validation_fn = step.config.get("validation_fn")

        if not validation_fn:
            raise ValueError("Validation step requires 'validation_fn'")

        return validation_fn(context)

    async def _execute_transform(self, step: WorkflowStep, context: Dict) -> Any:
        """Execute transform step"""
        transform_fn = step.config.get("transform_fn")

        if not transform_fn:
            raise ValueError("Transform step requires 'transform_fn'")

        return transform_fn(context)

    def _topological_sort(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """
        Sort steps in dependency order using topological sort

        Args:
            steps: List of workflow steps

        Returns:
            Steps sorted in dependency order
        """
        # Build adjacency list
        graph = {step.name: step.depends_on for step in steps}
        step_map = {step.name: step for step in steps}

        # Kahn's algorithm
        in_degree = {step.name: len(step.depends_on) for step in steps}
        queue = [name for name, degree in in_degree.items() if degree == 0]
        sorted_steps = []

        while queue:
            current = queue.pop(0)
            sorted_steps.append(step_map[current])

            # Reduce in-degree for dependent steps
            for step in steps:
                if current in step.depends_on:
                    in_degree[step.name] -= 1
                    if in_degree[step.name] == 0:
                        queue.append(step.name)

        if len(sorted_steps) != len(steps):
            raise ValueError("Circular dependency detected in workflow")

        return sorted_steps

    def _load_templates(self) -> Dict[str, List[WorkflowStep]]:
        """Load pre-built workflow templates"""
        templates = {}

        # Template 1: Investment Evaluation
        templates["investment_evaluation"] = [
            WorkflowStep(
                name="regulatory_check",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "regulatory",
                    "query": "Is this investment allowed: {investment_description}?"
                }
            ),
            WorkflowStep(
                name="operational_check",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "operational",
                    "query": "Do we have procedures for: {investment_description}?"
                },
                depends_on=["regulatory_check"],
                condition=lambda ctx: ctx.get("step_regulatory_check_result", {}).get("confidence", 0) > 0.5
            ),
            WorkflowStep(
                name="expert_analysis",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "domain",
                    "query": "Should we invest in: {investment_description}?"
                },
                depends_on=["regulatory_check", "operational_check"]
            ),
            WorkflowStep(
                name="peer_comparison",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "industry",
                    "query": "What do peers typically do for: {investment_description}?"
                },
                depends_on=["regulatory_check"]
            ),
            WorkflowStep(
                name="final_synthesis",
                step_type=StepType.SYNTHESIS,
                config={
                    "source_steps": ["regulatory_check", "operational_check", "expert_analysis", "peer_comparison"]
                },
                depends_on=["regulatory_check", "operational_check", "expert_analysis", "peer_comparison"]
            )
        ]

        # Template 2: Compliance Review
        templates["compliance_review"] = [
            WorkflowStep(
                name="regulatory_analysis",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "regulatory",
                    "query": "Review for compliance: {proposal}"
                }
            ),
            WorkflowStep(
                name="procedure_validation",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "operational",
                    "query": "Review our procedures for: {proposal}"
                },
                depends_on=["regulatory_analysis"]
            ),
            WorkflowStep(
                name="synthesis",
                step_type=StepType.SYNTHESIS,
                config={
                    "source_steps": ["regulatory_analysis", "procedure_validation"]
                },
                depends_on=["regulatory_analysis", "procedure_validation"]
            )
        ]

        # Template 3: Strategy Assessment
        templates["strategy_assessment"] = [
            WorkflowStep(
                name="parallel_evaluation",
                step_type=StepType.PARALLEL,
                config={
                    "dimensions": ["regulatory", "domain", "industry"],
                    "query": "Evaluate this strategy: {strategy_description}"
                }
            ),
            WorkflowStep(
                name="operational_feasibility",
                step_type=StepType.AGENT_QUERY,
                config={
                    "dimension": "operational",
                    "query": "Can we operationally support: {strategy_description}?"
                },
                depends_on=["parallel_evaluation"]
            ),
            WorkflowStep(
                name="synthesis",
                step_type=StepType.SYNTHESIS,
                config={
                    "source_steps": ["parallel_evaluation", "operational_feasibility"]
                },
                depends_on=["parallel_evaluation", "operational_feasibility"]
            )
        ]

        return templates

    async def execute_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> WorkflowResult:
        """
        Execute a pre-built workflow template

        Args:
            template_name: Name of template to execute
            context: Context variables for template

        Returns:
            WorkflowResult
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.templates.keys())}")

        steps = self.templates[template_name]
        return await self.execute_workflow(steps, context, workflow_name=template_name)

    def list_templates(self) -> List[str]:
        """List available workflow templates"""
        return list(self.templates.keys())

    def describe_template(self, template_name: str) -> str:
        """
        Get description of a workflow template

        Args:
            template_name: Template name

        Returns:
            Human-readable description
        """
        if template_name not in self.templates:
            return f"Unknown template: {template_name}"

        steps = self.templates[template_name]

        description = f"""
Workflow Template: {template_name}
{'='*50}

Steps ({len(steps)}):
"""

        for i, step in enumerate(steps, 1):
            description += f"\n{i}. {step.name} ({step.step_type.value})"
            if step.depends_on:
                description += f"\n   Depends on: {', '.join(step.depends_on)}"
            if step.condition:
                description += f"\n   Conditional: Yes"

        return description.strip()


# Example usage
if __name__ == "__main__":
    import os
    import asyncio

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)

    async def main():
        # Initialize workflow engine
        engine = WorkflowEngine(api_key)

        print("=" * 70)
        print("WORKFLOW ENGINE EXAMPLE")
        print("=" * 70)

        # List available templates
        print("\nAvailable Templates:")
        for template in engine.list_templates():
            print(f"  • {template}")

        # Describe a template
        print("\n" + engine.describe_template("investment_evaluation"))

        # Execute template
        print("\n" + "=" * 70)
        print("EXECUTING: investment_evaluation")
        print("=" * 70)

        context = {
            "investment_description": "15% allocation to emerging market corporate bonds"
        }

        result = await engine.execute_template("investment_evaluation", context)

        print(f"\nStatus: {result.status}")
        print(f"Steps Executed: {len(result.steps_executed)}")
        print(f"Steps Failed: {len(result.steps_failed)}")
        print(f"Total Time: {result.total_time_ms:.0f}ms")

        print("\n" + "-" * 70)
        print("FINAL OUTPUT:")
        print("-" * 70)
        print(result.final_output)

    asyncio.run(main())
