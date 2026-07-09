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
employees, migration metadata and archive requirements. Too many variants would
make it hard for vendors and importers to know what to implement.

The draft should therefore define one minimum:

- SAF-T XML
- all posting-related files available in the source system
- manifest links and checksums
- structured omissions

Everything else should be recommended, not required for the minimum.

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

### EHF/Peppol should be primary invoice evidence

If an invoice or credit note exists as EHF Billing 3.0 or Peppol BIS Billing
3.0 XML, the XML should be exported as the original evidence. A PDF should be a
rendering, not the only invoice file, unless the source system no longer has the
original XML.

### The example package is illustrative

The current example is useful for showing package shape and manifest links, but
it should eventually use a fully valid SAF-T sample based on official examples.

## Improvements to Add

### 1. Document type registry

Create a controlled list of document types, for example:

- `invoice`
- `credit-note`
- `invoice-rendering`
- `invoice-attachment`
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

When an invoice exists as EHF/Peppol XML, the package should include the
original XML, not only a PDF rendering. The PDF is useful for humans; the XML is
useful for verification, audit and migration.

Next improvements:

- validate UBL invoice and credit note roots
- extract and compare CustomizationID, ProfileID, invoice ID and issue date
- define how embedded EHF/Peppol attachments should be extracted
- decide whether EHF/Peppol XML should be validated with Schematron in a later
  validator version

### 4. Integrity and signing

SHA-256 checksums are a start. A stronger profile should define:

- package-level hash
- optional signing
- timestamping
- checksum file format
- rules for ZIP or TAR packaging

### 5. Privacy and purpose

The same package format may be used for archive, audit, migration or authority
requests. It should stay one package format, but it may still need
purpose-specific guidance for privacy and legal minimization:

- archive profile
- audit profile
- migration profile
- authority-request profile

Each purpose should state what personal data should normally be excluded.

### 6. Validation tooling

The repository should include a validator that checks:

- all referenced files exist
- checksums match
- file IDs are unique
- document types are registered
- linked file IDs exist
- EHF/Peppol invoice metadata matches the XML where practical
- completeness and known omissions are structured

### 7. Real-world test exports

The profile should be tested against exports from several accounting systems.
The purpose is not to publish customer data, but to discover which data is
actually available, missing or hard to map.

### 8. Vendor outreach

Accounting-system vendors should be invited to implement the minimum export and
to give feedback before the profile is treated as stable.

The outreach should emphasize:

- low implementation threshold
- good PR for early implementers
- customer trust and lower switching friction
- alignment with SAF-T, EHF and Peppol rather than a competing format
- a chance to shape the baseline before journalists, customers or authorities
  use it as a public comparison point

### 9. Governance

If vendors, accountants, auditors or authorities engage with the draft, the
repository needs a lightweight governance model:

- how changes are proposed
- how document types are added
- how incompatible changes are versioned
- how official SAF-T changes are incorporated

## Strongest Next Step

The next useful step is deeper EHF/Peppol validation plus a stricter document
type registry.

That turns the profile from a written proposal into something vendors can test
against and journalists/regulators can understand concretely.
