"""Validate experience entries and convert them to JSON for the frontend.

Reads every Markdown file in content/entries/, checks its frontmatter against
the schema in content/README.md, and writes frontend/src/data/entries.json:
dated entries newest first, then projects (which have no dates) by scale.
All problems across all files are reported together, and nothing is written
unless every entry is valid.

Usage (from the repository root):
    uv run --project pipeline python pipeline/build_entries.py           # validate and write
    uv run --project pipeline python pipeline/build_entries.py --check   # validate only
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTENT_DIR = REPO_ROOT / "content" / "entries"
DEFAULT_OUTPUT = REPO_ROOT / "frontend" / "src" / "data" / "entries.json"

ENTRY_TYPES = ("project", "experience", "leadership", "other")
# Every type except project has a start and an end ("present" if ongoing).
DATED_TYPES = ("experience", "leadership", "other")
ONGOING = "present"
REQUIRED_FIELDS = ("id", "title", "type", "scale", "skills", "summary", "links")
DATE_FIELDS = ("start", "end")
ALLOWED_FIELDS = set(REQUIRED_FIELDS) | set(DATE_FIELDS)
LINK_FIELDS = {"label", "url"}

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
URL_PATTERN = re.compile(r"^https?://\S+$")
# Opening '---' on the first line, then everything up to the next line that is
# exactly '---' is frontmatter; the rest of the file is the body.
FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\r?\n(?P<front>.*?)^---[ \t]*$\r?\n?(?P<body>.*)\Z",
    re.DOTALL | re.MULTILINE,
)

Problem = tuple[str, str]  # (field, message)


def split_frontmatter(text: str) -> tuple[str, str] | None:
    """Return (frontmatter, body), or None if the file has no frontmatter block."""
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        return None
    return match.group("front"), match.group("body")


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _check_month(field: str, value: Any) -> Problem | None:
    if isinstance(value, (datetime.date, datetime.datetime)):
        return (field, 'is a full date; use a quoted year and month, e.g. "2025-06"')
    if not isinstance(value, str) or not MONTH_PATTERN.match(value):
        hint = f", or {ONGOING} if ongoing" if field == "end" else ""
        return (field, f'must be a year and month like "2025-06"{hint}')
    return None


def _check_dates(data: dict[str, Any], entry_type: Any) -> list[Problem]:
    """Projects have no dates; other types need a start and an end (or "present").

    If the type is missing or invalid, only the format of any dates is checked,
    so the type error isn't buried under follow-on date errors.
    """
    if entry_type == "project":
        return [
            (field, "projects don't have dates; delete this line")
            for field in DATE_FIELDS
            if field in data
        ]

    problems: list[Problem] = []
    required = entry_type in DATED_TYPES
    start, end = data.get("start"), data.get("end")

    start_problem = _check_month("start", start) if start is not None else None
    if start is None and required:
        problems.append(("start", f"required for {entry_type} entries"))
    elif start_problem:
        problems.append(start_problem)

    if end is None:
        if required:
            problems.append(("end", f'required for {entry_type} entries; use {ONGOING} if ongoing'))
    elif end != ONGOING:
        end_problem = _check_month("end", end)
        if end_problem:
            problems.append(end_problem)
        elif start is not None and start_problem is None and end < start:
            problems.append(("end", "is before start"))
    return problems


def validate_fields(data: dict[str, Any], file_stem: str) -> list[Problem]:
    """Check one entry's frontmatter. Returns every problem found."""
    problems: list[Problem] = []

    for field in sorted(set(data) - ALLOWED_FIELDS):
        allowed = ", ".join(REQUIRED_FIELDS + DATE_FIELDS)
        problems.append((field, f"unknown field (allowed: {allowed})"))

    for field in REQUIRED_FIELDS:
        if data.get(field) is None:
            problems.append((field, "required field is missing"))

    entry_id = data.get("id")
    if entry_id is not None:
        if not isinstance(entry_id, str) or not ID_PATTERN.match(entry_id):
            problems.append(("id", "must be lowercase words joined by hyphens, e.g. my-project"))
        elif entry_id != file_stem:
            problems.append(("id", f"must match the filename ({file_stem}.md)"))

    for field in ("title", "summary"):
        value = data.get(field)
        if value is not None and not _is_non_empty_string(value):
            problems.append((field, "must be non-empty text"))

    entry_type = data.get("type")
    if entry_type is not None and entry_type not in ENTRY_TYPES:
        problems.append(("type", f"must be one of: {', '.join(ENTRY_TYPES)}"))

    problems.extend(_check_dates(data, entry_type))

    scale = data.get("scale")
    if scale is not None and (
        isinstance(scale, bool) or not isinstance(scale, int) or not 1 <= scale <= 5
    ):
        problems.append(("scale", "must be a whole number from 1 to 5"))

    skills = data.get("skills")
    if skills is not None:
        if not isinstance(skills, list) or not skills:
            problems.append(("skills", "must be a non-empty list"))
        elif not all(_is_non_empty_string(skill) for skill in skills):
            problems.append(("skills", "every skill must be non-empty text"))
        elif len({skill.strip() for skill in skills}) != len(skills):
            problems.append(("skills", "contains a duplicate skill"))

    links = data.get("links")
    if links is not None:
        if not isinstance(links, list):
            problems.append(("links", "must be a list (use [] for none)"))
        else:
            urls: list[str] = []
            for index, link in enumerate(links, start=1):
                where = f"links[{index}]"
                if not isinstance(link, dict):
                    problems.append((where, "must have a label and a url"))
                    continue
                for key in sorted(set(link) - LINK_FIELDS):
                    problems.append((where, f"unknown field '{key}' (allowed: label, url)"))
                if not _is_non_empty_string(link.get("label")):
                    problems.append((where, "label must be non-empty text"))
                url = link.get("url")
                if not isinstance(url, str) or not URL_PATTERN.match(url):
                    problems.append((where, "url must start with http:// or https://"))
                else:
                    urls.append(url)
            if len(set(urls)) != len(urls):
                problems.append(("links", "contains a duplicate url"))

    return problems


def to_entry(data: dict[str, Any], body: str) -> dict[str, Any]:
    """Build the JSON shape for a validated entry, in a fixed field order."""
    entry: dict[str, Any] = {
        "id": data["id"],
        "title": data["title"].strip(),
        "type": data["type"],
    }
    for field in DATE_FIELDS:
        if field in data:
            entry[field] = data[field]
    entry["scale"] = data["scale"]
    entry["skills"] = [skill.strip() for skill in data["skills"]]
    entry["summary"] = data["summary"].strip()
    entry["links"] = [
        {"label": link["label"].strip(), "url": link["url"]} for link in data["links"]
    ]
    body = body.strip()
    if body:
        entry["body"] = body
    return entry


def parse_entry_file(path: Path) -> tuple[dict[str, Any] | None, list[Problem]]:
    """Parse and validate one file. Returns (entry, problems); entry is None if invalid."""
    text = path.read_text(encoding="utf-8-sig")
    parts = split_frontmatter(text)
    if parts is None:
        return None, [("file", "must start with a frontmatter block between '---' lines")]
    front, body = parts

    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as error:
        return None, [("file", "invalid YAML: " + " ".join(str(error).split()))]
    if not isinstance(data, dict):
        return None, [("file", "frontmatter must be a list of 'field: value' lines")]

    problems = validate_fields(data, path.stem)
    if problems:
        return None, problems
    return to_entry(data, body), []


def sort_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dated entries newest first (ties by id), then projects by scale, highest first."""
    dated = sorted(
        (entry for entry in entries if "start" in entry),
        key=lambda entry: (_descending(entry["start"]), entry["id"]),
    )
    undated = sorted(
        (entry for entry in entries if "start" not in entry),
        key=lambda entry: (-entry["scale"], entry["title"].lower(), entry["id"]),
    )
    return dated + undated


def _descending(month: str) -> tuple[int, int]:
    year, month_number = month.split("-")
    return (-int(year), -int(month_number))


def build_entries(content_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse every entry in content_dir. Returns (sorted entries, error lines)."""
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(content_dir.glob("*.md")):
        entry, problems = parse_entry_file(path)
        for field, message in problems:
            errors.append(f"{path.name}: {field}: {message}")
        if entry is not None:
            entries.append(entry)
    return sort_entries(entries), errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="validate only; do not write JSON")
    parser.add_argument("--content-dir", type=Path, default=DEFAULT_CONTENT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    if not args.content_dir.is_dir():
        print(f"Content folder not found: {args.content_dir}", file=sys.stderr)
        return 1

    entries, errors = build_entries(args.content_dir)
    if errors:
        print(f"Found {len(errors)} problem(s); nothing was written:", file=sys.stderr)
        for line in errors:
            print(f"  {line}", file=sys.stderr)
        return 1
    if not entries:
        print(f"Warning: no entries found in {args.content_dir}", file=sys.stderr)

    if args.check:
        print(f"All {len(entries)} entries are valid.")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(entries)} entries to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
