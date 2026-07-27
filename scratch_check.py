import json
d = json.load(open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', encoding='utf-8'))

def find_all(n, target, results=None, path=''):
    if results is None: results = []
    p = path + '/' + n['name'] if path else n['name']
    if n['name'] == target:
        results.append((p, n.get('description', '')))
    for c in n.get('children', []):
        find_all(c, target, results, p)
    return results

for name in ['fileName', 'data', 'unit', 'city', 'coverageFactor']:
    results = find_all(d, name)
    filled = [r for r in results if r[1]]
    empty = [r for r in results if not r[1]]
    print(f'--- {name}: {len(filled)} filled, {len(empty)} empty ---')
    if empty:
        print(f'  First empty path: {empty[0][0]}')
    if filled:
        print(f'  First filled desc: {filled[0][1][:80]}')
    print()
