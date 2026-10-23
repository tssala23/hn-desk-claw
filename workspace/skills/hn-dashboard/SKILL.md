---
name: hn-dashboard
description: Build or refresh the "HN Desk — Front Page" dashboard of today's top Hacker News stories. Use when asked for the HN dashboard, the front page, or to update the dashboard.
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
---

# HN Desk dashboard

Run every command from the workspace. Three steps:

## 1. Fetch the front page

This is the "Front Page Items" query from the imported hacker-news skill
(`skills/hacker-news/search.md`). Run exactly:

```bash
mkdir -p output && curl -sf "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=10" -o output/frontpage.json
```

If curl fails, report it and stop. Do not reuse an old `output/frontpage.json`.

## 2. Write your notes

Read `output/frontpage.json`. Each story is in `hits` with `objectID`, `title`,
`url`, `points`, `num_comments` and `author`. Write `output/notes.json` with
exactly this shape:

```json
{
  "overview": "One or two sentences on the themes across today's front page.",
  "takeaways": {
    "EXACT_OBJECT_ID": "One short sentence: what the story is about."
  }
}
```

Base takeaways only on the title (and `story_text` if present); do not open
links. Keep the overview under 300 characters and each takeaway under 140. Use
only objectIDs from the file. Do not write titles, links, numbers or HTML;
those come from the API data and the template.

## 3. Publish

```bash
python3 scripts/hn_dashboard.py publish
```

The helper validates both files, fills `templates/dashboard.html`, and publishes
it to the "HN Desk — Front Page" dashboard. Never write or edit the HTML yourself.

Finish by saying how many stories were published and that the dashboard is under
Dashboards → "HN Desk — Front Page".
