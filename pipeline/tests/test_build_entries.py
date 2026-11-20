"""Tests for build_entries.py. All entries here are fake test data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import build_entries

TEMPLATE = Path(__file__).resolve().parents[2] / "content" / "entry-template.md"

# A dated entry (experience) and an undated one (project), both valid.
VALID_DATED = """\
id: test-entry
title: Test Entry
type: experience
start: "2024-01"
end: "2024-03"
scale: 2
skills: [Skill A, Skill B]
summary: Fake summary for testing.
links:
  - label: Example
    url: https://example.com
"""

VALID_PROJECT = """\
id: test-entry
title: Test Project
type: project
scale: 2
skills: [Skill A]
summary: Fake project for testing.
links: []
"""


def write_entry(folder: Path, name: str, frontmatter: str, body: str = "") -> Path:
    path = folder / f"{name}.md"
    path.write_text(f"---\n{frontmatter}---\n{body}", encoding="utf-8")
    return path


def replace_line(frontmatter: str, key: str, new_line: str | None) -> str:
    """Replace the line that starts with 'key:', remove it (None), or append new_line if absent."""
    lines, found = [], False
    for line in frontmatter.splitlines(keepends=True):
        if line.startswith(f"{key}:"):
            found = True
            if new_line is not None:
                lines.append(new_line + "\n")
        else:
            lines.append(line)
    if not found and new_line is not None:
        lines.append(new_line + "\n")
    return "".join(lines)


def problems_for(tmp_path: Path, frontmatter: str, name: str = "test-entry") -> list[str]:
    write_entry(tmp_path, name, frontmatter)
    _, errors = build_entries.build_entries(tmp_path)
    return errors


# --- Valid entries --------------------------------------------------------------


def test_valid_dated_entry_is_converted(tmp_path: Path) -> None:
    write_entry(tmp_path, "test-entry", VALID_DATED, "\nSome **body** text.\n\n")
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert entries == [
        {
            "id": "test-entry",
            "title": "Test Entry",
            "type": "experience",
            "start": "2024-01",
            "end": "2024-03",
            "scale": 2,
            "skills": ["Skill A", "Skill B"],
            "summary": "Fake summary for testing.",
            "links": [{"label": "Example", "url": "https://example.com"}],
            "body": "Some **body** text.",
        }
    ]


def test_project_without_dates_is_valid(tmp_path: Path) -> None:
    write_entry(tmp_path, "test-entry", VALID_PROJECT)
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert "start" not in entries[0] and "end" not in entries[0]


@pytest.mark.parametrize("entry_type", ["experience", "leadership", "other"])
def test_ongoing_entry_uses_present(tmp_path: Path, entry_type: str) -> None:
    frontmatter = replace_line(VALID_DATED, "type", f"type: {entry_type}")
    write_entry(tmp_path, "test-entry", replace_line(frontmatter, "end", "end: present"))
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert entries[0]["end"] == "present"


def test_empty_body_is_omitted(tmp_path: Path) -> None:
    write_entry(tmp_path, "test-entry", VALID_DATED, "  \n")
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert "body" not in entries[0]


def test_unquoted_month_and_empty_links_are_allowed(tmp_path: Path) -> None:
    frontmatter = replace_line(VALID_DATED, "start", "start: 2024-01")
    frontmatter = frontmatter.split("links:")[0] + "links: []\n"
    assert problems_for(tmp_path, frontmatter) == []


def test_sort_dated_newest_first_then_projects_by_scale(tmp_path: Path) -> None:
    dated = [("b-old", "2020-05"), ("c-new", "2024-02"), ("a-new", "2024-02"), ("d-mid", "2023-11")]
    for name, start in dated:
        frontmatter = replace_line(VALID_DATED, "id", f"id: {name}")
        frontmatter = replace_line(frontmatter, "start", f'start: "{start}"')
        frontmatter = replace_line(frontmatter, "end", "end: present")
        write_entry(tmp_path, name, frontmatter)
    projects = [("p-small", 1, "Zeta"), ("p-big", 4, "Beta"), ("p-big-2", 4, "alpha")]
    for name, scale, title in projects:
        frontmatter = replace_line(VALID_PROJECT, "id", f"id: {name}")
        frontmatter = replace_line(frontmatter, "scale", f"scale: {scale}")
        frontmatter = replace_line(frontmatter, "title", f"title: {title}")
        write_entry(tmp_path, name, frontmatter)
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert [entry["id"] for entry in entries] == [
        "a-new", "c-new", "d-mid", "b-old", "p-big-2", "p-big", "p-small",
    ]


def test_template_is_a_valid_entry(tmp_path: Path) -> None:
    shutil.copy(TEMPLATE, tmp_path / "your-entry-id.md")
    entries, errors = build_entries.build_entries(tmp_path)
    assert errors == []
    assert len(entries) == 1


# --- Field problems -------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "new_line", "expected"),
    [
        ("title", None, "title: required field is missing"),
        ("summary", 'summary: "  "', "summary: must be non-empty text"),
        ("id", "id: Test_Entry", "id: must be lowercase words joined by hyphens"),
        ("id", "id: other-entry", "id: must match the filename (test-entry.md)"),
        ("type", "type: job", "type: must be one of: project, experience, leadership, other"),
        ("scale", "scale: 0", "scale: must be a whole number from 1 to 5"),
        ("scale", "scale: 6", "scale: must be a whole number from 1 to 5"),
        ("scale", 'scale: "3"', "scale: must be a whole number from 1 to 5"),
        ("scale", "scale: true", "scale: must be a whole number from 1 to 5"),
        ("start", None, "start: required for experience entries"),
        ("start", "start: 2024-01-15", "start: is a full date"),
        ("start", 'start: "2024-13"', 'start: must be a year and month like "2025-06"'),
        ("start", "start: 2024", 'start: must be a year and month like "2025-06"'),
        ("end", None, "end: required for experience entries; use present if ongoing"),
        ("end", "end:", "end: required for experience entries; use present if ongoing"),
        ("end", "end: Present", "end: must be a year and month like \"2025-06\", or present"),
        ("end", 'end: "2024-13"', "end: must be a year and month like \"2025-06\", or present"),
        ("end", 'end: "2023-12"', "end: is before start"),
        ("skills", "skills: []", "skills: must be a non-empty list"),
        ("skills", 'skills: [A, ""]', "skills: every skill must be non-empty text"),
        ("skills", "skills: [A, A]", "skills: contains a duplicate skill"),
    ],
)
def test_field_problem(tmp_path: Path, key: str, new_line: str | None, expected: str) -> None:
    errors = problems_for(tmp_path, replace_line(VALID_DATED, key, new_line))
    assert any(expected in error for error in errors), errors


@pytest.mark.parametrize("key", ["start", "end"])
def test_project_with_dates_is_rejected(tmp_path: Path, key: str) -> None:
    errors = problems_for(tmp_path, replace_line(VALID_PROJECT, key, f'{key}: "2024-01"'))
    assert errors == [f"test-entry.md: {key}: projects don't have dates; delete this line"]


def test_invalid_type_does_not_add_date_errors(tmp_path: Path) -> None:
    errors = problems_for(tmp_path, replace_line(VALID_PROJECT, "type", "type: job"))
    assert len(errors) == 1 and "type: must be one of" in errors[0], errors


def test_unknown_field_is_rejected(tmp_path: Path) -> None:
    errors = problems_for(tmp_path, VALID_DATED + "skils: [Typo]\n")
    assert any("skils: unknown field" in error for error in errors), errors


@pytest.mark.parametrize(
    ("links_yaml", "expected"),
    [
        ("links:\n  - url: https://example.com\n", "links[1]: label must be non-empty text"),
        ("links:\n  - label: X\n    url: ftp://example.com\n", "links[1]: url must start with"),
        ("links:\n  - label: X\n    url: javascript:alert(1)\n", "links[1]: url must start with"),
        (
            "links:\n  - label: X\n    url: https://example.com\n    note: hi\n",
            "links[1]: unknown field 'note'",
        ),
        ("links:\n  - https://example.com\n", "links[1]: must have a label and a url"),
        ("links: https://example.com\n", "links: must be a list"),
        (
            "links:\n  - {label: A, url: https://example.com}\n"
            "  - {label: B, url: https://example.com}\n",
            "links: contains a duplicate url",
        ),
    ],
)
def test_link_problem(tmp_path: Path, links_yaml: str, expected: str) -> None:
    frontmatter = VALID_DATED.split("links:")[0] + links_yaml
    errors = problems_for(tmp_path, frontmatter)
    assert any(expected in error for error in errors), errors


# --- File problems --------------------------------------------------------------


def test_missing_frontmatter(tmp_path: Path) -> None:
    (tmp_path / "test-entry.md").write_text("# No frontmatter\n", encoding="utf-8")
    _, errors = build_entries.build_entries(tmp_path)
    assert errors == ["test-entry.md: file: must start with a frontmatter block between '---' lines"]


def test_invalid_yaml(tmp_path: Path) -> None:
    write_entry(tmp_path, "test-entry", "title: [unclosed\n")
    _, errors = build_entries.build_entries(tmp_path)
    assert len(errors) == 1 and "file: invalid YAML" in errors[0]


def test_frontmatter_must_be_fields(tmp_path: Path) -> None:
    write_entry(tmp_path, "test-entry", "- just\n- a list\n")
    _, errors = build_entries.build_entries(tmp_path)
    assert errors == ["test-entry.md: file: frontmatter must be a list of 'field: value' lines"]


def test_all_problems_across_files_are_reported(tmp_path: Path) -> None:
    first = replace_line(replace_line(VALID_DATED, "id", "id: first"), "type", "type: job")
    second = replace_line(replace_line(VALID_DATED, "id", "id: second"), "scale", "scale: 9")
    write_entry(tmp_path, "first", first)
    write_entry(tmp_path, "second", second)
    write_entry(tmp_path, "test-entry", VALID_DATED)
    entries, errors = build_entries.build_entries(tmp_path)
    assert [entry["id"] for entry in entries] == ["test-entry"]
    assert any(error.startswith("first.md: type:") for error in errors)
    assert any(error.startswith("second.md: scale:") for error in errors)


# --- Command line ---------------------------------------------------------------


def test_main_writes_json_when_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    content, output = tmp_path / "entries", tmp_path / "out" / "entries.json"
    content.mkdir()
    write_entry(content, "test-entry", VALID_DATED)
    assert build_entries.main(["--content-dir", str(content), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))[0]["id"] == "test-entry"
    assert "Wrote 1 entries" in capsys.readouterr().out


def test_main_writes_nothing_when_invalid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    content, output = tmp_path / "entries", tmp_path / "entries.json"
    content.mkdir()
    output.write_text("previous good data", encoding="utf-8")
    write_entry(content, "test-entry", replace_line(VALID_DATED, "type", "type: job"))
    assert build_entries.main(["--content-dir", str(content), "--output", str(output)]) == 1
    assert output.read_text(encoding="utf-8") == "previous good data"
    assert "nothing was written" in capsys.readouterr().err


def test_main_check_does_not_write(tmp_path: Path) -> None:
    content, output = tmp_path / "entries", tmp_path / "entries.json"
    content.mkdir()
    write_entry(content, "test-entry", VALID_DATED)
    assert build_entries.main(["--check", "--content-dir", str(content), "--output", str(output)]) == 0
    assert not output.exists()


def test_main_missing_content_dir(tmp_path: Path) -> None:
    assert build_entries.main(["--content-dir", str(tmp_path / "missing")]) == 1
