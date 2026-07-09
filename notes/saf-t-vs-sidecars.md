# SAF-T vs Sidecar Object Files

## Recommendation

Use SAF-T as far as it goes, and use sidecar object files only for the parts it
does not model clearly.

## Why

Norwegian SAF-T Financial already supports:

- General ledger accounts
- Customer master data
- Supplier master data
- Tax tables
- Analysis dimensions
- Owners
- General ledger entries
- SourceDocuments structures in the schema, with official work underway to make
  the full format available from 2027

The official documentation also says optional elements that are available in the
same source should be included in the XML export. That gives SAF-T Extended an
important lever: we can define a stricter profile for completeness without
inventing a parallel customer/supplier format.

## Customers and Suppliers

Do not create mandatory `customers.jsonl` and `suppliers.jsonl` files for normal
master data.

Instead:

- require complete use of SAF-T `MasterFiles/Customers`
- require complete use of SAF-T `MasterFiles/Suppliers`
- require stable IDs that match posting lines
- require all available optional fields from the source system
- use sidecars only for extra non-SAF-T data, such as custom fields or document
  relations

## Employees

Use SAF-T `AnalysisTypeTable` and line-level `Analysis` for employee dimensions
where the accounting system uses employees as accounting dimensions.

Use `objects/employees.jsonl` only when employee master data is actually needed
for archive, audit or migration.

Do not include sensitive employee details by default.

## Documents

Documents should be package files, not XML extensions.

The manifest should link documents to SAF-T identifiers. This keeps the official
SAF-T XML valid and keeps binary files easy to inspect.

## Practical Rule

If the data is needed to understand the ledger, first ask:

1. Does official SAF-T already have a place for it?
2. Can it be expressed through a SAF-T identifier and a manifest link?
3. Is it a full object SAF-T does not model?

Only use sidecars for the third case.
