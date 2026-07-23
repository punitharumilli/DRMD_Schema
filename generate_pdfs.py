import os
from fpdf import FPDF

class ChecklistPDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "DRMD Best Practice (v1.0)", border=False, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(232, 234, 246) # Indigo lighter
        self.cell(0, 10, title, border=True, align="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(40, 53, 147) # Indigo
        self.cell(0, 8, title, border=False, align="L", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def checklist_item(self, text):
        self.set_font("helvetica", "", 10)
        # Draw a checkbox
        self.set_line_width(0.3)
        self.rect(self.get_x() + 2, self.get_y() + 1, 4, 4)
        # Write text next to it
        self.set_xy(self.get_x() + 8, self.get_y())
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

def generate_pdf(filename, title, data):
    pdf = ChecklistPDF()
    pdf.add_page()
    pdf.chapter_title(title)
    
    for section_title, items in data.items():
        pdf.section_title(section_title)
        for item in items:
            pdf.checklist_item(item)
        pdf.ln(5)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf.output(filename)

producer_data = {
    "A. Document Identity & Administration": [
        "Schema Versioning: The root element contains the schemaVersion attribute.",
        "Document Title: titleOfTheDocument is set correctly (e.g. referenceMaterialCertificate).",
        "Unique Identifier: A mandatory UUID is generated for the document.",
        "Document Identifiers: At least one external identifier (DOI, Batch ID) is included.",
        "Validity Period: Exactly one method is chosen to define the certificate's lifespan.",
        "Producer Contact: Mandatory name, email/phone, and structured location are provided.",
        "Responsible Persons: A list is included with at least one person flagged as mainSigner."
    ],
    "B. Physical Material Definition": [
        "Material Identity: Every material entry has a human-readable name and at least one canonical materialIdentifier.",
        "Sample Constraints: The mandatory minimumSampleSize is defined with a numeric value and D-SI unit.",
        "Classification: The material is tied to a formal scheme using reference and classID.",
        "Multi-Material Integrity: If multiple materials exist, each is assigned a unique @id."
    ],
    "C. Technical Property Data (The Certified Value Core)": [
        "Certification Flag: Every materialProperties block explicitly declares @isCertified.",
        "Certified Presence: At least one block has @isCertified='true' (for Profiles B/C).",
        "Property Identifiers: Every quantity row includes a propertyIdentifier (e.g., CAS #).",
        "D-SI Unit Quality: Unit strings use backslash identifiers (e.g., \gram) and meet Gold/Platinum class.",
        "Unit Prefix Policy: For certified values, prefixes are avoided where feasible.",
        "Uncertainty Completeness: Every certified value includes valueExpandedMU plus coverageFactor/Probability.",
        "Numeric Validation: valueExpandedMU >= 0, coverageFactor > 0, coverageProbability in (0, 1].",
        "Consistency: A single result table does not mix list-encoded and row-encoded quantities.",
        "Traceability: A structured measurementMetaData block or narrative statement confirms traceability to SI."
    ],
    "D. Statements & Archival": [
        "Mandatory Narrative: intendedUse, storageInformation, and instructionsForHandlingAndUse are non-empty.",
        "Safety Info: Hazards are documented in healthAndSafetyInformation.",
        "Embedded PDF: Profile C documents include a Base64-encoded PDF.",
        "Digital Signature: At least one ds:Signature is applied."
    ]
}

software_data = {
    "A. Parser Configuration & Namespace Handling": [
        "Namespace Awareness: Parser matches elements by URI + local name.",
        "Prefix Independence: Logic MUST NOT rely on document-provided prefixes.",
        "URI Mapping: Stable internal map for DRMD, DCC, SI, XMLDSig.",
        "XXE Protection: External entity resolution MUST be disabled.",
        "Schema Resolution: Resolve imports from trusted, pinned offline bundles."
    ],
    "B. Validation & Conformance Layers": [
        "Structural Check: Perform XSD validation against drmd.xsd and all imported schemas.",
        "Profile Determination: Automatically classify the document as the highest profile (A, B, or C).",
        "Business Rule Enforcement: Verify mandatory narratives, finite numbers, uncertainty boundaries.",
        "D-SI Unit Validation: Implement regex checks for unit strings (e.g., flagging double prefixes).",
        "Reporting: Generate a machine-readable JSON report."
    ],
    "C. Data Extraction & Normalization": [
        "Unified Quantity Algorithm: Implement a single extraction logic prioritizing si:real.",
        "Multilingual Selection: Implement the fallback algorithm (requested lang -> no lang -> first block).",
        "Identifier Keys: Normalize identifiers by trimming whitespace and using (scheme, value) pair.",
        "Unit Preservation: Store original D-SI unit string as-is.",
        "Numeric Precision: Store values in high-precision types (double/decimal) without rounding."
    ],
    "D. Security & Trust Management": [
        "Cryptographic Verification: For Profile C, use full XMLDSig library.",
        "Attachment Safety: Enforce size limits, verify MIME types, scan for malware.",
        "Version Handling: Inspect schemaVersion and implement strategy-based parsing."
    ]
}

instrument_data = {
    "A. Material Identification & Integration": [
        "Library Mapping: Map material to internal libraries using stable materialIdentifiers.",
        "Deterministic Linking: Use identifiers as canonical keys for multi-material documents.",
        "Traceability Verification: Confirm document refers to a clearly identified material."
    ],
    "B. Property Data Ingestion & Calibration": [
        "Certified Value Prioritization: Filter blocks by @isCertified to ensure only certified values are used for calibration.",
        "Robust Analyte Mapping: Map measured results using propertyIdentifier (CAS, element symbols).",
        "Metrological Ingestion: Reliably parse numerical values, units, and uncertainties.",
        "Uncertainty Interpretation: Correctly interpret confidence levels and coverage factors.",
        "Property Families: Group quantities into logical output tables."
    ],
    "C. Workflow & Operational Safety": [
        "Sample Size Enforcement: Display minimumSampleSize and trigger automated warnings if planned mass is low.",
        "Handling Alerts: Use storage and handling instructions to prevent misuse.",
        "Method Templates: Support automated method templates by ingesting standardized metadata.",
        "Operational Notes: Display root-level comments in UI logs."
    ],
    "D. Security, Trust & Documentation": [
        "Trust Anchor Verification: Optionally verify digital signatures.",
        "Integrity Policy: For Profile C, implement full cryptographic signature validation.",
        "Official Representation: Provide users access to the official PDF representation."
    ],
    "E. Data Normalization for Instruments": [
        "Unit Normalization: Parse D-SI unit strings into internal units safely.",
        "Language Selection: Apply display selection algorithm.",
        "Numeric High-Precision: Store values as double/decimal."
    ]
}

auditor_data = {
    "A. Governance & Accountability": [
        "Document Status: titleOfTheDocument correctly distinguishes CRM vs PIS.",
        "Unique Identification: Presence of a mandatory uniqueIdentifier (UUID).",
        "Responsible Persons: respPersons list identifies who prepared, reviewed, and authorized.",
        "Role Authorization: Specific roles are assigned to satisfy governance.",
        "Electronic Signature Flags: Check cryptographic capability flags."
    ],
    "B. Traceability & Measurement Quality": [
        "Certified vs. Informative: Certified values explicitly distinguished.",
        "Metrological Traceability: Narrative confirms chain to SI."
    ]
}

generate_pdf("docs/assets/pdfs/producer_checklist.pdf", "16.1 Producer Checklist", producer_data)
generate_pdf("docs/assets/pdfs/software_checklist.pdf", "16.2 Software/LIMS Checklist", software_data)
generate_pdf("docs/assets/pdfs/instrument_checklist.pdf", "16.3 Instrument Vendor Checklist", instrument_data)
generate_pdf("docs/assets/pdfs/auditor_checklist.pdf", "16.4 Auditor Checklist", auditor_data)
