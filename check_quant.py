import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_node(n, target_name):
    if n['name'] == target_name:
        return n
    for c in n.get('children', []):
        res = find_node(c, target_name)
        if res: return res
    return None

q = find_node(data, 'quantity')
if q:
    print(f"Found {q['name']} ({q.get('type')})")
    for c in q.get('children', []):
        print(f"  - {c['name']} ({c.get('type')}) [children: {len(c.get('children', []))}]")
