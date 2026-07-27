import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def summarize(node, max_depth=6, current_depth=0):
    indent = "  " * current_depth
    t = node.get('type', '')
    desc = node.get('description', '')[:40]
    print(f"{indent}- {node['name']} ({t}) [children: {len(node.get('children', []))}]")
    if current_depth < max_depth:
        for c in node.get('children', []):
            summarize(c, max_depth, current_depth + 1)

print("TOP LEVEL AND CHILDREN OF ROOT:")
summarize(data, max_depth=3)
