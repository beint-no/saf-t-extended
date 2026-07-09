#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


DOCUMENT_TYPES = {
    "invoice",
    "credit-note",
    "invoice-rendering",
    "invoice-attachment",
    "receipt",
    "voucher-attachment",
    "bank-statement",
    "payment-documentation",
    "customer-contract",
    "supplier-contract",
    "engagement-letter",
    "kyc-document",
    "correspondence",
    "board-document",
    "system-report",
    "import-log",
    "export-log",
    "employee-document",
    "project-document",
    "department-document",
}

COMPLETENESS_SCOPES = {
    "saf-t-xml",
    "electronic-invoices",
    "invoice-renderings",
    "invoice-attachments",
    "posting-attachments",
    "non-posting-documents",
    "master-data",
    "sidecar-objects",
}

COMPLETENESS_STATUSES = {"complete", "partial", "not_available", "not_applicable"}

OMISSION_REASONS = {
    "not_available_in_source_system",
    "not_exported_by_source_system",
    "outside_selected_period",
    "outside_selected_scope",
    "privacy_or_legal_exclusion",
    "unknown",
}

XML_MEDIA_TYPES = {"application/xml", "text/xml"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
FILE_ID = re.compile(r"^[A-Za-z0-9._:-]+$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_xml_media_type(media_type):
    return media_type in XML_MEDIA_TYPES or media_type.endswith("+xml")


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def first_text(root, name):
    for element in root.iter():
        if local_name(element.tag) == name and element.text:
            return element.text.strip()
    return ""


def first_text_inside(root, parent_name, child_name):
    for parent in root.iter():
        if local_name(parent.tag) != parent_name:
            continue
        for child in parent.iter():
            if local_name(child.tag) == child_name and child.text:
                return child.text.strip()
    return ""


def package_path(root, path_value, location, errors):
    if not isinstance(path_value, str) or not path_value:
        errors.append(f"{location}: missing path")
        return None
    if path_value.startswith("/") or ".." in Path(path_value).parts:
        errors.append(f"{location}: path must be relative and stay inside the package")
        return None
    return root / path_value


def validate_hash(root, item, errors, location):
    path = package_path(root, item.get("path"), location, errors)
    if path is None:
        return
    if not path.exists():
        errors.append(f"{location}: missing file {item.get('path')}")
        return
    expected = item.get("sha256")
    if not expected:
        errors.append(f"{location}: missing sha256")
        return
    if not SHA256.match(expected):
        errors.append(f"{location}: invalid sha256 format")
        return
    actual = sha256(path)
    if actual != expected:
        errors.append(f"{location}: sha256 mismatch for {item.get('path')}")


def validate_electronic_invoice(root, item, errors, warnings, location):
    path = package_path(root, item.get("path"), location, errors)
    if path is None or not path.exists():
        return

    metadata = item.get("electronicInvoice")
    if not isinstance(metadata, dict):
        errors.append(f"{location}: invoice and credit-note files must include electronicInvoice metadata")
        return

    media_type = item.get("mediaType", "")
    if not is_xml_media_type(media_type):
        errors.append(f"{location}: invoice and credit-note files must have an XML mediaType")

    try:
        root_element = ET.parse(path).getroot()
    except ET.ParseError as error:
        errors.append(f"{location}: XML parse error: {error}")
        return

    expected_root = "Invoice" if item.get("documentType") == "invoice" else "CreditNote"
    actual_root = local_name(root_element.tag)
    if actual_root != expected_root:
        errors.append(f"{location}: XML root is {actual_root}, expected {expected_root}")

    if metadata.get("ublDocumentType") != expected_root:
        errors.append(f"{location}: electronicInvoice.ublDocumentType must be {expected_root}")

    comparisons = {
        "invoiceId": first_text(root_element, "ID"),
        "issueDate": first_text(root_element, "IssueDate"),
        "customizationId": first_text(root_element, "CustomizationID"),
        "profileId": first_text(root_element, "ProfileID"),
        "sellerOrganizationNumber": first_text_inside(root_element, "AccountingSupplierParty", "CompanyID"),
        "buyerOrganizationNumber": first_text_inside(root_element, "AccountingCustomerParty", "CompanyID"),
    }
    for field, actual in comparisons.items():
        expected = metadata.get(field)
        if expected and actual and expected != actual:
            errors.append(f"{location}: electronicInvoice.{field} is {expected!r}, XML has {actual!r}")

    customization_id = metadata.get("customizationId", "")
    if metadata.get("standard") in {"ehf-billing-3.0", "peppol-bis-billing-3.0"}:
        if customization_id and "poacc:billing:3.0" not in customization_id:
            warnings.append(f"{location}: customizationId does not look like Peppol BIS Billing 3.0")


def validate_package_file(root, item, file_ids, errors, warnings, location):
    file_id = item.get("id")
    if not file_id:
        errors.append(f"{location}: missing id")
    elif not FILE_ID.match(file_id):
        errors.append(f"{location}: invalid id {file_id!r}")
    elif file_id in file_ids:
        errors.append(f"{location}: duplicate file id {file_id!r}")
    else:
        file_ids.add(file_id)

    validate_hash(root, item, errors, location)

    path = item.get("path", "")
    if not path.startswith("files/"):
        errors.append(f"{location}: path must start with files/")

    media_type = item.get("mediaType")
    if not media_type:
        errors.append(f"{location}: missing mediaType")

    document_type = item.get("documentType")
    if document_type not in DOCUMENT_TYPES:
        errors.append(f"{location}: unknown documentType {document_type!r}")

    if document_type in {"invoice", "credit-note"}:
        validate_electronic_invoice(root, item, errors, warnings, location)

    if document_type == "invoice-rendering":
        if media_type != "application/pdf":
            errors.append(f"{location}: invoice-rendering must use mediaType application/pdf")
        if not item.get("relatedFileIds"):
            errors.append(f"{location}: invoice-rendering must link to the original invoice with relatedFileIds")

    if document_type == "invoice-attachment":
        if not item.get("extractedFromFileId") and not item.get("relatedFileIds"):
            errors.append(f"{location}: invoice-attachment must use extractedFromFileId or relatedFileIds")


def validate_references(manifest, errors):
    file_ids = {item["id"] for item in manifest.get("files", []) if "id" in item}
    for index, item in enumerate(manifest.get("files", [])):
        location = f"files[{index}]"
        for related_id in item.get("relatedFileIds", []):
            if related_id not in file_ids:
                errors.append(f"{location}: relatedFileIds references unknown file id {related_id!r}")
        extracted_from = item.get("extractedFromFileId")
        if extracted_from and extracted_from not in file_ids:
            errors.append(f"{location}: extractedFromFileId references unknown file id {extracted_from!r}")


def validate_completeness(manifest, errors):
    statements = manifest.get("completeness")
    if not isinstance(statements, list) or not statements:
        errors.append("manifest.completeness must contain at least one statement")
        return

    seen_scopes = set()
    for index, statement in enumerate(statements):
        location = f"completeness[{index}]"
        scope = statement.get("scope")
        status = statement.get("status")
        if scope not in COMPLETENESS_SCOPES:
            errors.append(f"{location}: unknown scope {scope!r}")
        elif scope in seen_scopes:
            errors.append(f"{location}: duplicate completeness scope {scope!r}")
        else:
            seen_scopes.add(scope)
        if status not in COMPLETENESS_STATUSES:
            errors.append(f"{location}: unknown status {status!r}")

    if "saf-t-xml" not in seen_scopes:
        errors.append("manifest.completeness must include scope saf-t-xml")
    if "electronic-invoices" not in seen_scopes:
        errors.append("manifest.completeness must include scope electronic-invoices")


def validate_known_omissions(manifest, errors):
    omissions = manifest.get("knownOmissions")
    if not isinstance(omissions, list):
        errors.append("manifest.knownOmissions must be an array")
        return

    for index, omission in enumerate(omissions):
        location = f"knownOmissions[{index}]"
        if not isinstance(omission, dict):
            errors.append(f"{location}: omission must be an object")
            continue
        if omission.get("scope") not in COMPLETENESS_SCOPES:
            errors.append(f"{location}: unknown scope {omission.get('scope')!r}")
        if omission.get("reason") not in OMISSION_REASONS:
            errors.append(f"{location}: unknown reason {omission.get('reason')!r}")


def validate_listed_files(root, manifest, errors):
    listed = set()
    listed.update(item.get("path", "") for item in manifest.get("safTFiles", []))
    listed.update(item.get("path", "") for item in manifest.get("files", []))
    listed.update(item.get("path", "") for item in manifest.get("objectFiles", []))
    for directory in ("saf-t", "files", "objects"):
        base = root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            relative = path.relative_to(root).as_posix()
            if relative not in listed:
                errors.append(f"unlisted package file: {relative}")


def validate_package(root):
    errors = []
    warnings = []
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        return ["missing manifest.json"], warnings

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as error:
        return [f"manifest.json is not valid JSON: {error}"], warnings

    if manifest.get("profile") != "saf-t-extended-package":
        errors.append("manifest.profile must be saf-t-extended-package")

    if not manifest.get("profileVersion"):
        errors.append("manifest.profileVersion is required")

    saf_t_files = manifest.get("safTFiles")
    if not isinstance(saf_t_files, list) or not saf_t_files:
        errors.append("manifest.safTFiles must contain at least one SAF-T XML file")
    else:
        for index, item in enumerate(saf_t_files):
            validate_hash(root, item, errors, f"safTFiles[{index}]")
            path = item.get("path", "")
            if not path.startswith("saf-t/"):
                errors.append(f"safTFiles[{index}]: path must start with saf-t/")

    file_ids = set()
    for index, item in enumerate(manifest.get("files", [])):
        validate_package_file(root, item, file_ids, errors, warnings, f"files[{index}]")

    for index, item in enumerate(manifest.get("objectFiles", [])):
        validate_hash(root, item, errors, f"objectFiles[{index}]")
        path = item.get("path", "")
        if not path.startswith("objects/"):
            errors.append(f"objectFiles[{index}]: path must start with objects/")

    validate_references(manifest, errors)
    validate_completeness(manifest, errors)
    validate_known_omissions(manifest, errors)
    validate_listed_files(root, manifest, errors)

    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    args = parser.parse_args()

    root = args.package_dir.resolve()
    errors, warnings = validate_package(root)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {root}")


if __name__ == "__main__":
    main()
