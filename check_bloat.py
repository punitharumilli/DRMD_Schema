import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def count_nodes(node):
    c = 1
    for child in node.get('children', []):
        c += count_nodes(child)
    return c

print("NODE COUNT PER TOP-LEVEL BRANCH:")
for child in data.get('children', []):
    print(f"  {child['name']} ({child.get('type')}): {count_nodes(child)} nodes")
