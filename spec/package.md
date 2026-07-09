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
    e-invoices/
      incoming/
        2026/
          INV-1001.xml
      renderings/
        2026/
          INV-1001.pdf
      attachments/
        2026/
          INV-1001-timesheet.pdf
    postings/
      2026/
        receipt-42.jpg
    documents/
      contracts/
        customer-agreement-42.pdf
  objects/
    employees.jsonl
    document-index.jsonl
```

Minimum valid export:

- `manifest.json`
- at least one `saf-t/*.xml` file
- every file in the source system that relates directly to postings in the
  SAF-T selection
- every exported file listed in `manifest.json`
- SHA-256 checksum for every listed file
- structured omissions for posting-related files that are unavailable or cannot
  be exported

Standard directories:

- `files/e-invoices/` for EHF/Peppol invoice and credit note XML, renderings
  and extracted attachments
- `files/postings/` for other files linked to postings, source documents or
  payment lines
- `files/documents/` for accounting documents that are not directly linked to a
  posting and are included as recommended additions
- `objects/` for sidecar object files that SAF-T does not express adequately

## Manifest

The manifest describes the export package and makes completeness auditable.

It should include:

- exporter identity
- accounting system identity
- exported company
- export period
- SAF-T XML files
- exported files and their checksums
- links from files to SAF-T references
- links between original EHF/Peppol XML, renderings and attachments
- sidecar object files
- completeness statements
- known omissions

See [manifest.schema.json](manifest.schema.json).
See [document-types.md](document-types.md) for the initial document type
registry.

## Minimum Scope

The minimum package is a SAF-T export plus all posting-related files the source
system has.

Posting-related files include:

- original EHF/Peppol invoice and credit note XML
- PDF renderings of invoices and credit notes
- attachments embedded in or associated with EHF/Peppol invoices
- voucher attachments
- receipt images
- bank and payment documentation
- other files needed to understand, verify or audit the postings in the SAF-T
  file

The minimum is deliberately practical. A vendor should be able to implement it
without solving full migration of every master-data object first.

If a posting-related file exists in the source system, it should be included. If
it cannot be exported, the package should include a structured `knownOmissions`
entry explaining the reason.

## Recommended Additions

The following are optional, but recommended when available and useful for the
export purpose:

- complete customer and supplier data through SAF-T optional fields
- customer/supplier sidecar data only where SAF-T lacks a suitable field
- employee sidecar data when employees are accounting dimensions or relevant to
  archive, audit or migration
- contracts, KYC/AML files, engagement letters and correspondence not tied to a
  SAF-T posting
- stable source-system identifiers and migration metadata

## EHF and Peppol Invoices

When an invoice or credit note exists as EHF Billing 3.0 or Peppol BIS Billing
3.0 XML, the original XML should be exported.

The original XML should be listed as:

- `documentType: "invoice"` for invoices
- `documentType: "credit-note"` for credit notes
- `mediaType: "application/xml"` or a more specific XML media type
- `electronicInvoice.standard: "ehf-billing-3.0"` or
  `"peppol-bis-billing-3.0"`

PDFs generated from the original XML should be listed as
`documentType: "invoice-rendering"` and linked to the original XML using
`relatedFileIds`.

Attachments embedded in the EHF/Peppol XML should be extracted as ordinary files
with `documentType: "invoice-attachment"` and linked to the original XML using
`extractedFromFileId`.

The package should preserve the original EHF/Peppol XML even when a PDF
rendering exists. If the source system has only a PDF and not the original XML,
that omission should be stated in `knownOmissions`.

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

- receipt image
- bank transaction attachment
- voucher documentation that is not an invoice or credit note
- payment confirmation file

Each file should have a manifest entry with:

- `id`
- `documentType`
- `path`
- `sha256`
- `mediaType`
- `safTReferences`
- optional `relatedFileIds`
- optional `extractedFromFileId`
- optional `systemReferences`

The `documentType` value must come from the registry. The profile should expand
the registry when a generally useful new document type is needed rather than
allowing private permanent labels.

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

- How should open customer/supplier items be represented if they are
  insufficiently clear from SAF-T alone?
- Should embedded EHF/Peppol attachments always be extracted as separate package
  files, or should the original base64 content in the XML be enough when the
  attachment is not needed by the receiving system?
