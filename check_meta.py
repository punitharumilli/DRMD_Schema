import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def count_nodes(node):
    c = 1
    for child in node.get('children', []):
        c += count_nodes(child)
    return c

p = [c for c in data['children'] if c['name']=='propertiesList'][0]
meta = [c for c in p['children'][0]['children'] if c['name']=='measurementMetaData'][0]

print("CHILDREN OF measurementMetaData:")
for c in meta.get('children', []):
    print(f"  {c['name']} ({c.get('type')}): {count_nodes(c)} nodes")
    for cc in c.get('children', []):
        print(f"    {cc['name']} ({cc.get('type')}): {count_nodes(cc)} nodes")
        for ccc in cc.get('children', []):
            print(f"      {ccc['name']} ({ccc.get('type')}): {count_nodes(ccc)} nodes")
