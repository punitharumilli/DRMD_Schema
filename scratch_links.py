import os, glob, re

links = {}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\- ]', '', text)
    text = text.replace(' ', '-')
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

for f in glob.glob(r'c:\Users\parumill\Downloads\schema\docs\*.md'):
    basename = os.path.basename(f)
    if basename in ['schema_tree.md', 'index.md', 'checklists.md', 'architecture.md']:
        continue
    page = basename.replace('.md', '')
    with open(f, 'r', encoding='utf-8') as file:
        for line in file:
            m = re.match(r'^#+\s+(.*)$', line.strip())
            if m:
                header = m.group(1)
                slug = slugify(header)
                # Look for backticks containing element names
                el_match = re.search(r'`([^`]+)`', header)
                if el_match:
                    el_name = el_match.group(1)
                    if ':' in el_name:
                        el_name = el_name.split(':')[1]
                    if el_name not in links:
                        links[el_name] = page + '/#' + slug
                
                # Manual mappings for known ones that lack backticks
                lower_h = header.lower()
                if 'administrative data' in lower_h and 'administrativeData' not in links: links['administrativeData'] = page + '/#' + slug
                elif 'materials' in lower_h and 'materials' not in links: links['materials'] = page + '/#' + slug
                elif 'properties' in lower_h and 'propertiesList' not in links: links['propertiesList'] = page + '/#' + slug
                elif 'statements' in lower_h and 'statements' not in links: links['statements'] = page + '/#' + slug

# Add specific ones we know we missed
links['document'] = 'comments_documents/#61-document-attachment-document'
links['comment'] = 'comments_documents/#62-general-comment-comment'
links['Signature'] = 'signatures/#71-signature-element-signature'

print('const bestPracticeLinks = {')
for k, v in links.items():
    print('    \'' + k + '\': \'' + v + '\',')
print('};')
