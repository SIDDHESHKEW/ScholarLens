import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline.acquisition.csv_adapter import SOURCE_COLUMNS, SENTINELS


def inspect(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
    headers = reader.fieldnames or []
    invalid_urls = []
    for row_number, row in enumerate(rows, start=2):
        for field in ("official_source_url", "application_url"):
            value = (row.get(field) or "").strip()
            parsed = urlparse(value)
            if value and (parsed.scheme not in {"http", "https"} or not parsed.netloc):
                invalid_urls.append({"row": row_number, "field": field, "value": value})
    names = Counter((row.get("scholarship_name") or "").strip().casefold() for row in rows)
    return {
        "path": str(path),
        "records": len(rows),
        "columns": len(headers),
        "headers": headers,
        "missing_headers": sorted(SOURCE_COLUMNS - set(headers)),
        "empty_values": {
            field: sum(not (row.get(field) or "").strip() for row in rows)
            for field in headers
        },
        "not_specified_values": {
            field: sum((row.get(field) or "").strip().casefold() in SENTINELS for row in rows)
            for field in headers
        },
        "duplicate_name_rows": sum(count - 1 for count in names.values() if count > 1),
        "invalid_urls": invalid_urls,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect a scholarship CSV without modifying it")
    parser.add_argument("path", type=Path)
    print(json.dumps(inspect(parser.parse_args().path), indent=2))


if __name__ == "__main__":
    main()