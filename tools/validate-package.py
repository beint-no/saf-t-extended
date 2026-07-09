#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
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
    "posting-related-documents",
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

SHA256 = re.compile(r"^[a-f0-9]{64}$")
FILE_ID = re.compile(r"^[A-Za-z0-9._:-]+$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def validate_package_file(root, item, file_ids, errors, location):
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

    if document_type == "invoice-rendering" and media_type != "application/pdf":
        errors.append(f"{location}: invoice-rendering should use mediaType application/pdf")


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
    if "posting-related-documents" not in seen_scopes:
        errors.append("manifest.completeness must include scope posting-related-documents")

    omission_scopes = {omission.get("scope") for omission in manifest.get("knownOmissions", []) if isinstance(omission, dict)}
    for statement in statements:
        if statement.get("status") in {"partial", "not_available"} and statement.get("scope") not in omission_scopes:
            errors.append(
                f"manifest.completeness scope {statement.get('scope')!r} is {statement.get('status')!r} "
                "but knownOmissions has no matching scope"
            )


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
        validate_package_file(root, item, file_ids, errors, f"files[{index}]")

    for index, item in enumerate(manifest.get("objectFiles", [])):
        validate_hash(root, item, errors, f"objectFiles[{index}]")
        path = item.get("path", "")
        if not path.startswith("objects/"):
            errors.append(f"objectFiles[{index}]: path must start with objects/")

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
