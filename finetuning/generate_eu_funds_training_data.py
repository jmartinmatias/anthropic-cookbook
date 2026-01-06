"""
Generate Fine-tuning Training Data from EU Investment Funds Regulatory Texts

This script creates training examples from regulatory documents such as:
- UCITS Directive
- AIFMD (Alternative Investment Fund Managers Directive)
- MiFID II
- PRIIPs Regulation
- SFDR (Sustainable Finance Disclosure Regulation)
- And other EU fund regulations

Usage:
    python generate_eu_funds_training_data.py --input regulations.pdf --output training_data.jsonl
"""

import anthropic
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import re


class EUFundsTrainingDataGenerator:
    """Generate training data from EU investment funds regulatory texts"""

    # Common regulatory frameworks
    REGULATORY_FRAMEWORKS = [
        "UCITS",
        "AIFMD",
        "MiFID II",
        "PRIIPs",
        "SFDR",
        "Taxonomy Regulation",
        "ELTIF",
        "EMIR",
        "Prospectus Regulation"
    ]

    # Question types for comprehensive coverage
    QUESTION_TYPES = {
        "definitional": "What is the definition of {term}?",
        "procedural": "What are the requirements for {process}?",
        "compliance": "What are the obligations under {regulation} for {entity}?",
        "comparative": "What is the difference between {concept_a} and {concept_b}?",
        "threshold": "What are the thresholds/limits for {requirement}?",
        "timeline": "What are the deadlines/timelines for {obligation}?",
        "exemption": "What exemptions exist for {requirement}?",
        "penalty": "What are the consequences of non-compliance with {rule}?",
        "reporting": "What reporting requirements apply to {entity}?",
        "disclosure": "What disclosure obligations apply to {scenario}?"
    }

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize the generator with Anthropic API key"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def read_document(self, file_path: str) -> str:
        """Read document from various formats"""
        path = Path(file_path)

        if path.suffix == '.txt':
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        elif path.suffix == '.pdf':
            # For PDF, you'd need PyPDF2 or similar
            print("Note: PDF support requires PyPDF2. Reading as text for now.")
            try:
                import PyPDF2
                with open(path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                return text
            except ImportError:
                print("Install PyPDF2 for PDF support: pip install PyPDF2")
                return ""
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

    def chunk_document(self, text: str, chunk_size: int = 80000) -> List[str]:
        """Split document into manageable chunks for processing"""
        # Try to split on article/section boundaries for regulatory texts

        # Look for common regulatory text patterns
        section_patterns = [
            r'\nArticle \d+',
            r'\nSection \d+',
            r'\nChapter \d+',
            r'\n\(\d+\)',  # Numbered paragraphs
        ]

        chunks = []
        current_chunk = ""

        # Split by paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
            else:
                current_chunk += "\n\n" + para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    def generate_examples_from_chunk(
        self,
        chunk: str,
        num_examples: int = 20,
        system_prompt: str = None
    ) -> List[Dict]:
        """Generate training examples from a document chunk using Claude"""

        if system_prompt is None:
            system_prompt = """You are an expert in EU investment funds regulation. You provide accurate,
precise answers based on regulatory texts. You cite specific articles and directives when relevant."""

        prompt = f"""Based on the following regulatory text, generate {num_examples} diverse training examples.

Create examples covering these question types:
1. Definitions of key terms (e.g., "What is a UCITS?", "Define alternative investment fund")
2. Procedural requirements (e.g., "What are the authorization requirements for an AIFM?")
3. Compliance obligations (e.g., "What are the disclosure obligations under SFDR?")
4. Thresholds and limits (e.g., "What are the leverage limits for UCITS?")
5. Exemptions and exclusions (e.g., "Which funds are exempt from AIFMD?")
6. Reporting requirements (e.g., "What must be included in a UCITS annual report?")
7. Deadlines and timelines (e.g., "When must a Key Information Document be provided?")
8. Multi-turn conversations (include some follow-up questions)

IMPORTANT FORMATTING RULES:
- Return ONLY valid JSON objects
- One JSON object per line (JSONL format)
- Each object must have this exact structure:
  {{"system": "system prompt", "messages": [{{"role": "user", "content": "question"}}, {{"role": "assistant", "content": "detailed answer with citations"}}]}}
- For multi-turn examples, include multiple user/assistant exchanges
- Answers should cite specific articles/paragraphs when possible
- Answers should be comprehensive but concise
- Do NOT include any text outside the JSON objects
- Do NOT number the examples
- Do NOT add explanatory text

Regulatory Text:
{chunk}

Generate {num_examples} training examples now:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            examples = []
            text_response = response.content[0].text

            # Parse JSONL response
            for line in text_response.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('//') or line.startswith('#'):
                    continue

                try:
                    # Try to extract JSON from the line
                    # Handle cases where there might be surrounding text
                    json_match = re.search(r'\{.*\}', line)
                    if json_match:
                        example = json.loads(json_match.group())

                        # Validate structure
                        if self._validate_example(example, system_prompt):
                            examples.append(example)
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse line as JSON: {line[:100]}...")
                    continue

            return examples

        except Exception as e:
            print(f"Error generating examples: {e}")
            return []

    def _validate_example(self, example: Dict, default_system: str) -> bool:
        """Validate that example follows required format"""
        try:
            # Must have messages
            if 'messages' not in example:
                return False

            messages = example['messages']

            # Must have at least 2 messages
            if len(messages) < 2:
                return False

            # First must be user, last must be assistant
            if messages[0]['role'] != 'user' or messages[-1]['role'] != 'assistant':
                return False

            # Messages must alternate
            for i in range(len(messages) - 1):
                if messages[i]['role'] == messages[i+1]['role']:
                    return False

            # Add default system prompt if missing
            if 'system' not in example or not example['system']:
                example['system'] = default_system

            # All messages must have content
            for msg in messages:
                if 'content' not in msg or not msg['content']:
                    return False

            return True

        except (KeyError, TypeError, IndexError):
            return False

    def create_specialized_examples(self) -> List[Dict]:
        """Create hand-crafted examples for specific EU funds scenarios"""

        examples = [
            {
                "system": "You are an expert in EU investment funds regulation, specializing in UCITS compliance.",
                "messages": [
                    {"role": "user", "content": "What is a UCITS fund?"},
                    {"role": "assistant", "content": "A UCITS (Undertakings for Collective Investment in Transferable Securities) is a regulated investment fund that can be marketed across the EU under a single authorization. UCITS are governed by Directive 2009/65/EC and must comply with strict rules on eligible assets, diversification, liquidity, leverage, and investor protection. They are designed to be highly liquid, diversified retail investment products."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in UCITS compliance.",
                "messages": [
                    {"role": "user", "content": "What are the diversification requirements for UCITS?"},
                    {"role": "assistant", "content": "Under Article 52 of the UCITS Directive, the key diversification requirements are:\n\n1. Maximum 10% of assets in securities from a single issuer\n2. Maximum 20% if the issuer is a credit institution with special supervision\n3. Maximum 5% in unlisted securities\n4. The 10% limit can be raised to 25% for covered bonds and certain other instruments\n5. The aggregate of positions exceeding 5% cannot exceed 40% of assets\n\nThese rules ensure appropriate risk spreading and investor protection."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in AIFMD.",
                "messages": [
                    {"role": "user", "content": "What is the difference between UCITS and AIF?"},
                    {"role": "assistant", "content": "The key differences are:\n\n**UCITS (Directive 2009/65/EC):**\n- Retail-focused investment funds\n- Strict investment restrictions (mainly transferable securities)\n- Automatic EU passporting rights\n- Daily liquidity required\n- Leverage limits\n- Lower operational flexibility\n\n**AIF (under AIFMD 2011/61/EU):**\n- Catch-all category for non-UCITS funds (hedge funds, private equity, real estate, etc.)\n- More flexible investment strategies\n- Primarily for professional/institutional investors\n- Less restrictive liquidity requirements\n- Higher leverage permitted\n- More complex operational requirements\n\nBasically, any collective investment vehicle that is not UCITS is classified as an AIF."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in SFDR and sustainable finance.",
                "messages": [
                    {"role": "user", "content": "What are Article 8 and Article 9 funds under SFDR?"},
                    {"role": "assistant", "content": "Under the Sustainable Finance Disclosure Regulation (SFDR - Regulation EU 2019/2088):\n\n**Article 8 Funds (Light Green):**\n- Promote environmental or social characteristics\n- Must invest in companies with good governance practices\n- Required to disclose how E/S characteristics are met\n- No minimum threshold for sustainable investments (though many have one)\n\n**Article 9 Funds (Dark Green):**\n- Have sustainable investment as their objective\n- Must demonstrate measurable positive impact\n- Highest level of sustainability commitment\n- Strictest disclosure requirements\n- Must use a sustainability benchmark or explain why not\n\nArticle 6 funds (not mentioned) are traditional funds without specific sustainability claims."},
                    {"role": "user", "content": "What are the disclosure requirements for Article 8 funds?"},
                    {"role": "assistant", "content": "Article 8 funds under SFDR must provide:\n\n**Pre-contractual disclosures:**\n- Description of E/S characteristics promoted\n- Information on methodologies used\n- Data sources and screening criteria\n- Due diligence processes\n- Engagement policies\n\n**Website disclosures:**\n- Summary of E/S characteristics\n- No significant harm (DNSH) assessment if applicable\n- Sustainability indicators used\n\n**Periodic reporting (annual):**\n- Extent to which E/S characteristics were met\n- Proportion of sustainable investments (if committed)\n- Principal adverse impact (PAI) indicators (if applicable)\n- Actions taken to meet characteristics\n\nThese disclosures must be clear, accessible, and updated regularly per Articles 6, 8, and 11 of SFDR."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in MiFID II and investor protection.",
                "messages": [
                    {"role": "user", "content": "What is the difference between professional and retail clients under MiFID II?"},
                    {"role": "assistant", "content": "Under MiFID II (Directive 2014/65/EU), the classification determines the level of protection:\n\n**Retail Clients:**\n- Highest level of protection\n- Full appropriateness/suitability assessments required\n- Best execution reporting\n- Detailed cost and charges disclosure\n- Stronger conduct of business rules apply\n\n**Professional Clients (Annex II):**\n- Presumed to have knowledge and experience\n- Reduced protection requirements\n- Can opt down to retail status\n- Includes: credit institutions, investment firms, insurance companies, UCITS, pension funds, large corporates (€20M balance sheet, €40M turnover, €2M own funds)\n\n**Eligible Counterparties:**\n- Lowest protection (for certain services only)\n- Only for investment firms, credit institutions, insurance companies, UCITS, pension funds\n\nThe classification affects disclosure requirements, suitability assessments, and conduct obligations."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in fund documentation and PRIIPs.",
                "messages": [
                    {"role": "user", "content": "What must be included in a UCITS KIID?"},
                    {"role": "assistant", "content": "The UCITS Key Investor Information Document (KIID) must include (per Commission Regulation 583/2010):\n\n1. **Identification:** Fund name, ISIN, management company, competent authority\n\n2. **Objectives and investment policy:** Clear description in plain language\n\n3. **Risk and reward profile:** SRRI indicator (1-7 scale) and explanation\n\n4. **Material risks:** Not adequately captured by SRRI\n\n5. **Costs:** \n   - Entry/exit charges\n   - Ongoing charges figure\n   - Performance fees\n   - Impact on returns illustration\n\n6. **Past performance:** Bar chart (10 years if available, minimum 1 year)\n\n7. **Practical information:** \n   - Depositary name\n   - Where to find additional information\n   - Tax information\n   - Liability statement\n\nMaximum 2 sides of A4, updated annually. Note: Being replaced by PRIIPs KID for new funds."}
                ]
            },
            {
                "system": "You are an expert in EU investment funds regulation, specializing in depositary requirements.",
                "messages": [
                    {"role": "user", "content": "What are the main duties of a UCITS depositary?"},
                    {"role": "assistant", "content": "Under Article 22 of the UCITS Directive (2009/65/EC), the depositary must:\n\n**1. Safekeeping:**\n- Hold financial instruments in custody (segregated accounts)\n- Verify ownership and maintain records for other assets\n- Liable for loss of held instruments unless can prove uncontrollable external event\n\n**2. Oversight:**\n- Ensure sales/redemptions comply with law and fund rules\n- Verify NAV calculation is per UCITS rules\n- Ensure investment income is properly allocated\n- Monitor cash flows\n\n**3. Instructions:**\n- Carry out management company instructions unless contrary to law/fund rules\n\n**4. Independence:**\n- Must be independent from the management company\n- Strict conflict of interest requirements\n\nThe depositary has a critical investor protection role and can be held liable for losses due to breach of duties."}
                ]
            }
        ]

        return examples

    def generate_from_document(
        self,
        file_path: str,
        output_path: str,
        examples_per_chunk: int = 15,
        include_specialized: bool = True,
        system_prompt: Optional[str] = None
    ) -> int:
        """
        Generate complete training dataset from a regulatory document

        Args:
            file_path: Path to regulatory document
            output_path: Path to save JSONL training data
            examples_per_chunk: Number of examples to generate per chunk
            include_specialized: Whether to include hand-crafted examples
            system_prompt: Custom system prompt (uses default if None)

        Returns:
            Number of examples generated
        """
        print(f"Reading document: {file_path}")
        document = self.read_document(file_path)

        if not document:
            print("Error: Could not read document")
            return 0

        print(f"Document length: {len(document)} characters")

        # Chunk the document
        chunks = self.chunk_document(document)
        print(f"Split into {len(chunks)} chunks")

        all_examples = []

        # Add specialized examples if requested
        if include_specialized:
            specialized = self.create_specialized_examples()
            all_examples.extend(specialized)
            print(f"Added {len(specialized)} specialized examples")

        # Generate examples from each chunk
        for i, chunk in enumerate(chunks):
            print(f"\nProcessing chunk {i+1}/{len(chunks)}...")
            examples = self.generate_examples_from_chunk(
                chunk,
                num_examples=examples_per_chunk,
                system_prompt=system_prompt
            )
            all_examples.extend(examples)
            print(f"Generated {len(examples)} examples from chunk {i+1}")

        # Save to JSONL
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for example in all_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        print(f"\n✅ Successfully generated {len(all_examples)} training examples")
        print(f"📁 Saved to: {output_path}")

        return len(all_examples)

    def validate_training_file(self, file_path: str) -> Dict[str, any]:
        """Validate a JSONL training file for Bedrock compatibility"""

        results = {
            'total_examples': 0,
            'valid_examples': 0,
            'errors': [],
            'warnings': []
        }

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                results['total_examples'] += 1

                try:
                    example = json.loads(line)

                    # Validate structure
                    if 'messages' not in example:
                        results['errors'].append(f"Line {line_num}: Missing 'messages' field")
                        continue

                    messages = example['messages']

                    if len(messages) < 2:
                        results['errors'].append(f"Line {line_num}: Must have at least 2 messages")
                        continue

                    if messages[0]['role'] != 'user':
                        results['errors'].append(f"Line {line_num}: First message must be from user")
                        continue

                    if messages[-1]['role'] != 'assistant':
                        results['errors'].append(f"Line {line_num}: Last message must be from assistant")
                        continue

                    # Check alternation
                    for i in range(len(messages) - 1):
                        if messages[i]['role'] == messages[i+1]['role']:
                            results['errors'].append(f"Line {line_num}: Messages must alternate between user and assistant")
                            break
                    else:
                        results['valid_examples'] += 1

                    # Warnings
                    if 'system' not in example or not example['system']:
                        results['warnings'].append(f"Line {line_num}: No system prompt")

                except json.JSONDecodeError:
                    results['errors'].append(f"Line {line_num}: Invalid JSON")

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Generate fine-tuning training data from EU investment funds regulatory texts'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to regulatory document (txt, pdf)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='eu_funds_training_data.jsonl',
        help='Output path for JSONL training data'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '--examples-per-chunk',
        type=int,
        default=15,
        help='Number of examples to generate per document chunk'
    )
    parser.add_argument(
        '--no-specialized',
        action='store_true',
        help='Exclude hand-crafted specialized examples'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing training file'
    )
    parser.add_argument(
        '--system-prompt',
        type=str,
        help='Custom system prompt for training examples'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')
    if not api_key and not args.validate_only:
        print("Error: API key required. Set ANTHROPIC_API_KEY env var or use --api-key")
        return 1

    generator = EUFundsTrainingDataGenerator(api_key=api_key)

    # Validation mode
    if args.validate_only:
        print(f"Validating training file: {args.output}")
        results = generator.validate_training_file(args.output)

        print(f"\n📊 Validation Results:")
        print(f"Total examples: {results['total_examples']}")
        print(f"Valid examples: {results['valid_examples']}")
        print(f"Errors: {len(results['errors'])}")
        print(f"Warnings: {len(results['warnings'])}")

        if results['errors']:
            print("\n❌ Errors:")
            for error in results['errors'][:10]:  # Show first 10
                print(f"  - {error}")

        if results['warnings']:
            print("\n⚠️  Warnings:")
            for warning in results['warnings'][:10]:
                print(f"  - {warning}")

        return 0 if len(results['errors']) == 0 else 1

    # Generation mode
    num_examples = generator.generate_from_document(
        file_path=args.input,
        output_path=args.output,
        examples_per_chunk=args.examples_per_chunk,
        include_specialized=not args.no_specialized,
        system_prompt=args.system_prompt
    )

    if num_examples > 0:
        print("\n🔍 Validating generated file...")
        results = generator.validate_training_file(args.output)
        print(f"Valid examples: {results['valid_examples']}/{results['total_examples']}")

        if results['errors']:
            print(f"⚠️  Found {len(results['errors'])} errors - please review")

        print("\n✅ Training data generation complete!")
        print(f"\nNext steps:")
        print(f"1. Review the generated file: {args.output}")
        print(f"2. Upload to S3: aws s3 cp {args.output} s3://your-bucket/")
        print(f"3. Launch fine-tuning job in Bedrock")

    return 0


if __name__ == '__main__':
    import os
    import sys
    sys.exit(main())
