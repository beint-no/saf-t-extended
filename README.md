# SAF-T Extended

An open export package profile for complete accounting data portability.

SAF-T Extended keeps the official SAF-T Financial XML file as the canonical
ledger export, and defines a portable folder structure around it for:

- SAF-T XML files
- PDF/image/source attachments linked to postings, invoices, payments or other
  SAF-T references
- accounting documents that are not directly linked to postings, such as
  contracts, correspondence, KYC files, board documents or system-specific files
- optional sidecar object files only where SAF-T cannot represent the data well

The goal is practical portability: a company should be able to export its own
accounting records in a form that can be archived, audited, inspected and used
when changing accounting software.

## Naming

The working name is **SAF-T Extended** and the repository slug is
`saf-t-extended`.

This is intentionally not a replacement for Norwegian SAF-T Financial and not a
fork of the official XML schema. A better technical description is:

> a SAF-T-based export package profile.

The profile should follow official SAF-T first. It should add package-level
conventions only where the current official exchange leaves practical gaps for
data portability.

The Norwegian Tax Administration already publishes official SAF-T schemas and
has public work underway for broader SourceDocuments support. This repository is
therefore scoped as an unofficial interoperability profile for package layout,
manifesting, attachments and sidecar data.

## Current Scope

The first draft defines:

1. package folder structure
2. package manifest
3. rules for linking files to SAF-T references
4. guidance for customers, suppliers, employees and other master data
5. extension principles for data that does not belong in SAF-T XML

See [spec/package.md](spec/package.md) for the initial draft.
See [notes/naming-and-scope.md](notes/naming-and-scope.md) for the naming
rationale.

## Design Principles

- **SAF-T first.** Use official SAF-T Financial XML where it has a field,
  structure or identifier.
- **Do not break SAF-T validation.** Do not add unofficial XML elements to the
  official SAF-T file unless the official schema explicitly allows it.
- **Keep attachments as files.** PDFs, images and binary source documents should
  be stored as ordinary files and referenced from a manifest.
- **Use sidecars sparingly.** Sidecar object files are for data that SAF-T does
  not model clearly, such as employees as full person/master objects.
- **Make completeness auditable.** The manifest should explain what is included,
  how it links to SAF-T, and whether anything is missing.
- **Avoid competition-sensitive content.** This profile is about customer-owned
  data and interoperability only.

## Status

Draft. This repository is intended to collect a concrete proposal and examples
for discussion with accounting-system vendors, accounting offices, auditors,
standard-setting organizations and public authorities.

## Sources

This work is designed to align with the official Norwegian SAF-T Financial
documentation and schemas published by the Norwegian Tax Administration:

- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/
- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/documentation/
- https://github.com/Skatteetaten/saf-t
