import xmlschema
import json

xsd_path = r'c:\Users\parumill\Downloads\schema\drmd.xsd'
schema = xmlschema.XMLSchema(xsd_path)

def get_annotation(component):
    if hasattr(component, 'annotation') and component.annotation:
        docs = component.annotation.documentation
        if docs:
            return " ".join([d.text for d in docs if d.text]).replace('\n', ' ').strip()
    return ""

def get_short_name(name):
    if name and '}' in name:
        return name.split('}')[-1]
    return name

def build_dict(element, processed=None):
    if processed is None:
        processed = set()
        
    name = get_short_name(element.name)
    type_name = get_short_name(element.type.name) if element.type and hasattr(element.type, 'name') else 'complexType'
    
    if element in processed:
        return {"name": name, "type": type_name, "recursive": True}
        
    processed.add(element)
    
    min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1
    max_occurs = element.max_occurs if hasattr(element, 'max_occurs') else 1
    max_str = "*" if max_occurs is None or max_occurs > 100 else str(max_occurs)
    
    doc = get_annotation(element)
    if not doc and element.type:
        doc = get_annotation(element.type)
        
    node = {
        "name": name,
        "type": type_name,
        "cardinality": f"[{min_occurs}..{max_str}]",
        "description": doc,
        "attributes": [],
        "children": []
    }
    
    if hasattr(element.type, 'attributes'):
        for attr_name, attr in element.type.attributes.items():
            if attr_name is None: continue
            attr_type = get_short_name(attr.type.name) if attr.type and hasattr(attr.type, 'name') else 'simpleType'
            use_str = attr.use if hasattr(attr, 'use') else 'optional'
            attr_doc = get_annotation(attr)
            node["attributes"].append({
                "name": get_short_name(attr_name),
                "type": attr_type,
                "use": use_str,
                "description": attr_doc
            })
            
    if element.type and element.type.is_complex() and hasattr(element.type, 'content') and hasattr(element.type.content, 'iter_elements'):
        for child in element.type.content.iter_elements():
            node["children"].append(build_dict(child, processed.copy()))
            
    return node

root_element = schema.elements['digitalReferenceMaterialDocument']
tree_dict = build_dict(root_element)

with open(r'c:\Users\parumill\Downloads\schema\docs\schema.json', 'w', encoding='utf-8') as f:
    json.dump(tree_dict, f)

print("JSON dumped successfully!")
