import json

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Type of root data:", type(data))
if isinstance(data, dict):
    print("Root name:", data.get('name'))
    print("Number of children of root:", len(data.get('children', [])))
    for c in data.get('children', []):
        print(f"  Child: {c['name']} ({c.get('type')})")
elif isinstance(data, list):
    print("Root is a list of length:", len(data))
    for item in data:
        print(f"  Item: {item.get('name')} ({item.get('type')})")
