import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

empty_names = []
empty_descs = []
total_nodes = 0

def inspect(n, path=''):
    global total_nodes
    total_nodes += 1
    p = f"{path}/{n['name']}" if path else n['name']
    if not n.get('name') or n['name'].strip() == '':
        empty_names.append(p)
    if not n.get('description') or n['description'].strip() == '':
        empty_descs.append((p, n.get('type', '')))
    for c in n.get('children', []):
        inspect(c, p)

inspect(data)
print(f"Total nodes inspected: {total_nodes}")
print(f"Nodes with empty name: {len(empty_names)}")
if empty_names:
    print("  Examples:", empty_names[:5])
print(f"Nodes with empty description: {len(empty_descs)}")
if empty_descs:
    print("  Examples:", empty_descs[:5])
