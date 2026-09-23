#!/usr/bin/env python3
"""Validate a SAF-T Extended 0.4 or 0.5 package without third-party dependencies."""

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
    "period", "safT", "objects", "documents", "extras", "missingDocuments",
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
DEPARTMENT_FIELDS = {"id", "number", "name", "active"}
PROJECT_FIELDS = {
    "id", "number", "name", "customerId", "departmentId",
    "managerEmployeeId", "parentProjectId", "startDate", "endDate", "active",
}
PRODUCT_FIELDS = {
    "id", "number", "name", "description", "unitCode", "currency",
    "salesPriceExcludingTax", "purchasePriceExcludingTax", "barcode",
    "stockItem", "active",
}
ORDER_FIELDS = {
    "id", "number", "customerId", "projectId", "departmentId", "orderDate",
    "deliveryDate", "currency", "status", "reference", "note",
    "paymentTermsDays", "deliveryAddress", "lines",
}
ORDER_LINE_FIELDS = {
    "id", "sequence", "productId", "description", "quantity", "unitCode",
    "unitPriceExcludingTax", "discountPercent", "amountExcludingTax",
    "taxAmount", "amountIncludingTax",
}
DRIVING_LOG_VEHICLE_FIELDS = {"id", "registrationNumber", "name", "accountingMode", "archived"}
DRIVING_LOG_TRIP_FIELDS = {
    "id", "vehicleId", "employeeId", "projectId", "date", "fromLocation",
    "toLocation", "purpose", "kilometers", "odometerStart", "odometerEnd",
    "accountingMode", "ratePerKilometer", "mileageAmount", "roadTollAmount",
    "transaction", "createdAt", "updatedAt", "deletedAt",
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
    prefixes = (prefix,) if isinstance(prefix, str) else prefix
    if pure.is_absolute() or ".." in pure.parts or not any(value.startswith(item) for item in prefixes):
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


def nullable_number(value):
    return value is None or (
        isinstance(value, (int, float)) and not isinstance(value, bool)
    )


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
    if row["currency"] is not None and not re.fullmatch(r"[A-Z]{3}", row["currency"]):
        errors.append(f"{location}.currency: must be an ISO 4217 code or null")
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
            except (TypeError, ValueError):
                errors.append(f"{location}.{field}: invalid ISO date")
    if not isinstance(row["active"], bool):
        errors.append(f"{location}.active: must be a boolean")
    validate_address(row["address"], f"{location}.address", errors)


def validate_department(row, location, errors):
    if not exact_fields(row, DEPARTMENT_FIELDS, location, errors):
        return
    if not isinstance(row["id"], str) or not row["id"]:
        errors.append(f"{location}.id: must be a non-empty string")
    if not nullable_string(row["number"]):
        errors.append(f"{location}.number: must be a string or null")
    if not isinstance(row["name"], str) or not row["name"]:
        errors.append(f"{location}.name: must be a non-empty string")
    if not isinstance(row["active"], bool):
        errors.append(f"{location}.active: must be a boolean")


def validate_project(row, location, errors):
    if not exact_fields(row, PROJECT_FIELDS, location, errors):
        return
    if not isinstance(row["id"], str) or not row["id"]:
        errors.append(f"{location}.id: must be a non-empty string")
    if not isinstance(row["name"], str) or not row["name"]:
        errors.append(f"{location}.name: must be a non-empty string")
    for field in PROJECT_FIELDS - {"id", "name", "active"}:
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    for field in ("startDate", "endDate"):
        if row[field] is not None:
            try:
                date.fromisoformat(row[field])
            except (TypeError, ValueError):
                errors.append(f"{location}.{field}: invalid ISO date")
    if row["parentProjectId"] == row["id"]:
        errors.append(f"{location}.parentProjectId: project cannot be its own parent")
    if not isinstance(row["active"], bool):
        errors.append(f"{location}.active: must be a boolean")


def validate_product(row, location, errors):
    if not exact_fields(row, PRODUCT_FIELDS, location, errors):
        return
    if not isinstance(row["id"], str) or not row["id"]:
        errors.append(f"{location}.id: must be a non-empty string")
    if not isinstance(row["name"], str) or not row["name"]:
        errors.append(f"{location}.name: must be a non-empty string")
    for field in {"number", "description", "unitCode", "currency", "barcode"}:
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    if row["currency"] is not None and not re.fullmatch(r"[A-Z]{3}", row["currency"]):
        errors.append(f"{location}.currency: must be an ISO 4217 code or null")
    for field in {"salesPriceExcludingTax", "purchasePriceExcludingTax"}:
        if not nullable_number(row[field]):
            errors.append(f"{location}.{field}: must be a number or null")
    for field in {"stockItem", "active"}:
        if not isinstance(row[field], bool):
            errors.append(f"{location}.{field}: must be a boolean")


def validate_order(row, location, errors):
    if not exact_fields(row, ORDER_FIELDS, location, errors):
        return
    for field in {"id", "number"}:
        if not isinstance(row[field], str) or not row[field]:
            errors.append(f"{location}.{field}: must be a non-empty string")
    for field in {"customerId", "projectId", "departmentId", "reference", "note"}:
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    for field in {"orderDate", "deliveryDate"}:
        if row[field] is not None:
            try:
                date.fromisoformat(row[field])
            except (TypeError, ValueError):
                errors.append(f"{location}.{field}: invalid ISO date")
    if not nullable_string(row["currency"]) or (
        row["currency"] is not None
        and not re.fullmatch(r"[A-Z]{3}", row["currency"])
    ):
        errors.append(f"{location}.currency: must be an ISO 4217 code or null")
    if row["status"] not in {"open", "closed", "cancelled", "unknown"}:
        errors.append(f"{location}.status: invalid value")
    days = row["paymentTermsDays"]
    if days is not None and (
        not isinstance(days, int) or isinstance(days, bool) or days < 0
    ):
        errors.append(
            f"{location}.paymentTermsDays: must be a non-negative integer or null"
        )
    validate_address(row["deliveryAddress"], f"{location}.deliveryAddress", errors)
    if not isinstance(row["lines"], list):
        errors.append(f"{location}.lines: must be an array")
        return
    line_ids = []
    sequences = []
    for index, line in enumerate(row["lines"], 1):
        line_location = f"{location}.lines[{index}]"
        if not exact_fields(line, ORDER_LINE_FIELDS, line_location, errors):
            continue
        if not isinstance(line["id"], str) or not line["id"]:
            errors.append(f"{line_location}.id: must be a non-empty string")
        else:
            line_ids.append(line["id"])
        if (
            not isinstance(line["sequence"], int)
            or isinstance(line["sequence"], bool)
            or line["sequence"] < 0
        ):
            errors.append(f"{line_location}.sequence: must be a non-negative integer")
        else:
            sequences.append(line["sequence"])
        if not nullable_string(line["productId"]):
            errors.append(f"{line_location}.productId: must be a string or null")
        if not isinstance(line["description"], str) or not line["description"]:
            errors.append(f"{line_location}.description: must be a non-empty string")
        if not nullable_string(line["unitCode"]):
            errors.append(f"{line_location}.unitCode: must be a string or null")
        for field in {
            "quantity", "unitPriceExcludingTax", "discountPercent",
            "amountExcludingTax", "taxAmount", "amountIncludingTax",
        }:
            if not nullable_number(line[field]) or (
                field == "quantity" and line[field] is None
            ):
                errors.append(f"{line_location}.{field}: must be a number"
                              if field == "quantity"
                              else f"{line_location}.{field}: must be a number or null")
        discount = line["discountPercent"]
        if discount is not None and not 0 <= discount <= 100:
            errors.append(f"{line_location}.discountPercent: must be between 0 and 100")
    if len(line_ids) != len(set(line_ids)):
        errors.append(f"{location}.lines: duplicate id")
    if sequences != sorted(sequences):
        errors.append(f"{location}.lines: must be ordered by sequence")


def validate_driving_log_vehicle(row, location, errors):
    if not exact_fields(row, DRIVING_LOG_VEHICLE_FIELDS, location, errors):
        return
    for field in ("id", "registrationNumber", "name"):
        if not isinstance(row[field], str) or not row[field]:
            errors.append(f"{location}.{field}: must be a non-empty string")
    if row["accountingMode"] not in {"mileage-allowance", "log-only"}:
        errors.append(f"{location}.accountingMode: invalid value")
    if not isinstance(row["archived"], bool):
        errors.append(f"{location}.archived: must be a boolean")


def validate_driving_log_trip(row, location, errors):
    if not exact_fields(row, DRIVING_LOG_TRIP_FIELDS, location, errors):
        return
    for field in ("id", "fromLocation", "toLocation", "purpose"):
        if not isinstance(row[field], str) or not row[field]:
            errors.append(f"{location}.{field}: must be a non-empty string")
    for field in ("vehicleId", "employeeId", "projectId"):
        if not nullable_string(row[field]):
            errors.append(f"{location}.{field}: must be a string or null")
    try:
        date.fromisoformat(row["date"])
    except (TypeError, ValueError):
        errors.append(f"{location}.date: invalid ISO date")
    if row["accountingMode"] not in {"mileage-allowance", "log-only"}:
        errors.append(f"{location}.accountingMode: invalid value")
    for field in ("kilometers", "ratePerKilometer", "mileageAmount", "roadTollAmount"):
        value = row[field]
        if not nullable_number(value) or value is None or value < 0 or (field == "kilometers" and value == 0):
            errors.append(f"{location}.{field}: must be a positive number" if field == "kilometers"
                          else f"{location}.{field}: must be a non-negative number")
    start, end = row["odometerStart"], row["odometerEnd"]
    if (start is None) != (end is None) or not nullable_number(start) or not nullable_number(end):
        errors.append(f"{location}: odometerStart and odometerEnd must both be numbers or null")
    elif start is not None and (start < 0 or end <= start):
        errors.append(f"{location}: invalid odometer range")
    for field in ("createdAt", "updatedAt", "deletedAt"):
        value = row[field]
        if value is None and field == "deletedAt":
            continue
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError):
            errors.append(f"{location}.{field}: invalid ISO date-time")


def validate_jsonl(path, validator, errors):
    try:
        body = path.read_bytes()
        if body.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{path}: UTF-8 byte-order mark is not allowed")
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: invalid UTF-8: {exc}")
        return []
    if not text:
        errors.append(f"{path}: empty JSONL files must be omitted")
        return []
    if text and not text.endswith("\n"):
        errors.append(f"{path}: final record must end with LF")
    ids = []
    rows = []
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
            rows.append(row)
    if ids != sorted(ids):
        errors.append(f"{path}: records must be sorted by id")
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate id")
    return rows


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


def validate_transaction_reference(reference, location, saf_t_indexes, errors):
    fields = {"safTFile", "journalId", "transactionId", "recordIds"}
    if not exact_fields(reference, fields, location, errors):
        return
    if not isinstance(reference["safTFile"], str) or not isinstance(reference["journalId"], str) or not isinstance(reference["transactionId"], str):
        errors.append(f"{location}: SAF-T reference identifiers must be strings")
        return
    record_ids = reference["recordIds"]
    if not isinstance(record_ids, list) or any(not isinstance(value, str) for value in record_ids):
        errors.append(f"{location}.recordIds: must be an array of strings")
        return
    candidates = saf_t_indexes.get(reference["safTFile"])
    if candidates is None:
        errors.append(f"{location}: unknown SAF-T file")
        return
    matching = [records for journal, transaction, records in candidates
                if (journal, transaction) == (reference["journalId"], reference["transactionId"])]
    if not matching:
        errors.append(f"{location}: transaction does not exist in SAF-T")
    elif not set(record_ids) <= set(matching[0]):
        errors.append(f"{location}: RecordID does not exist in transaction")


def validate_package(root):
    errors = []
    manifest_path = root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid or missing manifest.json: {exc}"]
    if not exact_fields(manifest, ROOT_FIELDS, "manifest", errors):
        return errors
    if manifest["format"] != "saf-t-extended" or manifest["version"] not in {"0.4", "0.5"}:
        errors.append("manifest: expected SAF-T Extended version 0.4 or 0.5")
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
            path = checked_file(root, item, "", location, listed, errors)
            if path is not None and (len(PurePosixPath(item["path"]).parts) != 1 or path.suffix != ".xml"):
                errors.append(f"{location}: SAF-T XML files must be at the package root")
            elif path is not None:
                saf_t_indexes[item["path"]] = saf_t_index(path, errors)

    objects = manifest["objects"]
    object_names = {
        "customers", "suppliers", "employees", "departments", "projects",
        "products", "orders",
    }
    if manifest["version"] == "0.5":
        object_names.update({"driving-log-vehicles", "driving-log-trips"})
    if not isinstance(objects, dict):
        errors.append("manifest.objects: must be an object")
    else:
        unknown_objects = set(objects) - object_names
        if unknown_objects:
            errors.append(
                f"manifest.objects: unknown fields {', '.join(sorted(unknown_objects))}"
            )
        validators = {
            "customers": validate_party,
            "suppliers": validate_party,
            "employees": validate_employee,
            "departments": validate_department,
            "projects": validate_project,
            "products": validate_product,
            "orders": validate_order,
            "driving-log-vehicles": validate_driving_log_vehicle,
            "driving-log-trips": validate_driving_log_trip,
        }
        object_rows = {}
        for name in sorted(set(objects) & object_names):
            item = objects[name]
            location = f"manifest.objects.{name}"
            if not exact_fields(item, {"sha256"}, location, errors):
                continue
            wrapped = {"path": f"objects/{name}.jsonl", "sha256": item["sha256"]}
            path = checked_file(root, wrapped, "objects/", location, listed, errors)
            if path is not None:
                object_rows[name] = validate_jsonl(path, validators[name], errors)
        object_ids = {
            name: {row["id"] for row in rows}
            for name, rows in object_rows.items()
        }
        project_references = {
            "customerId": "customers",
            "departmentId": "departments",
            "managerEmployeeId": "employees",
            "parentProjectId": "projects",
        }
        for index, project in enumerate(object_rows.get("projects", []), 1):
            for field, target in project_references.items():
                value = project.get(field)
                if value is not None and value not in object_ids.get(target, set()):
                    errors.append(
                        f"projects.jsonl:{index}.{field}: unknown {target} id {value!r}"
                    )
        order_references = {
            "customerId": "customers",
            "projectId": "projects",
            "departmentId": "departments",
        }
        for index, order in enumerate(object_rows.get("orders", []), 1):
            for field, target in order_references.items():
                value = order.get(field)
                if value is not None and value not in object_ids.get(target, set()):
                    errors.append(
                        f"orders.jsonl:{index}.{field}: unknown {target} id {value!r}"
                    )
            for line_index, line in enumerate(order.get("lines", []), 1):
                product_id = line.get("productId") if isinstance(line, dict) else None
                if (
                    product_id is not None
                    and product_id not in object_ids.get("products", set())
                ):
                    errors.append(
                        f"orders.jsonl:{index}.lines[{line_index}].productId: "
                        f"unknown products id {product_id!r}"
                    )
        trip_references = {
            "vehicleId": "driving-log-vehicles",
            "employeeId": "employees",
            "projectId": "projects",
        }
        for index, trip in enumerate(object_rows.get("driving-log-trips", []), 1):
            if not DRIVING_LOG_TRIP_FIELDS <= set(trip):
                continue
            location = f"driving-log-trips.jsonl:{index}"
            for field, target in trip_references.items():
                value = trip[field]
                if value is not None and value not in object_ids.get(target, set()):
                    errors.append(f"{location}.{field}: unknown {target} id {value!r}")
            if trip["transaction"] is not None:
                validate_transaction_reference(trip["transaction"], f"{location}.transaction", saf_t_indexes, errors)

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
                validate_transaction_reference(reference, ref_location, saf_t_indexes, errors)

    extras = manifest["extras"]
    if not isinstance(extras, list):
        errors.append("manifest.extras: must be an array")
    else:
        for index, item in enumerate(extras):
            location = f"manifest.extras[{index}]"
            if not exact_fields(item, {"path", "sha256", "mediaType"}, location, errors):
                continue
            checked_file(root, item, ("reports/", "extras/"), location, listed, errors)
            if not isinstance(item["mediaType"], str) or not item["mediaType"]:
                errors.append(f"{location}.mediaType: must be a non-empty string")

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
