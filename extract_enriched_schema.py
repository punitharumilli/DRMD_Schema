import xmlschema
import xml.etree.ElementTree as ET
import json
import os
import re

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

# =============================================
# FALLBACK DESCRIPTIONS DICTIONARY
# For elements/attributes/types that have no
# xs:documentation in the XSD files
# =============================================
FALLBACK_DESCRIPTIONS = {
    # --- DCC elements without inline documentation ---
    'fileName': 'The original file name of the embedded binary data (e.g., "certificate_scan.pdf").',
    'mimeType': 'The MIME type identifying the format of the embedded file (e.g., "application/pdf", "image/png").',
    'dataBase64': 'The binary file content encoded as a Base64 string for XML-safe embedding.',
    'content': 'String element with an additional language attribute for multilingual text content.',
    'further': 'Additional rich content information for the location, such as building details or directions.',
    'latex': 'A LaTeX-formatted mathematical expression or formula string.',
    'label': 'A human-readable label string identifying the quantity or coordinate.',
    'dateTime': 'A date-time value in ISO 8601 format (e.g., "2024-06-15T10:30:00Z").',
    'positionCoordinates': 'Container for geographic or spatial position coordinates of a location.',
    'positionCoordinateSystem': 'Identifier of the coordinate reference system used (e.g., "WGS84", "EPSG:4326").',
    'positionCoordinate1': 'First position coordinate value (e.g., latitude or X-axis).',
    'positionCoordinate2': 'Second position coordinate value (e.g., longitude or Y-axis).',
    'positionCoordinate3': 'Third position coordinate value (e.g., altitude or Z-axis).',

    # --- DCC types used as element descriptions ---
    'file': 'Data block used for adding binary-encoded files (dcc:byteDataType).',
    'formula': 'Data block used for adding formula and equation content (dcc:formulaType).',
    'noQuantity': 'Container to combine text, formulas and files when no numeric quantity is needed (dcc:richContentType).',
    'charsXMLList': 'List of strings (xs:string) separated by blank spaces (dcc:charsXMLListType).',
    'description': 'A rich content description that may contain multilingual text, formulas, and embedded files.',
    'link': 'An optional persistent canonical landing-page URI or direct URL for origin lookup validation.',
    
    # --- SI Format elements ---
    'real': 'Metadata element definition for a real measurement quantity (si:realQuantityType).',
    'realListXMLList': 'Meta data element definition for a list of real measurement quantities based on the XML xsd:list type, separated by blank spaces.',
    'measurementUncertaintyUnivariate': 'Univariate measurement uncertainty container with standard, expanded, and coverage interval options.',
    'valueStandardMU': 'Scientific decimal value of the standard measurement uncertainty (must be >= 0). Based on xs:double.',
    'distribution': 'String providing the statistical distribution of measurement values (e.g., "normal", "rectangular").',
    'valueExpandedMU': 'Scientific decimal value of the expanded measurement uncertainty (must be >= 0). Based on xs:double.',
    'coverageFactor': 'Coverage factor (k-value) for expanded uncertainties (must be >= 1). Based on xs:double.',
    'coverageProbability': 'Coverage probability value within the interval [0,1]. Based on xs:double.',
    'intervalMin': 'Minimum boundary of the coverage interval. Scientific decimal format based on xs:double.',
    'intervalMax': 'Maximum boundary of the coverage interval. Scientific decimal format based on xs:double.',
    'quantityType': 'Definition of placeholder element for providing different quantity types.',

    # --- DCC common attributes ---
    '@id': 'A unique XML ID attribute for cross-referencing this element within the document.',
    '@refId': 'One or more IDREF values pointing to other elements in the document for cross-referencing.',
    '@refType': 'Specifies the type of cross-reference relationship (e.g., "hasPart", "isBasedOn").',
    '@lang': 'ISO 639-1 language code identifying the language of the text content (e.g., "en", "de").',
    '@Algorithm': 'URI identifying the algorithm used (e.g., canonicalization, signature, or digest algorithm).',
    '@URI': 'URI reference identifying the data object to be signed or retrieved.',
    '@Type': 'URI identifying the type of the referenced data object.',
    '@Id': 'A unique identifier for the XML Digital Signature element.',
    '@MimeType': 'MIME type of the Object element content.',
    '@Encoding': 'Encoding type of the Object element content (e.g., base64).',

    # --- XMLDSig elements (W3C XML Digital Signature) ---
    'Signature': 'The root XML Digital Signature element (W3C XMLDSig). Contains the digital signature over the document, including signed info, signature value, key info, and optional signed objects.',
    'SignedInfo': 'The signed information block containing the canonicalization method, signature algorithm, and references to the signed data. This element is itself signed to ensure integrity.',
    'CanonicalizationMethod': 'Specifies the canonicalization algorithm applied to the SignedInfo element before signing (e.g., Exclusive XML Canonicalization).',
    'SignatureMethod': 'Identifies the algorithm used for signature generation and validation (e.g., RSA-SHA256, ECDSA-SHA384).',
    'HMACOutputLength': 'Optional element specifying the truncation length of an HMAC signature output in bits.',
    'Reference': 'A reference to a specific data object to be signed, including optional transforms, the digest algorithm, and the computed digest value.',
    'Transforms': 'An ordered list of processing transforms applied to the referenced data object before digest computation.',
    'Transform': 'A single processing step applied to referenced data (e.g., enveloped-signature transform, XPath filtering, or canonicalization).',
    'XPath': 'An XPath expression used as a filter transform to select specific portions of the XML document for signing.',
    'DigestMethod': 'Identifies the digest (hash) algorithm applied to the referenced data object (e.g., SHA-256, SHA-384).',
    'DigestValue': 'The Base64-encoded digest (hash) value computed over the referenced and transformed data object.',
    'SignatureValue': 'The Base64-encoded cryptographic signature value computed over the canonicalized SignedInfo element.',
    'KeyInfo': 'Optional element providing information about the key used to validate the signature, such as key names, key values, X.509 certificates, or retrieval methods.',
    'KeyName': 'A human-readable string name identifying the signing key (e.g., "BAM-RM-Signing-Key-2024").',
    'KeyValue': 'Contains the actual public key value used for signature validation, either as DSA or RSA key parameters.',
    'DSAKeyValue': 'Contains the DSA public key parameters (P, Q, G, Y) and optional PGen counter values.',
    'P': 'DSA key parameter P: the prime modulus.',
    'Q': 'DSA key parameter Q: the sub-prime (order of the subgroup).',
    'G': 'DSA key parameter G: the generator of the subgroup.',
    'Y': 'DSA key parameter Y: the public key value (G^x mod P).',
    'J': 'DSA key parameter J: an optional cofactor value ((P-1)/Q).',
    'Seed': 'DSA domain parameter generation seed value.',
    'PgenCounter': 'DSA domain parameter generation counter value.',
    'RSAKeyValue': 'Contains the RSA public key parameters: Modulus and Exponent.',
    'Modulus': 'The RSA public key modulus value (Base64-encoded).',
    'Exponent': 'The RSA public key exponent value (Base64-encoded).',
    'RetrievalMethod': 'A URI-based mechanism for retrieving key information from an external source.',
    'X509Data': 'Contains X.509 certificate data for the signing key, including certificates, issuer/serial pairs, subject key identifiers, and CRLs.',
    'X509IssuerSerial': 'Pair of issuer distinguished name and serial number uniquely identifying an X.509 certificate.',
    'X509IssuerName': 'The distinguished name of the X.509 certificate issuer.',
    'X509SerialNumber': 'The serial number of the X.509 certificate.',
    'X509SKI': 'The Subject Key Identifier (SKI) extension value from the X.509 certificate.',
    'X509SubjectName': 'The subject distinguished name from the X.509 certificate.',
    'X509Certificate': 'The Base64-encoded DER representation of the X.509 certificate.',
    'X509CRL': 'The Base64-encoded Certificate Revocation List (CRL) for verifying certificate validity.',
    'PGPData': 'Contains PGP public key data for signature validation.',
    'PGPKeyID': 'The PGP key identifier.',
    'PGPKeyPacket': 'The PGP key packet data.',
    'SPKIData': 'Contains SPKI (Simple Public Key Infrastructure) key data.',
    'SPKISexp': 'An SPKI S-expression containing key information.',
    'MgmtData': 'In-band key distribution data (deprecated; not recommended for new implementations).',
    'Object': 'A container for arbitrary data objects that may be signed along with the document. Can hold manifests, signature properties, or application-specific data.',

    # --- DCC common elements without inline documentation ---
    'byteData': 'Data block used for adding binary-encoded files (dcc:byteDataType).',
    'certificate': 'An embedded digital certificate or certificate reference.',
    'city': 'The city or municipality portion of a postal address.',
    'classID': 'A classification identifier string referencing a specific class within a classification scheme.',
    'column': 'A single column of data in a structured list or matrix.',
    'columnXMLList': 'A column of data values provided as a space-separated XML list.',
    'complex': 'Metadata element definition for a complex measurement quantity with real and imaginary parts.',
    'complexList': 'A list of complex measurement quantities with Cartesian or polar representations.',
    'complexListXMLList': 'A list of complex measurement quantities as space-separated XML list values.',
    'conformity': 'A conformity assessment result (pass/fail/notApplicable) for a measured quantity.',
    'conformityXMLList': 'A space-separated list of conformity assessment results.',
    'constant': 'Definition of a real number representing a fundamental physical or mathematical constant.',
    'convention': 'The sign or measurement convention applied (e.g., phase convention for impedance).',
    'countryCode': 'An ISO 3166-1 alpha-2 country code (e.g., "DE", "US").',
    'covariance': 'A covariance value between two measurement quantities.',
    'covarianceMatrix': 'A matrix of covariance values for multivariate measurement uncertainty.',
    'covarianceMatrixXMLList': 'A covariance matrix provided as space-separated XML list values.',
    'covarianceXMLList': 'Covariance values provided as a space-separated XML list.',
    'coverageFactorXMLList': 'Coverage factor values provided as a space-separated XML list.',
    'coverageInterval': 'A coverage interval defined by minimum and maximum bounds with a coverage probability.',
    'coverageIntervalMU': 'Coverage interval measurement uncertainty data with min/max bounds and probability.',
    'coverageIntervalMUXMLList': 'Coverage interval uncertainty data as space-separated XML list values.',
    'coverageIntervalXMLList': 'Coverage interval values as a space-separated XML list.',
    'coverageProbabilityXMLList': 'Coverage probability values as a space-separated XML list.',
    'cryptElectronicSeal': 'Boolean flag indicating whether the producer supports electronic seals.',
    'cryptElectronicSignature': 'Boolean flag indicating whether the producer supports electronic signatures.',
    'cryptElectronicTimeStamp': 'Boolean flag indicating whether the producer supports electronic time stamps.',
    'data': 'Container for various data, e.g., text, formulas, and quantities.',
    'date': 'A calendar date value in ISO 8601 format (YYYY-MM-DD).',
    'dateTimeXMLList': 'Date-time values provided as a space-separated XML list.',
    'descriptionData': 'Optional rich content attachment providing supplementary descriptive information.',
    'distributionXMLList': 'Distribution identifiers as a space-separated XML list.',
    'eMail': 'An email address for electronic communication.',
    'ellipsoidalRegion': 'An ellipsoidal region for multivariate measurement uncertainty.',
    'ellipsoidalRegionMUXMLList': 'Ellipsoidal region uncertainty data as space-separated XML list values.',
    'ellipsoidalRegionXMLList': 'Ellipsoidal region values as a space-separated XML list.',
    'equipmentClass': 'Classification information for a piece of measuring equipment.',
    'expandedMU': 'Expanded measurement uncertainty data with coverage factor and probability.',
    'expandedMUXMLList': 'Expanded measurement uncertainty as space-separated XML list values.',
    'expandedUnc': 'Expanded uncertainty value for a measurement result.',
    'expandedUncXMLList': 'Expanded uncertainty values as a space-separated XML list.',
    'fax': 'A facsimile (fax) telephone number.',
    'identification': 'A single identifier entry for equipment or an organization.',
    'identifications': 'A collection of identification entries.',
    'inValidityRange': 'Boolean indicating whether the result is within the valid measurement range.',
    'influenceCondition': 'An environmental or operational influence condition affecting the measurement.',
    'installedSoftware': 'Software installed on or used by the measuring equipment.',
    'intervalMaxXMLList': 'Maximum interval boundary values as a space-separated XML list.',
    'intervalMinXMLList': 'Minimum interval boundary values as a space-separated XML list.',
    'issuer': 'The issuing authority or organization for a certificate or identifier.',
    'labelXMLList': 'Label strings provided as a space-separated XML list.',
    'linkedReport': 'A reference to an externally linked calibration or measurement report.',
    'list': 'A recursive list for structuring quantities and related data (lists, matrices, tensors).',
    'listBivariateUnc': 'A list of bivariate measurement uncertainty values.',
    'listMeasurementUncertaintyUnivariate': 'A list of univariate measurement uncertainty structures.',
    'listQuantityType': 'A list of quantity type definitions.',
    'listUnit': 'A list of unit strings (SI units).',
    'listUnitPhase': 'A list of unit phase strings for complex quantities.',
    'listUnivariateUnc': 'A list of univariate uncertainty structures.',
    'listsignificantDigit': 'A list of significant digit exponent values.',
    'location': 'A physical address or geographic location.',
    'mainSigner': 'Boolean flag indicating whether this responsible person is the main document signer.',
    'manufacturer': 'Information about the manufacturer of measuring equipment.',
    'mathml': 'A MathML-encoded mathematical expression or formula.',
    'measurementUncertaintyBivariateXMLList': 'Bivariate measurement uncertainty as space-separated XML list values.',
    'measurementUncertaintyMultivariateXMLList': 'Multivariate measurement uncertainty as space-separated XML list values.',
    'measurementUncertaintyUnivaraite': 'Univariate measurement uncertainty (alternate spelling variant).',
    'measurementUncertaintyUnivariateXMLList': 'Univariate measurement uncertainty as space-separated XML list values.',
    'measuringEquipment': 'Information about a piece of measuring equipment used in calibration.',
    'measuringEquipmentQuantities': 'Container for quantities associated with the measuring equipment.',
    'measuringEquipmentQuantity': 'A single quantity associated with the measuring equipment.',
    'metaData': 'Additional metadata associated with a measurement or calibration result.',
    'model': 'The model designation or name of equipment.',
    'name': 'The official multilingual name of an entity (producer, person, equipment, etc.).',
    'nonSIDefinition': 'Definition of a non-SI unit in human-readable text.',
    'nonSIUnit': 'A non-SI unit string (e.g., "ppm", "dB").',
    'norm': 'A normative reference or standard identifier (e.g., "ISO 17025").',
    'owner': 'Information about the owner of measuring equipment or calibration items.',
    'period': 'A time duration or period value (e.g., validity period in ISO 8601 duration format).',
    'phone': 'A telephone number for communication.',
    'postCode': 'The postal or ZIP code portion of an address.',
    'postOfficeBox': 'A post office box number.',
    'procedure': 'A procedure identifier or name describing the measurement or identification method.',
    'quantity': 'A single measurement quantity containing a name, description, D-SI value, and text.',
    'quantityTypeXMLList': 'Quantity type identifiers as a space-separated XML list.',
    'realList': 'A list of real measurement quantities for independent or multivariate vector quantities.',
    'rectangularRegion': 'A rectangular region for multivariate measurement uncertainty.',
    'rectangularRegionMUXMLList': 'Rectangular region uncertainty data as space-separated XML list values.',
    'rectangularRegionXMLList': 'Rectangular region values as a space-separated XML list.',
    'reference': 'A normative reference, standard, or URI identifying a classification scheme.',
    'referral': 'A referral entry linking to an external identification scheme or registry.',
    'referralID': 'The unique identifier within a referral or identification scheme.',
    'relativeUncertaintySingle': 'A single relative uncertainty value.',
    'relativeUncertaintyXmlList': 'Relative uncertainty values as a space-separated XML list.',
    'release': 'The release or version identifier of a schema, software, or standard.',
    'respAuthority': 'The responsible authority or regulatory body.',
    'role': 'The organizational role or function of a responsible person (e.g., "Laboratory Manager").',
    'scheme': 'The identifier scheme or namespace URI for a document identifier.',
    'significantDigit': 'Integer exponent of a power of 10 identifying the rounding range of the significant digit.',
    'significantDigitXMLList': 'Significant digit values as a space-separated XML list.',
    'software': 'Information about software used during measurement or calibration.',
    'standardMU': 'Standard measurement uncertainty data.',
    'standardMUXMLList': 'Standard measurement uncertainty as space-separated XML list values.',
    'standardUnc': 'Standard uncertainty value for a measurement result.',
    'standardUncXMLList': 'Standard uncertainty values as a space-separated XML list.',
    'state': 'The state, province, or region portion of a postal address.',
    'status': 'Current status information for an item or process.',
    'street': 'The street name portion of a postal address.',
    'streetNo': 'The street or building number portion of a postal address.',
    'text': 'Free-form multilingual text content.',
    'traceable': 'Boolean indicating whether a measurement is metrologically traceable to SI.',
    'type': 'A type classifier or category identifier.',
    'uncertainty': 'A general uncertainty value for a measurement.',
    'uncertaintyXMLList': 'Uncertainty values as a space-separated XML list.',
    'unit': 'A BIPM SI brochure unit string (e.g., "\\kelvin", "\\milli\\metre").',
    'unitPhase': 'A unit string for the phase component of a complex quantity.',
    'unitPhaseXMLList': 'Phase unit strings as a space-separated XML list.',
    'unitXMLList': 'Unit strings as a space-separated XML list.',
    'usedMethod': 'A measurement or calibration method used during the process.',
    'usedMethodQuantities': 'Container for quantities associated with a used method.',
    'usedMethodQuantity': 'A single quantity associated with a used method.',
    'valid': 'Boolean indicating whether a value is valid.',
    'validXMLList': 'Validity flags as a space-separated XML list.',
    'value': 'A string or numeric value element.',
    'valueExpandedMUXMLList': 'Expanded measurement uncertainty values as a space-separated XML list.',
    'valueImag': 'The imaginary part of a complex quantity value.',
    'valueImagXMLList': 'Imaginary part values as a space-separated XML list.',
    'valueMagnitude': 'The magnitude value of a complex quantity in polar form.',
    'valueMagnitudeXMLList': 'Magnitude values as a space-separated XML list.',
    'valuePhase': 'The phase angle value of a complex quantity in polar form.',
    'valuePhaseXMLList': 'Phase angle values as a space-separated XML list.',
    'valueReal': 'The real part of a complex quantity value.',
    'valueRealXMLList': 'Real part values as a space-separated XML list.',
    'valueStandardMUXMLList': 'Standard measurement uncertainty values as a space-separated XML list.',
    'valueXMLList': 'Measurement values as a space-separated XML list.',
    'xml': 'Container for embedding user- and application-specific XML content.',
    'declaration': 'A formal declaration or assertion within the document.',
    'influenceConditions': 'Container for environmental or operational influence conditions affecting the measurement.',
}

def get_annotation(component):
    docs = []
    
    # Try the component itself (element or attribute)
    if hasattr(component, 'annotation') and component.annotation:
        if component.annotation.documentation:
            docs.extend(component.annotation.documentation)
            
    # If it's an element reference, check the referred element
    if not docs and hasattr(component, 'ref') and component.ref:
        if hasattr(component.ref, 'annotation') and component.ref.annotation:
             if component.ref.annotation.documentation:
                 docs.extend(component.ref.annotation.documentation)

    # Try the type of the component
    if not docs and hasattr(component, 'type') and component.type:
        if hasattr(component.type, 'annotation') and component.type.annotation:
            if component.type.annotation.documentation:
                docs.extend(component.type.annotation.documentation)
                
        # Try base type
        if not docs and hasattr(component.type, 'base_type') and component.type.base_type:
            bt = component.type.base_type
            if hasattr(bt, 'annotation') and bt.annotation:
                if bt.annotation.documentation:
                    docs.extend(bt.annotation.documentation)
                    
    if docs:
        text = " ".join([d.text for d in docs if getattr(d, 'text', None)]).replace('\n', ' ').strip()
        return re.sub(r'\s+', ' ', text)
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
        if 'www.w3.org/2001/XMLSchema' in uri: prefix = 'xs'
        elif 'xmldsig' in uri or 'www.w3.org/2000/09' in uri: prefix = 'ds'
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
    if element in processed or depth > 12:
        fb_doc = FALLBACK_DESCRIPTIONS.get(name, "")
        return {"name": name, "type": type_name, "description": fb_doc, "recursive": True}
        
    processed.add(element)
    
    min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1
    max_occurs = element.max_occurs if hasattr(element, 'max_occurs') else 1
    max_str = "*" if max_occurs is None or max_occurs > 100 else str(max_occurs)
    
    doc = get_annotation(element)
    
    # Apply fallback if no description found
    if not doc and name in FALLBACK_DESCRIPTIONS:
        doc = FALLBACK_DESCRIPTIONS[name]
        
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
            
            # Apply fallback for attributes
            attr_short = get_short_name(attr_name)
            if not attr_doc and f'@{attr_short}' in FALLBACK_DESCRIPTIONS:
                attr_doc = FALLBACK_DESCRIPTIONS[f'@{attr_short}']
            
            # Match rules for attributes
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
            child_name = get_short_name(child.name)
            if not child_name:
                continue
                
            # Prune external schema bloat NOT indicated in DRMD:
            # 1. Under measurementMetaData or procedures or equipment: do not expand data/quantities tables
            if name in ('metaData', 'usedMethod', 'measuringEquipment', 'influenceCondition') and child_name in ('data', 'usedMethodQuantities', 'measuringEquipmentQuantities', 'influenceConditions'):
                continue
                
            # 2. In lists: prevent infinite recursion of list -> list / hybrid
            if name == 'list' and child_name in ('list', 'hybrid'):
                continue
                
            # 3. In quantity/itemQuantity: prevent recursive list/hybrid explosions from SI/DCC
            if name in ('quantity', 'itemQuantity', 'real', 'complex', 'constant') and child_name in ('hybrid', 'realListXMLList', 'complexListXMLList', 'realList', 'complexList', 'list', 'charsXMLList'):
                continue
                
            # 4. In Signature: exclude unused XMLDSig mechanisms (PGP, SPKI, MgmtData, DSAKeyValue, Object)
            if child_name in ('PGPData', 'SPKIData', 'MgmtData', 'DSAKeyValue', 'Object'):
                continue
                
            node["children"].append(build_dict(child, processed.copy(), new_path))
            
    return node

root_element = schema.elements['digitalReferenceMaterialDocument']
tree_dict = build_dict(root_element)

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(tree_dict, f, indent=2)

print(f"JSON dumped successfully to {out_file}!")

# Print stats
empty_el = []
filled_el = []
def count_stats(n):
    if n.get('description'):
        filled_el.append(n['name'])
    else:
        empty_el.append(n['name'])
    for c in n.get('children', []):
        count_stats(c)
count_stats(tree_dict)
print(f"Elements with descriptions: {len(filled_el)}")
print(f"Elements still missing descriptions: {len(empty_el)}")
if empty_el:
    unique_empty = sorted(set(empty_el))
    print(f"Unique empty element names ({len(unique_empty)}):")
    for e in unique_empty:
        print(f"  - {e}")
