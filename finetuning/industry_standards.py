"""
Industry Standards and Market Practices Extension

This module captures market conventions, industry standards, and common practices
that aren't written in regulations or procedures but are essential knowledge:

- Market conventions (settlement periods, day counts, quotation methods)
- Industry benchmarks (typical fees, expense ratios, performance metrics)
- Trading practices (execution methods, best practices, market microstructure)
- Documentation standards (standard agreements, templates, clauses)
- Peer practices (what other funds do, industry norms)
- Pricing conventions (clean vs dirty, accrual methods)
- Communication standards (reporting frequency, disclosure practices)
- Technology standards (data formats, platforms, APIs)

This is the "industry knowledge" that experienced professionals have but
isn't found in regulations, procedures, or strategy documents.
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class StandardType(Enum):
    """Types of industry standards"""
    MARKET_CONVENTION = "Market Convention"
    TRADING_PRACTICE = "Trading Practice"
    PRICING_CONVENTION = "Pricing Convention"
    DOCUMENTATION_STANDARD = "Documentation Standard"
    BENCHMARK_STANDARD = "Benchmark & Metric"
    TECHNOLOGY_STANDARD = "Technology Standard"
    COMMUNICATION_PRACTICE = "Communication Practice"
    SETTLEMENT_PRACTICE = "Settlement Practice"
    VALUATION_PRACTICE = "Valuation Practice"
    PEER_PRACTICE = "Peer Practice"


class AssetClass(Enum):
    """Asset class categories"""
    EQUITIES = "Equities"
    FIXED_INCOME = "Fixed Income"
    DERIVATIVES = "Derivatives"
    ALTERNATIVES = "Alternatives"
    FX = "Foreign Exchange"
    COMMODITIES = "Commodities"
    MULTI_ASSET = "Multi-Asset"
    CROSS_ASSET = "Cross-Asset"


@dataclass
class IndustryStandard:
    """Represents an industry standard or practice"""
    title: str
    standard_type: StandardType
    asset_class: Optional[AssetClass]
    description: str
    examples: List[str]
    variations: List[str]
    exceptions: List[str]
    evolution: str  # How it's changing
    geographic_differences: Dict[str, str]
    metadata: Dict[str, Any]


class IndustryStandardsParser:
    """Parse documents containing industry standards and practices"""

    def parse_standards_document(
        self,
        content: str,
        title: str = ""
    ) -> List[IndustryStandard]:
        """Parse a document containing industry standards"""

        standards = []

        # Split into sections
        sections = self._split_into_sections(content)

        for section_title, section_content in sections:
            standard = self._parse_section(section_title, section_content)
            if standard:
                standards.append(standard)

        return standards

    def _split_into_sections(self, content: str) -> List[tuple]:
        """Split content into titled sections"""
        sections = []

        # Look for section headers (lines that are all caps or start with ###)
        lines = content.split('\n')
        current_title = "General Standards"
        current_content = []

        for line in lines:
            # Check if this is a header
            if (line.strip() and
                (line.strip().isupper() or
                 line.strip().startswith('###') or
                 line.strip().startswith('##'))):

                # Save previous section
                if current_content:
                    sections.append((current_title, '\n'.join(current_content)))

                # Start new section
                current_title = line.strip().replace('#', '').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))

        return sections

    def _parse_section(self, title: str, content: str) -> Optional[IndustryStandard]:
        """Parse a section into an IndustryStandard"""

        # Detect standard type
        standard_type = self._detect_standard_type(title, content)

        # Detect asset class
        asset_class = self._detect_asset_class(content)

        # Extract components
        examples = self._extract_examples(content)
        variations = self._extract_variations(content)
        exceptions = self._extract_exceptions(content)
        evolution = self._extract_evolution(content)
        geo_diff = self._extract_geographic_differences(content)

        return IndustryStandard(
            title=title,
            standard_type=standard_type,
            asset_class=asset_class,
            description=self._extract_description(content),
            examples=examples,
            variations=variations,
            exceptions=exceptions,
            evolution=evolution,
            geographic_differences=geo_diff,
            metadata={}
        )

    def _detect_standard_type(self, title: str, content: str) -> StandardType:
        """Detect the type of standard"""
        title_lower = title.lower()
        content_lower = content.lower()

        if any(word in title_lower for word in ['settlement', 'clearing']):
            return StandardType.SETTLEMENT_PRACTICE
        elif any(word in title_lower for word in ['trading', 'execution']):
            return StandardType.TRADING_PRACTICE
        elif any(word in title_lower for word in ['pricing', 'valuation', 'quote']):
            return StandardType.PRICING_CONVENTION
        elif any(word in title_lower for word in ['documentation', 'agreement', 'contract']):
            return StandardType.DOCUMENTATION_STANDARD
        elif any(word in title_lower for word in ['benchmark', 'metric', 'typical', 'average']):
            return StandardType.BENCHMARK_STANDARD
        elif any(word in title_lower for word in ['technology', 'platform', 'system']):
            return StandardType.TECHNOLOGY_STANDARD
        elif any(word in title_lower for word in ['reporting', 'communication', 'disclosure']):
            return StandardType.COMMUNICATION_PRACTICE
        elif 'peer' in title_lower or 'industry practice' in title_lower:
            return StandardType.PEER_PRACTICE
        else:
            return StandardType.MARKET_CONVENTION

    def _detect_asset_class(self, content: str) -> Optional[AssetClass]:
        """Detect asset class from content"""
        content_lower = content.lower()

        asset_keywords = {
            AssetClass.EQUITIES: ['equity', 'stock', 'share'],
            AssetClass.FIXED_INCOME: ['bond', 'fixed income', 'debt'],
            AssetClass.DERIVATIVES: ['derivative', 'option', 'future', 'swap'],
            AssetClass.FX: ['fx', 'currency', 'foreign exchange'],
            AssetClass.ALTERNATIVES: ['alternative', 'private equity', 'hedge'],
            AssetClass.COMMODITIES: ['commodity', 'gold', 'oil']
        }

        for asset_class, keywords in asset_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return asset_class

        return None

    def _extract_description(self, content: str) -> str:
        """Extract main description"""
        # Get first substantial paragraph
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 50:
                return para.strip()
        return content[:200].strip()

    def _extract_examples(self, content: str) -> List[str]:
        """Extract examples"""
        examples = []

        patterns = [
            r'Example[s]?:\s*(.+)',
            r'For example[,]?\s*(.+)',
            r'E\.g\.,?\s*(.+)',
            r'Such as:\s*(.+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            examples.extend([m.strip() for m in matches])

        return list(set(examples))[:5]

    def _extract_variations(self, content: str) -> List[str]:
        """Extract variations or alternatives"""
        variations = []

        patterns = [
            r'Variation[s]?:\s*(.+)',
            r'Alternative[s]?:\s*(.+)',
            r'Some firms:\s*(.+)',
            r'Other approach:\s*(.+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            variations.extend([m.strip() for m in matches])

        return variations

    def _extract_exceptions(self, content: str) -> List[str]:
        """Extract exceptions to the standard"""
        exceptions = []

        patterns = [
            r'Exception[s]?:\s*(.+)',
            r'However[,]?\s*(.+)',
            r'But:\s*(.+)',
            r'Not applicable:\s*(.+)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            exceptions.extend([m.strip() for m in matches])

        return exceptions

    def _extract_evolution(self, content: str) -> str:
        """Extract information about how standard is evolving"""
        patterns = [
            r'Evolving:\s*(.+)',
            r'Changing:\s*(.+)',
            r'Future:\s*(.+)',
            r'Trend:\s*(.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_geographic_differences(self, content: str) -> Dict[str, str]:
        """Extract geographic variations"""
        geo_diff = {}

        regions = ['US', 'Europe', 'EU', 'UK', 'Asia', 'Japan', 'China']

        for region in regions:
            pattern = rf'{region}[:\s]+(.+?)(?:\.|$)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                geo_diff[region] = match.group(1).strip()

        return geo_diff


class IndustryStandardsGenerator:
    """Generate training data from industry standards"""

    def __init__(self, anthropic_client):
        """Initialize with Anthropic client"""
        self.client = anthropic_client

    def generate_from_standards(
        self,
        standards: List[IndustryStandard],
        num_examples: int = 30
    ) -> List[Dict]:
        """Generate training examples from industry standards"""

        examples = []

        # Generate different question types
        examples.extend(self._generate_what_is_standard_questions(standards, num_examples // 5))
        examples.extend(self._generate_comparison_questions(standards, num_examples // 5))
        examples.extend(self._generate_practical_application_questions(standards, num_examples // 5))
        examples.extend(self._generate_exception_questions(standards, num_examples // 5))
        examples.extend(self._generate_evolution_questions(standards, num_examples // 5))

        return examples

    def _generate_what_is_standard_questions(
        self,
        standards: List[IndustryStandard],
        num: int
    ) -> List[Dict]:
        """Generate questions about what the standard is"""

        standards_desc = self._format_standards_for_prompt(standards)

        prompt = f"""Based on these industry standards, generate {num} questions about market conventions and practices.

Industry Standards:
{standards_desc}

Generate questions like:
- "What is the standard settlement period for [instrument]?"
- "What's the market convention for [practice]?"
- "How is [metric] typically quoted in the market?"
- "What's the industry standard for [documentation/agreement]?"

Answers should explain the standard, give context, and mention any variations.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in financial markets with deep knowledge of industry standards and market practices.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer explaining standard"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_comparison_questions(
        self,
        standards: List[IndustryStandard],
        num: int
    ) -> List[Dict]:
        """Generate questions comparing practices"""

        standards_desc = self._format_standards_for_prompt(standards)

        prompt = f"""Based on these industry standards, generate {num} questions comparing different market practices.

Industry Standards:
{standards_desc}

Generate questions like:
- "What's the difference between US and European market practice for [activity]?"
- "How does [practice A] differ from [practice B]?"
- "Why do some firms use [approach A] while others use [approach B]?"
- "What are the pros and cons of [standard practice]?"

Answers should compare different approaches and explain the trade-offs.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in global financial markets with knowledge of regional differences in market practices.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "comparative answer"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_practical_application_questions(
        self,
        standards: List[IndustryStandard],
        num: int
    ) -> List[Dict]:
        """Generate questions about applying standards in practice"""

        standards_desc = self._format_standards_for_prompt(standards)

        prompt = f"""Based on these industry standards, generate {num} practical application questions.

Industry Standards:
{standards_desc}

Generate questions like:
- "In practice, how do you [implement standard]?"
- "What happens if you deviate from the market standard?"
- "When is it acceptable to use [non-standard approach]?"
- "How do you handle situations where the standard doesn't fit?"

Answers should provide practical guidance based on industry norms.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an experienced market practitioner with deep knowledge of how industry standards work in practice.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "practical guidance"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_exception_questions(
        self,
        standards: List[IndustryStandard],
        num: int
    ) -> List[Dict]:
        """Generate questions about exceptions to standards"""

        standards_desc = self._format_standards_for_prompt(standards)

        prompt = f"""Based on these industry standards, generate {num} questions about exceptions and special cases.

Industry Standards:
{standards_desc}

Generate questions like:
- "When doesn't the standard [practice] apply?"
- "What are the exceptions to [market convention]?"
- "Which instruments don't follow the standard [rule]?"
- "How do you handle [special case] that doesn't fit the standard?"

Answers should explain exceptions clearly with examples.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in financial market conventions with knowledge of exceptions and special cases.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer about exceptions"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_evolution_questions(
        self,
        standards: List[IndustryStandard],
        num: int
    ) -> List[Dict]:
        """Generate questions about how standards are evolving"""

        standards_desc = self._format_standards_for_prompt(standards)

        prompt = f"""Based on these industry standards, generate {num} questions about market evolution.

Industry Standards:
{standards_desc}

Generate questions like:
- "How has [market practice] evolved over time?"
- "What's changing in the industry regarding [standard]?"
- "What's driving the shift from [old practice] to [new practice]?"
- "What will replace the current standard for [activity]?"

Answers should explain historical context and future direction.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are a market expert who understands the evolution of industry practices and emerging standards.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer about evolution"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _format_standards_for_prompt(self, standards: List[IndustryStandard]) -> str:
        """Format standards for inclusion in prompt"""
        formatted = []

        for std in standards[:10]:  # Limit to 10 standards to fit in prompt
            formatted.append(f"""
Standard: {std.title}
Type: {std.standard_type.value}
Description: {std.description[:200]}
Examples: {', '.join(std.examples[:3])}
""")

        return '\n'.join(formatted)

    def _call_claude_for_examples(self, prompt: str) -> List[Dict]:
        """Call Claude to generate examples"""
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                temperature=0.7,
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
            return True
        except (KeyError, TypeError, IndexError):
            return False


def create_sample_industry_standards() -> str:
    """Create sample industry standards document"""

    return """
INDUSTRY STANDARDS AND MARKET PRACTICES COMPENDIUM

### SETTLEMENT PRACTICES

Standard Settlement Periods:
- Equities: T+2 (US, Europe since 2014, moved from T+3)
- Government bonds: T+1 in most markets
- Corporate bonds: T+2 (US), T+2 (Europe)
- FX spot: T+2
- FX forward: Varies by contract
- Derivatives: Varies (futures typically T+1, options exercise varies)

Note: India moved to T+1 for equities in 2023. US exploring T+1 move.

Geographic Differences:
- China: T+0 for A-shares (immediate settlement)
- Japan: T+2 standard (moved from T+3 in 2019)

Exception: When settlement date falls on holiday, rolls to next business day.

### TRADING PRACTICES

Best Execution Standards:
- Institutional standard: Minimum 3 price quotes for liquid securities
- VWAP execution typical for orders >5% of ADV
- Avoid first and last 30 minutes for illiquid stocks (wider spreads)
- Algorithms: TWAP, VWAP, Implementation Shortfall most common
- Dark pools: Typically used for large blocks to minimize market impact

Typical Spreads (Indicative):
- Large-cap equities: 0.01-0.05%
- Mid-cap equities: 0.05-0.15%
- Small-cap equities: 0.15-0.50%
- IG Corporate bonds: 0.25-0.50%
- HY Corporate bonds: 0.50-2.00%

Europe: MiFID II requires demonstrating best execution with detail records.

### PRICING CONVENTIONS

Bond Quotations:
- US: Corporate bonds quoted clean price (excluding accrued interest)
- US: Trades settle at dirty price (clean + accrued)
- Europe: Similar clean/dirty convention
- Japan: Some bonds quoted with accrued included

Day Count Conventions:
- US Treasury: Actual/Actual
- US Corporate: 30/360
- US Municipal: 30/360
- Eurobonds: 30/360 or Actual/Actual
- UK Gilts: Actual/Actual
- Repo: Actual/360

These conventions affect accrual calculations and yield measures.

### DOCUMENTATION STANDARDS

Standard Agreements:
- Derivatives: ISDA Master Agreement (2002 version most common, 1992 still used)
- Securities Lending: GMSLA (Global Master Securities Lending Agreement)
- Repo: GMRA (Global Master Repurchase Agreement)
- Prime Brokerage: Custom but based on industry templates

ISDA Practices:
- Credit Support Annex (CSA) for collateral terms
- Standard credit events: bankruptcy, failure to pay, restructuring
- Threshold amounts vary but typical: $0-10M for corporates
- Most firms have 100-500 ISDs in place

Variations: Asian markets sometimes use local documentation standards.

### BENCHMARK STANDARDS

Fund Expense Ratios (Typical):
- Passive equity funds: 0.05-0.20%
- Active equity funds: 0.50-1.00%
- Bond funds: 0.25-0.75%
- Alternative funds: 1.00-2.00%
- Plus performance fees: 10-20% over hurdle

Performance Fee Structures:
- Hedge funds: Typical "2 and 20" (2% mgmt, 20% performance)
- UCITS: Increasingly "1 and 10" or "0.75 and 15"
- US mutual funds: Often 0-20% sliding scale based on outperformance

Evolving: Trend toward lower fees, especially passive. "2 and 20" rare for new launches.

Sharpe Ratio Benchmarks:
- Equity long-only: 0.5-1.0 considered good
- Multi-strategy hedge: 1.0-1.5 considered good
- Market neutral: 1.5+ expected (lower risk)

### COMMUNICATION PRACTICES

Investor Reporting:
- Monthly: Standard for institutional investors
- Quarterly: Common for retail/UCITS
- Daily NAV: Required for UCITS, common for liquid strategies
- Annual report: Required, typically 90 days after year-end

Performance Reporting Standards:
- GIPS (Global Investment Performance Standards) widely adopted
- Time-weighted returns for fund performance
- Money-weighted returns for client reporting
- Gross vs net of fees clearly disclosed

Industry Norm: Institutional investors expect performance commentary within 5 business days of month-end.

### TECHNOLOGY STANDARDS

Data Feeds:
- Bloomberg: Industry standard for pricing and analytics
- Refinitiv (formerly Thomson Reuters): Major alternative
- FactSet: Growing adoption
- Market data: Direct exchange feeds for high-frequency

Execution Platforms:
- FIX Protocol: Standard for trade communication
- Equities: Bloomberg AIM, Liquidnet, ITG common
- Fixed Income: Tradeweb, MarketAxess dominant

Order Management Systems (OMS):
- Large institutions: Bloomberg AIM, Charles River, Aladdin
- Mid-size: SimCorp, Eze, Advent
- Integration via FIX, APIs increasingly common

Evolving: Cloud-based systems growing, but many still on-premise for data control.

### VALUATION PRACTICES

Fair Value Hierarchy (IFRS 13 / ASC 820):
- Level 1: Quoted prices in active markets (most bonds, liquid stocks)
- Level 2: Observable inputs (most derivatives, illiquid bonds)
- Level 3: Unobservable inputs (private equity, distressed debt)

Pricing Sources Priority:
1. Exchange closing prices (equities)
2. Broker quotes (minimum 2-3 for Level 2)
3. Pricing services (Bloomberg, ICE, Markit)
4. Internal models (documented and tested)

Illiquid Security Pricing:
- Standard: Get 3 broker quotes, use median or average
- If quotes differ >5%: Investigate and document reason
- Stale quotes (>3 days old): Often not used

Month-End Pricing: Many firms use T-1 pricing (day before month-end) for month-end NAV to allow time for processing.

### PEER PRACTICES

NAV Calculation Timing:
- UCITS: Typically publish by 9 AM T+1
- US Mutual Funds: Typically calculate same day by 6 PM
- Hedge funds: Often T+3 to T+5

Redemption Terms:
- UCITS: Daily liquidity standard
- Hedge funds: Monthly/Quarterly common, 30-90 day notice
- Private equity: Quarterly/Annual, multi-year lockups

Side Pocket Usage:
- Triggered when position becomes illiquid
- Typically >5% of NAV and >30% price decline
- Separate series created for side-pocketed assets

Industry Norm: Most firms avoid side pockets if possible due to operational complexity.

### RISK MANAGEMENT STANDARDS

VaR Calculation:
- Industry standard: 95% or 99% confidence, 1-day holding period
- Some firms use 10-day for Basel compliance
- Methods: Historical simulation most common, Monte Carlo for complex portfolios

Stress Testing:
- Regulatory: Quarterly or annual stress tests
- Internal: Monthly stress tests common for risk oversight
- Scenarios: 2008 financial crisis, COVID-2020, custom scenarios

Position Limits:
- Typical single position limit: 3-5% of portfolio at cost
- Sector limits: 20-30% common
- Country limits: Vary widely, often 30-40% home bias allowed

Back-testing: Industry practice is to back-test VaR daily, with exception reporting when actual exceeds VaR.
"""


def load_industry_standards_from_document(file_path: str) -> List[IndustryStandard]:
    """Load industry standards from a document file"""
    parser = IndustryStandardsParser()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return parser.parse_standards_document(content)
