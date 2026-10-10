# CLIS — Creating Life In Spaces

Landing page for [clis.work](https://clis.work), the interior design studio in Surat led by Surbhi Kalsariya.

Plain HTML, CSS and JavaScript. No build step.

## Run locally

```bash
python3 -m http.server 4173
```

Then open http://localhost:4173.

## Structure

- `index.html` — the landing page
- `projects/` — one page per project, **generated** (see below)
- `journal/` — three journal articles
- `css/style.css` — all styles; brand tokens are at the top of the file
- `js/main.js` — hero reel, sticky project panels, client wall, image lightbox, WhatsApp button
- `assets/brand/` — logo mark, pattern and grain exported from the CLIS Figma file
- `assets/img/`, `assets/video/` — Siesta Villa stills and hero clips
- `assets/projects/<slug>/` — renders and floor plans for each project
- `tools/` — project data and the page generator

## Adding or editing a project

Project titles, facts, copy and image lists live in `tools/projects.json`. After changing it, run:

```bash
python3 tools/build_projects.py
```

This rewrites `projects/*.html`, the project panels on the landing page (between the `projects:start` and `projects:end` comments in `index.html`) and `sitemap.xml`. Do not edit those by hand.

## Things to check or swap

- **Design-stage projects** (Human Design Academy, Sattvam, both Aspire homes, Virat Nagar, Janki Heights) use 3D renders and furniture layouts taken from the CLIS drawing sets. Client names and flat numbers are deliberately left off the site.
- **Siesta Villa**: three real photographs plus wide views generated from them. Replace with real 16:9 photography when available, keeping the file names.
- **Founder portrait**: `assets/img/surbhi-portrait.jpg` is generated from two real photos. Replace with a studio portrait.
- **Project copy and journal articles**: drafts, to be reviewed by Surbhi.
- **WhatsApp number**: `917405441154`, used in every `wa.me` link.
