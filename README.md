# SAF-T Extended

SAF-T Extended is a draft export package profile for complete accounting-data
portability.

The profile keeps official SAF-T Financial XML as the ledger and master-data
core, and defines how an accounting system should package the related files,
documents and metadata needed to archive, audit, inspect or migrate the
accounting records.

## Problem

A SAF-T XML file is essential, but it is often not enough for a complete and
usable export from an accounting system.

Accounting records commonly depend on files and objects outside the ledger XML:

- invoice PDFs and original invoice files
- receipt images and voucher attachments
- bank, payment and import documentation
- customer, supplier and project documents
- contracts, engagement letters, KYC/AML files and correspondence
- system identifiers needed to reconcile an export with the source system

When these files are missing, unlinked or exported in a vendor-specific way, the
customer may technically have a ledger export but still lack a practical archive
or migration package.

## Goal

The goal is a complete, auditable export package that can be produced by one
accounting system and read by another system, auditor, accountant, customer or
authority without private knowledge of the exporting vendor's database.

A conforming export should make it possible to answer:

- which SAF-T files are included?
- which attachments belong to which postings, invoices, payments or other
  accounting references?
- which documents are included even though they are not tied to a posting?
- which optional SAF-T master-data fields were exported?
- which data was unavailable, intentionally omitted or outside the selected
  export scope?
- whether files were changed after export?

## Relationship to Official SAF-T

This profile does not replace Norwegian SAF-T Financial and does not define a
new tax submission format.

It uses official SAF-T Financial XML first. Package-level metadata is used only
for things that are outside the XML file itself, such as folder layout,
checksums, attachments, document links and limited sidecar data.

If official SAF-T Financial defines a suitable field or structure, exporters
should use that structure instead of inventing a parallel sidecar format.

## Package Contents

A complete export package should contain:

| Area | Requirement |
| --- | --- |
| Ledger and SAF-T master data | Official SAF-T Financial XML files for the selected period and scope. |
| Posting attachments | Files linked to postings, vouchers, invoices, payments or SAF-T SourceDocuments. |
| Non-posting accounting documents | Relevant accounting documents that are not directly tied to a posting. |
| Manifest | A machine-readable package index with checksums, document types, SAF-T references and known omissions. |
| Optional sidecar objects | Extra object files only when SAF-T cannot represent the data clearly or safely. |

See [spec/package.md](spec/package.md) and
[spec/manifest.schema.json](spec/manifest.schema.json).

## Validation

The repository includes a small validator for package smoke tests:

```bash
python3 tools/validate-package.py examples/minimal-package
```

It checks that the manifest parses, referenced files exist, checksums match,
the conformance level is known, and document types are registered or clearly
namespaced extension values.

## Master Data Policy

Customer and supplier master data should be exported through SAF-T
`MasterFiles/Customers` and `MasterFiles/Suppliers` wherever possible.

The profile should standardize completeness expectations for those SAF-T
structures rather than require duplicate `customers.json` or `suppliers.json`
files.

Employee master data is different. SAF-T can represent employees as accounting
dimensions when they are used that way, but it is not a general HR export
format. Employee data should therefore be optional, minimized and exported as a
sidecar only when needed for archive, audit or migration.

## Conformance Levels

The draft uses three intended conformance levels:

| Level | Purpose | Contents |
| --- | --- | --- |
| Core | Minimum portable ledger export | SAF-T XML and manifest. |
| Complete Archive | Accounting archive and audit use | Core plus posting attachments, non-posting accounting documents, checksums and completeness statements. |
| Migration | Moving between accounting systems | Complete Archive plus stable source-system references and carefully scoped sidecar objects. |

See [spec/conformance.md](spec/conformance.md).

## Privacy and Security

Accounting exports can contain personal data, confidential business documents
and bank information.

The package should include only data needed for the selected purpose, and should
make omissions explicit. Sensitive fields such as national identity numbers,
private addresses, health data, payroll details and bank account details should
not be included unless there is a clear legal, audit or migration need.

## Out of Scope

This draft does not define:

- a replacement for official SAF-T Financial
- a tax submission channel
- a full payroll or HR export standard
- a competing invoice format
- commercial terms, prices, customers or market conduct

## Open Work

The most important unresolved questions are:

- which document types should be standardized first?
- how should open customer and supplier items be represented when SAF-T is not
  sufficient in practice?
- should original EHF/Peppol XML be required when available, in addition to
  rendered PDFs?
- how should package signing and tamper evidence work?
- should there be separate legal profiles for archive, audit and migration?

See [docs/critique-and-roadmap.md](docs/critique-and-roadmap.md) for current
critique and improvement ideas.

## Official SAF-T Sources

This draft is intended to align with the official Norwegian SAF-T Financial
documentation and schemas published by the Norwegian Tax Administration:

- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/
- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/documentation/
- https://github.com/Skatteetaten/saf-t
