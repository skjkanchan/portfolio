# Content

Every experience on the site is one Markdown file in `entries/`. The site and the ML pipeline both read these files, through the generated `frontend/src/data/entries.json`.

## Adding or editing an entry

1. Copy `entry-template.md` into `entries/` and rename it to `<id>.md`.
2. Fill in the frontmatter (the fields between the `---` lines), and optionally a Markdown body below it.
3. From the repository root, regenerate the JSON:

   ```bash
   uv run --project pipeline python pipeline/build_entries.py
   ```

4. Commit both the entry and the updated `frontend/src/data/entries.json`.

The JSON is committed because Vercel's build only runs npm, not Python. If you edit an entry and skip step 3, the site keeps showing the old version.

To check entries without writing anything, add `--check`. If any entry has a problem, the script lists every problem in every file and writes nothing.

## Fields

| Field | Required | Format |
|---|---|---|
| `id` | yes | Lowercase words joined by hyphens, e.g. `my-project`. Must match the filename. |
| `title` | yes | Text |
| `type` | yes | `project`, `experience` (jobs, internships, lab roles), `leadership` or `other` |
| `start` | not for projects | Year and month in quotes, e.g. `"2025-06"` |
| `end` | not for projects | Same format as `start` and not before it, or `present` if ongoing |
| `scale` | yes | Whole number from 1 to 5; see the rubric below |
| `skills` | yes | Non-empty list, no duplicates, e.g. `[Python, AWS]` |
| `summary` | yes | One or two sentences |
| `links` | yes | List of `label` + `url` pairs (`http://` or `https://`); `[]` for none |

Any other field is rejected, which catches typos like `skils`.

**Dates depend on the type.** Experience, leadership and `other` entries need both `start` and `end`. Projects have no dates, so a project with a `start` or `end` line is rejected.

The **body** below the frontmatter is optional Markdown with more detail. It isn't shown on the site yet, but the ML features (embeddings, search, the chatbot) will use it, so more detail there means better results.

### Tips

- **Quote dates.** `"2025-06"` is safest. A full date like `2025-06-15` is rejected, because YAML turns it into a date instead of text.
- **Quote text with a colon** in it, e.g. `title: "Project: Part 2"`, or YAML will misread it.

## Scale rubric

`scale` drives progression ordering in recommendations (e.g. hackathon → project → internship), so it needs to mean the same thing across every entry.

> **Draft for you to replace.** This is a suggested starting point, not a decision. Edit it so it matches how you see your own experience, then delete this note.

| Scale | Meaning |
|---|---|
| 1 | Coursework or a small personal project |
| 2 | Hackathon or team project |
| 3 | Shipped project with real users, or scoped internship work |
| 4 | Production work you owned |
| 5 | Large-scale production impact, or leading a large group |
