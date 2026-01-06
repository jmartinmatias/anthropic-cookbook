"""
Domain Expertise Extension for EU Funds Fine-tuning

This module captures subject matter expertise from domain documents:
- Investment strategies and rationales
- Portfolio construction methodologies
- Risk management frameworks
- Market analysis and insights
- Best practices and conventions
- Decision-making frameworks
- Asset class expertise

Transforms domain documents into training data that teaches expert judgment,
not just rules and procedures.
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DomainAreaType(Enum):
    """Types of domain expertise areas"""
    INVESTMENT_STRATEGY = "Investment Strategy"
    PORTFOLIO_CONSTRUCTION = "Portfolio Construction"
    RISK_MANAGEMENT = "Risk Management"
    ASSET_CLASS = "Asset Class Expertise"
    MARKET_ANALYSIS = "Market Analysis"
    PERFORMANCE_ATTRIBUTION = "Performance Attribution"
    ESG_INTEGRATION = "ESG Integration"
    DERIVATIVES_USAGE = "Derivatives Usage"
    LIQUIDITY_MANAGEMENT = "Liquidity Management"
    VALUATION = "Valuation"


class DocumentType(Enum):
    """Types of domain documents"""
    INVESTMENT_MEMO = "Investment Committee Memo"
    RESEARCH_REPORT = "Research Report"
    STRATEGY_GUIDE = "Strategy Guide"
    RISK_REPORT = "Risk Report"
    POLICY_DOCUMENT = "Investment Policy"
    MARKET_COMMENTARY = "Market Commentary"
    BEST_PRACTICES = "Best Practices Guide"
    CASE_STUDY = "Case Study"
    DECISION_FRAMEWORK = "Decision Framework"
    PLAYBOOK = "Investment Playbook"


@dataclass
class DomainDocument:
    """Represents a domain expertise document"""
    title: str
    doc_type: DocumentType
    domain_area: DomainAreaType
    content: str
    key_concepts: List[str]
    principles: List[str]
    examples: List[str]
    decision_criteria: List[str]
    best_practices: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class DomainExpertiseParser:
    """Parse domain expertise documents"""

    CONCEPT_PATTERNS = [
        r'Key concept[s]?:\s*(.+)',
        r'Important:\s*(.+)',
        r'Principle:\s*(.+)',
        r'Definition:\s*(.+)'
    ]

    BEST_PRACTICE_PATTERNS = [
        r'Best practice[s]?:\s*(.+)',
        r'Recommendation[s]?:\s*(.+)',
        r'Guideline[s]?:\s*(.+)',
        r'Should:\s*(.+)',
        r'Always:\s*(.+)'
    ]

    WARNING_PATTERNS = [
        r'Warning[s]?:\s*(.+)',
        r'Risk[s]?:\s*(.+)',
        r'Avoid:\s*(.+)',
        r'Never:\s*(.+)',
        r'Pitfall[s]?:\s*(.+)',
        r'Common mistake[s]?:\s*(.+)'
    ]

    EXAMPLE_PATTERNS = [
        r'Example:\s*(.+)',
        r'For instance[,]?\s*(.+)',
        r'Case study:\s*(.+)',
        r'Consider:\s*(.+)'
    ]

    def parse_domain_document(
        self,
        content: str,
        title: str = "",
        doc_type: Optional[DocumentType] = None,
        domain_area: Optional[DomainAreaType] = None
    ) -> DomainDocument:
        """Parse a domain expertise document"""

        # Auto-detect document type if not provided
        if not doc_type:
            doc_type = self._detect_doc_type(content)

        # Auto-detect domain area if not provided
        if not domain_area:
            domain_area = self._detect_domain_area(content)

        # Extract components
        key_concepts = self._extract_patterns(content, self.CONCEPT_PATTERNS)
        best_practices = self._extract_patterns(content, self.BEST_PRACTICE_PATTERNS)
        warnings = self._extract_patterns(content, self.WARNING_PATTERNS)
        examples = self._extract_patterns(content, self.EXAMPLE_PATTERNS)
        principles = self._extract_principles(content)
        decision_criteria = self._extract_decision_criteria(content)

        return DomainDocument(
            title=title or self._extract_title(content),
            doc_type=doc_type,
            domain_area=domain_area,
            content=content,
            key_concepts=key_concepts,
            principles=principles,
            examples=examples,
            decision_criteria=decision_criteria,
            best_practices=best_practices,
            warnings=warnings,
            metadata={}
        )

    def _detect_doc_type(self, content: str) -> DocumentType:
        """Detect document type from content"""
        content_lower = content.lower()

        if "investment committee" in content_lower or "ic memo" in content_lower:
            return DocumentType.INVESTMENT_MEMO
        elif "research report" in content_lower or "analyst report" in content_lower:
            return DocumentType.RESEARCH_REPORT
        elif "strategy guide" in content_lower or "investment strategy" in content_lower:
            return DocumentType.STRATEGY_GUIDE
        elif "risk report" in content_lower or "risk analysis" in content_lower:
            return DocumentType.RISK_REPORT
        elif "investment policy" in content_lower or "ips" in content_lower:
            return DocumentType.POLICY_DOCUMENT
        elif "market commentary" in content_lower or "outlook" in content_lower:
            return DocumentType.MARKET_COMMENTARY
        elif "best practices" in content_lower:
            return DocumentType.BEST_PRACTICES
        elif "case study" in content_lower:
            return DocumentType.CASE_STUDY
        elif "framework" in content_lower or "methodology" in content_lower:
            return DocumentType.DECISION_FRAMEWORK
        else:
            return DocumentType.PLAYBOOK

    def _detect_domain_area(self, content: str) -> DomainAreaType:
        """Detect domain area from content"""
        content_lower = content.lower()

        domain_keywords = {
            DomainAreaType.INVESTMENT_STRATEGY: ["investment strategy", "strategy", "approach"],
            DomainAreaType.PORTFOLIO_CONSTRUCTION: ["portfolio construction", "asset allocation", "portfolio"],
            DomainAreaType.RISK_MANAGEMENT: ["risk management", "risk", "var", "volatility"],
            DomainAreaType.ASSET_CLASS: ["equity", "fixed income", "bonds", "alternatives"],
            DomainAreaType.MARKET_ANALYSIS: ["market analysis", "market view", "outlook"],
            DomainAreaType.PERFORMANCE_ATTRIBUTION: ["performance", "attribution", "returns"],
            DomainAreaType.ESG_INTEGRATION: ["esg", "sustainability", "environmental", "social"],
            DomainAreaType.DERIVATIVES_USAGE: ["derivatives", "options", "futures", "swaps"],
            DomainAreaType.LIQUIDITY_MANAGEMENT: ["liquidity", "redemption", "cash management"],
            DomainAreaType.VALUATION: ["valuation", "pricing", "fair value"]
        }

        # Count keyword matches
        matches = {}
        for area, keywords in domain_keywords.items():
            count = sum(1 for keyword in keywords if keyword in content_lower)
            matches[area] = count

        # Return area with most matches
        return max(matches.items(), key=lambda x: x[1])[0] if matches else DomainAreaType.INVESTMENT_STRATEGY

    def _extract_patterns(self, content: str, patterns: List[str]) -> List[str]:
        """Extract text matching patterns"""
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            results.extend([match.strip() for match in matches if match.strip()])
        return list(set(results))  # Remove duplicates

    def _extract_principles(self, content: str) -> List[str]:
        """Extract investment principles"""
        principles = []

        # Look for numbered principles
        numbered = re.findall(r'\d+\.\s*([A-Z][^.!?]+[.!?])', content)
        principles.extend(numbered)

        # Look for explicit principle statements
        principle_keywords = ["principle", "tenet", "philosophy", "belief", "conviction"]
        for keyword in principle_keywords:
            pattern = rf'{keyword}[:\s]+(.+?)(?:\n|$)'
            matches = re.findall(pattern, content, re.IGNORECASE)
            principles.extend(matches)

        return principles[:10]  # Limit to top 10

    def _extract_decision_criteria(self, content: str) -> List[str]:
        """Extract decision criteria and filters"""
        criteria = []

        # Look for criteria patterns
        criteria_patterns = [
            r'Criteria:\s*(.+)',
            r'Filter[s]?:\s*(.+)',
            r'Must [have|be]:\s*(.+)',
            r'Required:\s*(.+)',
            r'Screen[s]?:\s*(.+)'
        ]

        for pattern in criteria_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            criteria.extend([m.strip() for m in matches])

        return criteria

    def _extract_title(self, content: str) -> str:
        """Extract document title"""
        lines = content.split('\n')
        for line in lines[:5]:
            if line.strip() and len(line.strip()) > 10:
                return line.strip()
        return "Domain Expertise Document"


class DomainExpertiseGenerator:
    """Generate training data from domain expertise"""

    def __init__(self, anthropic_client):
        """Initialize with Anthropic client"""
        self.client = anthropic_client
        self.parser = DomainExpertiseParser()

    def generate_from_domain_doc(
        self,
        document: DomainDocument,
        num_examples: int = 20
    ) -> List[Dict]:
        """Generate training examples from domain document"""

        examples = []

        # Generate different types of questions based on document type
        if document.doc_type == DocumentType.INVESTMENT_MEMO:
            examples.extend(self._generate_investment_rationale_questions(document, num_examples // 4))
            examples.extend(self._generate_risk_assessment_questions(document, num_examples // 4))

        elif document.doc_type == DocumentType.STRATEGY_GUIDE:
            examples.extend(self._generate_strategy_questions(document, num_examples // 3))
            examples.extend(self._generate_implementation_questions(document, num_examples // 3))

        elif document.doc_type == DocumentType.RISK_REPORT:
            examples.extend(self._generate_risk_questions(document, num_examples // 2))

        # Universal question types
        examples.extend(self._generate_conceptual_questions(document, num_examples // 4))
        examples.extend(self._generate_best_practice_questions(document, num_examples // 4))
        examples.extend(self._generate_judgment_questions(document, num_examples // 4))

        return examples

    def _generate_investment_rationale_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about investment rationale and decision-making"""

        prompt = f"""Based on this investment expertise document, generate {num} questions about investment rationale and decision-making.

Document Type: {doc.doc_type.value}
Domain Area: {doc.domain_area.value}
Title: {doc.title}

Key Concepts: {', '.join(doc.key_concepts[:5])}
Decision Criteria: {', '.join(doc.decision_criteria[:3])}

Content excerpt:
{doc.content[:1500]}

Generate questions like:
- "Why would you invest in [asset/strategy]?"
- "What factors drive the investment decision for [opportunity]?"
- "How do you evaluate [investment characteristic]?"
- "What makes [investment] attractive from a risk/return perspective?"

Answers should demonstrate expert investment judgment, not just recite rules.
Include reasoning, trade-offs, and market context.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert investment manager with deep knowledge of fund management and investment strategy.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "expert answer with reasoning"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_risk_assessment_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about risk assessment and management"""

        prompt = f"""Based on this risk expertise document, generate {num} questions about risk assessment and management.

Document: {doc.title}
Domain Area: {doc.domain_area.value}

Warnings: {', '.join(doc.warnings[:5]) if doc.warnings else 'See content'}
Best Practices: {', '.join(doc.best_practices[:3]) if doc.best_practices else 'See content'}

Content excerpt:
{doc.content[:1500]}

Generate questions like:
- "What are the key risks in [strategy/position]?"
- "How do you manage [specific risk]?"
- "What are the warning signs of [risk scenario]?"
- "How would you hedge [risk exposure]?"

Answers should show sophisticated risk thinking with specific mitigation strategies.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in investment risk management with deep understanding of market risks and mitigation strategies.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "expert risk assessment"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_strategy_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about investment strategy"""

        prompt = f"""Based on this strategy document, generate {num} questions about investment strategy and approach.

Document: {doc.title}
Type: {doc.doc_type.value}
Domain: {doc.domain_area.value}

Principles: {', '.join(doc.principles[:5]) if doc.principles else 'See content'}

Content excerpt:
{doc.content[:1500]}

Generate questions like:
- "What is the core philosophy of [strategy]?"
- "How does [strategy] generate alpha?"
- "When should you deploy [strategy]?"
- "What market conditions favor [approach]?"

Answers should articulate clear investment philosophy with practical application.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert portfolio manager with deep knowledge of investment strategies and approaches.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "strategic answer with philosophy"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_implementation_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about strategy implementation"""

        prompt = f"""Based on this document, generate {num} questions about implementing investment strategies.

Document: {doc.title}
Best Practices: {', '.join(doc.best_practices[:5]) if doc.best_practices else 'See content'}
Examples: {', '.join(doc.examples[:3]) if doc.examples else 'See content'}

Content excerpt:
{doc.content[:1500]}

Generate questions like:
- "How do you implement [strategy] in practice?"
- "What are the practical challenges with [approach]?"
- "How do you size [position/allocation]?"
- "What execution considerations apply to [strategy]?"

Answers should provide practical implementation wisdom from experience.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert portfolio manager with extensive practical experience implementing investment strategies.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "practical implementation guidance"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_conceptual_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about key concepts"""

        prompt = f"""Based on this expertise document, generate {num} questions about key investment concepts.

Document: {doc.title}
Domain: {doc.domain_area.value}
Key Concepts: {', '.join(doc.key_concepts[:8])}

Content excerpt:
{doc.content[:1500]}

Generate questions like:
- "Explain [concept] in the context of [domain]"
- "What is the relationship between [concept A] and [concept B]?"
- "How does [concept] impact [outcome]?"
- "Why is [concept] important for [goal]?"

Answers should demonstrate deep conceptual understanding with practical context.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in investment management with deep conceptual knowledge and practical experience.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "conceptual explanation with context"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_best_practice_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions about best practices"""

        if not doc.best_practices:
            return []

        prompt = f"""Based on these best practices, generate {num} questions about investment best practices.

Document: {doc.title}
Domain: {doc.domain_area.value}

Best Practices:
{chr(10).join(f'- {bp}' for bp in doc.best_practices[:8])}

Warnings to Avoid:
{chr(10).join(f'- {w}' for w in doc.warnings[:5])}

Generate questions like:
- "What are best practices for [activity]?"
- "How should you approach [situation]?"
- "What should you avoid when [action]?"
- "What separates good from great [practice]?"

Answers should reflect industry wisdom and lessons learned.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are a seasoned investment professional sharing best practices and wisdom from years of experience.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "best practice guidance with rationale"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_judgment_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate questions requiring expert judgment"""

        prompt = f"""Based on this expertise document, generate {num} scenario-based questions requiring expert judgment.

Document: {doc.title}
Domain: {doc.domain_area.value}

Create realistic scenarios like:
- "Given [market condition], how would you adjust [portfolio/strategy]?"
- "An investor asks about [situation]. How do you respond?"
- "You observe [market signal]. What does this mean for [strategy]?"
- "Compare [approach A] vs [approach B] in [scenario]"

Answers should demonstrate sophisticated judgment, weighing trade-offs and considering context.
Include reasoning process, not just conclusions.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert investment professional with years of experience making complex investment decisions.", "messages": [{{"role": "user", "content": "scenario question"}}, {{"role": "assistant", "content": "expert judgment with reasoning"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_risk_questions(
        self,
        doc: DomainDocument,
        num: int
    ) -> List[Dict]:
        """Generate risk-focused questions"""

        prompt = f"""Based on this risk document, generate {num} questions about investment risks.

Document: {doc.title}

Content excerpt (focus on risk analysis):
{doc.content[:1500]}

Generate questions covering:
- Risk identification: "What are the key risks in [situation]?"
- Risk measurement: "How do you quantify [risk]?"
- Risk mitigation: "How do you manage [risk exposure]?"
- Risk monitoring: "What metrics track [risk]?"

Answers should show sophisticated risk management expertise.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in investment risk management with deep understanding of risk analysis and mitigation.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "risk expertise answer"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _call_claude_for_examples(self, prompt: str) -> List[Dict]:
        """Call Claude to generate examples"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0.8,  # Higher temp for diverse expert perspectives
                messages=[{"role": "user", "content": prompt}]
            )

            examples = []
            text_response = response.content[0].text

            for line in text_response.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    continue

                try:
                    json_match = re.search(r'\{.*\}', line)
                    if json_match:
                        example = json.loads(json_match.group())
                        if self._validate_example(example):
                            examples.append(example)
                except json.JSONDecodeError:
                    continue

            return examples

        except Exception as e:
            print(f"Error generating examples: {e}")
            return []

    def _validate_example(self, example: Dict) -> bool:
        """Validate example format"""
        try:
            if 'messages' not in example:
                return False
            messages = example['messages']
            if len(messages) < 2:
                return False
            if messages[0]['role'] != 'user' or messages[-1]['role'] != 'assistant':
                return False
            for msg in messages:
                if 'content' not in msg or not msg['content']:
                    return False
            return True
        except (KeyError, TypeError, IndexError):
            return False


def create_sample_domain_documents() -> List[DomainDocument]:
    """Create sample domain documents for testing"""

    sample1 = """
    Value Investing Strategy Guide

    Investment Philosophy:
    Our value investing approach is built on the principle that markets occasionally
    misprice securities, creating opportunities for patient, disciplined investors
    to achieve superior long-term returns.

    Core Principles:
    1. Intrinsic Value: Every security has an intrinsic value based on fundamentals
    2. Margin of Safety: Only invest when price is significantly below intrinsic value
    3. Long-term Focus: Hold positions for 3-5 years minimum
    4. Fundamental Analysis: Deep dive into business quality, not just numbers
    5. Contrarian Mindset: Best opportunities often emerge when others are fearful

    Investment Criteria:
    - P/E ratio < 12 (or below sector median)
    - P/B ratio < 1.5
    - Dividend yield > 3%
    - Free cash flow positive for 5+ years
    - Return on equity > 12%
    - Debt/Equity < 0.5

    Best Practices:
    - Always understand the business model before investing
    - Meet with management teams when possible
    - Read the last 5 years of annual reports
    - Consider competitive positioning and moat
    - Assess management quality and capital allocation track record
    - Look for catalysts that could unlock value

    Warnings:
    - Avoid value traps (cheap for a reason)
    - Be cautious of declining industries
    - Watch for accounting red flags
    - Never ignore deteriorating fundamentals
    - Beware of over-leverage
    - Don't confuse cheap with undervalued

    Example: Company XYZ
    - Trading at P/E 8 vs sector average 15
    - Strong free cash flow ($500M annually)
    - Temporary headwinds from regulatory change
    - Management buying shares aggressively
    - Thesis: Market overreacting to short-term issue
    - Position size: 3-5% of portfolio
    - Expected holding period: 3-4 years
    - Target return: 15-20% annualized

    Risk Management:
    - Position sizing: No single position > 5% at cost
    - Sector limits: Maximum 25% in any sector
    - Stop-loss: Reassess if thesis breaks or fundamentals deteriorate
    - Rebalancing: Trim winners above 8% of portfolio

    Key Concept: Circle of Competence
    Only invest in businesses you can understand and analyze with confidence.
    Staying within your circle of competence reduces error rates and improves outcomes.
    """

    sample2 = """
    ESG Integration Framework

    Purpose:
    This framework guides the integration of Environmental, Social, and Governance
    factors into investment analysis and decision-making.

    Principle:
    ESG factors are financially material and can significantly impact long-term returns.
    Ignoring ESG risks is ignoring investment risks.

    ESG Assessment Process:

    1. Environmental Assessment:
       - Carbon intensity and emissions trajectory
       - Climate risk exposure (physical and transition)
       - Resource efficiency and circular economy practices
       - Environmental incidents and regulatory violations
       - Alignment with Paris Agreement goals

    2. Social Assessment:
       - Labor practices and employee relations
       - Health and safety record
       - Product safety and quality
       - Data privacy and security
       - Community relations and social license to operate

    3. Governance Assessment:
       - Board independence and diversity
       - Executive compensation alignment
       - Shareholder rights
       - Audit quality and controls
       - Anti-corruption policies and practices

    Integration in Investment Process:

    Research Phase:
    - Conduct ESG screening using third-party data (MSCI, Sustainalytics)
    - Flag material ESG risks in investment memo
    - Assign ESG risk rating (Low/Medium/High)

    Decision Phase:
    - Consider ESG factors alongside traditional financial analysis
    - Adjust valuation for ESG risks (e.g., carbon pricing scenarios)
    - Exclude companies with severe ESG violations

    Ownership Phase:
    - Engage with management on ESG improvements
    - Exercise proxy voting aligned with ESG principles
    - Monitor ESG metrics quarterly
    - Escalate concerns or consider divestment

    Best Practices:
    - Be specific about which ESG factors matter for each sector
    - Quantify ESG impacts where possible
    - Look for ESG improvement trends, not just current scores
    - Consider ESG leaders and laggards within sectors
    - Use engagement to drive change before divesting
    - Document ESG rationale in all investment decisions

    Warning:
    Avoid "greenwashing" - ensure ESG claims are substantiated with evidence.
    ESG ratings can differ significantly across providers - do your own analysis.

    Example: Energy Sector Investment
    Company: European Utility XYZ
    - Traditional ESG rating: B (moderate)
    - Our assessment: Positive ESG trajectory
    - Renewable capacity: 40% (increasing 5% annually)
    - Coal phase-out: Committed by 2030
    - Just transition plan: Supporting affected workers
    - Board: 40% female, strong climate expertise
    - Engagement: Met with CEO on transition acceleration
    - Valuation: Pricing in €50/ton carbon by 2030
    - Thesis: ESG improvements will drive multiple re-rating

    Key Concept: Materiality
    Focus on ESG factors that are financially material for the specific company and sector.
    Not all ESG factors matter equally for all investments.
    """

    sample3 = """
    Risk Management Playbook

    Philosophy:
    Risk management is not about avoiding all risks - it's about taking calculated
    risks while protecting against catastrophic losses.

    Key Risks in Fund Management:

    1. Market Risk
       Definition: Risk of losses from adverse market movements
       Measurement: VaR, beta, correlation analysis
       Management: Diversification, hedging, position limits

    2. Liquidity Risk
       Definition: Risk of inability to meet redemptions without material loss
       Measurement: Redemption stress testing, days-to-liquidate analysis
       Management: Maintain liquid buffer (15-20% of AUM), redemption gates

    3. Concentration Risk
       Definition: Over-exposure to single positions, sectors, or factors
       Measurement: Position sizes, sector weights, factor exposures
       Management: Position limits (5% max), sector limits (25% max)

    4. Counterparty Risk
       Definition: Risk of counterparty default
       Measurement: Credit ratings, CDS spreads
       Management: ISDA agreements, collateral, counterparty limits

    5. Operational Risk
       Definition: Risk of loss from inadequate processes or systems
       Measurement: Incident tracking, control testing
       Management: Segregation of duties, automation, disaster recovery

    Risk Limits Framework:

    Portfolio Level:
    - Maximum VaR (95%, 1-day): 2% of NAV
    - Maximum drawdown before review: -10%
    - Minimum liquidity: 15% in T+3 liquid assets
    - Maximum gross leverage: 130%

    Position Level:
    - Maximum single position: 5% at cost
    - Maximum position after appreciation: 8%
    - Maximum sector exposure: 25%
    - Maximum country exposure: 40%

    Best Practices:
    - Stress test portfolio quarterly (market crash, liquidity crisis scenarios)
    - Monitor risk metrics daily
    - Review limits annually
    - Document all limit breaches and remediation
    - Independent risk function reporting to CIO
    - Risk committee meets monthly

    Warning Signs:
    - Rapidly increasing correlations (market stress building)
    - Falling liquidity (widening bid-ask spreads)
    - Rising volatility without commensurate return pickup
    - Crowded trades (many managers in same position)
    - Unusual redemption requests (early warning)

    Example: 2020 COVID Crisis Response
    - VaR spiked to 3.5% (exceeded limit)
    - Action: Reduced positions by 20% over 3 days
    - Maintained liquidity buffer at 20% (vs 15% target)
    - Hedged equity exposure with index puts
    - Increased cash to 25% temporarily
    - Result: Limited drawdown to -8% vs -15% for peer group

    Key Concept: Risk-Adjusted Returns
    Focus on Sharpe ratio, not absolute returns. A 12% return with 20% volatility
    (Sharpe 0.6) is inferior to a 10% return with 8% volatility (Sharpe 1.25).
    Consistent, moderate returns beat volatile high returns over time.

    Decision Framework: When to Cut Positions
    1. Fundamental thesis breaks
    2. Risk limit breached with no near-term remedy
    3. Liquidity deteriorates significantly
    4. Better opportunities emerge (opportunity cost)
    5. Position grows too large through appreciation
    """

    parser = DomainExpertiseParser()

    docs = [
        parser.parse_domain_document(
            sample1,
            title="Value Investing Strategy Guide",
            doc_type=DocumentType.STRATEGY_GUIDE,
            domain_area=DomainAreaType.INVESTMENT_STRATEGY
        ),
        parser.parse_domain_document(
            sample2,
            title="ESG Integration Framework",
            doc_type=DocumentType.DECISION_FRAMEWORK,
            domain_area=DomainAreaType.ESG_INTEGRATION
        ),
        parser.parse_domain_document(
            sample3,
            title="Risk Management Playbook",
            doc_type=DocumentType.PLAYBOOK,
            domain_area=DomainAreaType.RISK_MANAGEMENT
        )
    ]

    return docs
