# SAF-T Extended

SAF-T Extended is an open export package profile for complete accounting-data
portability.

It keeps official SAF-T Financial XML as the ledger and master-data core, and
defines how an accounting system should package the files needed to archive,
audit, inspect or migrate the accounting records.

The profile does not replace Norwegian SAF-T Financial, EHF or Peppol. It uses
those standards first and adds only package-level conventions for files,
checksums, completeness and optional sidecar data.

## Problem

A SAF-T XML file is essential, but it is often not enough for a complete and
usable export from an accounting system.

Accounting records commonly depend on files and objects outside the ledger XML:

- original EHF/Peppol invoice and credit note XML
- invoice PDFs and other human-readable renderings
- receipt images and voucher attachments
- bank, payment and import documentation
- customer, supplier and project documents
- contracts, engagement letters, KYC/AML files and correspondence
- system identifiers needed to reconcile an export with the source system

When these files are missing, unlisted or exported in a vendor-specific way, the
customer may technically have a ledger export but still lack a practical archive
or migration package.

## Goal

The goal is a complete, auditable export package that can be produced by one
accounting system and read by another system, auditor, accountant, customer or
authority without private knowledge of the exporting vendor's database.

A valid export should make it possible to answer:

- which SAF-T files are included?
- which posting-related files are included?
- which optional non-posting documents and sidecar objects are included?
- which data was unavailable, intentionally omitted or outside the selected
  export scope?
- whether files were changed after export?

## Minimum Valid Export

The minimum valid export is intentionally small enough for accounting-system
vendors to adopt:

1. official SAF-T Financial XML for the selected period and scope
2. every file in the source system that relates directly to postings in that
   SAF-T export
3. a manifest that lists package files with path, document type, media type and
   SHA-256 checksum, plus SAF-T references where available
4. structured omissions for posting-related files that are unavailable or cannot
   be exported

Posting-related files include original EHF/Peppol invoice and credit note XML,
invoice PDFs/renderings when present, voucher attachments, receipts, bank and
payment documentation, and other files needed to understand the postings in the
SAF-T file.

Everything beyond that minimum is optional, but recommended when the source
system has the data and the export purpose requires it.

## EHF and Peppol Invoices

When an invoice or credit note exists as EHF Billing 3.0 or Peppol BIS Billing
3.0 XML, include the original XML as a posting-related file.

If the same invoice also has a PDF or other file in the source system, include
that file too.

The manifest does not need to re-model relationships that already exist in
SAF-T, in the EHF/Peppol XML, or in the source document reference. It only needs
to list the exported files, checksums, document types and SAF-T references where
available.

## Recommended Additions

Recommended additions include:

| Area | Recommendation |
| --- | --- |
| Customer and supplier master data | Complete use of available SAF-T customer and supplier fields, with sidecars only for data SAF-T cannot represent. |
| Employee information | Minimal employee sidecar data when employees are used as accounting dimensions or needed for archive, audit or migration. |
| Non-posting accounting documents | Contracts, KYC/AML documents, engagement letters, correspondence and other relevant documents not tied directly to a posting. |
| Migration metadata | Stable source-system identifiers and sidecar objects needed by a receiving system. |

See [spec/package.md](spec/package.md) and
[spec/manifest.schema.json](spec/manifest.schema.json).

## Validation

The repository includes a small validator for package smoke tests:

```bash
python3 tools/validate-package.py examples/minimal-package
```

It checks that the manifest parses, referenced files exist, checksums match,
document types are registered, file IDs are unique, and the minimum
completeness statements are present.

## Implementers

Accounting-system vendors can be listed in
[IMPLEMENTERS.md](IMPLEMENTERS.md) after showing that their export supports the
minimum valid export.

A practical proof is a sample package that passes the validator and contains
SAF-T XML plus all posting-related files available in the source system for the
selected scope.

## Privacy and Security

Accounting exports can contain personal data, confidential business documents
and bank information.

The package should include only data needed for the selected purpose, and should
make omissions explicit. Sensitive fields such as national identity numbers,
private addresses, health data, payroll details and bank account details should
not be included unless there is a clear legal, audit or migration need.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Official Sources

This profile is intended to align with the official Norwegian SAF-T Financial,
EHF and Peppol documentation:

- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/
- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/documentation/
- https://github.com/Skatteetaten/saf-t
- https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/
- https://docs.peppol.eu/poacc/billing/3.0/bis/
