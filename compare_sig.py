import xml.etree.ElementTree as ET
import json

tree = ET.parse(r'c:\Users\parumill\Downloads\schema\xmldsig-core-schema.xsd')
root = tree.getroot()
ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}

xsd_elements = set()
for el in root.findall('.//xs:element', ns):
    name = el.get('name')
    if name:
        xsd_elements.add(name)

print("Elements in xmldsig-core-schema.xsd:", sorted(list(xsd_elements)))

with open(r'c:\Users\parumill\Downloads\schema\docs\schema_data\schema.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def get_all_names(n, s=None):
    if s is None: s = set()
    s.add(n['name'])
    for c in n.get('children', []):
        get_all_names(c, s)
    return s

json_names = get_all_names(data)
missing_from_json = xsd_elements - json_names
print("Elements in xsd but missing from JSON tree:", sorted(list(missing_from_json)))
