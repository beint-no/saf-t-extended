# SAF-T Extended Package Draft

Version: 0.1-draft

## Purpose

SAF-T Extended defines a package profile for exporting complete accounting data
from an accounting system.

The package is not a new tax submission format. It is a portability profile
around official SAF-T Financial:

- SAF-T XML remains the canonical ledger and master-data export.
- Binary files remain binary files.
- A manifest connects files, objects and SAF-T references.
- Additional sidecar data is used only where SAF-T cannot model the data
  sufficiently.

The profile should track official SAF-T Financial development, especially the
Norwegian Tax Administration's ongoing work on SourceDocuments. Where official
SAF-T adds a suitable structure, this profile should prefer that structure and
keep only the package-level file, checksum and manifest conventions outside the
XML.

## Package Layout

```text
saf-t-extended-package/
  manifest.json
  saf-t/
    SAF-T Financial_999999999_20260131235959_A_1_1.xml
  files/
    postings/
      2026/
        voucher-1001.pdf
    documents/
      contracts/
        customer-agreement-42.pdf
  objects/
    employees.jsonl
    document-index.jsonl
```

Required:

- `manifest.json`
- at least one `saf-t/*.xml` file

Recommended:

- `files/postings/` for files linked to postings, source documents or payment
  lines
- `files/documents/` for accounting documents that are not directly linked to a
  posting
- `objects/` for sidecar object files that SAF-T does not express adequately

## Manifest

The manifest describes the export package and makes completeness auditable.

It should include:

- exporter identity
- accounting system identity
- exported company
- export period
- SAF-T XML files
- binary files and their checksums
- links from files to SAF-T references
- sidecar object files
- completeness statements
- known omissions

See [manifest.schema.json](manifest.schema.json).

## Linking Files to SAF-T

Attachments should not be embedded in SAF-T XML. They should be ordinary files
listed in the manifest.

Each file can link to one or more SAF-T references:

- `journalId`
- `transactionId`
- `recordId`
- `sourceDocumentId`
- `voucherNumber`
- `customerId`
- `supplierId`
- `ownerId`
- `analysisType` and `analysisId`

When the accounting system has stronger internal identifiers, include them as
`systemReferences` in addition to the SAF-T references.

## Posting Attachments

Files related to postings should be placed under `files/postings/`.

Examples:

- purchase invoice PDF
- sales invoice PDF
- receipt image
- bank transaction attachment
- imported EHF/Peppol invoice rendered as PDF plus original XML where available

Each file should have a manifest entry with:

- `documentType`
- `path`
- `sha256`
- `mediaType`
- `safTReferences`
- optional `systemReferences`

## Non-Posting Documents

Accounting systems often contain documents that are relevant to bookkeeping,
audit, AML/KYC, customer work or migration, but are not tied to a specific
posting.

Examples:

- customer or supplier contracts
- accountant engagement letters
- KYC and AML documents
- correspondence
- payroll-related accounting documentation
- system reports
- import/export logs

These files should be placed under `files/documents/` and listed in the
manifest. If a document relates to a customer, supplier, employee, project or
department, use the closest SAF-T identifier where possible and a sidecar object
identifier where SAF-T has no suitable identifier.

## Customers and Suppliers

Use SAF-T MasterFiles for customers and suppliers whenever possible.

SAF-T Financial already has customer and supplier master structures with:

- customer/supplier ID
- registration number
- name
- address
- contact information
- tax registrations
- bank accounts
- balance accounts
- party analysis

This profile should not duplicate ordinary customer and supplier master data in
separate files by default.

Instead, this profile standardizes stricter export expectations:

- include all optional SAF-T customer/supplier fields that are available in the
  exporting system
- preserve stable IDs used in postings
- preserve registration numbers and tax IDs when available
- include contacts, addresses, bank accounts and balance accounts when present
- use sidecar files only for fields with no clear SAF-T representation

Possible sidecar examples:

- customer/supplier custom fields
- customer/supplier document relations not representable via SAF-T
- CRM-only metadata that is included for migration but not bookkeeping

## Employees

Employees should not be forced into the customer/supplier structures.

SAF-T can represent employees as analysis dimensions, for example through
`AnalysisTypeTable` and line-level `Analysis` references. That is useful for
accounting dimensions such as employee, department, project, cost center or
owner.

However, SAF-T Financial does not provide a full employee master structure for
ordinary HR/payroll information. If employee data is included, this profile
should use `objects/employees.jsonl` as a sidecar file and link it to SAF-T
analysis identifiers where relevant.

Employee sidecar data should be minimized and purpose-bound because it can
contain sensitive personal data.

Recommended employee sidecar fields:

- `employeeId`
- `analysisType`
- `analysisId`
- `displayName`
- `employmentStartDate`
- `employmentEndDate`
- `status`
- `sourceSystemId`
- `relatedDocuments`

Fields such as national identity number, private address, health data, salary
details and bank account should not be included unless there is a clear legal,
audit or migration need.

## Extension Rule

When deciding where data belongs:

1. If official SAF-T has a valid field or structure, use SAF-T.
2. If official SAF-T has an identifier but not the binary content, store the file
   and link it in the manifest.
3. If official SAF-T can represent the data as an analysis dimension, use SAF-T
   for the dimension and use sidecar data only for extra object details.
4. If official SAF-T cannot represent the object safely or clearly, use a
   sidecar file in `objects/`.
5. If the data is system-specific, include it only if it helps audit,
   bookkeeping, archiving or migration.

## Open Questions

- Should `objects/` use JSON Lines, CSV, Parquet or a mix?
- Which document types should be standardized first?
- Should the package allow original EHF/Peppol XML beside rendered PDFs?
- How should open customer/supplier items be represented if they are
  insufficiently clear from SAF-T alone?
- Should there be separate profiles for audit, archive and migration exports?
