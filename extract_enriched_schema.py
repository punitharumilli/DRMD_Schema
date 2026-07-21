import xmlschema
import xml.etree.ElementTree as ET
import json
import os

xsd_path = r'c:\Users\parumill\Downloads\schema\drmd.xsd'
sch_path = r'c:\Users\parumill\Downloads\schema\drmd-business-rules.sch'
out_dir = r'c:\Users\parumill\Downloads\schema\docs\schema_data'
out_file = os.path.join(out_dir, 'schema.json')

os.makedirs(out_dir, exist_ok=True)

schema = xmlschema.XMLSchema(xsd_path)

# Parse Schematron rules
sch_rules = []
ns = {'sch': 'http://purl.oclc.org/dsdl/schematron'}
try:
    sch_tree = ET.parse(sch_path)
    for assert_el in sch_tree.findall('.//sch:assert', ns):
        rule_id = assert_el.get('id', '')
        role = assert_el.get('role', 'warning')
        test = assert_el.get('test', '')
        text = " ".join(assert_el.itertext()).strip().replace('\n', ' ')
        # Clean up multiple spaces
        text = " ".join(text.split())
        sch_rules.append({
            'id': rule_id,
            'role': role,
            'test': test,
            'description': text
        })
except Exception as e:
    print(f"Error parsing Schematron: {e}")

def get_annotation(component):
    if hasattr(component, 'annotation') and component.annotation:
        docs = component.annotation.documentation
        if docs:
            return " ".join([d.text for d in docs if d.text]).replace('\n', ' ').strip()
    return ""

def get_short_name(name):
    if not name: return ""
    if '}' in name:
        return name.split('}')[-1]
    return name

def get_prefixed_name(name):
    if not name: return ""
    if '}' in name:
        uri, local = name.split('}', 1)
        uri = uri.strip('{')
        if 'www.w3.org' in uri: prefix = 'xs'
        elif 'dcc' in uri: prefix = 'dcc'
        elif 'si' in uri: prefix = 'si'
        elif 'drmd' in uri: prefix = 'drmd'
        else: prefix = 'ns'
        return f"{prefix}:{local}"
    return name

def build_dict(element, processed=None, current_path=""):
    if processed is None:
        processed = set()
        
    name = get_short_name(element.name)
    type_name = get_prefixed_name(element.type.name) if element.type and hasattr(element.type, 'name') else 'complexType'
    base_name = get_prefixed_name(element.type.base_type.name) if getattr(element.type, 'base_type', None) and getattr(element.type.base_type, 'name', None) else ""
    
    enums = getattr(element.type, 'enumeration', None)
    
    new_path = f"{current_path}/{name}" if current_path else name
    
    depth = current_path.count('/')
    if element in processed or depth > 8:
        return {"name": name, "type": type_name, "recursive": True}
        
    processed.add(element)
    
    min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1
    max_occurs = element.max_occurs if hasattr(element, 'max_occurs') else 1
    max_str = "*" if max_occurs is None or max_occurs > 100 else str(max_occurs)
    
    doc = get_annotation(element)
    if not doc and element.type:
        doc = get_annotation(element.type)
        
    # Find matching Schematron rules
    node_rules = []
    if name:
        for rule in sch_rules:
            # Simple heuristic: if the element name is in the test xpath
            if rule['test'] and name in rule['test']:
                # Make sure it's a whole word match or part of path
                if f"drmd:{name}" in rule['test'] or f"dcc:{name}" in rule['test']:
                    node_rules.append(rule)
                
    node = {
        "name": name,
        "type": type_name,
        "base": base_name,
        "enumerations": enums,
        "cardinality": f"[{min_occurs}..{max_str}]",
        "description": doc,
        "path": new_path,
        "attributes": [],
        "rules": node_rules,
        "children": []
    }
    
    if hasattr(element.type, 'attributes'):
        for attr_name, attr in element.type.attributes.items():
            if attr_name is None: continue
            attr_type = get_prefixed_name(attr.type.name) if attr.type and hasattr(attr.type, 'name') else 'simpleType'
            use_str = attr.use if hasattr(attr, 'use') else 'optional'
            attr_doc = get_annotation(attr)
            
            # Match rules for attributes
            attr_short = get_short_name(attr_name)
            attr_rules = [r for r in sch_rules if f"@{attr_short}" in r['test']]
            
            node["attributes"].append({
                "name": attr_short,
                "type": attr_type,
                "use": use_str,
                "description": attr_doc,
                "rules": attr_rules
            })
            
    if element.type and element.type.is_complex() and hasattr(element.type, 'content') and hasattr(element.type.content, 'iter_elements'):
        for child in element.type.content.iter_elements():
            node["children"].append(build_dict(child, processed.copy(), new_path))
            
    return node

root_element = schema.elements['digitalReferenceMaterialDocument']
tree_dict = build_dict(root_element)

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(tree_dict, f, indent=2)

print(f"JSON dumped successfully to {out_file}!")
