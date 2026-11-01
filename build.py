"""Build the trilingual static portfolio site from projects.json + translations."""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "projects.json")
OUT = os.path.join(ROOT, "docs")
LANGS = ["de", "en", "fa"]

with open(SRC, encoding="utf-8") as f:
    DATA = json.load(f)

META = DATA["meta"]
CATEGORIES = DATA["categories"]
PROJECTS = DATA["projects"]
AUTHOR = META["author_profile"]

# Load translations
with open(os.path.join(ROOT, "translations.json"), encoding="utf-8") as f:
    TR = json.load(f)

CONTACT_EMAIL = "ahmad.vahidi1203@gmail.com"

# GitHub Pages serves the site under /infrastructure-portfolio/
BASE = "/infrastructure-portfolio"

# ---------- helpers ----------

def t(lang, key):
    """Translate a UI string."""
    return TR["ui"][key].get(lang, TR["ui"][key]["en"])


def project_field(slug, field, lang):
    """Get a translated project field. English falls back to the source data."""
    if lang == "en":
        for p in PROJECTS:
            if p["slug"] == slug:
                return p.get(field, "")
        return ""
    p = TR["projects"].get(slug, {})
    f = p.get(field, {})
    return f.get(lang) or f.get("en", "")


def project_lessons(slug, lang):
    if lang == "en":
        for p in PROJECTS:
            if p["slug"] == slug:
                return p.get("lessons", [])
        return []
    p = TR["projects"].get(slug, {})
    lessons = p.get("lessons", {})
    return lessons.get(lang) or lessons.get("en", [])


def cat_title(cat_id, lang):
    for c in CATEGORIES:
        if c["id"] == cat_id:
            return TR["categories"].get(cat_id, {}).get(lang, c["title"])
    return cat_id


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def lang_meta(lang):
    if lang == "fa":
        return 'lang="fa" dir="rtl"'
    return f'lang="{lang}" dir="ltr"'


def hreflang_links(slug_path, current_lang):
    """Generate hreflang link tags."""
    out = []
    for l in LANGS:
        url = f"/{l}/{slug_path}" if slug_path else f"/{l}/"
        out.append(f'<link rel="alternate" hreflang="{l}" href="{url}">')
    return "\n".join(out)


def lang_switcher(slug_path, current_lang):
    """Language switcher that keeps the reader on the same project."""
    labels = {"de": "Deutsch", "en": "English", "fa": "فارسی"}
    items = []
    for l in LANGS:
        url = f"/{l}/{slug_path}" if slug_path else f"/{l}/"
        active = ' class="active"' if l == current_lang else ""
        items.append(f'<a href="{url}"{active} hreflang="{l}">{labels[l]}</a>')
    return '<nav class="lang-switch" aria-label="Language">' + "".join(items) + "</nav>"


def page_head(lang, title, desc, slug_path, og_type="website"):
    return f"""<!DOCTYPE html>
<html {lang_meta(lang)}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{hreflang_links(slug_path, lang)}
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<a class="skip-link" href="#main">{t(lang, 'skip')}</a>
<header class="site-header">
  <div class="header-inner">
    <a class="site-title" href="/{lang}/">{t(lang, 'site_name')}</a>
    {lang_switcher(slug_path, lang)}
  </div>
  <nav class="main-nav" aria-label="Main">
    <a href="/{lang}/">{t(lang, 'nav_home')}</a>
    <a href="/{lang}/projects/">{t(lang, 'nav_projects')}</a>
    <a href="/{lang}/about/">{t(lang, 'nav_about')}</a>
  </nav>
</header>
<main id="main">
"""


PAGE_FOOT = """</main>
<footer class="site-footer">
  <p>{contact}</p>
</footer>
</body>
</html>
"""


def footer(lang):
    contact = t(lang, "footer_contact").replace("CONTACT_EMAIL", CONTACT_EMAIL)
    return PAGE_FOOT.replace("{contact}", contact)


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


# ---------- CSS ----------

CSS = """/* Infrastructure Portfolio — shared design */
:root{
  --bg:#ffffff; --bg-soft:#f6f7f9; --surface:#ffffff;
  --ink:#1a1d23; --dim:#4a505c; --muted:#6b7280;
  --line:#e3e6ea; --line-strong:#c9ced6;
  --accent:#1f5fbf; --accent-ink:#ffffff;
  --good:#1a7f4b;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
  --mono:'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',monospace;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#14161a; --bg-soft:#1b1e24; --surface:#1b1e24;
    --ink:#e6e8ec; --dim:#a8aeb8; --muted:#7d8490;
    --line:#2a2e36; --line-strong:#3a3f4a;
    --accent:#6ea8ff; --accent-ink:#0d1117;
    --good:#4cc38a;
  }
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--font);line-height:1.65;-webkit-font-smoothing:antialiased}
[dir="rtl"] body{font-family:'Vazirmatn',var(--font)}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.skip-link{position:absolute;inset-inline-start:-9999px;top:0;background:var(--accent);color:var(--accent-ink);padding:8px 16px;z-index:200}
.skip-link:focus{inset-inline-start:0}
.site-header{border-bottom:1px solid var(--line);background:var(--bg)}
.header-inner{max-width:960px;margin:0 auto;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.site-title{font-weight:700;font-size:17px;color:var(--ink);letter-spacing:-.01em}
.lang-switch{display:flex;gap:4px}
.lang-switch a{font-size:13px;padding:4px 10px;border-radius:6px;border:1px solid var(--line);color:var(--dim)}
.lang-switch a.active{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.main-nav{max-width:960px;margin:0 auto;padding:0 24px 12px;display:flex;gap:20px}
.main-nav a{font-size:14px;color:var(--dim);font-weight:500}
.main-nav a:hover{color:var(--ink)}
main{max-width:960px;margin:0 auto;padding:40px 24px 64px}
h1{font-size:clamp(28px,4vw,40px);font-weight:800;letter-spacing:-.02em;line-height:1.15;margin-bottom:16px}
h2{font-size:clamp(22px,3vw,28px);font-weight:700;letter-spacing:-.01em;margin:40px 0 12px}
h3{font-size:18px;font-weight:600;margin:24px 0 8px}
p{margin-bottom:16px;max-width:72ch}
.lead{font-size:18px;color:var(--dim);max-width:72ch;margin-bottom:32px}
.sec-label{font-family:var(--mono);font-size:12px;color:var(--accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;font-weight:600}
.cat-list{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}
.cat-pill{font-size:13px;padding:6px 14px;border-radius:100px;border:1px solid var(--line);color:var(--dim)}
.cat-pill:hover{border-color:var(--accent);color:var(--accent)}
.proj-list{list-style:none;margin:24px 0}
.proj-list li{border-bottom:1px solid var(--line);padding:20px 0}
.proj-list a{display:block}
.proj-list .ptitle{font-size:17px;font-weight:600;color:var(--ink);margin-bottom:4px}
.proj-list .psum{font-size:14px;color:var(--dim)}
.proj-list .pcat{font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:6px}
.lessons{background:var(--bg-soft);border:1px solid var(--line);border-radius:12px;padding:24px;margin:24px 0}
.lessons h2{margin-top:0}
.lessons ul{list-style:none;padding:0}
.lessons li{padding:12px 0;border-bottom:1px solid var(--line);padding-inline-start:24px;position:relative}
.lessons li:last-child{border-bottom:none}
.lessons li::before{content:'→';position:absolute;inset-inline-start:0;color:var(--accent);font-weight:700}
[dir="rtl"] .lessons li::before{content:'←'}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}
.tag{font-family:var(--mono);font-size:12px;padding:5px 12px;border-radius:6px;background:var(--bg-soft);border:1px solid var(--line);color:var(--dim)}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin-top:40px;padding-top:24px;border-top:1px solid var(--line)}
.prevnext a{font-size:14px;font-weight:500}
.site-footer{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:13px}
.site-footer a{color:var(--dim)}
.filter-bar{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}
.filter-bar button{font-size:13px;padding:6px 14px;border-radius:100px;border:1px solid var(--line);background:var(--surface);color:var(--dim);cursor:pointer;font-family:var(--font)}
.filter-bar button.active{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.proj-item[hidden]{display:none}
@media (max-width:640px){
  .header-inner{flex-direction:column;align-items:flex-start}
  main{padding:28px 16px 48px}
}
@media (prefers-reduced-motion: reduce){
  *{scroll-behavior:auto !important;transition:none !important}
}
"""


# ---------- build ----------

def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    # assets
    write("assets/style.css", CSS)
    os.makedirs(os.path.join(OUT, "assets", "fonts"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "assets", "fonts")):
        shutil.copy(os.path.join(ROOT, "assets", "fonts", f), os.path.join(OUT, "assets", "fonts", f))

    # root redirect
    redirect = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<script>var l=(navigator.language||'en').toLowerCase();var t=l.indexOf('fa')===0?'fa':(l.indexOf('de')===0?'de':'en');location.replace('/'+t+'/');</script>
<meta http-equiv="refresh" content="0;url=/en/">
</head>
<body><p>Redirecting… <a href="/en/">English</a> · <a href="/de/">Deutsch</a> · <a href="/fa/">فارسی</a></p></body>
</html>
"""
    write("index.html", redirect)

    # robots.txt + sitemap
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://ahmadvahidi.github.io/infrastructure-portfolio/sitemap.xml\n")

    sitemap_urls = ["https://ahmadvahidi.github.io/infrastructure-portfolio/"]
    for l in LANGS:
        sitemap_urls.append(f"https://ahmadvahidi.github.io/infrastructure-portfolio/{l}/")
        sitemap_urls.append(f"https://ahmadvahidi.github.io/infrastructure-portfolio/{l}/projects/")
        sitemap_urls.append(f"https://ahmadvahidi.github.io/infrastructure-portfolio/{l}/about/")
        for p in PROJECTS:
            sitemap_urls.append(f"https://ahmadvahidi.github.io/infrastructure-portfolio/{l}/projects/{p['slug']}/")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in sitemap_urls:
        sitemap += f"  <url><loc>{u}</loc></url>\n"
    sitemap += "</urlset>\n"
    write("sitemap.xml", sitemap)

    # per-language pages
    for lang in LANGS:
        build_lang(lang)

    # Post-process: prefix absolute URLs for GitHub Pages subpath
    _prefix_urls()

    print(f"Built {len(PROJECTS)} projects x {len(LANGS)} languages.")


def _prefix_urls():
    """Rewrite absolute URLs to include the GitHub Pages base path."""
    import re
    for dirpath, _, filenames in os.walk(OUT):
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(dirpath, fn)
            with open(fp, encoding="utf-8") as f:
                c = f.read()
            # href/src absolute paths
            c = re.sub(r'(href|src)="/', r'\1="' + BASE + '/', c)
            # JS redirect
            c = c.replace("location.replace('/'+t+'/')", f"location.replace('{BASE}/'+t+'/')")
            # no-JS meta refresh (must carry the Pages base path too)
            c = c.replace('content="0;url=/en/"', f'content="0;url={BASE}/en/"')
            with open(fp, "w", encoding="utf-8") as f:
                f.write(c)


def build_lang(lang):
    # home
    home = page_head(lang, t(lang, "site_name"), t(lang, "home_desc"), "")
    home += f'<h1>{t(lang, "home_title")}</h1>\n'
    home += f'<p class="lead">{t(lang, "home_lead")}</p>\n'
    home += f'<div class="sec-label">{t(lang, "categories_label")}</div>\n'
    home += '<div class="cat-list">\n'
    for c in CATEGORIES:
        home += f'  <a class="cat-pill" href="/{lang}/projects/#{c["id"]}">{esc(cat_title(c["id"], lang))}</a>\n'
    home += '</div>\n'
    home += f'<h2>{t(lang, "all_projects")}</h2>\n'
    home += '<ul class="proj-list">\n'
    for p in PROJECTS:
        title = project_field(p["slug"], "title", lang)
        summary = project_field(p["slug"], "summary", lang)
        home += f'  <li><a href="/{lang}/projects/{p["slug"]}/"><span class="ptitle">{esc(title)}</span><span class="psum">{esc(summary)}</span><span class="pcat">{esc(cat_title(p["category"], lang))}</span></a></li>\n'
    home += '</ul>\n'
    home += footer(lang)
    write(f"{lang}/index.html", home)

    # projects index (filterable)
    proj = page_head(lang, t(lang, "nav_projects"), t(lang, "projects_desc"), "projects/")
    proj += f'<h1>{t(lang, "nav_projects")}</h1>\n'
    proj += f'<p class="lead">{t(lang, "projects_lead")}</p>\n'
    proj += '<div class="filter-bar" role="group" aria-label="Filter">\n'
    proj += f'  <button class="active" data-filter="all">{t(lang, "filter_all")}</button>\n'
    for c in CATEGORIES:
        proj += f'  <button data-filter="{c["id"]}">{esc(cat_title(c["id"], lang))}</button>\n'
    proj += '</div>\n'
    proj += '<ul class="proj-list">\n'
    for p in PROJECTS:
        title = project_field(p["slug"], "title", lang)
        summary = project_field(p["slug"], "summary", lang)
        proj += f'  <li class="proj-item" data-cat="{p["category"]}"><a href="/{lang}/projects/{p["slug"]}/"><span class="ptitle">{esc(title)}</span><span class="psum">{esc(summary)}</span><span class="pcat">{esc(cat_title(p["category"], lang))}</span></a></li>\n'
    proj += '</ul>\n'
    proj += """<script>
(function(){
  var btns=document.querySelectorAll('.filter-bar button');
  var items=document.querySelectorAll('.proj-item');
  btns.forEach(function(b){
    b.addEventListener('click',function(){
      btns.forEach(function(x){x.classList.remove('active')});
      b.classList.add('active');
      var f=b.getAttribute('data-filter');
      items.forEach(function(it){
        it.hidden = (f!=='all' && it.getAttribute('data-cat')!==f);
      });
    });
  });
})();
</script>
"""
    proj += footer(lang)
    write(f"{lang}/projects/index.html", proj)

    # about
    about = page_head(lang, t(lang, "nav_about"), t(lang, "about_desc"), "about/")
    about += f'<h1>{t(lang, "nav_about")}</h1>\n'
    about += f'<p class="lead">{t(lang, "about_lead")}</p>\n'
    about += f'<h2>{t(lang, "about_focus")}</h2>\n'
    about += f'<p>{esc(AUTHOR["focus"])}</p>\n'
    about += f'<h2>{t(lang, "about_stack")}</h2>\n'
    about += '<div class="tags">\n'
    for s in AUTHOR["core_stack"]:
        about += f'  <span class="tag">{esc(s)}</span>\n'
    about += '</div>\n'
    about += footer(lang)
    write(f"{lang}/about/index.html", about)

    # project pages
    for i, p in enumerate(PROJECTS):
        build_project(lang, p, i)


def build_project(lang, p, idx):
    slug = p["slug"]
    title = project_field(slug, "title", lang)
    summary = project_field(slug, "summary", lang)
    problem = project_field(slug, "problem", lang)
    approach = project_field(slug, "approach", lang)
    solution = project_field(slug, "solution", lang)
    result = project_field(slug, "result", lang)
    lessons = project_lessons(slug, lang)

    path = f"projects/{slug}/"
    html = page_head(lang, title, summary, path, "article")
    html += f'<h1>{esc(title)}</h1>\n'
    html += f'<p class="lead">{esc(summary)}</p>\n'

    if problem:
        html += f'<h2>{t(lang, "sec_problem")}</h2>\n<p>{esc(problem)}</p>\n'
    if approach:
        html += f'<h2>{t(lang, "sec_approach")}</h2>\n<p>{esc(approach)}</p>\n'
    if solution:
        html += f'<h2>{t(lang, "sec_solution")}</h2>\n<p>{esc(solution)}</p>\n'
    if result:
        html += f'<h2>{t(lang, "sec_result")}</h2>\n<p>{esc(result)}</p>\n'

    if lessons:
        html += f'<div class="lessons"><h2>{t(lang, "sec_lessons")}</h2><ul>\n'
        for l in lessons:
            html += f'  <li>{esc(l)}</li>\n'
        html += '</ul></div>\n'

    # stack + skills tags
    html += '<div class="tags">\n'
    for s in p.get("stack", []):
        html += f'  <span class="tag">{esc(s)}</span>\n'
    for s in p.get("skills", []):
        html += f'  <span class="tag">{esc(s)}</span>\n'
    html += '</div>\n'

    # prev/next in same category
    same_cat = [x for x in PROJECTS if x["category"] == p["category"]]
    pos = same_cat.index(p)
    prev_p = same_cat[pos - 1] if pos > 0 else None
    next_p = same_cat[pos + 1] if pos < len(same_cat) - 1 else None
    html += '<div class="prevnext">\n'
    if prev_p:
        html += f'  <a href="/{lang}/projects/{prev_p["slug"]}/">← {esc(project_field(prev_p["slug"], "title", lang))}</a>\n'
    else:
        html += '  <span></span>\n'
    if next_p:
        html += f'  <a href="/{lang}/projects/{next_p["slug"]}/">{esc(project_field(next_p["slug"], "title", lang))} →</a>\n'
    else:
        html += '  <span></span>\n'
    html += '</div>\n'

    html += footer(lang)
    write(f"{lang}/projects/{slug}/index.html", html)


if __name__ == "__main__":
    build()
