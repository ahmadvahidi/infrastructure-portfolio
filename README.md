# IT Infrastructure & Automation — Portfolio

A trilingual (German / English / Persian) static portfolio and knowledge base documenting real problems from daily IT infrastructure work, written up as reusable solutions.

Built from a single data file (`projects.json`) — the only source of content.

## Structure

```
/                       redirect to browser language (default /en/)
/{lang}/                home: intro, categories, all projects
/{lang}/projects/       all projects, filterable by category
/{lang}/projects/{slug} one page per project
/{lang}/about/          short profile
```

## Languages

- **German** (`/de/`) — professional, factual, correct technical terms
- **English** (`/en/`) — source language
- **Persian** (`/fa/`) — RTL, Vazirmatn font

## Project page layout

Each project page follows the same structure:

1. Title + summary
2. Problem
3. Approach
4. Solution
5. Result
6. **What I learned** (the most valuable section for other admins)
7. Stack + skills tags
8. Previous/next project in the same category

## Design

- One shared design across all three languages, RTL-safe (CSS logical properties)
- Readable and quiet — a professional portfolio, not a landing page
- Responsive down to 360px, visible keyboard focus, sufficient contrast
- Dark mode via `prefers-color-scheme`
- No tracking, no analytics, no external scripts, self-hosted fonts
- Content readable with JavaScript disabled (only the category filter needs JS)

## Build

```bash
python build.py
```

Reads `projects.json` + `translations.json`, writes the static site to `site/`.

## License

[MIT](LICENSE)
