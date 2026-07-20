# 🏗️ Schema Overview & Architecture

The DRMD schema is carefully engineered to be both human-readable and strictly machine-parsable. It is organized into **six interconnected containers**, each serving a specific function in representing a complete reference material certificate.

## The Six Core Containers

!!! abstract "1. Administrative Data (`administrativeData`)"
    Captures essential document metadata and organizational information required for certificate identification and traceability. This includes the document title, unique identifier, validity period, producer contact details, and responsible person signatures.

!!! abstract "2. Materials (`materials`)"
    Defines the reference materials covered by the certificate. It includes the material name, detailed description, classification, minimum sample sizes, and item quantity information.

!!! abstract "3. Material Properties (`materialProperties`)"
    The core data payload. Documents the **certified** and **informational** properties of the material. It includes measurement procedures, results (values, units, and uncertainties), and metrological traceability.

!!! abstract "4. Statements (`statements`)"
    Provides essential non-numerical guidelines including intended use, storage requirements, handling instructions, health and safety information, and legal notices.

!!! abstract "5. Comments & Documents (`comments`, `document`)"
    Allows for supplementary free-text comments and the embedding of binary files (such as a Base64-encoded PDF rendition of the original certificate).

!!! abstract "6. Digital Signature (`ds:Signature`)"
    Provides cryptographic digital signatures (XMLDSig) that guarantee the authenticity, integrity, and non-repudiation of the DRMD certificate.

---

## 🌐 XML Namespaces

DRMD certificates utilize multiple XML namespaces to securely organize different types of information and borrow from established international standards:

*   **`drmd`** (`https://example.org/drmd`): Contains the primary DRMD-specific elements.
*   **`dcc`** (`https://ptb.de/dcc`): Provides common data elements shared across digital certificate standards (Digital Calibration Certificate).
*   **`si`** (`https://ptb.de/si`): Handles scientific and metrological data including numerical values and units (Digital System of Units).
*   **`ds`** (`http://www.w3.org/2000/09/xmldsig#`): Defines the standard XML Digital Signature elements.

---

## 🔄 Versioning & Compatibility

Every DRMD document MUST declare its schema specification version in the root element (e.g., `@schemaVersion="0.3.0"`). 

Software parsing DRMD certificates should implement version checking logic to ensure backward compatibility and prevent misinterpretation of data during major schema upgrades.
