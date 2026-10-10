#!/usr/bin/env python3
"""Builds the project pages and the landing-page project panels from tools/projects.json.

Run from the site root:  python3 tools/build_projects.py
It rewrites projects/*.html, the block between the projects:start / projects:end
markers in index.html, and sitemap.xml. Edit projects.json, not the generated files.
"""
import json
import os
import re
from html import escape
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://clis.work"
WA = "https://wa.me/917405441154?text="
ARROW = ('<span class="link__dot" aria-hidden="true"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" '
         'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h10M9 4l4 4-4 4"/></svg></span>')
WA_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M3.5 20.5l1.3-4.6A8.5 8.5 0 1 1 8.2 19.3z"/>'
           '<path d="M9 8.2c-.4.9-.2 2.300 1.300 3.900s3.100 2.300 4.100 2c.6-.2 1.100-.7 1.200-1.200l-1.700-1-.9.8c-.7-.3-1.500-1.100-1.900-1.800'
           'l.8-.9-.9-1.800c-.6-.1-1.600.2-2 1z"/></svg>')
FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..500,0..100;"
         "1,9..144,300..500,0..100&family=Hanken+Grotesk:wght@300..600&family=Julius+Sans+One&display=swap")


def e(text):
    return escape(text, quote=True)


def ask_link(title):
    return WA + quote(f"Hi CLIS, I saw {title} on your site and would like to talk about my space.")


def gallery_rows(items):
    """Group images into rows: portraits in threes, mediums in pairs, a lone medium goes full width."""
    rows, run = [], []

    def flush():
        while run:
            kind = run[0]["role"]
            size = 3 if kind == "p" else 2
            chunk = [run.pop(0) for _ in range(min(size, len(run)))]
            if kind == "m" and len(chunk) == 1:
                rows.append(("l", chunk))
            else:
                rows.append((kind, chunk))

    for it in items:
        if it["role"] == "l":
            flush()
            rows.append(("l", [it]))
        else:
            if run and run[0]["role"] != it["role"]:
                flush()
            run.append(it)
    flush()
    return rows


def figure(it, cls):
    return (f'<figure class="shot shot--{cls} reveal"><button class="shot__btn" type="button" data-zoom="../{e(it["src"])}" '
            f'aria-label="Enlarge: {e(it["cap"])}"><img src="../{e(it["src"])}" alt="{e(it["cap"])}" loading="lazy" '
            f'width="{it["w"]}" height="{it["h"]}"></button><figcaption>{e(it["cap"])}</figcaption></figure>')


def page(p, n, total, nxt):
    url = f"{SITE}/projects/{p['slug']}.html"
    desc = f"{p['lede']} {p['kind'].replace(' · ', ', ')} project by CLIS Interior Studio, {p['place']}."
    facts = "\n".join(f"            <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in p["facts"])
    body = "\n".join(f"          <p class=\"reveal\">{e(t)}</p>" for t in p["body"])
    rows = []
    for kind, chunk in gallery_rows(p["gallery"]):
        rows.append(f'        <div class="shots shots--{kind}">' + "".join(figure(it, kind) for it in chunk) + "</div>")
    plans = ""
    if p["plans"]:
        figs = "\n".join(
            f'        <figure class="plan__sheet reveal"><button class="shot__btn" type="button" data-zoom="../{e(pl["src"])}" '
            f'aria-label="Enlarge the plan"><img src="../{e(pl["src"])}" alt="{e(pl.get("cap", "Furniture layout for " + p["title"]))}" '
            f'loading="lazy" width="{pl["w"]}" height="{pl["h"]}"></button>'
            + (f'<figcaption>{e(pl["cap"])}</figcaption>' if pl.get("cap") else "") + "</figure>"
            for pl in p["plans"])
        plans = f"""
    <section class="plan" data-theme="light">
      <div class="wrap">
        <div class="tag-row reveal"><span class="pill">Plan</span><span class="eyebrow">How the space is laid out</span></div>
{figs}
      </div>
    </section>
"""
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CreativeWork", "name": p["title"], "description": p["lede"], "url": url,
             "image": f"{SITE}/{p['cover']}", "locationCreated": {"@type": "Place", "name": p["place"]},
             "creator": {"@type": "Organization", "name": "CLIS — Creating Life In Spaces", "url": SITE + "/"},
             "genre": "Interior design", "inLanguage": "en-IN"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "CLIS", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Projects", "item": SITE + "/#projects"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]},
        ],
    }
    return f"""<!doctype html>
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(p['title'])} | {e(p['place'])} | CLIS Interior Studio</title>
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#718385">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="CLIS — Creating Life In Spaces">
  <meta property="og:locale" content="en_IN">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{e(p['title'])} | CLIS Interior Studio">
  <meta property="og:description" content="{e(p['lede'])}">
  <meta property="og:image" content="{SITE}/{e(p['cover'])}">
  <meta property="og:image:width" content="{p['cover_w']}">
  <meta property="og:image:height" content="{p['cover_h']}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(p['title'])} | CLIS Interior Studio">
  <meta name="twitter:description" content="{e(p['lede'])}">
  <meta name="twitter:image" content="{SITE}/{e(p['cover'])}">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/assets/brand/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONTS}" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
  <script>document.documentElement.classList.add('js')</script>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
  <header class="site-header" data-header>
    <div class="site-header__left"><span class="pill">Surat</span><span class="pill" data-clock>--:--</span><span class="site-header__tz">IST</span></div>
    <a class="logo-chip" href="../" aria-label="CLIS home"><span class="mark"></span><span class="wordmark wordmark--sm">Creat<b>ING</b><br>life in space<b>S</b></span></a>
    <nav class="site-header__right" aria-label="Primary">
      <a class="nav-link" href="../#projects">Projects</a>
      <a class="nav-link" href="../#journal">Journal</a>
      <a class="talk" href="#ask"><span>Enquire</span>{ARROW.replace('link__dot', 'talk__dot')}</a>
    </nav>
  </header>

  <main>
    <section class="proj-hero" data-theme="dark">
      <picture>
        <source media="(max-width: 699px)" srcset="../{e(p['cover_sm'])}">
        <img src="../{e(p['cover'])}" alt="{e(p['cover_alt'])}" fetchpriority="high">
      </picture>
      <div class="proj-hero__inner">
        <a class="proj-hero__back" href="../#projects">All projects</a>
        <div class="project__count"><span class="pill">{n:02d}</span><span class="pill">{total:02d}</span></div>
        <h1 class="proj-hero__title">{e(p['title'])}</h1>
        <p class="proj-hero__meta">{e(p['place'])}<br>{e(p['kind'])}</p>
      </div>
    </section>

    <section class="proj-intro" data-theme="light">
      <div class="wrap proj-intro__grid">
        <dl class="facts reveal">
{facts}
        </dl>
        <div class="proj-intro__text">
          <p class="lede reveal">{e(p['lede'])}</p>
{body}
          <a class="link reveal" href="#ask"><span>Ask about this project</span>{ARROW}</a>
        </div>
      </div>
    </section>

    <section class="gallery" data-theme="light" aria-label="Project gallery">
      <div class="wrap">
{chr(10).join(rows)}
        <p class="gallery__note reveal">{e(p['gallery_note'])}</p>
      </div>
    </section>
{plans}
    <section class="ask" id="ask" data-theme="sage">
      <img class="process__pattern" src="../assets/brand/clis-pattern.svg" alt="" aria-hidden="true">
      <div class="wrap ask__grid">
        <h2 class="display display--sm reveal">Planning a space<br><em>like this one?</em></h2>
        <div class="ask__side reveal">
          <p>Tell us about your home, shop or office. Mention {e(p['title'])} and we will know exactly what caught your eye.</p>
          <div class="cta__actions">
            <a class="btn btn--light" href="{e(ask_link(p['title']))}" target="_blank" rel="noopener">{WA_ICON}<span>Ask on WhatsApp</span></a>
            <a class="btn btn--outline" href="tel:+917405441154">+91 74054 41154</a>
          </div>
        </div>
      </div>
    </section>

    <a class="next" href="{e(nxt['slug'])}.html" data-theme="dark">
      <picture>
        <source media="(max-width: 699px)" srcset="../{e(nxt['cover_sm'])}">
        <img src="../{e(nxt['cover'])}" alt="" loading="lazy">
      </picture>
      <span class="next__inner">
        <span class="eyebrow">Next project</span>
        <span class="next__title">{e(nxt['title'])}</span>
        <span class="link link--light"><span>{e(nxt['place'])}</span>{ARROW}</span>
      </span>
    </a>
  </main>

  <footer class="footer" data-theme="dark">
    <div class="footer__brand" aria-hidden="true"><span class="mark mark--lg"></span><span class="footer__word">CLIS</span></div>
    <div class="footer__main">
      <div class="footer__meter"><p><strong>CLIS Interior Studio</strong><span>We create life in your spaces.</span></p></div>
      <div class="footer__cols">
        <div>
          <h4>Find us</h4>
          <address>323, CLIS Interior Studio<br>Soham Arcade, Green City Road<br>Pal, Surat, Gujarat</address>
          <h4>Call or WhatsApp</h4>
          <p><a href="tel:+917405441154">+91 74054 41154</a></p>
        </div>
        <div>
          <h4>Explore</h4>
          <ul class="footer__nav"><li><a href="../#projects">Projects</a></li><li><a href="../#founder">Founder</a></li><li><a href="../#journal">Journal</a></li></ul>
        </div>
      </div>
    </div>
    <div class="footer__base"><span>© 2026 CLIS — Creating Life In Spaces</span><span><a href="https://www.instagram.com/creatinglifeinspaces/" target="_blank" rel="noopener">Instagram</a></span></div>
  </footer>

  <a class="wa-float" data-wa-float href="{e(ask_link(p['title']))}" target="_blank" rel="noopener" aria-label="Ask CLIS about {e(p['title'])} on WhatsApp">
    {WA_ICON}
    <span>Ask on WhatsApp</span>
  </a>

  <dialog class="zoom" data-zoom-dialog aria-label="Enlarged image"><button class="zoom__close" type="button" data-zoom-close aria-label="Close">Close</button><img alt=""></dialog>
  <script src="../js/main.js" defer></script>
</body>
</html>
"""


def panel(p, n, total):
    href = f"projects/{p['slug']}.html"
    return f"""      <article class="project" data-theme="dark">
        <a class="project__media" href="{href}" aria-label="Explore {e(p['title'])}" tabindex="-1">
          <picture><source media="(max-width: 699px)" srcset="{e(p['cover_sm'])}"><img src="{e(p['cover'])}" alt="{e(p['cover_alt'])}" loading="lazy"></picture>
        </a>
        <div class="project__info">
          <div class="project__lead">
            <div class="project__count"><span class="pill">{n:02d}</span><span class="pill">{total:02d}</span><span class="pill pill--solid">{e(p['status'])}</span></div>
            <h3 class="project__title"><a href="{href}">{e(p['title'])}</a></h3>
            <p class="project__meta">{e(p['place'])}<br>{e(p['kind'])}</p>
          </div>
          <blockquote class="project__note">
            <span class="project__mark" aria-hidden="true">“</span>
            <p>{e(p['note'])}</p>
            <footer>Design note<br><span>CLIS Interior Studio</span></footer>
            <div class="project__links">
              <a class="link link--light" href="{href}"><span>Explore project</span>{ARROW}</a>
              <a class="link link--light link--quiet" href="{href}#ask"><span>Ask about this project</span></a>
            </div>
          </blockquote>
        </div>
      </article>"""


def main():
    projects = json.load(open(os.path.join(ROOT, "tools", "projects.json"), encoding="utf-8"))
    total = len(projects)
    os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
    for i, p in enumerate(projects):
        html = page(p, i + 1, total, projects[(i + 1) % total])
        with open(os.path.join(ROOT, "projects", p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(html)

    index_path = os.path.join(ROOT, "index.html")
    index = open(index_path, encoding="utf-8").read()
    panels = "\n\n".join(panel(p, i + 1, total) for i, p in enumerate(projects))
    index, count = re.subn(r"(<!-- projects:start -->).*?(<!-- projects:end -->)",
                           lambda m: m.group(1) + "\n" + panels + "\n      " + m.group(2), index, flags=re.S)
    assert count == 1, "projects markers not found in index.html"
    open(index_path, "w", encoding="utf-8").write(index)

    urls = [("", "2026-10-10")] + [(f"projects/{p['slug']}.html", "2026-10-10") for p in projects] + [
        ("journal/on-site-decisions.html", "2026-10-02"), ("journal/meet-surbhi.html", "2026-09-18"),
        ("journal/styling-siesta-villa.html", "2026-08-28")]
    body = "\n".join(f"  <url>\n    <loc>{SITE}/{u}</loc>\n    <lastmod>{d}</lastmod>\n  </url>" for u, d in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')
    print(f"built {total} project pages, landing panels and sitemap")


if __name__ == "__main__":
    main()
