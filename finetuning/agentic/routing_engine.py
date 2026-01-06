"""
Routing Engine - Intelligent Query Classification and Routing

This module provides intelligent routing of user queries to the appropriate
dimension expert(s) based on query type and complexity.

Key Features:
- Pattern-based query classification
- ML-based intent detection using Claude
- Multi-dimension routing for complex queries
- Confidence scoring
- Route explanation and transparency
"""

import re
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import anthropic


class QueryType(Enum):
    """Types of queries that can be routed to dimension experts"""
    COMPLIANCE_CHECK = "compliance_check"          # "Is this allowed under UCITS?"
    HOW_TO = "how_to"                              # "How do I calculate NAV?"
    SHOULD_WE = "should_we"                        # "Should we invest in..."
    WHY = "why"                                    # "Why do we use this approach?"
    WHAT_DO_OTHERS_DO = "what_do_others_do"        # "What's the market standard?"
    COMPLEX_DECISION = "complex_decision"          # Needs multiple dimensions
    EVALUATE = "evaluate"                          # "Evaluate this strategy"
    COMPARE = "compare"                            # "Compare approach A vs B"
    EXPLAIN = "explain"                            # "Explain how X works"
    TROUBLESHOOT = "troubleshoot"                  # "Why is X not working?"


class DimensionType(Enum):
    """The four dimensions of expertise"""
    REGULATORY = "regulatory"        # WHAT rules require
    OPERATIONAL = "operational"      # HOW to do it
    DOMAIN = "domain"                # WHY decisions are made
    INDUSTRY = "industry"            # WHAT everyone does


@dataclass
class RoutingDecision:
    """Result of routing analysis"""
    query: str
    query_type: QueryType
    dimensions: List[DimensionType]
    confidence: float
    reasoning: str
    requires_orchestration: bool
    suggested_strategy: str  # "sequential", "parallel", "routing_only"


class RoutingEngine:
    """
    Intelligent routing engine that classifies queries and routes them
    to appropriate dimension experts.

    Uses both pattern matching and Claude-based intent detection for
    accurate routing decisions.
    """

    # Pattern-based routing rules
    REGULATORY_PATTERNS = [
        r'\b(ucits|aifmd|mifid|sfdr|priips|regulation|directive|compliant?|allowed|permitted|forbidden|prohibited|legal|rule|requirement)\b',
        r'\b(can we|may we|are we allowed|is it legal|is this compliant)\b',
        r'\b(article \d+|annex [ivxlcdm]+)\b',
        r'\b(esma|eba|european commission|competent authority)\b',
    ]

    OPERATIONAL_PATTERNS = [
        r'\b(how (do|to)|procedure|process|step|workflow|calculate|execute|perform|implement)\b',
        r'\b(sop|standard operating|checklist|run book)\b',
        r'\b(who is responsible|who does|which team|escalate)\b',
        r'\b(when do we|timing|deadline|frequency)\b',
        r'\b(nav calculation|trade settlement|reconciliation|reporting)\b',
    ]

    DOMAIN_PATTERNS = [
        r'\b(should we|recommend|strategy|approach|best practice|rationale)\b',
        r'\b(why (do|does|is)|reasoning|judgment|opinion|assess|evaluate)\b',
        r'\b(risk|return|performance|alpha|beta|sharpe|volatility)\b',
        r'\b(value investing|growth|momentum|factor|quant|fundamental)\b',
        r'\b(portfolio construction|asset allocation|diversification)\b',
    ]

    INDUSTRY_PATTERNS = [
        r'\b(market (standard|practice|convention)|industry norm|peer|competitor)\b',
        r'\b(what do others|how do peers|typical|common practice|usually)\b',
        r'\b(benchmark|comparison|relative to market)\b',
        r'\b(t\+\d+|settlement|pricing convention|day count)\b',
        r'\b(isda|icma|industry association)\b',
    ]

    # Complex query indicators (need multiple dimensions)
    COMPLEX_INDICATORS = [
        r'\b(evaluate|assess|analyze|review|comprehensive|complete)\b',
        r'\b(feasibility|viability|readiness)\b',
        r'\b(new (strategy|product|market|investment))\b',
        r'\b(change|modify|update|revise) (strategy|approach|policy)\b',
    ]

    def __init__(self, api_key: str = None, use_ml_routing: bool = True):
        """
        Initialize routing engine

        Args:
            api_key: Anthropic API key for ML-based routing
            use_ml_routing: Whether to use Claude for intent detection (more accurate)
        """
        self.api_key = api_key
        self.use_ml_routing = use_ml_routing
        if use_ml_routing and api_key:
            self.client = anthropic.Anthropic(api_key=api_key)

    def route_query(self, query: str) -> RoutingDecision:
        """
        Route a query to appropriate dimension expert(s)

        Args:
            query: User query

        Returns:
            RoutingDecision with routing details
        """
        # First, try pattern-based routing (fast)
        pattern_result = self._pattern_based_routing(query)

        # If ML routing enabled and available, enhance with Claude
        if self.use_ml_routing and self.api_key:
            ml_result = self._ml_based_routing(query, pattern_result)
            return ml_result

        return pattern_result

    def _pattern_based_routing(self, query: str) -> RoutingDecision:
        """
        Pattern-based routing using regex matching

        Fast but less accurate than ML-based routing.
        """
        query_lower = query.lower()

        # Score each dimension
        dimension_scores = {
            DimensionType.REGULATORY: self._count_patterns(query_lower, self.REGULATORY_PATTERNS),
            DimensionType.OPERATIONAL: self._count_patterns(query_lower, self.OPERATIONAL_PATTERNS),
            DimensionType.DOMAIN: self._count_patterns(query_lower, self.DOMAIN_PATTERNS),
            DimensionType.INDUSTRY: self._count_patterns(query_lower, self.INDUSTRY_PATTERNS),
        }

        # Check for complex query indicators
        complexity_score = self._count_patterns(query_lower, self.COMPLEX_INDICATORS)

        # Determine routing
        if complexity_score > 0 or sum(dimension_scores.values()) >= 2:
            # Complex query - needs orchestration
            dimensions = [dim for dim, score in dimension_scores.items() if score > 0]
            if not dimensions:
                dimensions = list(DimensionType)  # Use all if unclear

            return RoutingDecision(
                query=query,
                query_type=QueryType.COMPLEX_DECISION,
                dimensions=dimensions,
                confidence=0.7,
                reasoning=f"Multiple dimensions detected: {[d.value for d in dimensions]}",
                requires_orchestration=True,
                suggested_strategy="sequential" if len(dimensions) > 2 else "parallel"
            )

        # Simple query - route to single dimension
        max_dimension = max(dimension_scores.items(), key=lambda x: x[1])

        if max_dimension[1] == 0:
            # No clear match - default to domain expert
            return RoutingDecision(
                query=query,
                query_type=QueryType.EXPLAIN,
                dimensions=[DimensionType.DOMAIN],
                confidence=0.5,
                reasoning="No clear pattern match, routing to domain expert",
                requires_orchestration=False,
                suggested_strategy="routing_only"
            )

        # Determine query type
        query_type = self._infer_query_type(query_lower)

        return RoutingDecision(
            query=query,
            query_type=query_type,
            dimensions=[max_dimension[0]],
            confidence=0.8 if max_dimension[1] >= 2 else 0.6,
            reasoning=f"Matched {max_dimension[1]} patterns for {max_dimension[0].value}",
            requires_orchestration=False,
            suggested_strategy="routing_only"
        )

    def _ml_based_routing(
        self,
        query: str,
        pattern_result: RoutingDecision
    ) -> RoutingDecision:
        """
        ML-based routing using Claude for intent detection

        More accurate than pattern matching, but slower and requires API calls.
        """
        routing_prompt = f"""Analyze this query and determine which dimension(s) of expertise should handle it:

Query: "{query}"

Four Dimensions:
1. REGULATORY: Legal compliance, regulations (UCITS, AIFMD, SFDR, etc.)
2. OPERATIONAL: Procedures, how-to, processes, workflows
3. DOMAIN: Investment strategy, expert judgment, why decisions are made
4. INDUSTRY: Market practices, what peers do, conventions

Pattern-based analysis suggests: {pattern_result.dimensions[0].value if len(pattern_result.dimensions) == 1 else "multiple dimensions"}

Provide your routing decision in this exact format:

DIMENSIONS: [list one or more: regulatory, operational, domain, industry]
QUERY_TYPE: [compliance_check, how_to, should_we, why, what_do_others_do, complex_decision, evaluate, compare, explain, troubleshoot]
CONFIDENCE: [0.0-1.0]
ORCHESTRATION: [yes/no - whether multiple agents need to work together]
STRATEGY: [routing_only, sequential, parallel]
REASONING: [brief explanation]"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": routing_prompt}]
            )

            response = message.content[0].text

            # Parse response
            return self._parse_ml_response(query, response, pattern_result)

        except Exception as e:
            # Fall back to pattern-based routing on error
            print(f"ML routing failed: {e}, using pattern-based routing")
            return pattern_result

    def _parse_ml_response(
        self,
        query: str,
        response: str,
        fallback: RoutingDecision
    ) -> RoutingDecision:
        """Parse Claude's routing response"""
        try:
            # Extract dimensions
            dimensions_match = re.search(r'DIMENSIONS:\s*\[(.*?)\]', response, re.IGNORECASE)
            if dimensions_match:
                dim_names = [d.strip() for d in dimensions_match.group(1).split(',')]
                dimensions = [DimensionType(name) for name in dim_names if name]
            else:
                dimensions = fallback.dimensions

            # Extract query type
            type_match = re.search(r'QUERY_TYPE:\s*(\w+)', response, re.IGNORECASE)
            if type_match:
                query_type = QueryType(type_match.group(1))
            else:
                query_type = fallback.query_type

            # Extract confidence
            conf_match = re.search(r'CONFIDENCE:\s*([\d.]+)', response)
            confidence = float(conf_match.group(1)) if conf_match else fallback.confidence

            # Extract orchestration requirement
            orch_match = re.search(r'ORCHESTRATION:\s*(yes|no)', response, re.IGNORECASE)
            requires_orchestration = orch_match.group(1).lower() == 'yes' if orch_match else fallback.requires_orchestration

            # Extract strategy
            strat_match = re.search(r'STRATEGY:\s*(\w+)', response, re.IGNORECASE)
            strategy = strat_match.group(1) if strat_match else fallback.suggested_strategy

            # Extract reasoning
            reason_match = re.search(r'REASONING:\s*(.+)', response, re.IGNORECASE)
            reasoning = reason_match.group(1).strip() if reason_match else fallback.reasoning

            return RoutingDecision(
                query=query,
                query_type=query_type,
                dimensions=dimensions,
                confidence=confidence,
                reasoning=reasoning,
                requires_orchestration=requires_orchestration,
                suggested_strategy=strategy
            )

        except Exception as e:
            print(f"Failed to parse ML response: {e}")
            return fallback

    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Count how many patterns match in text"""
        count = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        return count

    def _infer_query_type(self, query_lower: str) -> QueryType:
        """Infer query type from query text"""
        if re.search(r'\b(is|are|can|may|allowed|permitted|compliant)\b', query_lower):
            return QueryType.COMPLIANCE_CHECK
        elif re.search(r'\bhow (do|to|can|should)\b', query_lower):
            return QueryType.HOW_TO
        elif re.search(r'\bshould (we|i)\b', query_lower):
            return QueryType.SHOULD_WE
        elif re.search(r'\bwhy\b', query_lower):
            return QueryType.WHY
        elif re.search(r'\bwhat (do|does) (others|peers|market|competitors)\b', query_lower):
            return QueryType.WHAT_DO_OTHERS_DO
        elif re.search(r'\b(evaluate|assess|analyze)\b', query_lower):
            return QueryType.EVALUATE
        elif re.search(r'\b(compare|versus|vs|versus)\b', query_lower):
            return QueryType.COMPARE
        elif re.search(r'\b(explain|what is|tell me about)\b', query_lower):
            return QueryType.EXPLAIN
        else:
            return QueryType.EXPLAIN

    def explain_routing(self, decision: RoutingDecision) -> str:
        """
        Generate human-readable explanation of routing decision

        Args:
            decision: RoutingDecision to explain

        Returns:
            Human-readable explanation
        """
        explanation = f"""
🧭 Routing Analysis
==================

Query: "{decision.query}"

Query Type: {decision.query_type.value.replace('_', ' ').title()}
Confidence: {decision.confidence:.0%}

Routed To:
{chr(10).join(f"  • {dim.value.upper()} Expert" for dim in decision.dimensions)}

Reasoning: {decision.reasoning}

Strategy: {decision.suggested_strategy.replace('_', ' ').title()}
Orchestration Required: {"Yes" if decision.requires_orchestration else "No"}
"""
        return explanation.strip()


# Example usage
if __name__ == "__main__":
    import asyncio

    # Initialize router
    router = RoutingEngine(use_ml_routing=False)  # Pattern-based only for demo

    # Example queries
    test_queries = [
        "Is this investment allowed under UCITS?",
        "How do I calculate NAV for the fund?",
        "Should we invest in high-yield bonds?",
        "What do other fund managers typically allocate to emerging markets?",
        "Evaluate this new ESG screening methodology",
        "Why do we use value investing instead of growth?",
    ]

    print("=" * 70)
    print("ROUTING ENGINE EXAMPLES")
    print("=" * 70)

    for query in test_queries:
        decision = router.route_query(query)
        print(f"\n{router.explain_routing(decision)}")
        print("-" * 70)
