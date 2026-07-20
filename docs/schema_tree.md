# 🌳 Schema Interactive Tree

Click on any element block to expand and explore its child elements, attributes, and types. This interactive tree covers the complete DRMD schema and its imported namespaces.

???+ note "**E** `drmd:digitalReferenceMaterialDocument`"
    - **Type**: `drmd:digitalReferenceMaterialDocumentType`
    - **Cardinality**: `[1..1]`

    *The structural root of the DRMD configuration. Supports both Reference Material Certificate (CRM) and         Product Information Sheet (RM) document profiles. Systematically coordinates core metadata, physical product         catalogs, measurement results, and cryptographic blocks into six interconnected electronic containers,         maintaining data integrity for global laboratory data exchanges. The document profile is determined by         the titleOfTheDocument element in coreData; profile-specific constraints are enforced via companion         Schematron rules (drmd-business-rules.sch) per ISO 33401:2024, Table 1.*

    - 🟡 `@` `schemaVersion` : `drmd:schemaVersionType` (required)

