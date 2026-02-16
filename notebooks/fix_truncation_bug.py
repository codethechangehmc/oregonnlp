"""
Fix truncated_document error by removing tokenizer parameter entirely
"""
import json

# Read the notebook
with open('bertopic_explore_3.ipynb', 'r') as f:
    nb = json.load(f)

# Find and update the setup_offline_llm function
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'def setup_offline_llm' in ''.join(cell['source']):
        source = ''.join(cell['source'])

        # Remove the tokenizer parameter from TextGeneration completely
        old_text = """    # Create representation model with model-specific tokenizer
    representation_model = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=10,
        diversity=0.3,
        doc_length=100,
        tokenizer=selected_config['tokenizer']
    )"""

        new_text = """    # Create representation model WITHOUT tokenizer to avoid truncation bug
    # BERTopic 0.17.3 has a bug with custom tokenizers - omitting it uses default truncation
    representation_model = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=10,
        diversity=0.3,
        doc_length=100
        # tokenizer parameter removed - causes UnboundLocalError in BERTopic 0.17.3
    )"""

        source = source.replace(old_text, new_text)

        # Update the print statement
        source = source.replace(
            '    print(f"   Tokenizer: {selected_config[\'tokenizer\']} (None = uses default truncation)")',
            '    print(f"   Tokenizer: Default (custom tokenizer removed to fix bug)")'
        )

        cell['source'] = source.split('\n')
        print("✅ Removed tokenizer parameter from TextGeneration")
        break

# Save the updated notebook
with open('bertopic_explore_3.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("\n" + "=" * 70)
print("✅ FIX APPLIED!")
print("=" * 70)
print("Changed:")
print("  - Removed 'tokenizer' parameter from TextGeneration()")
print("  - This avoids the UnboundLocalError in truncate_document()")
print("  - BERTopic will now use default string truncation (first N chars)")
print("\nThe LLM labeling should now work!")
print("=" * 70)
