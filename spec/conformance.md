# Conformance

Version: 0.1-draft

## Terms

The words must, should and may are used in their ordinary standards sense:

- **must** means required for the relevant conformance level
- **should** means recommended unless there is a documented reason not to
- **may** means optional

## Levels

### Core

Core is the minimum portable ledger export.

A Core package must include:

- `manifest.json`
- at least one official SAF-T Financial XML file
- SHA-256 checksum for each SAF-T file
- exported company name and, when available, organization number
- export period
- exporter and source-system identity when available

A Core package should include:

- explicit completeness statements
- known omissions
- SAF-T version for each XML file

### Complete Archive

Complete Archive is intended for accounting archive, review and audit use.

A Complete Archive package must satisfy Core and must include:

- posting attachments available in the source system
- non-posting accounting documents included in the selected export scope
- document type for every file
- media type for every file when known
- SHA-256 checksum for every file
- SAF-T references for every file where a SAF-T reference exists
- known omissions for unavailable attachments, unsupported document classes or
  deliberately excluded data

A Complete Archive package should include:

- original structured documents such as EHF/Peppol XML when available
- rendered PDF versions when the original file is not human-readable
- source-system references that help reconcile files with the exporting system
- a document index sidecar when the manifest alone becomes too large

### Migration

Migration is intended for moving accounting data from one system to another.

A Migration package must satisfy Complete Archive and must include:

- stable source-system identifiers for postings, documents and relevant master
  data when available
- sidecar object files for migration-relevant data that SAF-T cannot represent
  clearly
- documented mapping from sidecar objects to SAF-T identifiers where such a
  relationship exists
- explicit statement of data that cannot be migrated from the source system

A Migration package should include:

- customer and supplier custom fields when they are relevant to bookkeeping or
  migration and cannot be represented in SAF-T
- employee dimension sidecars only when employees are used as accounting
  dimensions or are otherwise needed for migration
- project, department or dimension metadata when SAF-T analysis tables do not
  contain enough information for the receiving system

## Non-Conformance Examples

An export should not claim conformance if:

- it includes only a SAF-T XML file while silently omitting available voucher
  attachments
- it exports files without a manifest or checksums
- it uses private database IDs without mapping them to SAF-T identifiers where
  SAF-T identifiers exist
- it omits known unavailable document categories without saying so
- it duplicates customer and supplier master data in sidecars while leaving
  SAF-T MasterFiles incomplete
