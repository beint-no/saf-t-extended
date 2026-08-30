# SAF-T Extended

SAF-T Extended is a small, vendor-neutral accounting archive format.

It combines four things:

1. official SAF-T Financial XML for the ledger
2. original accounting documents
3. `customers.jsonl`, `suppliers.jsonl`, and `employees.jsonl`
4. one manifest containing checksums, document-to-transaction links and any
   source documents the exporting system could not return

That is the complete version 0.2 format. It deliberately excludes generated
voucher PDFs, reports, duplicate CSV/SQLite views, raw vendor API dumps, and
additional object types.

## Why this exists

SAF-T is the right interchange format for accounts, tax codes, dimensions and
ledger transactions. It is less suitable as a simple application import format
for customer, supplier and employee records, and it does not carry the source
files behind the postings.

SAF-T Extended fills only those two gaps. It does not replace or modify SAF-T.

## Package

```text
manifest.json
saf-t/
objects/
  customers.jsonl
  suppliers.jsonl
  employees.jsonl
documents/
```

All three JSONL files are required, even when empty. Every field defined by their
schemas is emitted for every record; an unknown value is `null`. Documents are
stored once and linked to exact SAF-T transactions in `manifest.json` whenever
the relationship is known. `missingDocuments` is also always present and is an
empty array when every discovered document was exported.

The normative rules are in [spec/package.md](spec/package.md). JSON Schemas are
in [`spec/`](spec/), and [`examples/minimal-package/`](examples/minimal-package/)
is a complete package that passes the validator:

```sh
python3 tools/validate-package.py examples/minimal-package
```

## Distribution

A package is distributed as a Zstandard-compressed tar archive named
`*.tar.zst`. Extract it with:

```sh
zstd -dc export.tar.zst | tar -xf -
```

The uncompressed directory and the archive contain the same package. Compression
and media optimization do not change the logical format.

## Implementer

[ReAI](https://reai.no) is the only listed implementer of version 0.2. See
[IMPLEMENTERS.md](IMPLEMENTERS.md).

## Design principles

- one canonical representation of each fact
- original evidence, not export-generated presentations
- fixed names and schemas instead of vendor conventions
- checksums and explicit transaction links
- formats that can be read without a database engine or proprietary software
- fail validation instead of silently accepting a partial or ambiguous package

SAF-T Extended is based on practical export and import work. New object types
should be added only after an implementation demonstrates that SAF-T plus the
three required JSONL files cannot carry the needed data.

## Official sources

- https://www.skatteetaten.no/en/business-and-organisation/start-and-run/best-practices-accounting-and-cash-register-systems/saf-t-financial/
- https://github.com/Skatteetaten/saf-t
- https://anskaffelser.dev/postaward/g3/spec/current/billing-3.0/norway/
- https://docs.peppol.eu/poacc/billing/3.0/bis/
