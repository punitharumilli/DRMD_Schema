import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def count_nodes(node):
    c = 1
    for child in node.get('children', []):
        c += count_nodes(child)
    return c

m = [c for c in data['children'] if c['name']=='materials'][0]
mat = m['children'][0] # material
print("CHILDREN OF material:")
for c in mat.get('children', []):
    print(f"  {c['name']} ({c.get('type')}): {count_nodes(c)} nodes")
    for cc in c.get('children', []):
        if count_nodes(cc) > 10:
            print(f"    {cc['name']} ({cc.get('type')}): {count_nodes(cc)} nodes")
            for ccc in cc.get('children', []):
                if count_nodes(ccc) > 10:
                    print(f"      {ccc['name']} ({ccc.get('type')}): {count_nodes(ccc)} nodes")
