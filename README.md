# DRMD Schema - README

## What is DRMD?

DRMD stands for **Digital Reference Material Document**. It is an XML format for describing reference materials used in laboratories. Think of it as a digital version of the paper certificates and information sheets that come with chemical or physical reference standards.

---

## Two Types of Documents

The DRMD schema supports **two types** of documents. The type is set by the `titleOfTheDocument` field:

| Document Type | XML Value | What It Represents |
|---|---|---|
| **Reference Material Certificate** | `referenceMaterialCertificate` | A Certified Reference Material (CRM) per ISO 33401:2024. Must contain at least one property value with associated measurement uncertainty and metrological traceability. Used for calibration. |
| **Product Information Sheet** | `productInformationSheet` | A Reference Material (RM) per ISO 33401:2024. Contains valid measurement values that do not require uncertainty or traceability. Used for quality control and informational purposes. |

**In simple words:**
- A **Certificate** says: *"This value is 0.045% ± 0.002%, traceable to SI units."* (At least one value must have uncertainty and traceability.)
- A **Product Information Sheet** says: *"This material has 0.045% of this element."* (The value is a valid measurement result, but uncertainty and traceability are not required.)

> **Key distinction (ISO 33401:2024):** The *only* structural difference between a certificate and a product information sheet is that a certificate must include at least one property value with an associated measurement uncertainty and a metrological traceability statement. Values on a product information sheet are still valid numbers - they are not approximate.

---

## How the Schema Works - The Big Picture

We use **two files working together** to validate DRMD documents:

```
┌──────────────────────────────────────────────────────┐
│                YOUR XML DOCUMENT                      │
│  (either a Certificate or Product Information Sheet)  │
└──────────────────────┬───────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   drmd.xsd          │  │  drmd-business-rules.sch │
│   (Base Schema)     │  │  (Schematron Rules)      │
│                     │  │                          │
│  Checks:            │  │  Checks:                 │
│  • Element names    │  │  • Is it a Certificate   │
│  • Data types       │  │    or Info Sheet?         │
│  • Basic structure  │  │  • Are the RIGHT fields  │
│                     │  │    filled in for THAT     │
│  Same rules for     │  │    type?                  │
│  BOTH document      │  │  • Are certified values   │
│  types              │  │    properly supported?    │
└─────────────────────┘  └─────────────────────────┘
           │                       │
           ▼                       ▼
    ┌──────────┐           ┌───────────┐
    │  PASS?   │           │  PASS?    │
    └────┬─────┘           └─────┬─────┘
         │                       │
         └───────────┬───────────┘
                     ▼
          ┌─────────────────────┐
          │  BOTH must pass     │
          │  for the document   │
          │  to be valid!       │
          └─────────────────────┘
```

**Why two files?**
- The **XSD** (XML Schema) can check structure (e.g., "is this element present?"), but it **cannot** say: *"If the document is a Certificate, THEN this element is required."*
- The **Schematron** file **can** make these "if/then" checks. It reads the `titleOfTheDocument` value and applies the correct rules for that document type.

---

## Document Structure Overview

Every DRMD document has this structure, whether it is a Certificate or a Product Information Sheet:

```
digitalReferenceMaterialDocument
│
├── administrativeData                    [Required for BOTH]
│   ├── coreData
│   │   ├── titleOfTheDocument            ← "referenceMaterialCertificate"
│   │   │                                    or "productInformationSheet"
│   │   ├── uniqueIdentifier              [Required for BOTH]
│   │   ├── documentVersion               [Required for BOTH]
│   │   ├── documentIdentifiers           [Optional]
│   │   └── validity                      [Required for BOTH]
│   │
│   ├── referenceMaterialProducer         [Required for BOTH]
│   │   ├── name
│   │   ├── contact
│   │   └── organizationIdentifiers      [Optional]
│   │
│   └── respPersons                       [Optional for PIS, Required for CRM]
│
├── materials                             [Required for BOTH]
│   └── material (can repeat)
│       ├── name                          [Required for BOTH]
│       ├── description                   [Recommended for PIS, Required for CRM]
│       ├── materialClass                 [Optional]
│       ├── minimumSampleSize             [Mandatory whenever applicable]
│       ├── itemQuantities                [Optional]
│       └── materialIdentifiers           [Optional, Recommended]
│
├── propertiesList                [Required for BOTH]
│   └── properties (can repeat)
│       ├── name                          [Required for BOTH]
│       ├── description                   [Optional]
│       ├── procedures                    [Mandatory whenever applicable]
│       ├── results                       [Required for BOTH]
│       │   └── result (can repeat)
│       │       ├── name
│       │       ├── data
│       │       │   ├── quantity (with si:real, si:hybrid, etc.)
│       │       │   └── list
│       │       │       └── quantity (repeats)
│       │       └── description           [Optional]
│       ├── measurementMetaData           [Optional]
│       └── @isCertified                  ← true ONLY for Certificates!
│
├── statements                            [Required for BOTH]
│   ├── intendedUse                       [Required for BOTH]
│   ├── commutability                     [Mandatory whenever applicable]
│   ├── storageInformation                [Required for BOTH]
│   ├── instructionsForHandlingAndUse     [Required for BOTH]
│   ├── metrologicalTraceability          [Required for CRM ONLY]  ← KEY DIFFERENCE
│   ├── healthAndSafetyInformation        [Recommended]
│   ├── subcontractors                    [Optional]
│   ├── legalNotice                       [Optional]
│   ├── referenceToCertificationReport    [Optional]
│   └── statement (generic, can repeat)   [Optional]
│
├── comment                               [Optional]
├── document (embedded PDF)               [Optional]
└── Signature (XMLDSig)                   [Optional]
```

---

## What is Different Between the Two Document Types?

Here is a comparison showing the key differences:

```
╔═══════════════════════════════════════════════════════════════════╗
║           PRODUCT INFORMATION SHEET (RM)                         ║
║                                                                   ║
║  ✅ intendedUse               → Required                         ║
║  ✅ storageInformation        → Required                         ║
║  ✅ instructionsForHandling   → Required                         ║
║  ✅ minimumSampleSize         → Mandatory whenever applicable    ║
║  ✅ property values           → Required (where values assigned) ║
║  ✅ material description      → Recommended                     ║
║  ❌ metrologicalTraceability  → NOT required                     ║
║  ❌ uncertainty on values     → NOT required                     ║
║  ❌ respPersons               → NOT required                     ║
║  ❌ @isCertified="true"       → FORBIDDEN                       ║
╚═══════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════╗
║           REFERENCE MATERIAL CERTIFICATE (CRM)                   ║
║                                                                   ║
║  ✅ intendedUse               → Required                         ║
║  ✅ storageInformation        → Required                         ║
║  ✅ instructionsForHandling   → Required                         ║
║  ✅ minimumSampleSize         → Mandatory whenever applicable    ║
║  ✅ property values           → Required                         ║
║  ✅ material description      → REQUIRED (must be present!)      ║
║  ✅ metrologicalTraceability  → REQUIRED (must be present!)      ║
║  ✅ uncertainty on values     → REQUIRED for certified values    ║
║  ✅ respPersons               → REQUIRED (approving officer)     ║
║  ✅ @isCertified="true"       → REQUIRED on at least one block   ║
╚═══════════════════════════════════════════════════════════════════╝
```

The elements marked differently between the two profiles are enforced by the **Schematron rules**, not the XSD.

---

## How the Validation Rules are Organized

The Schematron file has **4 groups of rules** (called "Patterns"):

```
┌────────────────────────────────────────────────────────────────┐
│                    SCHEMATRON RULE GROUPS                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PATTERN 1: Shared Rules (DRMD-001 to DRMD-015)          │  │
│  │  Apply to ALL documents - both Certificates & Info Sheets │  │
│  │                                                           │  │
│  │  Examples:                                                │  │
│  │  • Must have a titleOfTheDocument                         │  │
│  │  • Must have at least one material                        │  │
│  │  • Must have intendedUse, storageInformation              │  │
│  │  • Must have responsible persons                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PATTERN 2: Certificate-Only Rules (RMC-001 to RMC-011)  │  │
│  │  Apply ONLY when title = "referenceMaterialCertificate"   │  │
│  │                                                           │  │
│  │  Examples:                                                │  │
│  │  • MUST have metrologicalTraceability statement           │  │
│  │  • MUST have at least one isCertified="true" block        │  │
│  │  • MUST have respPersons (approving officer)              │  │
│  │  • MUST have material description                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PATTERN 3: Uncertainty Rules (RMC-006 to RMC-009)       │  │
│  │  Apply ONLY to certified property values in Certificates  │  │
│  │                                                           │  │
│  │  Every certified measurement value MUST include:          │  │
│  │  • Expanded uncertainty (si:expandedMU)                   │  │
│  │  • OR Standard uncertainty (si:standardMU)                │  │
│  │  • OR Coverage interval (si:coverageIntervalMU)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  PATTERN 4: Info Sheet Rules (PIS-001 to PIS-005)         │  │
│  │  Apply ONLY when title = "productInformationSheet"        │  │
│  │                                                           │  │
│  │  Examples:                                                │  │
│  │  • MUST NOT use isCertified="true" (FORBIDDEN)            │  │
│  │  • Must have results where values are assigned            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Severity Levels - The 3-Tier Model

The Schematron rules use a **3-tier severity model** that maps directly to ISO 33401:2024's requirement categories:

| Tier | Schematron `role` | ISO Requirement Level | What It Means |
|---|---|---|---|
| 🔴 **Hard Error** | `error` | Mandatory | Document is **non-compliant**. The element is unconditionally required. Validation fails. |
| 🟠 **Conditional Error** | `conditional-error` | Mandatory whenever applicable | Element is **required if applicable** to this specific material. If the element genuinely does not apply (e.g., minimum sample size for a gas), the absence is acceptable. The producer must make this determination. |
| 🟡 **Warning** | `warning` | Recommended | Document is **compliant**, but the element is recommended for best practice. Producers are encouraged to include it. |
| *(no rule)* | - | Optional | No validation. The element is accepted if present but never flagged if absent. |

> **Note on `conditional-error`:** This is a custom Schematron role (the spec allows any string). Standard tools will report it as a "failed assertion" in the SVRL output. Your validation pipeline should parse the `role` attribute from the SVRL to correctly classify it. See the [Python](#validate-with-python) and [Java](#validate-with-java) examples below.

---

## Safety - How We Prevent Misuse

A key concern: *"If we relax the rules for Product Information Sheets, can someone cheat and submit an incomplete Certificate?"*

**Answer: No. Here is how the safety works:**

```
SCENARIO 1: Someone submits a Certificate without traceability
┌──────────────────────────────────────────────────┐
│  titleOfTheDocument = "referenceMaterialCertificate" │
│  metrologicalTraceability = (missing)             │
└──────────────────────┬───────────────────────────┘
                       ▼
              Rule RMC-001 fires!
              ❌ VALIDATION FAILS
              "Certificates MUST include metrological traceability"


SCENARIO 2: Someone marks a Product Info Sheet as certified
┌──────────────────────────────────────────────────┐
│  titleOfTheDocument = "productInformationSheet"  │
│  properties @isCertified = "true"        │
└──────────────────────┬───────────────────────────┘
                       ▼
              Rule PIS-001 fires!
              ❌ VALIDATION FAILS
              "Product Information Sheets MUST NOT use isCertified=true"


SCENARIO 3: Certificate has certified values but no uncertainty
┌──────────────────────────────────────────────────┐
│  titleOfTheDocument = "referenceMaterialCertificate" │
│  properties @isCertified = "true"        │
│  si:real → value = 0.045, unit = \percent        │
│  si:measurementUncertaintyUnivariate = (missing) │
└──────────────────────┬───────────────────────────┘
                       ▼
              Rule RMC-006 fires!
              ❌ VALIDATION FAILS
              "Certified values MUST include measurement uncertainty"


SCENARIO 4: Valid Product Information Sheet (simple, no traceability needed)
┌──────────────────────────────────────────────────┐
│  titleOfTheDocument = "productInformationSheet"  │
│  properties (no @isCertified)            │
│  intendedUse ✓  storageInfo ✓  handling ✓        │
│  metrologicalTraceability = (not provided)       │
└──────────────────────┬───────────────────────────┘
                       ▼
              All rules pass!
              ✅ VALID DOCUMENT
```

---

## How the Schema Maps to ISO 33401:2024

The rules are based on **ISO 33401:2024, Table 1** (Contents of the product information sheet or the RM certificate). Here is how each requirement is handled:

| ISO 33401:2024 Requirement | Subclause | PIS (Info Sheet) | RMC (Certificate) | How It Is Enforced |
|---|---|---|---|---|
| Title of the document | 5.2.2 | Mandatory | Mandatory | XSD: `titleOfTheDocument` enum. Schematron: DRMD-001 |
| Unique identifier of the RM | 5.2.3 | Mandatory | Mandatory | XSD: `uniqueIdentifier` is mandatory |
| Name of the RM | 5.2.4 | Mandatory | Mandatory | XSD: `material/name` is mandatory. Schematron: DRMD-007 |
| Name and contact details of the RM producer | 5.2.5 | Mandatory | Mandatory | XSD + Schematron: DRMD-010 |
| Intended use | 5.2.6 | Mandatory | Mandatory | XSD: `intendedUse` is mandatory. Schematron: DRMD-004 |
| Minimum sample size | 5.2.7 | Mandatory whenever applicable | Mandatory whenever applicable | Schematron: DRMD-008 (conditional-error) |
| Period of validity | 5.2.8 | Mandatory | Mandatory | XSD: `validity` is mandatory. Schematron: DRMD-012 |
| Commutability | 5.2.9 | Mandatory whenever applicable | Mandatory whenever applicable | Schematron: DRMD-013 (conditional-error) |
| Storage information | 5.2.10 | Mandatory | Mandatory | XSD: `storageInformation` is mandatory. Schematron: DRMD-005 |
| Instructions for handling and use | 5.2.11 | Mandatory | Mandatory | XSD: `instructionsForHandlingAndUse` is mandatory. Schematron: DRMD-006 |
| Document components | 5.2.12 | Mandatory | Mandatory | Implicit in schema structure |
| Document version | 5.2.13 | Mandatory | Mandatory | XSD: `documentVersion` is mandatory |
| Measurement procedures (operationally defined) | 5.2.14 | Mandatory whenever applicable | Mandatory whenever applicable | Schematron: DRMD-014 (conditional-error) |
| Property of interest | 5.2.15 | Mandatory | Mandatory | Schematron: DRMD-003, DRMD-009 |
| **Description of the material** | **5.3.2** | **Recommended** | **Mandatory** | **Schematron: PIS-005 (warning for PIS), RMC-011 (error for CRM)** |
| **Property value and associated uncertainty** | **5.3.3** | **Optional** | **Mandatory** | **Schematron: RMC-002, RMC-006 to RMC-009** |
| **Metrological traceability** | **5.3.4** | **Optional** | **Mandatory** | **Schematron: RMC-001 (error for CRM)** |
| **Approving officer** | **5.3.5** | **Optional** | **Mandatory** | **Schematron: RMC-010 (error for CRM)** |
| Measurement procedures (non-operationally defined) | 5.4.2 | Recommended | Recommended | Schematron: RMC-005 (warning for CRM). Also covered by DRMD-014 |
| Health and safety information | 5.4.3 | Recommended | Recommended | Schematron: DRMD-015 (warning) |
| Subcontractors | 5.4.4 | Optional | Optional | XSD: `subcontractors` optional |
| Indicative values | 5.4.5 | Optional | Optional | Supported via non-certified properties blocks |
| Legal notice | 5.4.6 | Optional | Optional | XSD: `legalNotice` optional |
| Reference to a certification report | 5.4.7 | Optional | Optional | XSD: `referenceToCertificationReport` optional |

> **Note:** Some organizational process requirements (Production planning, Production control, Distribution service, Management of non-conforming work, Handling of complaints) are operational processes of the producer. They are not data fields in the document, so they do not appear in the schema.

---

## Complete List of Validation Rules

### Shared Rules (apply to ALL documents)

| Rule ID | Severity | What It Checks |
|---|---|---|
| DRMD-001 | 🔴 Error | Document must declare `titleOfTheDocument` |
| DRMD-002 | 🔴 Error | At least one `material` entry must exist |
| DRMD-003 | 🔴 Error | At least one `properties` block must exist |
| DRMD-004 | 🔴 Error | `intendedUse` statement must be present |
| DRMD-005 | 🔴 Error | `storageInformation` must be present |
| DRMD-006 | 🔴 Error | `instructionsForHandlingAndUse` must be present |
| DRMD-007 | 🔴 Error | Every material must have a `name` |
| DRMD-008 | 🟠 Conditional Error | `minimumSampleSize` MUST be present whenever applicable |
| DRMD-009 | 🔴 Error | Every `properties` block must have at least one `result` |
| DRMD-010 | 🔴 Error | `referenceMaterialProducer` must be identified |
| DRMD-012 | 🔴 Error | `validity` period must be specified |
| DRMD-013 | 🟠 Conditional Error | `commutability` statement MUST be present whenever applicable |
| DRMD-014 | 🟠 Conditional Error | `procedures` MUST be present whenever applicable |
| DRMD-015 | 🟡 Warning | `healthAndSafetyInformation` SHOULD be included |

### Certificate-Only Rules

| Rule ID | Severity | What It Checks |
|---|---|---|
| RMC-001 | 🔴 Error | `metrologicalTraceability` statement MUST be present |
| RMC-002 | 🔴 Error | At least one `properties` block MUST have `@isCertified="true"` |
| RMC-003 | 🔴 Error | Property values MUST exist |
| RMC-005 | 🟡 Warning | `procedures` SHOULD be documented for certified property blocks |
| RMC-006 | 🔴 Error | Certified `si:real` quantities MUST have uncertainty |
| RMC-007 | 🔴 Error | Certified `si:real` in lists MUST have uncertainty |
| RMC-008 | 🔴 Error | Certified `si:realListXMLList` MUST have uncertainty |
| RMC-009 | 🔴 Error | Certified `si:hybrid` containing `si:real` MUST have uncertainty |
| RMC-010 | 🔴 Error | `respPersons` (approving officer) MUST be present |
| RMC-011 | 🔴 Error | `material/description` MUST be present |

### Product Information Sheet Rules

| Rule ID | Severity | What It Checks |
|---|---|---|
| PIS-001 | 🔴 Error | `@isCertified="true"` is FORBIDDEN on any `properties` block |
| PIS-002 | 🔴 Error | Characterization results must exist where values are assigned |
| PIS-003 | 🔴 Error | Individual property blocks MUST NOT claim certification |
| PIS-005 | 🟡 Warning | `material/description` SHOULD be included (recommended) |

---

## File Inventory

| File | Purpose | Format |
|---|---|---|
| `drmd.xsd` | **Base schema** - defines the XML structure for both document types | XSD 1.0 |
| `drmd-business-rules.sch` | **Validation rules** - enforces profile-specific requirements | ISO Schematron |
| `dcc.xsd` | DCC (Digital Calibration Certificate) base types - imported dependency | XSD 1.0 |
| `SI_Format.xsd` | D-SI (Digital System of Units) - measurement values and uncertainty types | XSD 1.0 |
| `xmldsig-core-schema.xsd` | XML Digital Signature - optional document signing | XSD 1.0 |

---

## How to Validate a Document

### Step 1: Validate against the XSD (structure check)

Use any XML validation tool. Example with `xmllint`:

```bash
xmllint --schema drmd.xsd your-document.xml --noout
```

This checks:
- Are all element names correct?
- Are data types correct (dates, numbers, strings)?
- Are required elements present?

### Step 2: Validate against Schematron (business rule check)

Use a Schematron processor (e.g., Saxon, SchXSLT). Example:

```bash
# First, compile Schematron to XSLT
java -jar saxon.jar -s:drmd-business-rules.sch -xsl:iso_schematron_skeleton_for_xslt2.xsl -o:drmd-rules.xsl

# Then, validate your document
java -jar saxon.jar -s:your-document.xml -xsl:drmd-rules.xsl
```

This checks:
- Is the document type correctly identified?
- Are the right fields filled in for that document type?
- Do certified values have uncertainty?

### Both steps must PASS for the document to be valid.

---

## Validate with Python

Using `lxml` for both XSD and Schematron validation:

```python
from lxml import etree
from lxml.isoschematron import Schematron
from collections import defaultdict

def validate_drmd(xml_path, xsd_path='drmd.xsd', sch_path='drmd-business-rules.sch'):
    """
    Validate a DRMD XML document against both the XSD schema and Schematron business rules.
    Returns a dict with categorized results using the 3-tier severity model.
    """
    results = {
        'xsd_valid': False,
        'errors': [],             # role="error"             - Mandatory (hard failure)
        'conditional_errors': [], # role="conditional-error"  - Mandatory whenever applicable
        'warnings': [],           # role="warning"            - Recommended
    }

    # --- Step 1: XSD Validation ---
    xml_doc = etree.parse(xml_path)
    xsd_doc = etree.parse(xsd_path)
    xsd_schema = etree.XMLSchema(xsd_doc)

    results['xsd_valid'] = xsd_schema.validate(xml_doc)
    if not results['xsd_valid']:
        for error in xsd_schema.error_log:
            results['errors'].append(f"[XSD] Line {error.line}: {error.message}")
        return results  # Stop early - XSD must pass before Schematron

    # --- Step 2: Schematron Validation ---
    sch_doc = etree.parse(sch_path)
    schematron = Schematron(sch_doc, store_report=True)
    is_valid = schematron.validate(xml_doc)

    # --- Step 3: Parse SVRL output for 3-tier severity ---
    svrl = schematron.validation_report
    ns = {'svrl': 'http://purl.oclc.org/dml/svrl'}

    for failed in svrl.xpath('//svrl:failed-assert', namespaces=ns):
        role = failed.get('role', 'error')
        rule_id = failed.get('id', 'unknown')
        text = failed.find('svrl:text', namespaces=ns).text.strip()

        if role == 'error':
            results['errors'].append(f"[{rule_id}] {text}")
        elif role == 'conditional-error':
            results['conditional_errors'].append(f"[{rule_id}] {text}")
        elif role == 'warning':
            results['warnings'].append(f"[{rule_id}] {text}")

    return results


# --- Usage ---
results = validate_drmd('my-document.xml')

print("=== XSD Validation ===")
print("PASSED" if results['xsd_valid'] else "FAILED")

print(f"\n=== Hard Errors ({len(results['errors'])}) ===")
for msg in results['errors']:
    print(f"  🔴 {msg}")

print(f"\n=== Conditional Errors ({len(results['conditional_errors'])}) ===")
for msg in results['conditional_errors']:
    print(f"  🟠 {msg}")

print(f"\n=== Warnings ({len(results['warnings'])}) ===")
for msg in results['warnings']:
    print(f"  🟡 {msg}")

# --- Compliance decision ---
is_compliant = len(results['errors']) == 0
has_conditions = len(results['conditional_errors']) > 0

if not is_compliant:
    print("\n❌ DOCUMENT IS NON-COMPLIANT (hard errors found)")
elif has_conditions:
    print("\n⚠️  DOCUMENT HAS CONDITIONAL ERRORS - review if elements are applicable")
else:
    print("\n✅ DOCUMENT IS FULLY COMPLIANT")
```

> **Install dependency:** `pip install lxml`

---

## Validate with Java

Using `javax.xml.validation` for XSD and Saxon for Schematron:

```java
import net.sf.saxon.s9api.*;
import org.w3c.dom.*;
import javax.xml.transform.*;
import javax.xml.transform.stream.*;
import javax.xml.validation.*;
import java.io.*;
import java.util.*;

public class DrmdValidator {

    /**
     * Step 1: Validate against the XSD schema.
     */
    public static List<String> validateXsd(String xmlPath, String xsdPath) throws Exception {
        List<String> errors = new ArrayList<>();
        SchemaFactory factory = SchemaFactory.newInstance("http://www.w3.org/2001/XMLSchema");
        Schema schema = factory.newSchema(new File(xsdPath));
        Validator validator = schema.newValidator();

        try {
            validator.validate(new StreamSource(new File(xmlPath)));
        } catch (org.xml.sax.SAXException e) {
            errors.add("[XSD] " + e.getMessage());
        }
        return errors;
    }

    /**
     * Step 2: Validate against Schematron rules using Saxon.
     * Compiles the Schematron to XSLT, then runs it against the XML document.
     * Parses the SVRL output to categorize results by the 3-tier severity model.
     */
    public static Map<String, List<String>> validateSchematron(
            String xmlPath, String schPath) throws Exception {

        Map<String, List<String>> results = new LinkedHashMap<>();
        results.put("errors", new ArrayList<>());             // role="error"
        results.put("conditionalErrors", new ArrayList<>());  // role="conditional-error"
        results.put("warnings", new ArrayList<>());           // role="warning"

        Processor processor = new Processor(false);
        XsltCompiler compiler = processor.newXsltCompiler();

        // Step 2a: Compile Schematron → XSLT using the ISO skeleton
        XsltExecutable step1 = compiler.compile(
            new StreamSource(new File("iso_schematron_skeleton_for_xslt2.xsl")));
        XsltTransformer transformer1 = step1.load();
        transformer1.setSource(new StreamSource(new File(schPath)));
        XdmDestination xsltOutput = new XdmDestination();
        transformer1.setDestination(xsltOutput);
        transformer1.transform();

        // Step 2b: Run the compiled XSLT against the XML document
        XsltExecutable step2 = compiler.compile(xsltOutput.getXdmNode().asSource());
        XsltTransformer transformer2 = step2.load();
        transformer2.setSource(new StreamSource(new File(xmlPath)));
        XdmDestination svrlOutput = new XdmDestination();
        transformer2.setDestination(svrlOutput);
        transformer2.transform();

        // Step 2c: Parse SVRL output for the 3 severity tiers
        XdmNode svrl = svrlOutput.getXdmNode();
        XPathCompiler xpath = processor.newXPathCompiler();
        xpath.declareNamespace("svrl", "http://purl.oclc.org/dml/svrl");

        // Parse failed-assert elements
        for (XdmItem item : xpath.evaluate("//svrl:failed-assert", svrl)) {
            XdmNode node = (XdmNode) item;
            String role = node.getAttributeValue(new QName("role"));
            String id = node.getAttributeValue(new QName("id"));
            String text = xpath.evaluateSingle("svrl:text", node).getStringValue().trim();

            String message = "[" + id + "] " + text;
            if (role == null) role = "error";

            switch (role) {
                case "error":             results.get("errors").add(message); break;
                case "conditional-error": results.get("conditionalErrors").add(message); break;
                case "warning":           results.get("warnings").add(message); break;
                default:                  results.get("errors").add(message); break;
            }
        }

        return results;
    }

    public static void main(String[] args) throws Exception {
        String xmlPath = "my-document.xml";
        String xsdPath = "drmd.xsd";
        String schPath = "drmd-business-rules.sch";

        // Step 1: XSD validation
        List<String> xsdErrors = validateXsd(xmlPath, xsdPath);
        if (!xsdErrors.isEmpty()) {
            System.out.println("❌ XSD VALIDATION FAILED:");
            xsdErrors.forEach(e -> System.out.println("  🔴 " + e));
            return;
        }
        System.out.println("✅ XSD validation passed");

        // Step 2: Schematron validation
        Map<String, List<String>> results = validateSchematron(xmlPath, schPath);

        System.out.println("\n=== Hard Errors ===");
        results.get("errors").forEach(e -> System.out.println("  🔴 " + e));

        System.out.println("\n=== Conditional Errors ===");
        results.get("conditionalErrors").forEach(e -> System.out.println("  🟠 " + e));

        System.out.println("\n=== Warnings ===");
        results.get("warnings").forEach(e -> System.out.println("  🟡 " + e));

        // Compliance decision
        boolean isCompliant = results.get("errors").isEmpty();
        boolean hasConditions = !results.get("conditionalErrors").isEmpty();

        if (!isCompliant) {
            System.out.println("\n❌ DOCUMENT IS NON-COMPLIANT");
        } else if (hasConditions) {
            System.out.println("\n⚠️  CONDITIONAL ERRORS - review if elements are applicable");
        } else {
            System.out.println("\n✅ DOCUMENT IS FULLY COMPLIANT");
        }
    }
}
```

> **Dependencies:** [Saxon-HE](https://www.saxonica.com/download/java.xml) (for XSLT2/Schematron) + the [ISO Schematron skeleton XSLT](https://github.com/Schematron/schematron).

---

## Frequently Asked Questions

**Q: Can a Product Information Sheet include uncertainty values?**
A: Yes! Uncertainty is allowed but not required. Producers may voluntarily include uncertainty data on a Product Information Sheet. The Schematron only REQUIRES uncertainty for certified values in Certificates.

**Q: What happens if someone sets `titleOfTheDocument` to "referenceMaterialCertificate" but leaves out traceability?**
A: The Schematron rule RMC-001 will produce a validation ERROR. The document will be rejected as non-compliant.

**Q: What happens if someone sets `titleOfTheDocument` to "productInformationSheet" but marks properties as `isCertified="true"`?**
A: The Schematron rules PIS-001 and PIS-003 will produce validation ERRORS. The document will be rejected. This prevents misrepresentation.

**Q: What is the actual difference between a Certificate and a Product Information Sheet?**
A: The *only* structural difference is that a Certificate must include at least one property value with an associated measurement uncertainty and a metrological traceability statement. Values on a Product Information Sheet are still valid measurement results - they are not approximate or estimated. They simply do not carry the formal certification (uncertainty + traceability) that a certificate requires.

**Q: Are values on a Product Information Sheet approximate?**
A: No. Values on a Product Information Sheet are valid measurement numbers. The difference is not about accuracy - it is about whether the value carries a formal uncertainty statement and traceability chain. A PIS value of 0.045% is a real measured value, not an approximation.

**Q: Why not use two separate schemas instead of one?**
A: A single base schema avoids code duplication. Both document types share 95% of the same structure. Maintaining two separate schemas would mean fixing bugs and adding features in two places. The Schematron approach keeps everything in sync.

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 0.3.0 | - | Original schema (focused on Reference Material Certificates) |
| 0.4.0 | 2025 | Added dual-profile support (Certificate + Product Information Sheet). Created companion Schematron validation file. Updated annotations with ISO 17034 profile notes. |
| 1.0.0 | 2026 | **ISO 33401:2024 alignment.** Updated all references from ISO 17034 Table A.1 to ISO 33401:2024 Table 1. |
| 1.1.0 | 2026 | **3-Tier severity model & public release cleanup.** Introduced conditional-error role. Added DRMD-013 (commutability), DRMD-014 (procedures), DRMD-015 (health and safety), PIS-005 (material description). Renamed materialProperties/materialPropertiesList to properties/propertiesList. Removed PIS-004 info rule. Added Python and Java validation examples. |
