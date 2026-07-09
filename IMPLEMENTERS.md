# Implementers

Accounting-system vendors can be listed here after showing that their export
supports the minimum valid export.

Minimum support means:

1. official SAF-T Financial XML for the selected period and scope
2. all posting-related files available in the source system for that selection
3. a manifest with file paths, document types, media types and SHA-256 checksums
4. structured omissions for posting-related files that cannot be exported

A vendor can demonstrate support with a sample package that passes
`tools/validate-package.py`.

| System | Vendor | Status | Notes |
| --- | --- | --- | --- |
