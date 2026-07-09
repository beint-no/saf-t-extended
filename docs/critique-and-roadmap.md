# Critique and Roadmap

## Current Critique

### The name can imply official status

"SAF-T Extended" is understandable, but it can sound like an official extension
to SAF-T. Public text should always describe this as a package profile around
official SAF-T, not as a replacement schema.

Possible future names:

- SAF-T Portable Package
- SAF-T Export Package Profile
- Accounting Export Package, SAF-T Profile

### The scope can become too broad

The profile touches ledger data, attachments, contracts, KYC documents,
employees, migration metadata and archive requirements. Without conformance
levels, it can become an impossible all-or-nothing standard.

The draft therefore separates Core, Complete Archive and Migration.

### Sidecars can become a dumping ground

If sidecar files are too easy to add, vendors may bypass SAF-T instead of using
official structures. The profile should be strict:

- SAF-T first
- manifest links second
- sidecars only where SAF-T cannot express the data clearly

### Employee data is high risk

Employee data can contain sensitive personal information and should not become a
general HR export by accident.

The profile should include only minimal employee sidecars, and only when needed
for accounting dimensions, audit, archive or migration.

### The example package is illustrative

The current example is useful for showing package shape and manifest links, but
it should eventually use a fully valid SAF-T sample based on official examples.

## Improvements to Add

### 1. Document type registry

Create a controlled list of document types, for example:

- `purchase-invoice`
- `sales-invoice`
- `receipt`
- `bank-statement`
- `payment-documentation`
- `customer-contract`
- `supplier-contract`
- `engagement-letter`
- `kyc-document`
- `correspondence`
- `system-report`
- `import-log`
- `export-log`

The registry should define which document types normally require SAF-T
references and which can be non-posting documents.

### 2. Open items profile

Open customer and supplier items are critical for migration. SAF-T has customer
and supplier balances, and SourceDocuments work may improve this, but migration
often needs a clear open-item view.

The draft should analyze whether open items can be represented sufficiently with
official SAF-T structures or whether a migration-only sidecar is needed.

### 3. EHF/Peppol preservation

When an invoice exists as EHF/Peppol XML, the package should probably include
the original XML, not only a PDF rendering. The PDF is useful for humans; the XML
is useful for verification and migration.

### 4. Integrity and signing

SHA-256 checksums are a start. A stronger profile should define:

- package-level hash
- optional signing
- timestamping
- checksum file format
- rules for ZIP or TAR packaging

### 5. Privacy profiles

The same package format may need different privacy profiles:

- archive profile
- audit profile
- migration profile
- authority-request profile

Each profile should state what personal data should normally be excluded.

### 6. Validation tooling

The repository should include a small validator that checks:

- `manifest.json` against the schema
- all referenced files exist
- checksums match
- SAF-T references have plausible identifiers
- known omissions are present for declared partial exports

### 7. Real-world test exports

The profile should be tested against exports from several accounting systems.
The purpose is not to publish customer data, but to discover which data is
actually available, missing or hard to map.

### 8. Governance

If vendors, accountants, auditors or authorities engage with the draft, the
repository needs a lightweight governance model:

- how changes are proposed
- how document types are added
- how incompatible changes are versioned
- how official SAF-T changes are incorporated

## Strongest Next Step

The next useful step is a validator plus a stricter document type registry.

That turns the profile from a written proposal into something vendors can test
against and journalists/regulators can understand concretely.
