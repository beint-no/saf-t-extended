# Document Type Registry

Version: 0.1-draft

## Purpose

The document type registry gives exporters and importers a shared vocabulary for
files in the package.

The registry is intentionally small at first. New document types should be added
only when they improve archive, audit, inspection or migration.

## Rules

Each file listed in `manifest.json` must have a `documentType`.

Exporters must use a registered document type.

If no registered value fits, the registry should be expanded. The purpose of
this profile is to standardize common accounting export content, not to preserve
private labels from each accounting system.

## Posting-Linked Documents

These document types normally require at least one SAF-T reference.

| Type | Description | Expected references |
| --- | --- | --- |
| `invoice` | Original structured invoice, normally EHF Billing 3.0 or Peppol BIS Billing 3.0 XML. | Source document ID, customer ID, supplier ID, transaction ID or voucher number. |
| `credit-note` | Original structured credit note, normally EHF Billing 3.0 or Peppol BIS Billing 3.0 XML. | Source document ID, customer ID, supplier ID, transaction ID or voucher number. |
| `invoice-rendering` | Human-readable rendering of an invoice or credit note, normally PDF. | Related original invoice file ID and the same SAF-T references when available. |
| `invoice-attachment` | File embedded in or associated with an invoice or credit note. | Original invoice file ID and the same SAF-T references when available. |
| `receipt` | Receipt or image documentation for a posted transaction. | Transaction ID, record ID or voucher number. |
| `voucher-attachment` | General attachment to a voucher or posting. | Transaction ID, record ID or voucher number. |
| `bank-statement` | Bank statement file or statement extract. | Bank account, payment reference or transaction period. |
| `payment-documentation` | Payment file, payment confirmation or remittance documentation. | Payment/source document ID or transaction ID. |

## Electronic Invoice Rules

When the source system has the original EHF/Peppol invoice or credit note XML,
the original XML should be exported with `documentType` set to `invoice` or
`credit-note`.

PDFs should use `invoice-rendering` and link to the original XML with
`relatedFileIds`.

Attachments embedded in the EHF/Peppol XML should use `invoice-attachment` and
link to the original XML with `extractedFromFileId`.

If only a PDF exists and the original XML is unavailable, the package should
include the PDF as `invoice-rendering` and state the missing XML in
`knownOmissions`.

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

- Should original EHF/Peppol XML be mandatory whenever available?
- Should `invoice-rendering` be required in addition to original structured
  invoice files?
- Should bank statements use a separate object model instead of only document
  links?
- Should KYC/AML documents be excluded by default unless an archive or migration
  profile explicitly includes them?
