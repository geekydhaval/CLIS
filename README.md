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
- `journal/` — three journal articles
- `css/style.css` — all styles; brand tokens are at the top of the file
- `js/main.js` — hero reel, sticky project panels, client wall, WhatsApp button
- `assets/brand/` — logo mark, pattern and grain exported from the CLIS Figma file
- `assets/img/`, `assets/video/` — project stills and hero clips

## Things to swap when real material is ready

- **Client logos**: the "In good company" wall uses `Client name` placeholder tiles in `index.html` (`.logo-tile`).
- **Hero clips and wide project stills**: generated from the studio's Instagram photos. Replace the files in `assets/video/` and `assets/img/` with real 16:9 footage, keeping the same file names.
- **Founder portrait**: `assets/img/surbhi-portrait.jpg` is generated from two real photos. Replace with a studio portrait.
- **Journal articles**: draft copy, to be reviewed by Surbhi.
- **WhatsApp number**: `917405441154`, used in every `wa.me` link.
