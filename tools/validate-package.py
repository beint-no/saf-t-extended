#!/usr/bin/env python3
"""Validate a SAF-T Extended 0.2 package without third-party dependencies."""

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree


SHA256 = re.compile(r"^[a-f0-9]{64}$")
ROOT_FIELDS = {
    "format", "version", "createdAt", "exporter", "sourceSystem", "company",
    "period", "safT", "objects", "documents", "missingDocuments",
}
PARTY_FIELDS = {
    "id", "number", "name", "type", "organizationNumber", "vatNumber",
    "email", "phone", "invoiceEmail", "currency", "paymentTermsDays",
    "bankAccount", "iban", "bic", "address", "deliveryAddress", "active",
}
EMPLOYEE_FIELDS = {
    "id", "number", "name", "firstName", "lastName", "email", "phone",
    "address", "employmentStartDate", "employmentEndDate", "active",
}
ADDRESS_FIELDS = {"line1", "line2", "postalCode", "city", "region", "countryCode"}
DOCUMENT_TYPES = {
    "invoice", "credit-note", "receipt", "attachment", "bank-document",
    "payroll-document",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_fields(value, expected, location, errors):
    if not isinstance(value, dict):
        errors.append(f"{location}: must be an object")
        return False
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        errors.append(f"{location}: missing fields {', '.join(missing)}")
    if extra:
        errors.append(f"{location}: unknown fields {', '.join(extra)}")
    return not missing and not extra


def package_path(root, value, prefix, location, errors):
    if not isinstance(value, str) or not value:
        errors.append(f"{location}: missing path")
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or not value.startswith(prefix):
        errors.append(f"{location}: unsafe or misplaced path {value!r}")
        return None
    path = root.joinpath(*pure.parts)
    if not path.is_file() or path.is_symlink():
        errors.append(f"{location}: missing or unsafe file {value!r}")
        return None
    return path


def checked_file(root, item, prefix, location, listed, errors):
    path = package_path(root, item.get("path"), prefix, location, errors)
    value = item.get("path")
    if isinstance(value, str):
        if value in listed:
            errors.append(f"{location}: duplicate path {value!r}")
        listed.add(value)
    digest = item.get("sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        errors.append(f"{location}: invalid sha256")
    elif path is not None and sha256(path) != digest:
        errors.append(f"{location}: sha256 mismatch for {value}")
    return path


def nullable_string(value):
    return value is None or isinstance(value, str)


def validate_address(value, location, errors):
    if value is None:
        return
    if not exact_fields(value, ADDRESS_FIELDS, location, errors):
        return
    for field in ADDRESS_FIELDS:
        if not nullable_string(value[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    country = value["countryCode"]
    if country is not None and not re.fullmatch(r"[A-Z]{2}", country):
        errors.append(f"{location}.countryCode: must be an ISO 3166-1 alpha-2 code")


def validate_party(row, location, errors):
    if not exact_fields(row, PARTY_FIELDS, location, errors):
        return
    if not isinstance(row["id"], str) or not row["id"]:
        errors.append(f"{location}.id: must be a non-empty string")
    if not isinstance(row["name"], str) or not row["name"]:
        errors.append(f"{location}.name: must be a non-empty string")
    for field in PARTY_FIELDS - {"id", "name", "type", "paymentTermsDays", "address", "deliveryAddress", "active"}:
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    if row["type"] not in {"company", "person", "unknown"}:
        errors.append(f"{location}.type: invalid value")
    days = row["paymentTermsDays"]
    if days is not None and (not isinstance(days, int) or isinstance(days, bool) or days < 0):
        errors.append(f"{location}.paymentTermsDays: must be a non-negative integer or null")
    if not isinstance(row["active"], bool):
        errors.append(f"{location}.active: must be a boolean")
    validate_address(row["address"], f"{location}.address", errors)
    validate_address(row["deliveryAddress"], f"{location}.deliveryAddress", errors)


def validate_employee(row, location, errors):
    if not exact_fields(row, EMPLOYEE_FIELDS, location, errors):
        return
    if not isinstance(row["id"], str) or not row["id"]:
        errors.append(f"{location}.id: must be a non-empty string")
    if not isinstance(row["name"], str) or not row["name"]:
        errors.append(f"{location}.name: must be a non-empty string")
    for field in EMPLOYEE_FIELDS - {"id", "name", "address", "active"}:
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    for field in ("employmentStartDate", "employmentEndDate"):
        if row[field] is not None:
            try:
                date.fromisoformat(row[field])
            except ValueError:
                errors.append(f"{location}.{field}: invalid ISO date")
    if not isinstance(row["active"], bool):
        errors.append(f"{location}.active: must be a boolean")
    validate_address(row["address"], f"{location}.address", errors)


def validate_jsonl(path, validator, errors):
    try:
        body = path.read_bytes()
        if body.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path}: UTF-8 byte-order mark is not allowed")
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: invalid UTF-8: {exc}")
        return
    if text and not text.endswith("\n"):
        errors.append(f"{path}: final record must end with LF")
    ids = []
    for number, line in enumerate(text.splitlines(), 1):
        location = f"{path.name}:{number}"
        if not line:
            errors.append(f"{location}: blank lines are not allowed")
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{location}: invalid JSON: {exc}")
            continue
        validator(row, location, errors)
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            ids.append(row["id"])
    if ids != sorted(ids):
        errors.append(f"{path}: records must be sorted by id")
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate id")


def text_of(parent, name):
    for child in parent:
        if child.tag.rsplit("}", 1)[-1] == name:
            return (child.text or "").strip()
    return ""


def saf_t_index(path, errors):
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as exc:
        errors.append(f"{path}: invalid XML: {exc}")
        return set()
    values = set()
    for journal in root.iter():
        if journal.tag.rsplit("}", 1)[-1] != "Journal":
            continue
        journal_id = text_of(journal, "JournalID")
        for transaction in journal:
            if transaction.tag.rsplit("}", 1)[-1] != "Transaction":
                continue
            transaction_id = text_of(transaction, "TransactionID")
            record_ids = {
                text_of(line, "RecordID")
                for line in transaction
                if line.tag.rsplit("}", 1)[-1] == "Line"
            }
            values.add((journal_id, transaction_id, frozenset(record_ids - {""})))
    return values


def validate_package(root):
    errors = []
    manifest_path = root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid or missing manifest.json: {exc}"]
    if not exact_fields(manifest, ROOT_FIELDS, "manifest", errors):
        return errors
    if manifest["format"] != "saf-t-extended" or manifest["version"] != "0.2":
        errors.append("manifest: expected SAF-T Extended version 0.2")
    try:
        datetime.fromisoformat(str(manifest["createdAt"]).replace("Z", "+00:00"))
    except ValueError:
        errors.append("manifest.createdAt: invalid ISO date-time")
    exact_fields(manifest["exporter"], {"name", "url", "software"}, "manifest.exporter", errors)
    exact_fields(manifest["sourceSystem"], {"name", "version"}, "manifest.sourceSystem", errors)
    exact_fields(manifest["company"], {"name", "organizationNumber"}, "manifest.company", errors)
    if exact_fields(manifest["period"], {"start", "end"}, "manifest.period", errors):
        try:
            if date.fromisoformat(manifest["period"]["start"]) > date.fromisoformat(manifest["period"]["end"]):
                errors.append("manifest.period: start is after end")
        except (TypeError, ValueError):
            errors.append("manifest.period: invalid ISO dates")

    listed = set()
    saf_t = manifest["safT"]
    saf_t_indexes = {}
    if not isinstance(saf_t, list) or not saf_t:
        errors.append("manifest.safT: must contain at least one file")
    else:
        for index, item in enumerate(saf_t):
            location = f"manifest.safT[{index}]"
            if not exact_fields(item, {"path", "sha256", "version"}, location, errors):
                continue
            path = checked_file(root, item, "saf-t/", location, listed, errors)
            if path is not None and len(PurePosixPath(item["path"]).parts) != 2:
                errors.append(f"{location}: SAF-T files must be directly under saf-t/")
            if path is not None:
                saf_t_indexes[item["path"]] = saf_t_index(path, errors)

    objects = manifest["objects"]
    object_names = ("customers", "suppliers", "employees")
    if exact_fields(objects, set(object_names), "manifest.objects", errors):
        for name in object_names:
            item = objects[name]
            location = f"manifest.objects.{name}"
            if not exact_fields(item, {"sha256"}, location, errors):
                continue
            wrapped = {"path": f"objects/{name}.jsonl", "sha256": item["sha256"]}
            path = checked_file(root, wrapped, "objects/", location, listed, errors)
            if path is not None:
                validate_jsonl(path, validate_employee if name == "employees" else validate_party, errors)

    documents = manifest["documents"]
    document_hashes = set()
    source_ids = set()
    if not isinstance(documents, list):
        errors.append("manifest.documents: must be an array")
    else:
        fields = {"path", "sha256", "mediaType", "type", "sourceIds", "transactions"}
        for index, item in enumerate(documents):
            location = f"manifest.documents[{index}]"
            if not exact_fields(item, fields, location, errors):
                continue
            path = checked_file(root, item, "documents/", location, listed, errors)
            if path is not None and (not path.suffix or path.suffix.casefold() == ".bin"):
                errors.append(f"{location}: document needs a meaningful extension")
            if item["type"] not in DOCUMENT_TYPES:
                errors.append(f"{location}.type: invalid document type")
            if item["sha256"] in document_hashes:
                errors.append(f"{location}: duplicate document content must be stored once")
            document_hashes.add(item["sha256"])
            if not isinstance(item["sourceIds"], list) or any(not isinstance(value, str) or not value for value in item["sourceIds"]):
                errors.append(f"{location}.sourceIds: must be an array of non-empty strings")
            else:
                repeated = source_ids & set(item["sourceIds"])
                if repeated:
                    errors.append(f"{location}.sourceIds: reused identifiers {sorted(repeated)}")
                source_ids.update(item["sourceIds"])
            if not isinstance(item["transactions"], list):
                errors.append(f"{location}.transactions: must be an array")
                continue
            for ref_index, reference in enumerate(item["transactions"]):
                ref_location = f"{location}.transactions[{ref_index}]"
                ref_fields = {"safTFile", "journalId", "transactionId", "recordIds"}
                if not exact_fields(reference, ref_fields, ref_location, errors):
                    continue
                key = (reference["journalId"], reference["transactionId"])
                candidates = saf_t_indexes.get(reference["safTFile"])
                if candidates is None:
                    errors.append(f"{ref_location}: unknown SAF-T file")
                    continue
                matching = [records for journal, transaction, records in candidates if (journal, transaction) == key]
                if not matching:
                    errors.append(f"{ref_location}: transaction does not exist in SAF-T")
                elif not set(reference["recordIds"]) <= set(matching[0]):
                    errors.append(f"{ref_location}: RecordID does not exist in transaction")

    missing_documents = manifest["missingDocuments"]
    if not isinstance(missing_documents, list):
        errors.append("manifest.missingDocuments: must be an array")
    else:
        missing_ids = []
        for index, item in enumerate(missing_documents):
            location = f"manifest.missingDocuments[{index}]"
            if not exact_fields(item, {"sourceId", "reason"}, location, errors):
                continue
            if not isinstance(item["sourceId"], str) or not item["sourceId"]:
                errors.append(f"{location}.sourceId: must be a non-empty string")
            else:
                missing_ids.append(item["sourceId"])
            if item["reason"] not in {"not-found", "not-exportable"}:
                errors.append(f"{location}.reason: invalid value")
        if missing_ids != sorted(missing_ids):
            errors.append("manifest.missingDocuments: must be sorted by sourceId")
        if len(missing_ids) != len(set(missing_ids)):
            errors.append("manifest.missingDocuments: duplicate sourceId")

    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if actual != listed:
        for value in sorted(actual - listed):
            errors.append(f"unlisted package file: {value}")
        for value in sorted(listed - actual):
            errors.append(f"listed file is missing: {value}")
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
