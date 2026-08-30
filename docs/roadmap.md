# Roadmap

Version 0.3 covers the master data already proven useful by real accounting
migrations: customers, suppliers, employees, departments and projects.

Candidates are ranked by the accounting state an importer would otherwise lose:

1. **Open receivable and payable items.** Highest priority. SAF-T can reproduce
   balances and postings but not reliably which invoice residuals remain open,
   their due dates, KID/payment references or collection/payment state. Prefer
   one small `open-items.jsonl` over complete invoice API dumps.
2. **Bank transactions and reconciliation state.** Useful for a mid-period
   cutover so an importer can continue matching without re-importing or losing
   the source bank-line identity. Standardize only after proving a minimal model
   across at least two source systems.
3. **Products.** Useful for operational continuity after migration, but not
   needed to reconstruct the books. Pricing, units, discounts, inventory and VAT
   defaults make a portable minimal schema less obvious, so keep this outside
   the core until an importer uses it.
4. **Contacts.** Potentially useful for customer and supplier communication, but
   secondary to accounting reconstruction and often duplicated by CRM data.
5. **Payroll operational state.** Employment, leave and year-to-date payroll can
   matter for a payroll-system cutover, but it is sensitive, jurisdiction-specific
   and broader than an accounting archive. It should be a separate profile if
   implemented.

Do not add accounts, VAT types, currencies, tax tables or fixed assets merely as
JSONL mirrors. SAF-T already standardizes those facts. Signing and encryption
belong to transport guidance and should not make the logical package conditional.

Before adding a candidate, demonstrate a real exporter and importer, define one
small vendor-neutral record schema, add it to the example and validator, and
emit its JSONL file only when it has records.
