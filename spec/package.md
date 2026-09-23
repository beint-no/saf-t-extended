# SAF-T Extended 0.4

This document is normative.

## 1. Scope

SAF-T Extended is a portable accounting archive and interchange package, not a
tax submission format. Official SAF-T Financial XML remains unchanged and is
the source of truth for accounts, tax codes, dimensions and ledger transactions.

Version 0.4 consists of:

- predictable customer, supplier, employee, department, project, product and
  sales-order objects
- original accounting documents
- document-to-SAF-T transaction links
- integrity checksums

## 2. Required layout

Every package has this layout:

```text
manifest.json
saf-t/<one or more XML files>
objects/customers.jsonl    # when non-empty
objects/suppliers.jsonl    # when non-empty
objects/employees.jsonl    # when non-empty
objects/departments.jsonl  # when non-empty
objects/projects.jsonl     # when non-empty
objects/products.jsonl     # when non-empty
objects/orders.jsonl       # when non-empty
documents/<source documents, optionally grouped by document role and voucher type>
extras/<integrity-listed, non-standard files>
```

`manifest.json` and at least one SAF-T XML file are required. Each shown JSONL
file is present only when it contains at least one record; `objects/` may be
absent when there are no object records. `documents/` may be absent when there
are no documents. `extras/` may be absent when the always-present `extras`
manifest array is empty.

No other files or directories are part of version 0.4. A package containing
unlisted files is invalid.

## 3. Manifest

The manifest follows [manifest.schema.json](manifest.schema.json). It contains:

- the format version and creation time
- exporter, source system, company and period
- every SAF-T file and its SHA-256 checksum
- checksums for each present JSONL file
- every document, its media type, checksum, source identifiers and SAF-T links
- every non-standard supplementary file and its media type and checksum
- a `missingDocuments` array naming source documents that the source system
  reported but could not return

There is no separate index, duplicate report, completeness report or database.
`missingDocuments` is always present and is empty for a complete export. Each
non-empty entry has only a stable source ID and `not-found` or `not-exportable`;
request IDs, stack traces and other diagnostics stay outside the archive.

### Transaction links

Each known document relationship identifies:

- the SAF-T file path
- `JournalID`
- `TransactionID`
- zero or more line-level `RecordID` values

An empty `recordIds` array means the document relates to the whole transaction.
A document can link to several transactions. If no reliable relationship can be
established, `transactions` is an empty array; exporters must not invent a link
from a similar invoice number or amount.

`sourceIds` preserves identifiers assigned to the same bytes by the source
system. Values use the form `vendor:type:value`, for example
`accounting-system:document:1001`.

## 4. Documents

Include source evidence used to understand or substantiate the accounting:

- EHF/Peppol invoices and credit notes
- invoice or credit-note files actually received or sent
- receipts and voucher attachments
- bank and payment documentation
- payroll accounting documentation
- other original attachments

Do not include a PDF, HTML page, report or text file generated during export
from data already present in SAF-T or the JSONL files. A source system's
on-demand rendering is included only when it is the only retained readable
source document.

When EHF XML and a PDF were both independently received, sent or retained as
source artifacts, both are documents. When the PDF is merely a rendering of the
EHF generated for export, only the EHF is included.

Identical bytes are stored once. PDFs may also be stored once when a full stream
comparison proves that they differ only in generated PDF document IDs or
creation/modification timestamps and they link to the same SAF-T transaction.
Their source identifiers and transaction links are combined in the one manifest
entry. Visual similarity alone is not sufficient for deduplication.

Filenames must have an extension matching the detected content. Generic `.bin`
files are invalid. Exporters must identify the content or fail. HTML fragments
or diagnostic responses produced by an accounting-system endpoint are not
accounting documents and are ignored.

The document types in version 0.4 are intentionally small:

| Type | Meaning |
| --- | --- |
| `invoice` | Invoice source document, including EHF/Peppol XML or a retained PDF. |
| `credit-note` | Credit-note source document. |
| `receipt` | Receipt supporting a transaction. |
| `attachment` | Other voucher or accounting attachment. |
| `bank-document` | Bank statement, payment file or payment confirmation. |
| `payroll-document` | Payslip or other payroll accounting evidence. |

### Document folders

Exporters should group documents by their business role so a person can browse
the archive without first reading the manifest. A useful layout is
`documents/supplier-invoices/`, `documents/customer-invoices/`,
`documents/salary/`, `documents/inbox/` for received documents not yet posted,
and `documents/vouchers/<voucher-type>/` for other posted evidence. Additional
groups and year subdirectories are allowed. The manifest remains authoritative:
folder names do not establish document type, posting status or a transaction
link. A file with several roles is stored once and can carry all source IDs and
transaction links in its manifest entry.

## 5. Objects

The supported files are:

- `objects/customers.jsonl`, validated by
  [customers.schema.json](customers.schema.json)
- `objects/suppliers.jsonl`, validated by
  [suppliers.schema.json](suppliers.schema.json)
- `objects/employees.jsonl`, validated by
  [employees.schema.json](employees.schema.json)
- `objects/departments.jsonl`, validated by
  [departments.schema.json](departments.schema.json)
- `objects/projects.jsonl`, validated by
  [projects.schema.json](projects.schema.json)
- `objects/products.jsonl`, validated by
  [products.schema.json](products.schema.json)
- `objects/orders.jsonl`, validated by
  [orders.schema.json](orders.schema.json)

An exporter emits a file if and only if it has records. Empty JSONL files are
invalid because absence expresses the same fact with less ambiguity and fewer
files.

Each line is one UTF-8 JSON object followed by LF. Blank lines, comments, a
top-level JSON array and byte-order marks are invalid. Records are ordered by
`id` using Unicode code-point order. IDs are strings so numeric and non-numeric
source identifiers survive unchanged.

Every schema field is present on every record. Use `null` for an unknown scalar
or object value. Do not omit keys, add vendor fields, or serialize empty values
as ambiguous empty strings.

Exporters include inactive or closed records when the source system can return
them and set `active` accordingly. Every non-null object reference must resolve
to a record in the corresponding JSONL file; an exporter must not drop a
historical customer, product, department or project merely because it is no
longer active.

Customer and supplier `id` values must equal the corresponding SAF-T
`CustomerID` or `SupplierID` whenever that party is represented in SAF-T.
Employee `id` must equal the SAF-T analysis ID when the employee is used as an
analysis dimension. Department and project `id` values follow the same rule.
Non-null project references use IDs from the corresponding customer,
department, employee or project object file.

Non-null order references use IDs from the corresponding customer, project,
department or product object file. Order lines are embedded because their
meaning, sequence, quantities and amounts are inseparable from the order.

The object files duplicate IDs and names from SAF-T only where needed to join
records and detect conflicts. They define application master data SAF-T does
not reliably preserve: active state, source numbers, project hierarchy, project
ownership and project dates. This gives importers one fixed schema across SAF-T
versions and vendor-specific generators. Importers must reject conflicting
non-null identifiers or names instead of silently choosing one representation.

### Why JSONL

JSONL is used because it:

- can be streamed one record at a time
- preserves strings, numbers, booleans, nulls and nested addresses without CSV
  conventions
- is readable by standard JSON libraries in essentially every language
- supports per-record validation and recovery
- needs no database engine, binary columnar reader or vendor software

CSV cannot represent the nested and nullable fields without additional rules.
SQLite and columnar formats are binary containers with a larger implementation
surface. A single JSON array requires reading and rewriting the whole file.
JSONL is the smallest practical common denominator for archival imports.

## 6. Extras

`extras` is an always-present manifest array. Each entry has exactly `path`,
`sha256` and `mediaType`, and every path begins with `extras/`. The standard does
not define the semantics or schema of these files. Exporters use this area for
source-system data or convenient renderings that are useful to a specific
importer but are not universal enough to become standard objects. Conforming
importers may ignore every extra. An extra must never replace required SAF-T,
object or source-document content.

Exporters may include auditor-friendly CSV views such as an annual trial balance
or holiday allowance list under `extras/reports/`. These are supplementary
snapshots with explicit dates and column headers; the ledger in SAF-T remains
authoritative. A holiday allowance list may summarize payroll details outside
SAF-T, so exporters should include the available payroll source documents as
well. Report files must be listed with checksums in `extras` like every other
supplementary file.

## 7. Packaging

The delivery container is outside this specification. Package paths must be
relative, must not contain `..`, and must not be symbolic links. Extracting an
archive must yield the same package contents and validation result as the
unarchived directory.

Media may be optimized before checksums are calculated. Signed, encrypted or
otherwise integrity-protected files must remain byte-identical.
