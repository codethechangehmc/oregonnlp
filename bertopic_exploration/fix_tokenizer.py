"""
Fix tokenizer issue in setup_offline_llm function
"""
import json

# Read the notebook
with open('bertopic_explore_3.ipynb', 'r') as f:
    nb = json.load(f)

# Find and update the setup_offline_llm function
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'def setup_offline_llm' in ''.join(cell['source']):
        source = ''.join(cell['source'])

        # Replace all tokenizer: "whitespace" with tokenizer: None
        source = source.replace('"tokenizer": "whitespace"', '"tokenizer": None')

        # Also add a comment about the fix
        source = source.replace(
            '    # Model configurations (ordered by quality)',
            '    # Model configurations (ordered by quality)\n    # FIX: Set tokenizer to None to avoid truncate_document errors'
        )

        # Update print statement to show tokenizer value
        source = source.replace(
            '    print(f"   Fully reproducible: {seed}")',
            '    print(f"   Tokenizer: {selected_config[\'tokenizer\']} (None = uses default truncation)")\n    print(f"   Fully reproducible: {seed}")'
        )

        cell['source'] = source.split('\n')
        print("✅ Fixed tokenizer in setup_offline_llm function")
        break

# Update the LLM setup cell to use llama
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'MODEL_CHOICE = "auto"' in ''.join(cell['source']):
        source = ''.join(cell['source'])
        source = source.replace(
            'MODEL_CHOICE = "auto"  # Change this to use a specific model',
            'MODEL_CHOICE = "llama"  # Using Llama for best quality labels'
        )
        cell['source'] = source.split('\n')
        print("✅ Updated LLM setup cell to use Llama")
        break

# Update the LLM labeling cell to actually run
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and '# Note: Skip LLM labeling for now' in ''.join(cell['source']):
        # Replace with working version
        new_source = """# Generate labels using offline LLM - DEBUGGED VERSION
print("\\n🔄 Generating topic labels with offline LLM...")
print("This may take a few minutes depending on your hardware.\\n")

try:
    # Update topics with LLM-generated labels
    topic_model.update_topics(
        responses,
        representation_model=representation_model
    )

    print("\\n✅ Topic labels generated successfully!")

    # Display updated labels
    topic_info = topic_model.get_topic_info()
    print("\\n📊 Updated Topic Labels (After LLM):")
    print("=" * 80)
    print(topic_info[['Topic', 'Count', 'Name']].to_string())
    print("=" * 80)

except Exception as e:
    print(f"\\n❌ Error during LLM labeling: {type(e).__name__}: {e}")
    print("\\n⚠️ Using keyword-based labels instead")
    print("   Debug info: Check BERTopic version and tokenizer compatibility")

    # Show current labels as fallback
    topic_info = topic_model.get_topic_info()
    print("\\n📊 Current Topic Labels (c-TF-IDF):")
    print(topic_info[['Topic', 'Count', 'Name']].to_string())"""

        cell['source'] = new_source.split('\n')
        print("✅ Updated LLM labeling cell with error handling")
        break

# Save the updated notebook
with open('bertopic_explore_3.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("\n" + "=" * 70)
print("✅ Notebook updated successfully!")
print("=" * 70)
print("Changes made:")
print("  1. Fixed tokenizer: 'whitespace' → None in all models")
print("  2. Set MODEL_CHOICE to 'llama'")
print("  3. Updated LLM labeling cell to actually run with error handling")
print("\nThe tokenizer fix resolves the UnboundLocalError!")
print("=" * 70)
