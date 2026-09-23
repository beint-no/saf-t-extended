# SAF-T Extended

SAF-T Extended is a small, vendor-neutral accounting archive format.

It combines four things:

1. official SAF-T Financial XML for the ledger
2. original accounting documents
3. small JSONL files for customers, suppliers, employees, departments,
   projects, products and sales orders
4. one manifest containing checksums, document-to-transaction links and any
   source documents the exporting system could not return

Version 0.4 defines exactly those seven portable object schemas. Exporters may
also include integrity-listed files under `extras/`; those files have no
standardized meaning and conforming importers may ignore them.

## Why this exists

SAF-T is the right interchange format for accounts, tax codes, dimensions and
ledger transactions. It is less suitable as a simple application import format
for operational master data and sales orders, and it does not carry the source
files behind the postings.

SAF-T Extended fills only those two gaps. It does not replace or modify SAF-T.

## Package

```text
manifest.json
saf-t/
objects/
  customers.jsonl    # when non-empty
  suppliers.jsonl    # when non-empty
  employees.jsonl    # when non-empty
  departments.jsonl  # when non-empty
  projects.jsonl     # when non-empty
  products.jsonl     # when non-empty
  orders.jsonl       # when non-empty
documents/
extras/              # optional, non-standard supplementary files
```

Each JSONL file is written and listed only when it has at least one record. Every
field defined by its schema is emitted for every record; an unknown value is
`null`. Documents are stored once and linked to exact SAF-T transactions in
`manifest.json` whenever the relationship is known. `missingDocuments` is also
always present and is an empty array when every discovered document was exported.

The normative rules are in [spec/package.md](spec/package.md). JSON Schemas are
in [`spec/`](spec/), and [`examples/minimal-package/`](examples/minimal-package/)
is a complete package that passes the validator:

```sh
python3 tools/validate-package.py examples/minimal-package
```

## Distribution

A package may be delivered as a directory or an archive. Its delivery container
is outside this specification; the extracted files must follow the same package
layout and validate identically. Media optimization does not change the logical
format.

## Implementer

[ReAI](https://reai.no) is the only listed implementer of version 0.4. See
[IMPLEMENTERS.md](IMPLEMENTERS.md).

## Design principles

- one canonical representation of each fact
- original evidence, not export-generated presentations
- fixed names and schemas instead of vendor conventions
- checksums and explicit transaction links
- formats that can be read without a database engine or proprietary software
- fail validation instead of silently accepting a partial or ambiguous package

New object types require a vendor-neutral schema and a demonstrated accounting
use case that cannot be represented by SAF-T, the existing JSONL objects or
source documents.

## Official sources

- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/
- https://github.com/Skatteetaten/saf-t
- https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/
- https://docs.peppol.eu/poacc/billing/3.0/bis/
