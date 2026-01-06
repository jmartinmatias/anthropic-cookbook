"""
Dimension Agents - Four Specialized Expert Agents

This module provides four specialized agents, one for each dimension of expertise:
1. RegulatoryAgent: WHAT rules require (compliance, regulations)
2. OperationalAgent: HOW to do it (procedures, workflows)
3. DomainExpertAgent: WHY decisions are made (strategies, judgment)
4. IndustryAgent: WHAT everyone does (market practices)

Each agent has:
- Knowledge base specific to their dimension
- Specialized prompting
- Tool access for their dimension
- Capability to critique other agents' outputs
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import anthropic
import sys
import os

# Add parent directory to path to import dimension modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from generate_eu_funds_training_data import EUFundsTrainingDataGenerator
    from operational_procedures import OperationalProcedureParser, OperationalTrainingGenerator
    from domain_expertise import DomainExpertiseParser, DomainExpertiseGenerator
    from industry_standards import IndustryStandardsParser, IndustryStandardsGenerator
except ImportError:
    # Graceful degradation if modules not available
    EUFundsTrainingDataGenerator = None
    OperationalProcedureParser = None
    DomainExpertiseParser = None
    IndustryStandardsParser = None


class AgentRole(Enum):
    """Agent role in multi-agent interaction"""
    PRIMARY = "primary"        # Main agent answering the query
    REVIEWER = "reviewer"      # Reviewing another agent's output
    CONTRIBUTOR = "contributor"  # Contributing to multi-agent answer


@dataclass
class AgentResponse:
    """Response from a dimension agent"""
    dimension: str
    answer: str
    confidence: float
    sources: List[str]
    warnings: List[str]
    follow_up_questions: List[str]
    requires_other_dimensions: List[str]


class BaseDimensionAgent:
    """
    Base class for dimension agents

    All specialized agents inherit from this and override:
    - system_prompt
    - knowledge_sources
    - answer_query method
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize agent

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
        self.dimension_name = "base"
        self.system_prompt = "You are a helpful assistant."

    def answer_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        role: AgentRole = AgentRole.PRIMARY
    ) -> AgentResponse:
        """
        Answer a query from this dimension's perspective

        Args:
            query: User query
            context: Additional context (e.g., from other agents)
            role: Agent's role in this interaction

        Returns:
            AgentResponse with answer and metadata
        """
        # Build prompt based on role
        if role == AgentRole.PRIMARY:
            prompt = self._build_primary_prompt(query, context)
        elif role == AgentRole.REVIEWER:
            prompt = self._build_reviewer_prompt(query, context)
        else:
            prompt = self._build_contributor_prompt(query, context)

        # Call Claude
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Parse response
            return self._parse_response(response_text)

        except Exception as e:
            return AgentResponse(
                dimension=self.dimension_name,
                answer=f"Error: {str(e)}",
                confidence=0.0,
                sources=[],
                warnings=[f"Agent error: {str(e)}"],
                follow_up_questions=[],
                requires_other_dimensions=[]
            )

    def _build_primary_prompt(self, query: str, context: Optional[Dict] = None) -> str:
        """Build prompt when agent is primary responder"""
        prompt = f"""You are answering this query from the {self.dimension_name.upper()} perspective.

Query: {query}
"""
        if context:
            prompt += f"\nAdditional Context: {context}\n"

        prompt += """
Provide your answer in this format:

ANSWER:
[Your detailed answer]

CONFIDENCE: [0.0-1.0]
SOURCES: [List any regulations, procedures, or references]
WARNINGS: [Any caveats or warnings]
FOLLOW_UP: [Suggested follow-up questions]
OTHER_DIMENSIONS: [List any other dimensions that should weigh in]
"""
        return prompt

    def _build_reviewer_prompt(self, query: str, context: Optional[Dict] = None) -> str:
        """Build prompt when agent is reviewing another agent's answer"""
        other_answer = context.get('answer_to_review', '') if context else ''

        return f"""You are reviewing an answer from the {self.dimension_name.upper()} perspective.

Original Query: {query}

Answer to Review:
{other_answer}

Provide your review in this format:

REVIEW:
[Your review and any concerns from {self.dimension_name} perspective]

ISSUES: [Any compliance/operational/domain/industry issues you see]
SUGGESTIONS: [How to improve the answer]
APPROVAL: [yes/no - whether this answer is acceptable from your dimension]
"""

    def _build_contributor_prompt(self, query: str, context: Optional[Dict] = None) -> str:
        """Build prompt when agent is contributing to multi-agent answer"""
        return f"""You are contributing to a multi-agent answer from the {self.dimension_name.upper()} perspective.

Query: {query}

Other agents' contributions:
{context.get('other_contributions', '') if context else 'None yet'}

Provide your contribution focusing specifically on the {self.dimension_name} aspects:

CONTRIBUTION:
[Your specific contribution from {self.dimension_name} perspective]
"""

    def _parse_response(self, response_text: str) -> AgentResponse:
        """Parse Claude's response into AgentResponse"""
        import re

        # Extract answer
        answer_match = re.search(r'ANSWER:\s*(.+?)(?=\n(?:CONFIDENCE|SOURCES|WARNINGS|FOLLOW_UP|OTHER_DIMENSIONS|$))', response_text, re.DOTALL | re.IGNORECASE)
        answer = answer_match.group(1).strip() if answer_match else response_text

        # Extract confidence
        conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', response_text)
        confidence = float(conf_match.group(1)) if conf_match else 0.8

        # Extract sources
        sources_match = re.search(r'SOURCES:\s*(.+?)(?=\n(?:WARNINGS|FOLLOW_UP|OTHER_DIMENSIONS|$))', response_text, re.DOTALL | re.IGNORECASE)
        sources = [s.strip() for s in sources_match.group(1).split('\n') if s.strip()] if sources_match else []

        # Extract warnings
        warnings_match = re.search(r'WARNINGS:\s*(.+?)(?=\n(?:FOLLOW_UP|OTHER_DIMENSIONS|$))', response_text, re.DOTALL | re.IGNORECASE)
        warnings = [w.strip() for w in warnings_match.group(1).split('\n') if w.strip()] if warnings_match else []

        # Extract follow-up questions
        followup_match = re.search(r'FOLLOW_UP:\s*(.+?)(?=\nOTHER_DIMENSIONS|$)', response_text, re.DOTALL | re.IGNORECASE)
        follow_up = [q.strip() for q in followup_match.group(1).split('\n') if q.strip()] if followup_match else []

        # Extract other dimensions needed
        other_match = re.search(r'OTHER_DIMENSIONS:\s*(.+?)$', response_text, re.DOTALL | re.IGNORECASE)
        other_dims = [d.strip() for d in other_match.group(1).split(',') if d.strip()] if other_match else []

        return AgentResponse(
            dimension=self.dimension_name,
            answer=answer,
            confidence=confidence,
            sources=sources,
            warnings=warnings,
            follow_up_questions=follow_up,
            requires_other_dimensions=other_dims
        )


class RegulatoryAgent(BaseDimensionAgent):
    """
    Regulatory Expert Agent

    Focuses on: WHAT rules require
    - EU regulations (UCITS, AIFMD, SFDR, MiFID II, PRIIPs)
    - Compliance requirements
    - Legal restrictions
    - Regulatory interpretations
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.dimension_name = "regulatory"
        self.system_prompt = """You are a REGULATORY EXPERT for EU investment funds with deep knowledge of:

- UCITS Directive (2009/65/EC and amendments)
- AIFMD (Alternative Investment Fund Managers Directive)
- SFDR (Sustainable Finance Disclosure Regulation)
- MiFID II (Markets in Financial Instruments Directive)
- PRIIPs Regulation
- Taxonomy Regulation
- ELTIF Regulation
- EMIR (European Market Infrastructure Regulation)
- Prospectus Regulation

Your role is to:
1. Assess regulatory compliance
2. Identify applicable regulations and articles
3. Flag potential compliance risks
4. Provide clear compliance guidance
5. Reference specific regulations and articles

Always cite specific regulations, articles, and annexes. Be precise about compliance requirements.
If something is not clearly regulated, say so - don't invent requirements.

When reviewing proposals from other dimensions (operational, domain expertise, industry),
critically evaluate them for regulatory compliance and flag any issues."""

    def get_regulatory_context(self) -> str:
        """Get regulatory context for enhanced answers"""
        return """
Key EU Investment Fund Regulations:

UCITS (Undertakings for Collective Investment in Transferable Securities):
- Article 50: Risk-spreading rules (5/10/40 limits)
- Article 51: Borrowing limits (10% temporary)
- Article 52: Eligible assets
- Article 85: NAV calculation requirements

AIFMD (Alternative Investment Fund Managers Directive):
- Article 12: Investment in securitization positions
- Article 15: Valuation
- Article 16: Delegation
- Article 23: Annual reports

SFDR (Sustainable Finance Disclosure Regulation):
- Article 6: Sustainability risk integration
- Article 8: Light green funds
- Article 9: Dark green funds
- Article 10: Website disclosures

MiFID II:
- Article 24: Best execution
- Article 25: Suitability assessment
- Article 27: Client order handling
"""


class OperationalAgent(BaseDimensionAgent):
    """
    Operational Expert Agent

    Focuses on: HOW to do it
    - Standard Operating Procedures (SOPs)
    - Workflows and processes
    - Step-by-step guidance
    - Roles and responsibilities
    - Timing and frequency
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.dimension_name = "operational"
        self.system_prompt = """You are an OPERATIONAL PROCEDURES EXPERT for investment fund operations with deep knowledge of:

- NAV calculation procedures
- Trade settlement workflows
- Reconciliation processes
- Reporting procedures
- Risk monitoring workflows
- Client onboarding processes
- Escalation procedures

Your role is to:
1. Provide clear step-by-step procedures
2. Identify responsible parties and roles
3. Specify timing and deadlines
4. Highlight controls and checkpoints
5. Reference relevant SOPs and runbooks
6. Ensure procedures align with regulations

Always be specific about:
- WHO does what
- WHEN it should be done
- HOW to do it (exact steps)
- WHAT controls exist
- WHERE to escalate issues

When reviewing proposals from other dimensions, ensure they are operationally feasible
and that required procedures exist or can be created."""

    def get_common_procedures(self) -> List[str]:
        """Get list of common fund operation procedures"""
        return [
            "NAV Calculation (Daily)",
            "Trade Settlement (T+2)",
            "Cash Reconciliation (Daily)",
            "Position Reconciliation (Daily)",
            "Pricing Verification (Daily)",
            "Regulatory Reporting (Monthly/Quarterly)",
            "Client Reporting (Monthly)",
            "Risk Limit Monitoring (Real-time)",
            "Breach Escalation (As needed)",
            "Client Onboarding (As needed)",
            "Redemption Processing (Daily)",
            "Subscription Processing (Daily)",
        ]


class DomainExpertAgent(BaseDimensionAgent):
    """
    Domain Expertise Agent

    Focuses on: WHY decisions are made
    - Investment strategies
    - Risk management frameworks
    - Portfolio construction principles
    - Market analysis
    - Expert judgment and best practices
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.dimension_name = "domain"
        self.system_prompt = """You are a DOMAIN EXPERTISE specialist - a senior investment professional with 20+ years experience in:

- Investment strategy design (value, growth, momentum, factor investing)
- Portfolio construction and optimization
- Risk management frameworks
- Asset allocation strategies
- Performance attribution
- Market cycle analysis
- Behavioral finance

Your role is to:
1. Provide expert investment judgment
2. Explain the "why" behind decisions
3. Share best practices from experience
4. Assess investment rationale
5. Evaluate risk/return trade-offs
6. Consider market context and cycles

Always explain your reasoning:
- WHY this approach makes sense
- WHAT are the risks and trade-offs
- HOW it fits the investment philosophy
- WHEN this strategy works (and doesn't)

You have strong opinions based on experience, but remain humble about uncertainty.
When reviewing proposals from other dimensions, evaluate them for investment soundness
and strategic fit."""

    def get_investment_frameworks(self) -> List[str]:
        """Get list of common investment frameworks"""
        return [
            "Value Investing (Graham-Dodd)",
            "Growth Investing",
            "Momentum Investing",
            "Quality Investing",
            "Factor Investing (Multi-factor)",
            "Risk Parity",
            "Core-Satellite Strategy",
            "Tactical Asset Allocation",
            "Strategic Asset Allocation",
            "Absolute Return Strategies",
            "Long/Short Equity",
            "Market Neutral",
        ]


class IndustryAgent(BaseDimensionAgent):
    """
    Industry Standards Agent

    Focuses on: WHAT everyone does
    - Market conventions
    - Settlement practices
    - Pricing standards
    - Documentation standards
    - Peer practices
    - Technology standards
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.dimension_name = "industry"
        self.system_prompt = """You are an INDUSTRY STANDARDS expert with comprehensive knowledge of:

- Market conventions and practices
- Settlement standards (T+2, T+1, etc.)
- Pricing conventions (clean/dirty, day count)
- Documentation standards (ISDA, ICMA, ISLA)
- Technology standards (FIX, SWIFT, ISO 20022)
- Peer practices and benchmarks
- Geographic differences in practices

Your role is to:
1. Explain standard market practices
2. Identify what competitors/peers typically do
3. Highlight geographic or asset class variations
4. Reference industry associations (ISDA, ICMA, etc.)
5. Provide context on why practices exist
6. Flag departures from market norms

Always specify:
- WHAT the standard practice is
- WHO follows it (geographic/asset class specificity)
- WHY it became standard
- WHEN it applies
- VARIATIONS across markets/asset classes

When reviewing proposals from other dimensions, check whether they align with
industry norms and flag significant departures (which may create operational friction)."""

    def get_market_standards(self) -> Dict[str, str]:
        """Get common market standards"""
        return {
            "Equity Settlement": "T+2 (US, Europe), T+1 (moving to), T+0 (China A-shares)",
            "Bond Settlement": "T+1 (government), T+2 (corporate), varies by market",
            "FX Spot": "T+2",
            "FX Forward": "As agreed",
            "Repo": "Varies (overnight to term)",
            "Bond Pricing": "Clean price quoted, dirty price settled (accrued interest)",
            "Day Count": "30/360 (corporate bonds), Actual/Actual (government bonds)",
            "Trade Confirmation": "T+0 (same day)",
            "Documentation": "ISDA (derivatives), GMRA (repo), GMSLA (securities lending)",
            "Messaging": "SWIFT (cross-border), FIX (trading), ISO 20022 (payments)",
            "Typical Management Fees": "1.0-2.0% for active equity, 0.5-1.0% for active fixed income",
            "Performance Fees": "10-20% above high water mark (hedge funds)",
        }


# Example usage
if __name__ == "__main__":
    import os

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
    print("DIMENSION AGENTS EXAMPLE")
    print("=" * 70)
    print(f"\nQuery: {query}\n")

    # Get each agent's perspective
    print("\n" + "=" * 70)
    print("REGULATORY PERSPECTIVE")
    print("=" * 70)
    reg_response = regulatory.answer_query(query)
    print(f"\nAnswer:\n{reg_response.answer}")
    print(f"\nConfidence: {reg_response.confidence:.0%}")
    if reg_response.warnings:
        print(f"\nWarnings:\n" + "\n".join(f"  ⚠️  {w}" for w in reg_response.warnings))

    print("\n" + "=" * 70)
    print("OPERATIONAL PERSPECTIVE")
    print("=" * 70)
    op_response = operational.answer_query(query)
    print(f"\nAnswer:\n{op_response.answer}")

    print("\n" + "=" * 70)
    print("DOMAIN EXPERT PERSPECTIVE")
    print("=" * 70)
    dom_response = domain.answer_query(query)
    print(f"\nAnswer:\n{dom_response.answer}")

    print("\n" + "=" * 70)
    print("INDUSTRY PERSPECTIVE")
    print("=" * 70)
    ind_response = industry.answer_query(query)
    print(f"\nAnswer:\n{ind_response.answer}")
