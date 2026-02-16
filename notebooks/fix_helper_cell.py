"""
Fix the helper functions cell to remove tokenizer parameter
"""
import json
import re

# Read the notebook
with open('bertopic_explore_3.ipynb', 'r') as f:
    nb = json.load(f)

# Find cell-3 (helper functions)
for cell in nb['cells']:
    if cell.get('id') == 'cell-3' or ('setup_offline_llm' in ''.join(cell.get('source', []))):
        source = ''.join(cell['source'])

        # Replace the TextGeneration call - use regex to handle any whitespace
        old_pattern = r'representation_model = TextGeneration\(\s+generator,\s+prompt=prompt,\s+nr_docs=10,\s+diversity=0\.3,\s+doc_length=100,\s+tokenizer=selected_config\[\'tokenizer\'\]\s+\)'

        new_text = """representation_model = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=10,
        diversity=0.3,
        doc_length=100
        # tokenizer parameter removed - causes UnboundLocalError in BERTopic 0.17.3
    )"""

        # Try the replacement
        new_source = re.sub(old_pattern, new_text, source)

        if new_source != source:
            cell['source'] = new_source.split('\n')
            print("✅ Successfully removed tokenizer parameter!")
        else:
            # Try alternate approach - simple string replacement
            old_text = """    representation_model = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=10,
        diversity=0.3,
        doc_length=100,
        tokenizer=selected_config['tokenizer']
    )"""

            new_text2 = """    representation_model = TextGeneration(
        generator,
        prompt=prompt,
        nr_docs=10,
        diversity=0.3,
        doc_length=100
        # tokenizer parameter removed - causes UnboundLocalError in BERTopic 0.17.3
    )"""

            new_source = source.replace(old_text, new_text2)

            if new_source != source:
                cell['source'] = new_source.split('\n')
                print("✅ Successfully removed tokenizer parameter (alternate method)!")
            else:
                print("⚠️ Could not find exact match to replace")
                print("Looking for:")
                print(old_text)
        break

# Save
with open('bertopic_explore_3.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("\n✅ Notebook saved!")
