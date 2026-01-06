"""
Operational Procedures Extension for EU Funds Fine-tuning

This module extends the training data generator to handle operational procedures,
SOPs, workflows, checklists, and other practical operational documents.

Features:
- Parse operational procedures and workflows
- Generate training examples from SOPs
- Link procedures to regulatory requirements
- Create scenario-based training data
- Handle process diagrams and flowcharts
- Extract decision trees and checklists
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class ProcedureType(Enum):
    """Types of operational procedures"""
    SOP = "Standard Operating Procedure"
    WORKFLOW = "Workflow"
    CHECKLIST = "Checklist"
    DECISION_TREE = "Decision Tree"
    PROCESS_GUIDE = "Process Guide"
    COMPLIANCE_PROCEDURE = "Compliance Procedure"
    RISK_ASSESSMENT = "Risk Assessment"
    ESCALATION_PROCEDURE = "Escalation Procedure"


@dataclass
class OperationalProcedure:
    """Represents an operational procedure"""
    title: str
    procedure_type: ProcedureType
    content: str
    steps: List[str]
    related_regulations: List[str]
    roles: List[str]
    triggers: List[str]
    outputs: List[str]
    controls: List[str]
    metadata: Dict[str, Any]


class OperationalProcedureParser:
    """Parse operational procedures from various formats"""

    # Common procedure patterns
    STEP_PATTERNS = [
        r'Step \d+[:\.]?\s*(.+)',
        r'\d+\.\s*(.+)',
        r'[A-Z]\.\s*(.+)',
        r'►\s*(.+)',
        r'•\s*(.+)',
        r'-\s*(.+)'
    ]

    ROLE_PATTERNS = [
        r'Responsible:\s*(.+)',
        r'Role:\s*(.+)',
        r'Performed by:\s*(.+)',
        r'Owner:\s*(.+)',
        r'RACI:\s*(.+)'
    ]

    REGULATION_PATTERNS = [
        r'Regulation:\s*(.+)',
        r'Regulatory reference:\s*(.+)',
        r'Compliance:\s*(.+)',
        r'Article \d+',
        r'UCITS|AIFMD|SFDR|MiFID|PRIIPs'
    ]

    def parse_procedure(self, content: str, title: str = "") -> OperationalProcedure:
        """Parse a procedure document into structured format"""

        # Detect procedure type
        proc_type = self._detect_procedure_type(content)

        # Extract steps
        steps = self._extract_steps(content)

        # Extract roles
        roles = self._extract_roles(content)

        # Extract related regulations
        regulations = self._extract_regulations(content)

        # Extract triggers
        triggers = self._extract_triggers(content)

        # Extract outputs
        outputs = self._extract_outputs(content)

        # Extract controls
        controls = self._extract_controls(content)

        return OperationalProcedure(
            title=title or self._extract_title(content),
            procedure_type=proc_type,
            content=content,
            steps=steps,
            related_regulations=regulations,
            roles=roles,
            triggers=triggers,
            outputs=outputs,
            controls=controls,
            metadata={}
        )

    def _detect_procedure_type(self, content: str) -> ProcedureType:
        """Detect the type of procedure from content"""
        content_lower = content.lower()

        if "checklist" in content_lower:
            return ProcedureType.CHECKLIST
        elif "workflow" in content_lower or "process flow" in content_lower:
            return ProcedureType.WORKFLOW
        elif "decision" in content_lower and "tree" in content_lower:
            return ProcedureType.DECISION_TREE
        elif "escalation" in content_lower:
            return ProcedureType.ESCALATION_PROCEDURE
        elif "risk assessment" in content_lower:
            return ProcedureType.RISK_ASSESSMENT
        elif "compliance" in content_lower:
            return ProcedureType.COMPLIANCE_PROCEDURE
        elif "sop" in content_lower or "standard operating procedure" in content_lower:
            return ProcedureType.SOP
        else:
            return ProcedureType.PROCESS_GUIDE

    def _extract_steps(self, content: str) -> List[str]:
        """Extract procedural steps from content"""
        steps = []
        for pattern in self.STEP_PATTERNS:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            if matches:
                steps.extend([match.strip() for match in matches])

        # Deduplicate while preserving order
        seen = set()
        unique_steps = []
        for step in steps:
            if step not in seen and len(step) > 10:  # Filter out very short steps
                seen.add(step)
                unique_steps.append(step)

        return unique_steps

    def _extract_roles(self, content: str) -> List[str]:
        """Extract roles/responsibilities"""
        roles = []
        for pattern in self.ROLE_PATTERNS:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            roles.extend([match.strip() for match in matches])
        return list(set(roles))

    def _extract_regulations(self, content: str) -> List[str]:
        """Extract regulatory references"""
        regulations = []
        for pattern in self.REGULATION_PATTERNS:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            regulations.extend([match.strip() for match in matches])
        return list(set(regulations))

    def _extract_triggers(self, content: str) -> List[str]:
        """Extract procedure triggers"""
        trigger_patterns = [
            r'Trigger:\s*(.+)',
            r'When:\s*(.+)',
            r'Initiated by:\s*(.+)',
            r'Upon:\s*(.+)'
        ]
        triggers = []
        for pattern in trigger_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            triggers.extend([match.strip() for match in matches])
        return triggers

    def _extract_outputs(self, content: str) -> List[str]:
        """Extract procedure outputs/deliverables"""
        output_patterns = [
            r'Output:\s*(.+)',
            r'Deliverable:\s*(.+)',
            r'Result:\s*(.+)',
            r'Produces:\s*(.+)'
        ]
        outputs = []
        for pattern in output_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            outputs.extend([match.strip() for match in matches])
        return outputs

    def _extract_controls(self, content: str) -> List[str]:
        """Extract control points/checkpoints"""
        control_patterns = [
            r'Control:\s*(.+)',
            r'Checkpoint:\s*(.+)',
            r'Verify:\s*(.+)',
            r'Review:\s*(.+)'
        ]
        controls = []
        for pattern in control_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            controls.extend([match.strip() for match in matches])
        return controls

    def _extract_title(self, content: str) -> str:
        """Extract procedure title"""
        # Look for title patterns
        lines = content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.strip() and len(line.strip()) > 10:
                return line.strip()
        return "Operational Procedure"


class OperationalTrainingGenerator:
    """Generate training data from operational procedures"""

    def __init__(self, anthropic_client):
        """Initialize with Anthropic client"""
        self.client = anthropic_client
        self.parser = OperationalProcedureParser()

    def generate_from_procedure(
        self,
        procedure: OperationalProcedure,
        num_examples: int = 10
    ) -> List[Dict]:
        """Generate training examples from an operational procedure"""

        examples = []

        # Generate different types of questions
        examples.extend(self._generate_how_to_questions(procedure, num_examples // 5))
        examples.extend(self._generate_who_questions(procedure, num_examples // 5))
        examples.extend(self._generate_when_questions(procedure, num_examples // 5))
        examples.extend(self._generate_scenario_questions(procedure, num_examples // 5))
        examples.extend(self._generate_compliance_questions(procedure, num_examples // 5))

        return examples

    def _generate_how_to_questions(
        self,
        procedure: OperationalProcedure,
        num: int
    ) -> List[Dict]:
        """Generate 'how to' procedural questions"""

        prompt = f"""Based on this operational procedure, generate {num} 'how to' questions and detailed answers.

Procedure: {procedure.title}
Type: {procedure.procedure_type.value}

Steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(procedure.steps))}

Roles: {', '.join(procedure.roles)}
Related Regulations: {', '.join(procedure.related_regulations)}

Generate questions like:
- "How do I [perform this procedure]?"
- "What is the process for [specific step]?"
- "How should [role] handle [situation]?"

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations and compliance procedures.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "detailed step-by-step answer"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_who_questions(
        self,
        procedure: OperationalProcedure,
        num: int
    ) -> List[Dict]:
        """Generate questions about roles and responsibilities"""

        prompt = f"""Based on this operational procedure, generate {num} questions about roles and responsibilities.

Procedure: {procedure.title}
Roles: {', '.join(procedure.roles)}
Steps: {', '.join(procedure.steps[:3])}

Generate questions like:
- "Who is responsible for [task]?"
- "What is the role of [person/team] in [process]?"
- "Who should I escalate to if [situation]?"

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations and compliance procedures.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer with role details"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_when_questions(
        self,
        procedure: OperationalProcedure,
        num: int
    ) -> List[Dict]:
        """Generate questions about timing and triggers"""

        prompt = f"""Based on this operational procedure, generate {num} questions about when/timing.

Procedure: {procedure.title}
Triggers: {', '.join(procedure.triggers) if procedure.triggers else 'See content'}

Content excerpt:
{procedure.content[:1000]}

Generate questions like:
- "When should this procedure be initiated?"
- "What triggers [specific step]?"
- "What is the timeline for [process]?"

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations and compliance procedures.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer with timing details"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_scenario_questions(
        self,
        procedure: OperationalProcedure,
        num: int
    ) -> List[Dict]:
        """Generate scenario-based questions"""

        prompt = f"""Based on this operational procedure, generate {num} realistic scenario-based questions.

Procedure: {procedure.title}
Type: {procedure.procedure_type.value}

Create scenarios like:
- "What should I do if [specific situation] occurs during [process]?"
- "A [role] encounters [problem]. How should they proceed?"
- "If [condition] is not met, what is the next step?"

Include edge cases and exception handling.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations and compliance procedures.", "messages": [{{"role": "user", "content": "scenario question"}}, {{"role": "assistant", "content": "detailed answer with procedure to follow"}}]}}
"""

        return self._call_claude_for_examples(prompt)

    def _generate_compliance_questions(
        self,
        procedure: OperationalProcedure,
        num: int
    ) -> List[Dict]:
        """Generate questions linking procedures to regulations"""

        if not procedure.related_regulations:
            return []

        prompt = f"""Based on this operational procedure and its regulatory requirements, generate {num} compliance questions.

Procedure: {procedure.title}
Related Regulations: {', '.join(procedure.related_regulations)}
Controls: {', '.join(procedure.controls) if procedure.controls else 'See content'}

Generate questions like:
- "How does this procedure ensure compliance with [regulation]?"
- "What controls are in place for [requirement]?"
- "How do we demonstrate compliance with [specific article]?"

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations and regulatory compliance.", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "answer linking procedure to regulation"}}]}}
"""

        return self._call_claude_for_examples(prompt)

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
            for msg in messages:
                if 'content' not in msg or not msg['content']:
                    return False
            return True
        except (KeyError, TypeError, IndexError):
            return False

    def generate_cross_procedure_scenarios(
        self,
        procedures: List[OperationalProcedure],
        num_examples: int = 10
    ) -> List[Dict]:
        """Generate scenarios that involve multiple procedures"""

        if len(procedures) < 2:
            return []

        prompt = f"""Generate {num_examples} realistic operational scenarios that involve multiple procedures working together.

Procedures available:
{chr(10).join(f'- {p.title} ({p.procedure_type.value})' for p in procedures[:5])}

Generate complex scenarios like:
- "We need to onboard a new fund while ensuring UCITS compliance. What procedures do we follow?"
- "A NAV error was detected. Walk me through the error correction and escalation procedures."
- "How do the trade settlement and reconciliation procedures interact?"

Create multi-step answers that reference multiple procedures.

Return ONLY valid JSON objects in JSONL format (one per line):
{{"system": "You are an expert in fund operations with deep knowledge of operational procedures and workflows.", "messages": [{{"role": "user", "content": "complex scenario"}}, {{"role": "assistant", "content": "detailed answer referencing multiple procedures"}}]}}
"""

        return self._call_claude_for_examples(prompt)


class OperationalKnowledgeBase:
    """Manage a knowledge base of operational procedures"""

    def __init__(self):
        """Initialize knowledge base"""
        self.procedures: Dict[str, OperationalProcedure] = {}
        self.procedure_index: Dict[str, List[str]] = {
            'by_type': {},
            'by_regulation': {},
            'by_role': {}
        }

    def add_procedure(self, procedure: OperationalProcedure):
        """Add a procedure to the knowledge base"""
        proc_id = self._generate_id(procedure.title)
        self.procedures[proc_id] = procedure

        # Index by type
        ptype = procedure.procedure_type.value
        if ptype not in self.procedure_index['by_type']:
            self.procedure_index['by_type'][ptype] = []
        self.procedure_index['by_type'][ptype].append(proc_id)

        # Index by regulation
        for reg in procedure.related_regulations:
            if reg not in self.procedure_index['by_regulation']:
                self.procedure_index['by_regulation'][reg] = []
            self.procedure_index['by_regulation'][reg].append(proc_id)

        # Index by role
        for role in procedure.roles:
            if role not in self.procedure_index['by_role']:
                self.procedure_index['by_role'][role] = []
            self.procedure_index['by_role'][role].append(proc_id)

    def get_procedures_by_regulation(self, regulation: str) -> List[OperationalProcedure]:
        """Get all procedures related to a regulation"""
        proc_ids = self.procedure_index['by_regulation'].get(regulation, [])
        return [self.procedures[pid] for pid in proc_ids]

    def get_procedures_by_role(self, role: str) -> List[OperationalProcedure]:
        """Get all procedures involving a role"""
        proc_ids = self.procedure_index['by_role'].get(role, [])
        return [self.procedures[pid] for pid in proc_ids]

    def get_procedures_by_type(self, proc_type: str) -> List[OperationalProcedure]:
        """Get all procedures of a type"""
        proc_ids = self.procedure_index['by_type'].get(proc_type, [])
        return [self.procedures[pid] for pid in proc_ids]

    def _generate_id(self, title: str) -> str:
        """Generate a unique ID for a procedure"""
        import hashlib
        return hashlib.md5(title.encode()).hexdigest()[:12]

    def export_metadata(self) -> Dict:
        """Export knowledge base metadata"""
        return {
            'total_procedures': len(self.procedures),
            'by_type': {k: len(v) for k, v in self.procedure_index['by_type'].items()},
            'by_regulation': {k: len(v) for k, v in self.procedure_index['by_regulation'].items()},
            'by_role': {k: len(v) for k, v in self.procedure_index['by_role'].items()},
        }


def create_sample_procedures() -> List[OperationalProcedure]:
    """Create sample operational procedures for testing"""

    sample1 = """
    NAV Calculation Procedure

    Type: Standard Operating Procedure
    Regulation: UCITS Directive Article 85

    Responsible: Fund Accountant
    Review: Fund Controller

    Trigger: Daily, at market close

    Steps:
    1. Obtain closing prices from pricing vendors
    2. Verify price sources against approved list (Control: Price Source Validation)
    3. Calculate fund holdings value using latest prices
    4. Add accrued income and receivables
    5. Subtract liabilities and accrued expenses
    6. Divide by number of outstanding shares
    7. Review NAV movement vs. prior day (Control: NAV Movement Check)
    8. Escalate if NAV movement exceeds 5% (unless explained by market conditions)
    9. Obtain Controller approval
    10. Publish NAV to distribution channels

    Output: Daily NAV
    Control: Four-eyes principle, NAV movement threshold alerts
    """

    sample2 = """
    Trade Settlement Monitoring Workflow

    Type: Workflow
    Regulation: MiFID II best execution requirements

    Responsible: Middle Office

    Trigger: T+1 after trade execution

    Process:
    1. Receive trade confirmations from counterparties
    2. Match trade details against internal records
    3. Identify any breaks or discrepancies
    4. If breaks exist:
       - Investigate cause
       - Contact counterparty if needed
       - Escalate to Trading Desk if unresolved within 2 hours
    5. Monitor settlement date approach
    6. Flag trades at risk of failing settlement
    7. Coordinate with custodian for settlement
    8. Confirm cash and securities movements
    9. Update settlement status in system

    Escalation: Unmatched trades > 1% of fund value escalate to CIO
    """

    sample3 = """
    Investor Onboarding Compliance Checklist

    Type: Checklist
    Regulation: AML/KYC requirements, MiFID II

    Role: Client Services Team

    Prerequisites:
    □ Subscription agreement received
    □ Investor classification determined (Retail/Professional/Eligible Counterparty)

    KYC Checks:
    □ Identity verification completed (passport/ID card)
    □ Proof of address verified (< 3 months old)
    □ Source of funds documented
    □ PEP screening completed
    □ Sanctions screening completed
    □ Adverse media check performed

    Suitability Assessment (for retail investors):
    □ Investment objectives captured
    □ Risk tolerance assessed
    □ Financial situation documented
    □ Knowledge and experience evaluated
    □ Suitability determination made

    Documentation:
    □ Subscription agreement signed
    □ Prospectus/KIID provided
    □ Risk warnings acknowledged
    □ W-8/W-9 forms completed (if applicable)

    Final Approval:
    □ AML Officer approval obtained
    □ Compliance sign-off received
    □ Investor account created in system

    Regulation: UCITS Article 78 (disclosure), MiFID II Article 25 (suitability)
    """

    parser = OperationalProcedureParser()

    procedures = [
        parser.parse_procedure(sample1, "NAV Calculation Procedure"),
        parser.parse_procedure(sample2, "Trade Settlement Monitoring Workflow"),
        parser.parse_procedure(sample3, "Investor Onboarding Compliance Checklist")
    ]

    return procedures
