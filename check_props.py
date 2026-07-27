import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def count_nodes(node):
    c = 1
    for child in node.get('children', []):
        c += count_nodes(child)
    return c

p = [c for c in data['children'] if c['name']=='propertiesList'][0]
props = p['children'][0] # properties
print("CHILDREN OF properties:")
for c in props.get('children', []):
    print(f"  {c['name']} ({c.get('type')}): {count_nodes(c)} nodes")
