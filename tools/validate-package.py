#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


CONFORMANCE_LEVELS = {"core", "complete-archive", "migration"}

DOCUMENT_TYPES = {
    "purchase-invoice",
    "sales-invoice",
    "receipt",
    "voucher-attachment",
    "bank-statement",
    "payment-documentation",
    "ehf-invoice",
    "invoice-rendering",
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

EXTENSION_DOCUMENT_TYPE = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}:[a-z0-9][a-z0-9-]*$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_document_type(value, errors, location):
    if value in DOCUMENT_TYPES:
        return
    if EXTENSION_DOCUMENT_TYPE.match(value):
        return
    errors.append(f"{location}: unknown documentType {value!r}")


def validate_file(root, item, errors, location):
    path_value = item.get("path")
    if not path_value:
        errors.append(f"{location}: missing path")
        return
    path = root / path_value
    if not path.exists():
        errors.append(f"{location}: missing file {path_value}")
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
        errors.append(f"{location}: sha256 mismatch for {path_value}")


def validate_package(root):
    errors = []
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        return ["missing manifest.json"]

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as error:
        return [f"manifest.json is not valid JSON: {error}"]

    if manifest.get("profile") != "saf-t-extended-package":
        errors.append("manifest.profile must be saf-t-extended-package")

    level = manifest.get("conformanceLevel")
    if level not in CONFORMANCE_LEVELS:
        errors.append("manifest.conformanceLevel must be core, complete-archive or migration")

    saf_t_files = manifest.get("safTFiles")
    if not isinstance(saf_t_files, list) or not saf_t_files:
        errors.append("manifest.safTFiles must contain at least one SAF-T XML file")
    else:
        for index, item in enumerate(saf_t_files):
            validate_file(root, item, errors, f"safTFiles[{index}]")
            path = item.get("path", "")
            if not path.startswith("saf-t/"):
                errors.append(f"safTFiles[{index}]: path must start with saf-t/")

    for index, item in enumerate(manifest.get("files", [])):
        validate_file(root, item, errors, f"files[{index}]")
        path = item.get("path", "")
        if not path.startswith("files/"):
            errors.append(f"files[{index}]: path must start with files/")
        document_type = item.get("documentType")
        if document_type:
            validate_document_type(document_type, errors, f"files[{index}]")
        else:
            errors.append(f"files[{index}]: missing documentType")

    for index, item in enumerate(manifest.get("objectFiles", [])):
        validate_file(root, item, errors, f"objectFiles[{index}]")
        path = item.get("path", "")
        if not path.startswith("objects/"):
            errors.append(f"objectFiles[{index}]: path must start with objects/")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package_dir", type=Path)
    args = parser.parse_args()

    root = args.package_dir.resolve()
    errors = validate_package(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {root}")


if __name__ == "__main__":
    main()
