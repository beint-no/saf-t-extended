# Roadmap

Version 0.2 intentionally stops at customers, suppliers and employees.

Before adding another object type:

1. demonstrate a real export and import that cannot be reconstructed from SAF-T,
   the three JSONL files and source documents
2. define one small vendor-neutral record schema
3. make the new file required in the next format version
4. add it to the example package and validator

Likely future work is open-item/payment state and projects, but neither is part
of 0.2. Signing and encryption belong to transport guidance and should not make
the logical package format conditional.
