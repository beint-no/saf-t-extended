# Naming and Scope

## Recommendation

Use **SAF-T Extended** as the public working name and `saf-t-extended` as the
repository slug.

Describe it precisely as:

> a SAF-T-based export package profile for accounting-data portability.

## Why Not SAD-T

SAD-T, "Standard Audit Directory for Tax", is clever but weaker for adoption:

- it introduces a new acronym before the problem is accepted
- it sounds like a competing tax standard
- it loses the immediate recognition of SAF-T
- "directory" describes an implementation detail rather than the user outcome

## Why Not a SAF-T XML Fork

The official SAF-T Financial schema is owned and maintained by the Norwegian Tax
Administration. A community profile should not fork the XML schema unless there
is no other way.

The better route is:

1. keep official SAF-T XML valid
2. define a package manifest around it
3. link files to SAF-T references
4. define stricter completeness expectations for optional SAF-T fields
5. use sidecar files only for objects SAF-T cannot represent well

## Scope Boundary

In scope:

- folder structure
- manifest schema
- checksums and package integrity
- linking PDFs and other documents to SAF-T references
- object sidecars for data SAF-T does not model
- profile rules for complete customer and supplier export through SAF-T

Out of scope for now:

- replacing Norwegian SAF-T Financial
- tax submission to Altinn
- vendor pricing, commercial terms or market allocation
- full payroll export
- a competing invoice XML format

## Public Positioning

Use language like:

> SAF-T Extended is an open package profile that keeps SAF-T as the ledger core
> and adds a practical manifest for attachments, documents and migration data.

Avoid language like:

> SAF-T is insufficient, so we made a new standard.

The strongest public argument is that SAF-T already has the right foundation,
but users need a complete, auditable export package around it.
