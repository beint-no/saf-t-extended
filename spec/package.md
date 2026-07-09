# SAF-T Extended Package Profile

Version: 0.1

## Purpose

SAF-T Extended defines a package profile for exporting complete accounting data
from an accounting system.

The package is not a new tax submission format. It is a portability profile
around official SAF-T Financial:

- SAF-T XML remains the canonical ledger and master-data export.
- Binary files remain ordinary files.
- A manifest lists files, checksums and available SAF-T references.
- Sidecar data is optional and used only where SAF-T cannot model the data
  sufficiently.

Where official SAF-T has a suitable field or structure, exporters should use
SAF-T instead of inventing a parallel sidecar format.

## Package Layout

```text
saf-t-extended-package/
  manifest.json
  saf-t/
    SAF-T Financial_999999999_20260131235959_A_1_1.xml
  files/
    postings/
      2026/
        INV-1001.xml
        INV-1001.pdf
        receipt-42.jpg
    documents/
      contracts/
        customer-agreement-42.pdf
  objects/
    employees.jsonl
```

Standard directories:

- `saf-t/` contains official SAF-T Financial XML files.
- `files/postings/` contains all files related directly to postings in the
  selected SAF-T export.
- `files/documents/` contains optional accounting documents that are not tied
  directly to a posting.
- `objects/` contains optional sidecar object files that SAF-T does not express
  adequately.

## Minimum Valid Export

The minimum valid export is:

- `manifest.json`
- at least one `saf-t/*.xml` file
- every file in the source system that relates directly to postings in the
  SAF-T selection
- every exported file listed in `manifest.json`
- SHA-256 checksum for every listed file
- completeness statements for SAF-T XML and posting-related documents
- structured omissions for posting-related files that are unavailable or cannot
  be exported

Posting-related files include:

- original EHF/Peppol invoice and credit note XML
- invoice and credit note PDFs when present
- voucher attachments
- receipt images
- bank and payment documentation
- other files needed to understand, verify or audit the postings in the SAF-T
  file

The minimum is deliberately practical. A vendor should be able to implement it
without solving full migration of every master-data object first.

## Manifest

The manifest describes the export package and makes completeness auditable.

It should include:

- exporter identity
- accounting system identity
- exported company
- export period
- SAF-T XML files
- exported files and their checksums
- SAF-T references where available
- optional sidecar object files
- completeness statements
- known omissions

See [manifest.schema.json](manifest.schema.json).
See [document-types.md](document-types.md) for the document type registry.

## EHF and Peppol Invoices

When an invoice or credit note exists as EHF Billing 3.0 or Peppol BIS Billing
3.0 XML, the original XML should be included as a posting-related file.

If the source system also has a PDF rendering of the invoice, include the PDF as
another posting-related file.

The package should not require a separate invoice relationship model. The
manifest should list each file and include SAF-T references where available. If
SAF-T or the EHF/Peppol XML already identifies the invoice, the manifest does
not need to repeat all invoice metadata.

If a posting-related file exists in the source system but cannot be exported,
the package should include a structured `knownOmissions` entry explaining the
reason.

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

- original EHF/Peppol invoice XML
- PDF invoice copy
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
- `safTReferences` when available
- `systemReferences` when useful

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

These files are optional. When included, place them under `files/documents/` and
list them in the manifest.

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

## Employees

Employees should not be forced into the customer/supplier structures.

SAF-T can represent employees as analysis dimensions, for example through
`AnalysisTypeTable` and line-level `Analysis` references. That is useful for
accounting dimensions such as employee, department, project, cost center or
owner.

SAF-T Financial does not provide a full employee master structure for ordinary
HR/payroll information. If employee data is included, use
`objects/employees.jsonl` as a sidecar file and link it to SAF-T analysis
identifiers where relevant.

Employee sidecar data should be minimized and purpose-bound because it can
contain sensitive personal data.

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
