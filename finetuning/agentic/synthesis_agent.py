"""
Synthesis Agent - Intelligent Multi-Perspective Combination

This module provides sophisticated synthesis of multiple dimension agent responses
into cohesive, actionable answers.

The synthesis agent:
1. Identifies agreements and conflicts across dimensions
2. Weights perspectives based on query type
3. Resolves contradictions
4. Generates actionable recommendations
5. Highlights key risks and considerations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import anthropic

from .dimension_agents import AgentResponse


class SynthesisMode(Enum):
    """How to synthesize multiple perspectives"""
    CONSENSUS = "consensus"              # Highlight agreements
    COMPREHENSIVE = "comprehensive"      # Show all perspectives
    DECISION = "decision"                # Make clear recommendation
    RISK_FOCUSED = "risk_focused"        # Emphasize risks and warnings
    ACTIONABLE = "actionable"            # Focus on next steps


@dataclass
class SynthesisResult:
    """Result of synthesizing multiple agent responses"""
    query: str
    synthesis_mode: SynthesisMode
    final_answer: str
    key_agreements: List[str]
    key_conflicts: List[str]
    critical_warnings: List[str]
    recommended_action: Optional[str]
    confidence: float
    dimension_weights: Dict[str, float]


class SynthesisAgent:
    """
    Synthesizes responses from multiple dimension agents into coherent answers

    Uses Claude to intelligently combine perspectives, resolve conflicts,
    and generate actionable recommendations.
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize synthesis agent

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        self.system_prompt = """You are a SYNTHESIS EXPERT specializing in combining multiple expert perspectives into coherent, actionable answers.

Your role is to:
1. Identify agreements across dimensions
2. Highlight conflicts and contradictions
3. Resolve conflicts using sound reasoning
4. Weight perspectives appropriately based on query type
5. Generate clear, actionable recommendations
6. Emphasize critical risks and warnings

When synthesizing:
- Regulatory constraints are HARD LIMITS (cannot be violated)
- Operational feasibility is PRACTICAL (can be changed but takes time)
- Domain expertise provides JUDGMENT (subject to debate)
- Industry standards provide CONTEXT (what's normal vs exceptional)

Be clear about:
- What CAN be done (regulatory compliance)
- What SHOULD be done (expert judgment)
- What IS TYPICALLY done (market practice)
- What RISKS exist (warnings from all dimensions)"""

    def synthesize(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse],
        mode: SynthesisMode = SynthesisMode.COMPREHENSIVE,
        dimension_weights: Optional[Dict[str, float]] = None
    ) -> SynthesisResult:
        """
        Synthesize multiple agent responses

        Args:
            query: Original query
            agent_responses: Dict mapping dimension -> AgentResponse
            mode: Synthesis mode
            dimension_weights: Optional custom weights (default: equal)

        Returns:
            SynthesisResult with synthesized answer
        """
        # Default equal weights if not provided
        if dimension_weights is None:
            dimension_weights = {dim: 1.0/len(agent_responses) for dim in agent_responses.keys()}

        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(
            query,
            agent_responses,
            mode,
            dimension_weights
        )

        # Call Claude to synthesize
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[{"role": "user", "content": synthesis_prompt}]
            )

            response_text = message.content[0].text

            # Parse synthesis response
            return self._parse_synthesis(query, response_text, mode, dimension_weights)

        except Exception as e:
            # Fallback to simple concatenation
            return self._simple_synthesis(query, agent_responses, mode, dimension_weights)

    def _build_synthesis_prompt(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse],
        mode: SynthesisMode,
        dimension_weights: Dict[str, float]
    ) -> str:
        """Build prompt for synthesis"""
        prompt = f"""Synthesize these expert perspectives into a cohesive answer.

Query: "{query}"

Synthesis Mode: {mode.value.replace('_', ' ').title()}

Expert Perspectives:
"""

        # Add each perspective
        for dimension, response in agent_responses.items():
            weight = dimension_weights.get(dimension, 1.0)
            prompt += f"""
{'='*60}
{dimension.upper()} Expert (weight: {weight:.0%})
Confidence: {response.confidence:.0%}
{'='*60}

{response.answer}

"""
            if response.warnings:
                prompt += "⚠️ WARNINGS:\n"
                for warning in response.warnings:
                    prompt += f"  - {warning}\n"
                prompt += "\n"

            if response.sources:
                prompt += "📚 SOURCES:\n"
                for source in response.sources:
                    prompt += f"  - {source}\n"
                prompt += "\n"

        # Mode-specific instructions
        if mode == SynthesisMode.CONSENSUS:
            prompt += """
Focus on CONSENSUS - highlight where experts agree.
Minimize conflicts unless critical.
"""
        elif mode == SynthesisMode.COMPREHENSIVE:
            prompt += """
Provide COMPREHENSIVE view - show all perspectives.
Explain any conflicts and how to resolve them.
"""
        elif mode == SynthesisMode.DECISION:
            prompt += """
Make a clear DECISION - provide definitive recommendation.
Explain reasoning and account for all perspectives.
"""
        elif mode == SynthesisMode.RISK_FOCUSED:
            prompt += """
Focus on RISKS - emphasize all warnings and concerns.
Highlight what could go wrong.
"""
        elif mode == SynthesisMode.ACTIONABLE:
            prompt += """
Focus on ACTIONABLE next steps.
What specifically should be done? By whom? When?
"""

        prompt += """
Provide your synthesis in this format:

SYNTHESIS:
[Your synthesized answer combining all perspectives]

AGREEMENTS:
[Key points where experts agree]

CONFLICTS:
[Any conflicts or contradictions between perspectives]

CRITICAL_WARNINGS:
[Most important warnings across all dimensions]

RECOMMENDED_ACTION:
[Clear recommended action, if applicable]

CONFIDENCE: [0.0-1.0]
"""

        return prompt

    def _parse_synthesis(
        self,
        query: str,
        response_text: str,
        mode: SynthesisMode,
        dimension_weights: Dict[str, float]
    ) -> SynthesisResult:
        """Parse Claude's synthesis response"""
        import re

        # Extract synthesis
        synthesis_match = re.search(
            r'SYNTHESIS:\s*(.+?)(?=\n(?:AGREEMENTS|CONFLICTS|CRITICAL_WARNINGS|RECOMMENDED_ACTION|CONFIDENCE|$))',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        final_answer = synthesis_match.group(1).strip() if synthesis_match else response_text

        # Extract agreements
        agreements_match = re.search(
            r'AGREEMENTS:\s*(.+?)(?=\n(?:CONFLICTS|CRITICAL_WARNINGS|RECOMMENDED_ACTION|CONFIDENCE|$))',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        agreements = []
        if agreements_match:
            agreements = [
                a.strip().lstrip('- ')
                for a in agreements_match.group(1).split('\n')
                if a.strip() and a.strip() != '- None' and 'none' not in a.lower()[:10]
            ]

        # Extract conflicts
        conflicts_match = re.search(
            r'CONFLICTS:\s*(.+?)(?=\n(?:CRITICAL_WARNINGS|RECOMMENDED_ACTION|CONFIDENCE|$))',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        conflicts = []
        if conflicts_match:
            conflicts = [
                c.strip().lstrip('- ')
                for c in conflicts_match.group(1).split('\n')
                if c.strip() and c.strip() != '- None' and 'none' not in c.lower()[:10]
            ]

        # Extract critical warnings
        warnings_match = re.search(
            r'CRITICAL_WARNINGS:\s*(.+?)(?=\n(?:RECOMMENDED_ACTION|CONFIDENCE|$))',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        warnings = []
        if warnings_match:
            warnings = [
                w.strip().lstrip('- ')
                for w in warnings_match.group(1).split('\n')
                if w.strip() and w.strip() != '- None' and 'none' not in w.lower()[:10]
            ]

        # Extract recommended action
        action_match = re.search(
            r'RECOMMENDED_ACTION:\s*(.+?)(?=\nCONFIDENCE|$)',
            response_text,
            re.DOTALL | re.IGNORECASE
        )
        recommended_action = None
        if action_match:
            action = action_match.group(1).strip()
            if action and 'none' not in action.lower()[:10]:
                recommended_action = action

        # Extract confidence
        conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', response_text)
        confidence = float(conf_match.group(1)) if conf_match else 0.8

        return SynthesisResult(
            query=query,
            synthesis_mode=mode,
            final_answer=final_answer,
            key_agreements=agreements,
            key_conflicts=conflicts,
            critical_warnings=warnings,
            recommended_action=recommended_action,
            confidence=confidence,
            dimension_weights=dimension_weights
        )

    def _simple_synthesis(
        self,
        query: str,
        agent_responses: Dict[str, AgentResponse],
        mode: SynthesisMode,
        dimension_weights: Dict[str, float]
    ) -> SynthesisResult:
        """Fallback simple synthesis without Claude"""
        # Concatenate answers
        final_answer = f"# Multi-Perspective Answer: {query}\n\n"

        for dimension, response in agent_responses.items():
            final_answer += f"## {dimension.upper()}\n{response.answer}\n\n"

        # Collect all warnings
        all_warnings = []
        for response in agent_responses.values():
            all_warnings.extend(response.warnings)

        # Average confidence
        avg_confidence = sum(r.confidence for r in agent_responses.values()) / len(agent_responses)

        return SynthesisResult(
            query=query,
            synthesis_mode=mode,
            final_answer=final_answer,
            key_agreements=[],
            key_conflicts=[],
            critical_warnings=all_warnings,
            recommended_action=None,
            confidence=avg_confidence,
            dimension_weights=dimension_weights
        )

    def format_synthesis(self, result: SynthesisResult) -> str:
        """
        Format synthesis result for display

        Args:
            result: SynthesisResult to format

        Returns:
            Formatted string
        """
        output = f"""
🎯 Synthesized Answer
====================

Query: "{result.query}"
Mode: {result.synthesis_mode.value.replace('_', ' ').title()}
Confidence: {result.confidence:.0%}

{result.final_answer}

"""

        if result.key_agreements:
            output += """
✅ Key Agreements
----------------
"""
            for agreement in result.key_agreements:
                output += f"• {agreement}\n"
            output += "\n"

        if result.key_conflicts:
            output += """
⚠️ Conflicts to Resolve
----------------------
"""
            for conflict in result.key_conflicts:
                output += f"• {conflict}\n"
            output += "\n"

        if result.critical_warnings:
            output += """
🚨 Critical Warnings
-------------------
"""
            for warning in result.critical_warnings:
                output += f"• {warning}\n"
            output += "\n"

        if result.recommended_action:
            output += """
👉 Recommended Action
--------------------
"""
            output += result.recommended_action + "\n\n"

        # Show dimension weights
        output += "📊 Dimension Weights\n"
        output += "-------------------\n"
        for dimension, weight in sorted(result.dimension_weights.items(), key=lambda x: -x[1]):
            bar = "█" * int(weight * 20)
            output += f"{dimension:12s}: {bar} {weight:.0%}\n"

        return output.strip()


# Example usage
if __name__ == "__main__":
    import os
    from .dimension_agents import RegulatoryAgent, OperationalAgent, DomainExpertAgent, IndustryAgent

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)

    # Create agents
    regulatory = RegulatoryAgent(api_key)
    operational = OperationalAgent(api_key)
    domain = DomainExpertAgent(api_key)
    industry = IndustryAgent(api_key)

    # Test query
    query = "Should we invest 15% of the UCITS fund in emerging market corporate bonds?"

    print("=" * 70)
    print("SYNTHESIS AGENT EXAMPLE")
    print("=" * 70)
    print(f"\nQuery: {query}\n")

    # Get responses from all agents
    print("Gathering expert perspectives...\n")

    agent_responses = {
        "regulatory": regulatory.answer_query(query),
        "operational": operational.answer_query(query),
        "domain": domain.answer_query(query),
        "industry": industry.answer_query(query),
    }

    # Synthesize
    synthesizer = SynthesisAgent(api_key)

    # Try different synthesis modes
    modes = [
        SynthesisMode.COMPREHENSIVE,
        SynthesisMode.DECISION,
        SynthesisMode.RISK_FOCUSED,
    ]

    for mode in modes:
        print("\n" + "=" * 70)
        print(f"SYNTHESIS MODE: {mode.value.upper()}")
        print("=" * 70)

        result = synthesizer.synthesize(query, agent_responses, mode)
        print(synthesizer.format_synthesis(result))
        print()
