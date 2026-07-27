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

sig = find_node(data, 'Signature')
def dump_tree(n, indent=0):
    print("  " * indent + f"- '{n['name']}' ({n.get('type')}) [desc len: {len(n.get('description',''))}]")
    for c in n.get('children', []):
        dump_tree(c, indent + 1)

if sig:
    print("SIGNATURE TREE:")
    dump_tree(sig)
