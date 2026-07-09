# Roadmap

## Near Term

- test the minimum export against real accounting systems
- improve the validator for package integrity and completeness checks
- define a simple public proof checklist for compliant implementations
- list vendors that implement the minimum export
- refine the document type registry based on real exports

## Later

- recommended sidecar formats for employees, projects and migration metadata
- guidance for non-posting documents such as contracts, KYC/AML files and
  engagement letters
- package signing and timestamping
- ZIP or TAR packaging rules
- optional open customer and supplier item guidance if SAF-T is not sufficient
  in practice

## Vendor Participation

The first implementation target is the minimum valid export: SAF-T XML plus all
posting-related files available in the source system, listed in a manifest with
checksums.

Vendors that demonstrate this minimum can be listed publicly as implementers.
Feedback from real implementations should shape the next version before optional
sidecar formats become more detailed.
