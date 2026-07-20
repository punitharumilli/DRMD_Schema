import xmlschema
import os

xsd_path = r'c:\Users\parumill\Downloads\schema\drmd.xsd'
schema = xmlschema.XMLSchema(xsd_path)

out_file = r'c:\Users\parumill\Downloads\schema\docs\schema_tree.md'

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

def generate_markdown(element, depth=0, processed=None):
    if processed is None:
        processed = set()
        
    indent = "    " * depth
    prefix = "???+ " if depth == 0 else "??? "
    
    # Avoid infinite recursion (e.g. recursive schemas)
    if element in processed:
        return f"{indent}- **(Recursive)** `{get_short_name(element.name)}`\n"
    
    processed.add(element)
    
    # Get basic info
    name = get_short_name(element.name)
    type_name = get_short_name(element.type.name) if element.type and hasattr(element.type, 'name') else 'complexType'
    
    # Cardinality
    min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1
    max_occurs = element.max_occurs if hasattr(element, 'max_occurs') else 1
    max_str = "*" if max_occurs is None or max_occurs > 100 else str(max_occurs)
    cardinality = f"[{min_occurs}..{max_str}]"
    
    doc = get_annotation(element)
    if not doc and element.type:
        doc = get_annotation(element.type)
        
    md = f"{indent}{prefix}note \"**E** `{name}`\"\n"
    indent_inner = indent + "    "
    
    if type_name:
        md += f"{indent_inner}- **Type**: `{type_name}`\n"
    md += f"{indent_inner}- **Cardinality**: `{cardinality}`\n"
    
    if doc:
        md += f"\n{indent_inner}*{doc}*\n\n"
    
    # Handle attributes
    if hasattr(element.type, 'attributes'):
        for attr_name, attr in element.type.attributes.items():
            if attr_name is None: continue
            attr_type = get_short_name(attr.type.name) if attr.type and hasattr(attr.type, 'name') else 'simpleType'
            use_str = attr.use if hasattr(attr, 'use') else 'optional'
            attr_doc = get_annotation(attr)
            doc_str = f" - *{attr_doc}*" if attr_doc else ""
            md += f"{indent_inner}- 🟡 `@` `{get_short_name(attr_name)}` : `{attr_type}` ({use_str}){doc_str}\n"

    md += "\n"

    # Handle children
    if element.type and element.type.is_complex() and hasattr(element.type, 'content'):
        if hasattr(element.type.content, 'iter_elements'):
            for child in element.type.content.iter_elements():
                md += generate_markdown(child, depth + 1, processed.copy())
            
    return md

root_element = schema.elements['digitalReferenceMaterialDocument']
tree_md = generate_markdown(root_element)

with open(out_file, 'w', encoding='utf-8') as f:
    f.write("# 🌳 Schema Interactive Tree\n\n")
    f.write("Click on any element block to expand and explore its child elements, attributes, and types. This interactive tree covers the complete DRMD schema and its imported namespaces.\n\n")
    f.write(tree_md)

print("Schema tree generated successfully!")
