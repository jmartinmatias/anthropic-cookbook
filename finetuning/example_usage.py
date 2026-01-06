"""
Example: Using the EU Funds Training Data Generator

This script demonstrates how to use the generator both from command line
and programmatically.
"""

import os
from generate_eu_funds_training_data import EUFundsTrainingDataGenerator

# Set your API key (or set ANTHROPIC_API_KEY environment variable)
API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'your-api-key-here')


def example_1_basic_generation():
    """Example 1: Basic usage - generate from a regulatory document"""

    print("=" * 80)
    print("Example 1: Basic Training Data Generation")
    print("=" * 80)

    generator = EUFundsTrainingDataGenerator(api_key=API_KEY)

    # Generate training data from sample document
    num_examples = generator.generate_from_document(
        file_path='sample_ucits_text.txt',
        output_path='output/ucits_basic_training.jsonl',
        examples_per_chunk=15,
        include_specialized=True
    )

    print(f"\n✅ Generated {num_examples} examples")
    print(f"📁 Saved to: output/ucits_basic_training.jsonl")


def example_2_custom_system_prompt():
    """Example 2: Using a custom system prompt"""

    print("\n" + "=" * 80)
    print("Example 2: Custom System Prompt for Compliance Advisors")
    print("=" * 80)

    generator = EUFundsTrainingDataGenerator(api_key=API_KEY)

    custom_prompt = """You are a senior regulatory compliance advisor specializing in EU investment funds.
You provide practical, actionable guidance to fund managers on compliance with UCITS, AIFMD, and related regulations.
Your advice is accurate, cites specific regulatory provisions, and considers real-world implementation challenges."""

    num_examples = generator.generate_from_document(
        file_path='sample_ucits_text.txt',
        output_path='output/compliance_advisor_training.jsonl',
        examples_per_chunk=10,
        system_prompt=custom_prompt
    )

    print(f"\n✅ Generated {num_examples} examples with custom system prompt")


def example_3_specialized_examples_only():
    """Example 3: Use only hand-crafted specialized examples"""

    print("\n" + "=" * 80)
    print("Example 3: Hand-Crafted Examples Only")
    print("=" * 80)

    generator = EUFundsTrainingDataGenerator(api_key=API_KEY)

    # Get specialized examples
    examples = generator.create_specialized_examples()

    # Save to file
    import json
    output_path = 'output/specialized_examples.jsonl'
    os.makedirs('output', exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"\n✅ Generated {len(examples)} specialized examples")
    print(f"📁 Saved to: {output_path}")

    # Display one example
    print("\n📖 Sample example:")
    print(json.dumps(examples[0], indent=2, ensure_ascii=False))


def example_4_validate_training_data():
    """Example 4: Validate an existing training file"""

    print("\n" + "=" * 80)
    print("Example 4: Validate Training Data")
    print("=" * 80)

    generator = EUFundsTrainingDataGenerator(api_key=API_KEY)

    # Validate a file (create one first if needed)
    training_file = 'output/ucits_basic_training.jsonl'

    if os.path.exists(training_file):
        results = generator.validate_training_file(training_file)

        print(f"\n📊 Validation Results for {training_file}:")
        print(f"   Total examples: {results['total_examples']}")
        print(f"   Valid examples: {results['valid_examples']}")
        print(f"   Errors: {len(results['errors'])}")
        print(f"   Warnings: {len(results['warnings'])}")

        if results['errors']:
            print("\n   ❌ Errors found:")
            for error in results['errors'][:5]:
                print(f"      - {error}")

        if results['warnings']:
            print("\n   ⚠️  Warnings:")
            for warning in results['warnings'][:5]:
                print(f"      - {warning}")

        if results['valid_examples'] == results['total_examples']:
            print("\n   ✅ All examples valid!")
    else:
        print(f"File not found: {training_file}")
        print("Run example_1_basic_generation() first")


def example_5_batch_processing():
    """Example 5: Process multiple regulatory documents"""

    print("\n" + "=" * 80)
    print("Example 5: Batch Processing Multiple Documents")
    print("=" * 80)

    generator = EUFundsTrainingDataGenerator(api_key=API_KEY)

    # Example: Process multiple regulatory texts
    documents = {
        'sample_ucits_text.txt': {
            'output': 'output/ucits_training.jsonl',
            'system': 'You are a UCITS compliance expert.',
            'examples': 15
        },
        # Add more documents here:
        # 'aifmd_text.txt': {
        #     'output': 'output/aifmd_training.jsonl',
        #     'system': 'You are an AIFMD specialist.',
        #     'examples': 20
        # },
    }

    total_examples = 0

    for doc_path, config in documents.items():
        if os.path.exists(doc_path):
            print(f"\nProcessing: {doc_path}")

            num_examples = generator.generate_from_document(
                file_path=doc_path,
                output_path=config['output'],
                examples_per_chunk=config['examples'],
                system_prompt=config.get('system')
            )

            total_examples += num_examples
            print(f"✅ Generated {num_examples} examples")
        else:
            print(f"⚠️  File not found: {doc_path}")

    print(f"\n🎉 Total examples generated: {total_examples}")


def example_6_combine_datasets():
    """Example 6: Combine multiple training files"""

    print("\n" + "=" * 80)
    print("Example 6: Combine Multiple Training Files")
    print("=" * 80)

    import json

    output_files = [
        'output/ucits_training.jsonl',
        'output/compliance_advisor_training.jsonl',
        'output/specialized_examples.jsonl',
    ]

    combined_output = 'output/combined_eu_funds_training.jsonl'

    all_examples = []

    for file_path in output_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        all_examples.append(json.loads(line))
            print(f"✅ Read {file_path}")

    # Write combined file
    os.makedirs('output', exist_ok=True)
    with open(combined_output, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"\n🎉 Combined {len(all_examples)} examples")
    print(f"📁 Saved to: {combined_output}")


def main():
    """Run all examples"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        EU Investment Funds Training Data Generator - Examples               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Check API key
    if API_KEY == 'your-api-key-here':
        print("⚠️  Please set your ANTHROPIC_API_KEY environment variable")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Run examples
    try:
        example_1_basic_generation()
        example_2_custom_system_prompt()
        example_3_specialized_examples_only()
        example_4_validate_training_data()
        example_5_batch_processing()
        example_6_combine_datasets()

        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)

        print("\n📚 Next Steps:")
        print("1. Review the generated files in the 'output/' directory")
        print("2. Upload to S3: aws s3 cp output/combined_eu_funds_training.jsonl s3://your-bucket/")
        print("3. Launch fine-tuning job in AWS Bedrock (see finetuning_on_bedrock.ipynb)")
        print("4. Deploy your fine-tuned model with Provisioned Throughput")
        print("5. Test with real regulatory queries!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
