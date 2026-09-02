# Project history

## Origin

SAF-T Extended grew out of a practical data-portability problem observed during
accounting-system migrations in Norway. Official SAF-T Financial is well suited
to ledger and tax data, but a system change can also require source documents,
stable document-to-transaction links and operational records that are not
consistently represented in the official export.

In July 2026, ReAI asked the Norwegian Competition Authority to assess whether
friction in exporting complete accounting records from large accounting systems,
particularly Visma and Tripletex, could create harmful switching costs. This was
a request for assessment, not a finding that any supplier had broken the law.
The authority had not announced a conclusion when this history was written.

The practical question behind both the case and this repository is narrower:
can a business obtain a complete, understandable and machine-readable archive
of its own accounting records without a manual extraction project or continued
paid access to the old system?

## From case to specification

The initial work identified four parts that can be packaged without changing
official SAF-T Financial:

1. the official SAF-T XML for the ledger
2. original invoices, receipts and accounting attachments
3. small vendor-neutral object files for operational master data
4. a manifest with checksums, document links and an explicit list of missing
   documents

That model became SAF-T Extended. The project is an open implementation proposal,
not an official Norwegian standard and not a replacement for SAF-T. Its purpose
is to make the remaining export surface small, testable and implementable by
different accounting-system suppliers.

Tripletex later responded publicly that today's SAF-T does not cover all the
information in a modern accounting system and supported further common
standards. That point of agreement helped move the work from criticism of one
supplier toward a concrete, vendor-neutral package specification.

## Public chronology

- **3 July 2026:** ReAI sent the original submission to the Norwegian Competition
  Authority.
- **4 July 2026:** ReAI published its position and proposed a complete export
  package for accounting data.
- **July 2026:** Computerworld covered the submission and published Tripletex's
  response about common standards.
- **August 2026:** The proposal was shared with accounting-system suppliers and
  standards stakeholders. Standard Norge routed it to the relevant team, and
  PowerOffice said it would assess the proposal internally. Neither response was
  an adoption commitment.
- **18 August 2026:** Kode24 published a reader contribution about practical
  portability together with a response from Tripletex.
- **20 August 2026:** ReAI asked the Ministry of Finance to include complete,
  machine-readable exports in the Directorate of Taxes' assessment of possible
  requirements for accounting-system suppliers.
- **24 August 2026:** Anskaffelser24 published a procurement-focused contribution
  describing five questions buyers can use to test whether they can leave an IT
  supplier with usable data.
- **25 August 2026:** The Ministry of Finance forwarded ReAI's input to the
  Directorate of Taxes for assessment and possible follow-up. The forwarding was
  procedural and did not constitute endorsement.

## Evidence model

The original case file used the following evidence checklist. It remains useful
when evaluating this format or documenting a migration:

- record the number of export steps and whether several separate exports are
  required
- verify whether original attachments are included and linked to the correct
  transactions
- verify whether customers, suppliers, open items and other migration-relevant
  records are machine-readable
- document whether continued read-only access to the old system is needed
- use anonymized migration examples to record time spent, missing data and manual
  cleanup
- test the exported package with an independent validator and, ideally, a second
  accounting system

The issue is practical completeness, not whether a product has any export
function. Public descriptions should not say that Tripletex has no export, and
should not allege a legal violation without an authoritative finding. The same
portable-export expectation should apply to ReAI and every other implementer.

## Public references

- [ReAI's original position and Competition Authority submission](https://reai.no/pressemelding/visma-tripletex-klages-inn-til-konkurransetilsynet-for-dataeksport/)
- [Computerworld: ReAI asks the Competition Authority to assess Visma and Tripletex](https://www.cw.no/dataportabilitet-konkurransetilsynet-reai/reai-klager-visma-og-tripletex-inn-til-konkurransetilsynet/2456798)
- [Computerworld: Tripletex responds that common standards are the way forward](https://www.cw.no/dataportabilitet-reai-regnskapssystemer/tripletex-svarer-reai-felles-standarder-er-veien-videre/2456815)
- [Kode24: reader contribution and Tripletex response](https://www.kode24.no/artikkel/klager-inn-tripletex-laser-inn-kundene/269564)
- [Anskaffelser24: data export as part of an IT procurement](https://anskaffelser24.no/2026/08/24/svak-dataeksport-kan-gi-sittende-leverandor-et-skjult-forsprang-i-neste-it-anskaffelse/)
