# Document Type Registry

Version: 0.1-draft

## Purpose

The document type registry gives exporters and importers a shared vocabulary for
files in the package.

The registry is intentionally small at first. New document types should be added
only when they improve archive, audit, inspection or migration.

## Rules

Each file listed in `manifest.json` must have a `documentType`.

Exporters should use a registered document type when one exists.

If no registered value fits, exporters may use an extension value prefixed by
their domain, for example `example.com:custom-report`. Extension values should
be proposed for standardization if they are useful across systems.

## Posting-Linked Documents

These document types normally require at least one SAF-T reference.

| Type | Description | Expected references |
| --- | --- | --- |
| `purchase-invoice` | Supplier invoice or equivalent purchase documentation. | Supplier ID, source document ID, transaction ID or voucher number. |
| `sales-invoice` | Customer invoice or equivalent sales documentation. | Customer ID, source document ID, transaction ID or voucher number. |
| `receipt` | Receipt or image documentation for a posted transaction. | Transaction ID, record ID or voucher number. |
| `voucher-attachment` | General attachment to a voucher or posting. | Transaction ID, record ID or voucher number. |
| `bank-statement` | Bank statement file or statement extract. | Bank account, payment reference or transaction period. |
| `payment-documentation` | Payment file, payment confirmation or remittance documentation. | Payment/source document ID or transaction ID. |
| `ehf-invoice` | Original EHF/Peppol invoice XML. | Source document ID, customer ID or supplier ID. |
| `invoice-rendering` | Human-readable rendering of a structured invoice, normally PDF. | Source document ID, customer ID or supplier ID. |

## Non-Posting Accounting Documents

These document types may be linked to customer, supplier, owner, analysis or
sidecar object identifiers instead of posting identifiers.

| Type | Description | Expected references |
| --- | --- | --- |
| `customer-contract` | Contract or agreement with a customer. | Customer ID when available. |
| `supplier-contract` | Contract or agreement with a supplier. | Supplier ID when available. |
| `engagement-letter` | Agreement between customer and accountant, auditor or advisor. | Customer, supplier or owner reference when available. |
| `kyc-document` | KYC/AML documentation. | Customer, supplier, owner or sidecar object reference. |
| `correspondence` | Relevant accounting correspondence. | Closest customer, supplier, posting or object reference. |
| `board-document` | Board or governance document relevant to accounting records. | Owner or period reference when available. |
| `system-report` | Report generated from the source accounting system. | Period, report ID or source-system reference. |
| `import-log` | Log from data imported into the accounting system. | Source-system reference and period. |
| `export-log` | Log or report created as part of the export process. | Package or export ID. |

## Sidecar Object Documents

These document types may refer primarily to objects in `objects/`.

| Type | Description | Expected references |
| --- | --- | --- |
| `employee-document` | Employee-related accounting document included for archive, audit or migration. | Employee sidecar ID or SAF-T analysis ID. |
| `project-document` | Document linked to a project or equivalent dimension. | SAF-T analysis type and analysis ID. |
| `department-document` | Document linked to a department or equivalent dimension. | SAF-T analysis type and analysis ID. |

## Open Questions

- Should `ehf-invoice` be mandatory whenever available?
- Should `invoice-rendering` be required in addition to original structured
  invoice files?
- Should bank statements use a separate object model instead of only document
  links?
- Should KYC/AML documents be excluded by default unless an archive or migration
  profile explicitly includes them?
