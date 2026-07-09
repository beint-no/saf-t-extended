# Document Type Registry

Version: 0.1

## Purpose

The document type registry gives exporters and importers a shared vocabulary for
files in the package.

Exporters must use a registered document type. If no registered value fits, the
registry should be expanded rather than preserving private permanent labels from
each accounting system.

## Posting-Related Documents

These document types normally relate to one or more SAF-T postings.

| Type | Description | Expected references |
| --- | --- | --- |
| `invoice` | Original structured invoice, normally EHF Billing 3.0 or Peppol BIS Billing 3.0 XML. | Source document ID, customer ID, supplier ID, transaction ID or voucher number when available. |
| `credit-note` | Original structured credit note, normally EHF Billing 3.0 or Peppol BIS Billing 3.0 XML. | Source document ID, customer ID, supplier ID, transaction ID or voucher number when available. |
| `invoice-rendering` | Human-readable invoice or credit note file, normally PDF. | Same SAF-T references as the invoice when available. |
| `invoice-attachment` | File embedded in or associated with an invoice or credit note. | Same SAF-T references as the invoice when available. |
| `receipt` | Receipt or image documentation for a posted transaction. | Transaction ID, record ID or voucher number when available. |
| `voucher-attachment` | General attachment to a voucher or posting. | Transaction ID, record ID or voucher number when available. |
| `bank-statement` | Bank statement file or statement extract. | Bank account, payment reference or transaction period when available. |
| `payment-documentation` | Payment file, payment confirmation or remittance documentation. | Payment/source document ID or transaction ID when available. |

## EHF and Peppol

When the source system has the original EHF/Peppol invoice or credit note XML,
export the XML with `documentType` set to `invoice` or `credit-note`.

If the source system also has a PDF, export it with `documentType` set to
`invoice-rendering`.

The manifest does not need to link the PDF back to the XML if the SAF-T
reference or source document reference already makes the relationship clear.

## Non-Posting Accounting Documents

These document types may be linked to customer, supplier, owner, analysis or
sidecar object identifiers instead of posting identifiers.

| Type | Description | Expected references |
| --- | --- | --- |
| `customer-contract` | Contract or agreement with a customer. | Customer ID when available. |
| `supplier-contract` | Contract or agreement with a supplier. | Supplier ID when available. |
| `engagement-letter` | Agreement between customer and accountant, auditor or advisor. | Customer, supplier or owner reference when available. |
| `kyc-document` | KYC/AML documentation. | Customer, supplier, owner or sidecar object reference when available. |
| `correspondence` | Relevant accounting correspondence. | Closest customer, supplier, posting or object reference when available. |
| `board-document` | Board or governance document relevant to accounting records. | Owner or period reference when available. |
| `system-report` | Report generated from the source accounting system. | Period, report ID or source-system reference when available. |
| `import-log` | Log from data imported into the accounting system. | Source-system reference and period when available. |
| `export-log` | Log or report created as part of the export process. | Package or export ID when available. |

## Sidecar Object Documents

These document types may refer primarily to objects in `objects/`.

| Type | Description | Expected references |
| --- | --- | --- |
| `employee-document` | Employee-related accounting document included for archive, audit or migration. | Employee sidecar ID or SAF-T analysis ID when available. |
| `project-document` | Document linked to a project or equivalent dimension. | SAF-T analysis type and analysis ID when available. |
| `department-document` | Document linked to a department or equivalent dimension. | SAF-T analysis type and analysis ID when available. |
