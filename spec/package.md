# SAF-T Extended 0.2

This document is normative.

## 1. Scope

SAF-T Extended is an archive and migration package, not a tax submission
format. Official SAF-T Financial XML remains unchanged and is the source of
truth for accounts, tax codes, dimensions and ledger transactions.

Version 0.2 adds only:

- a predictable customer, supplier and employee object layer
- original accounting documents
- document-to-SAF-T transaction links
- integrity checksums

## 2. Required layout

Every package has this layout:

```text
manifest.json
saf-t/<one or more XML files>
objects/customers.jsonl
objects/suppliers.jsonl
objects/employees.jsonl
documents/<source documents, optionally grouped by year>
```

`manifest.json`, at least one SAF-T XML file, and all three JSONL files are
required. A JSONL file with no records is a zero-byte file. `documents/` may be
absent when there are no documents.

No other files or directories are part of version 0.2. A package containing
unlisted files is invalid.

## 3. Manifest

The manifest follows [manifest.schema.json](manifest.schema.json). It contains:

- the format version and creation time
- exporter, source system, company and period
- every SAF-T file and its SHA-256 checksum
- checksums for the three fixed JSONL files
- every document, its media type, checksum, source identifiers and SAF-T links
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
system. A useful form is `vendor:type:value`, for example
`tripletex:document:1003779074`.

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

The document types in version 0.2 are intentionally small:

| Type | Meaning |
| --- | --- |
| `invoice` | Invoice source document, including EHF/Peppol XML or a retained PDF. |
| `credit-note` | Credit-note source document. |
| `receipt` | Receipt supporting a transaction. |
| `attachment` | Other voucher or accounting attachment. |
| `bank-document` | Bank statement, payment file or payment confirmation. |
| `payroll-document` | Payslip or other payroll accounting evidence. |

## 5. Objects

The required files are:

- `objects/customers.jsonl`, validated by
  [customers.schema.json](customers.schema.json)
- `objects/suppliers.jsonl`, validated by
  [suppliers.schema.json](suppliers.schema.json)
- `objects/employees.jsonl`, validated by
  [employees.schema.json](employees.schema.json)

Each line is one UTF-8 JSON object followed by LF. Blank lines, comments, a
top-level JSON array and byte-order marks are invalid. Records are ordered by
`id` using Unicode code-point order. IDs are strings so numeric and non-numeric
source identifiers survive unchanged.

Every schema field is present on every record. Use `null` for an unknown scalar
or object value. Do not omit keys, add vendor fields, or serialize empty values
as ambiguous empty strings.

Customer and supplier `id` values must equal the corresponding SAF-T
`CustomerID` or `SupplierID` whenever that party is represented in SAF-T.
Employee `id` must equal the SAF-T analysis ID when the employee is used as an
analysis dimension.

The object files deliberately duplicate a small, stable subset of SAF-T master
data. This controlled duplication gives importers one fixed schema across SAF-T
versions and vendor-specific SAF-T generators. Importers must reject conflicting
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

## 6. Packaging

The transport form is a POSIX-compatible tar archive compressed with Zstandard
and named `*.tar.zst`. Paths must be relative, must not contain `..`, and must
not be symbolic links. The extracted package must validate identically to the
archive contents.

Media may be optimized before checksums are calculated. Signed, encrypted or
otherwise integrity-protected files must remain byte-identical.
