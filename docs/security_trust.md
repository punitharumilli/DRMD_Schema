# Security & Trust Model

The trust model ensures that technical data (values, units, uncertainties) remains authentic and entirely unaltered from the moment of issuance by the Reference Material Producer (RMP) to the moment of automated consumption by an analytical instrument or Laboratory Information Management System (LIMS).

While structural validation and Schematron business rules ensure the document makes sense, the Security & Trust Model ensures the document has not been tampered with.

---

## 14.1 Trust Store & Certificate Governance

Digital signatures (as defined in Chapter 8) are only as strong as the cryptographic infrastructure supporting them.

- **Trust Anchors:** Consumers (laboratories and software applications) must maintain a "Trust Store" of authorized Root Certificates from recognized Reference Material Producers (e.g., BAM, NIST, ERM).
- **Identity Verification:** RMPs should use organizational certificates (Electronic Seals) issued by Qualified Trust Service Providers (TSPs) to ensure the signature is legally linked to the institution, not just an individual.
- **Public Key Distribution:** Producers should publish their public keys or certificate fingerprints on official, secure websites (HTTPS) to allow software vendors to pre-configure trust.
- **Revocation Checks:** Software implementations should periodically check Certificate Revocation Lists (CRL) or use Online Certificate Status Protocol (OCSP) to ensure a producer's signing key hasn't been compromised.

---

## 14.2 Handling Embedded Documents

The DRMD schema allows embedding binary files like PDFs and images within the `drmd:document` element. Because these are "untrusted" data streams traversing the network, they require strict security processing.

!!! warning "Strict Payload Processing"
    Failure to properly sanitize embedded Base64 documents can result in malware execution or Denial-of-Service (DoS) attacks via memory exhaustion.

### Security Implementation Rules
1. **Size Limits:** To prevent "XML bomb" or memory exhaustion attacks, parsers should enforce a maximum size for `dcc:dataBase64` elements (e.g., a hard limit of 50 MB).
2. **Malware Scanning:** All extracted attachments **MUST** be scanned for viruses and malicious macros before being opened by the end-user or saved to disk.
3. **MIME-Type Whitelisting:** Systems should only process a restricted list of safe formats (e.g., `application/pdf`, `image/png`, `image/jpeg`). Executable files (e.g., `.exe`, `.bat`, `.js`) MUST be outright rejected.
4. **Content Consistency:** Software should verify that the `dcc:fileName` extension matches the declared `dcc:mimeType` to prevent "extension spoofing".

---

## 14.3 Transport & Storage Integrity

Even with a digital signature present, the operational environment must protect the DRMD from accidental or malicious corruption during its lifecycle.

- **Secure Transport:** DRMDs should always be exchanged over encrypted channels (e.g., HTTPS, SFTP, or TLS-encrypted API calls).
- **Storage Immutability:** Once a DRMD is imported into a LIMS or instrument library, it should be marked as **Read-Only**. Any changes to the data must require the issuance of a new DRMD with a completely new `uniqueIdentifier`.
- **Hashing for Quick Verification:** Systems should generate and store a cryptographic hash (e.g., SHA-256) of the entire DRMD file upon import. This allows for rapid integrity checks without performing a full, expensive XMLDSig verification every time the file is accessed.
- **Audit Trail Requirements:** All security-relevant events—such as signature verification success/failure, certificate expiration warnings, and attachment extractions—must be logged in a local system audit trail for regulatory review.

---

## 14.4 Summary of Security Responsibilities

Security is a shared responsibility across the entire supply chain. 

| Stakeholder | Primary Responsibility |
|-------------|------------------------|
| **Reference Material Producer** | Signs the document with a valid, non-expired organizational seal. Securely distributes their public keys. |
| **Software Developer** | Implements automated signature validation, strict XML parsing, and attachment malware scanning. |
| **Laboratory (End User)** | Maintains the local trust store and reviews system audit logs for any signature failures. |
| **Auditor** | Verifies that the digital "Chain of Trust" is intact, logged, and policy-compliant. |
