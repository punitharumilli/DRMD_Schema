# Implementation Checklists

This final chapter provides validation checklists for all stakeholders. Use these checklists to ensure that a DRMD instance is not only structurally valid (XSD) but also operationally ready for automated laboratory environments (passing all Schematron Profile business rules).

We have generated **Downloadable PDF Checklists** for your convenience. You can download and print these to track your implementation progress.

---

## 16.1 Reference Material Producer Checklist

Ensure every digital certificate you publish meets the exact technical and regulatory requirements.

[Download Producer PDF](assets/pdfs/producer_checklist.pdf){ .md-button .md-button--primary }

### A. Document Identity & Administration
- [ ] **Schema Versioning:** The root element contains the `schemaVersion` attribute.
- [ ] **Document Title:** `titleOfTheDocument` correctly distinguishes CRM vs PIS.
- [ ] **Unique Identifier:** A mandatory UUID is generated.
- [ ] **Document Identifiers:** At least one external identifier (DOI, Batch ID) is included.
- [ ] **Validity Period:** Exactly one method is chosen to define the certificate's lifespan.
- [ ] **Producer Contact:** Mandatory name, email/phone, and structured location are provided.
- [ ] **Responsible Persons:** A list is included with at least one `mainSigner`.

### B. Physical Material Definition
- [ ] **Material Identity:** Every material entry has a name and at least one canonical `materialIdentifier`.
- [ ] **Sample Constraints:** The mandatory `minimumSampleSize` is defined.
- [ ] **Classification:** The material is tied to a formal scheme using `reference` and `classID`.

### C. Technical Property Data
- [ ] **Certification Flag:** Every `materialProperties` explicitly declares `@isCertified`.
- [ ] **Property Identifiers:** Every quantity row includes a `propertyIdentifier`.
- [ ] **D-SI Unit Quality:** Unit strings use strict D-SI format (e.g., `\gram`).
- [ ] **Uncertainty Completeness:** Every certified value includes `valueExpandedMU` plus a coverage factor.
- [ ] **Traceability:** Traceability to SI is explicitly stated.

---

## 16.2 Software / LIMS Developer Checklist

Technical requirements for developers of Laboratory Information Management Systems (LIMS), ELNs, and data platforms.

[Download Software PDF](assets/pdfs/software_checklist.pdf){ .md-button .md-button--primary }

### A. Parser Configuration
- [ ] **Namespace Awareness:** The parser matches elements by URI + local name.
- [ ] **Prefix Independence:** Logic MUST NOT rely on document-provided prefixes.
- [ ] **XXE Protection:** External entity resolution MUST be disabled.

### B. Validation & Conformance Layers
- [ ] **Structural Check:** Perform XSD validation.
- [ ] **Profile Determination:** Automatically classify the document as Profile A, B, or C.
- [ ] **Business Rule Enforcement:** Verify Schematron requirements (mandatory narratives, finite numbers).
- [ ] **D-SI Unit Validation:** Implement regex checks for unit strings.

### C. Data Extraction
- [ ] **Unified Quantity Algorithm:** Implement extraction prioritizing `si:real`.
- [ ] **Multilingual Selection:** Implement the language fallback algorithm.
- [ ] **Numeric Precision:** Store values in high-precision types without rounding.

---

## 16.3 Instrument Vendor Checklist

For manufacturers of analytical instrumentation ingesting DRMD certificates for automated calibration.

[Download Instrument PDF](assets/pdfs/instrument_checklist.pdf){ .md-button .md-button--primary }

### A. Integration & Ingestion
- [ ] **Library Mapping:** Map material to internal libraries using stable identifiers.
- [ ] **Certified Value Prioritization:** Filter blocks by `@isCertified`.
- [ ] **Robust Analyte Mapping:** Map measured results using `propertyIdentifier` (CAS, element symbols).

### B. Workflow & Operational Safety
- [ ] **Sample Size Enforcement:** Display `minimumSampleSize` and trigger automated warnings.
- [ ] **Handling Alerts:** Display storage and handling instructions to operators.

### C. Trust Management
- [ ] **Integrity Policy:** Implement full cryptographic signature validation for Profile C.
- [ ] **Official Representation:** Provide users access to the embedded PDF.

---

## 16.4 Auditor Checklist

For accreditation bodies and quality managers evaluating whether a DRMD meets ISO 17034 requirements.

[Download Auditor PDF](assets/pdfs/auditor_checklist.pdf){ .md-button .md-button--primary }

### A. Governance & Accountability
- [ ] **Document Status:** `titleOfTheDocument` correctly distinguishes CRM vs PIS.
- [ ] **Responsible Persons:** `respPersons` list identifies who prepared, reviewed, and authorized.
- [ ] **Role Authorization:** Specific roles are assigned to satisfy governance.

### B. Traceability & Measurement Quality
- [ ] **Certified vs. Informative:** Certified values explicitly distinguished.
- [ ] **Metrological Traceability:** Narrative strictly confirms the unbroken chain to the SI.
