#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static site generator (idempotent).
Reads the <article> content from posts/*.html and regenerates home, category
list pages, post pages, sitemap, favicon, 404 with SEO (JSON-LD, canonical,
related posts, breadcrumbs). Add a category by extending CATS below."""
import re, os, glob, html, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root, portable
BASE = "https://jangwonh01.github.io/"
SITE_NAME = "여행하는 요리사 JUHWANDAD"
LOGO = BASE + "favicon.svg"

# category config — id prefix is the category key (e.g. travel-1, food-3, column-2)
CATS = [
    {"key": "travel", "name": "여행",      "hero": "travel-hero", "home": "최신 여행기",
     "sub": "발길 닿는 곳마다 새로운 이야기", "badge": "card-badge"},
    {"key": "food",   "name": "요리",      "hero": "food-hero",   "home": "인기 레시피",
     "sub": "집에서 만드는 전 세계의 맛",   "badge": "card-badge badge-food"},
    {"key": "column", "name": "경제 칼럼", "hero": "column-hero", "home": "경제 칼럼",
     "sub": "부동산·금융·정책을 보는 나만의 시선", "badge": "card-badge badge-column"},
]
CAT = {c["key"]: c for c in CATS}

css = open(os.path.join(REPO, "style.css"), encoding="utf-8").read()
img_urls = {}
for m in re.finditer(r"\.([a-z]+-img-\d+)\s*\{[^}]*url\('([^']+)'\)", css):
    img_urls[m.group(1)] = m.group(2)

def to_iso(kdate):
    m = re.match(r'(\d+)년\s*(\d+)월\s*(\d+)일', kdate)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

def strip(t): return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()

posts = []
for f in glob.glob(os.path.join(REPO, "posts", "*.html")):
    src = open(f, encoding="utf-8").read()
    a = re.search(r'<article class="post.*?</article>', src, re.S).group(0)
    pid = re.search(r'id="([^"]+)"', a).group(1)
    cat = pid.split('-')[0]
    imgcls = f"{cat}-img-{int(pid.split('-')[1])}"
    tag = re.search(r'<span class="post-tag[^"]*">([^<]+)</span>', a).group(1)
    title = re.search(r'<h2 class="post-title">([^<]+)</h2>', a).group(1)
    date = re.search(r'<time>([^<]+)</time>', a).group(1)
    first_p = re.search(r'<p>(.*?)</p>', a, re.S).group(1)
    excerpt = strip(first_p)
    is_recipe = 'recipe-post' in a
    ingredients = [strip(x) for x in re.findall(r'<div class="ingredient-box">.*?</div>', a, re.S) for x in re.findall(r'<li>(.*?)</li>', x, re.S)]
    steps = [strip(x) for block in re.findall(r'<ol class="recipe-steps">(.*?)</ol>', a, re.S) for x in re.findall(r'<li>(.*?)</li>', block, re.S)]
    posts.append(dict(id=pid, img=imgcls, tag=tag, title=title, date=date, iso=to_iso(date),
                      excerpt=excerpt, cat=cat, html=a, is_recipe=is_recipe,
                      ingredients=ingredients, steps=steps))

# per-category, newest first
bycat = {c["key"]: sorted([p for p in posts if p["cat"] == c["key"]], key=lambda p: p["iso"], reverse=True) for c in CATS}
active_cats = [c for c in CATS if bycat[c["key"]]]
posts = [p for c in CATS for p in bycat[c["key"]]]

def head(title, desc, canonical, prefix, og_image=None, jsonld=None):
    img_tag = f'\n    <meta property="og:image" content="{og_image}">' if og_image else ''
    ld = f'\n    <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ''
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="index, follow">
    <meta name="description" content="{html.escape(desc)}">
    <meta name="keywords" content="여행 블로그, 요리 레시피, 부동산, 금융, 정책, 경제 칼럼, JUHWANDAD">
    <meta name="author" content="{SITE_NAME}">
    <meta name="theme-color" content="#e63946">
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
    <link rel="apple-touch-icon" href="{prefix}favicon.svg">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">{img_tag}
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{prefix}style.css">
    <meta name="google-adsense-account" content="ca-pub-6724882635011810">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6724882635011810" crossorigin="anonymous"></script>{ld}
</head>
<body>'''

def nav(active, prefix):
    def link(href, label, key):
        cls = "nav-link active" if active == key else "nav-link"
        return f'<a href="{prefix}{href}" class="{cls}">{label}</a>'
    cat_links = "\n                ".join(link(f"{c['key']}.html", c['name'], c['key']) for c in active_cats)
    return f'''
    <nav class="nav" id="nav">
        <div class="nav-inner">
            <a href="{prefix}index.html" class="nav-logo">
                <span class="logo-icon">&#9992;</span>
                <span class="logo-text">{SITE_NAME}</span>
            </a>
            <button class="hamburger" id="hamburger" aria-label="메뉴 열기">
                <span></span><span></span><span></span>
            </button>
            <div class="nav-links" id="nav-links">
                {link("index.html","홈","home")}
                {cat_links}
                {link("about.html","소개","about")}
                {link("contact.html","문의","contact")}
            </div>
        </div>
    </nav>
'''

def footer(prefix):
    cat_items = "\n                        ".join(f'<li><a href="{prefix}{c["key"]}.html">{c["name"]}</a></li>' for c in active_cats)
    return f'''
    <footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <h4>{SITE_NAME}</h4>
                    <p>여행과 요리, 그리고 세상을 보는 시선을 나눕니다.</p>
                </div>
                <div class="footer-col">
                    <h4>카테고리</h4>
                    <ul>
                        {cat_items}
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>정보</h4>
                    <ul>
                        <li><a href="{prefix}about.html">블로거 소개</a></li>
                        <li><a href="{prefix}contact.html">문의하기</a></li>
                        <li><a href="{prefix}privacy.html">개인정보처리방침</a></li>
                        <li><a href="{prefix}privacy.html#site-policy">운영정책/광고고지</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2026 {SITE_NAME}. All rights reserved.</p>
            </div>
        </div>
    </footer>
    <script src="{prefix}main.js"></script>
</body>
</html>'''

def card(p, prefix):
    ex = html.escape(p['excerpt'][:75]) + ("…" if len(p['excerpt']) > 75 else "")
    return f'''<a class="card" href="{prefix}posts/{p['id']}.html">
                        <div class="card-img {p['img']}"><span class="{CAT[p['cat']]['badge']}">{p['tag']}</span></div>
                        <div class="card-body">
                            <time class="card-date">{p['date']}</time>
                            <h3 class="card-title">{html.escape(p['title'])}</h3>
                            <p class="card-excerpt">{ex}</p>
                        </div>
                    </a>'''

def write(path, content):
    open(os.path.join(REPO, path), "w", encoding="utf-8").write(content)

def org():
    return {"@type": "Organization", "name": SITE_NAME, "logo": {"@type": "ImageObject", "url": LOGO}}

# ---------- HOME ----------
def build_home():
    sections = ""
    for c in active_cats:
        cards = "\n                    ".join(card(p, "") for p in bycat[c["key"]][:3])
        sections += f'''
                <div class="section-header">
                    <h2>{c['home']}</h2>
                    <a href="{c['key']}.html" class="see-all">전체보기 &rarr;</a>
                </div>
                <div class="card-grid">
                    {cards}
                </div>'''
    featured = [p for c in active_cats for p in bycat[c["key"]][:3]]
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": BASE,
         "description": "여행·요리 이야기와 부동산·금융·정책 경제 칼럼"},
        {"@context": "https://schema.org", "@type": "ItemList",
         "itemListElement": [{"@type": "ListItem", "position": i+1, "url": BASE+f"posts/{p['id']}.html", "name": p['title']}
                             for i, p in enumerate(featured)]},
    ]
    out = head(f"{SITE_NAME} - 여행·요리 그리고 경제 칼럼",
               "여행과 요리 이야기, 그리고 부동산·금융·정책을 보는 경제 칼럼을 만나보세요.", BASE, "", jsonld=ld)
    out += nav("home", "")
    out += f'''
    <main class="main-content">
        <section class="page-block">
            <div class="hero">
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <p class="hero-sub">Travel &amp; Cook &amp; Life</p>
                    <h1 class="hero-title">여행하고, 요리하고,<br>세상을 이야기합니다</h1>
                    <p class="hero-desc">전 세계 여행기와 홈쿠킹 레시피,<br>그리고 부동산·금융·정책을 보는 나만의 시선.</p>
                    <div class="hero-buttons">
                        <a class="btn btn-primary" href="travel.html">여행 블로그</a>
                        <a class="btn btn-outline" href="food.html">요리 레시피</a>
                    </div>
                </div>
            </div>
            <div class="container">{sections}
            </div>
        </section>
    </main>'''
    out += footer("")
    write("index.html", out)

# ---------- LIST ----------
def list_page(c):
    items = bycat[c["key"]]
    cards = "\n                    ".join(card(p, "") for p in items)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{c['name']} - {SITE_NAME}",
          "url": BASE+f"{c['key']}.html",
          "hasPart": [{"@type": "Article", "headline": p['title'], "url": BASE+f"posts/{p['id']}.html",
                       "datePublished": p['iso']} for p in items]}
    out = head(f"{c['name']} - {SITE_NAME}", f"{SITE_NAME}의 {c['name']} 모음. {c['sub']}", BASE + f"{c['key']}.html", "", jsonld=ld)
    out += nav(c["key"], "")
    out += f'''
    <main class="main-content">
        <div class="page-hero {c['hero']}">
            <h1>{c['name']}</h1>
            <p>{c['sub']}</p>
        </div>
        <div class="container">
            <div class="card-grid card-grid-list">
                    {cards}
            </div>
        </div>
    </main>'''
    out += footer("")
    write(f"{c['key']}.html", out)

# ---------- POST ----------
def post_page(p, idx, siblings):
    desc = p['excerpt'][:150]
    og = img_urls.get(p['img'])
    url = BASE + f"posts/{p['id']}.html"
    c = CAT[p['cat']]
    cat_name, cat_url = c['name'], BASE + f"{p['cat']}.html"
    article_ld = {
        "@context": "https://schema.org", "@type": "Article", "headline": p['title'],
        "image": [og] if og else [], "datePublished": p['iso'], "dateModified": p['iso'],
        "author": {"@type": "Person", "name": SITE_NAME}, "publisher": org(),
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "description": desc,
        "articleSection": cat_name,
    }
    breadcrumb_ld = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": cat_url},
            {"@type": "ListItem", "position": 3, "name": p['title'], "item": url},
        ]}
    ld = [article_ld, breadcrumb_ld]
    if p['is_recipe'] and p['ingredients'] and p['steps']:
        ld.append({
            "@context": "https://schema.org", "@type": "Recipe", "name": p['title'],
            "image": [og] if og else [], "author": {"@type": "Person", "name": SITE_NAME},
            "datePublished": p['iso'], "description": desc,
            "recipeCategory": p['tag'], "recipeCuisine": p['tag'],
            "recipeIngredient": p['ingredients'],
            "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in p['steps']],
        })

    prev_p = siblings[idx-1] if idx > 0 else None
    next_p = siblings[idx+1] if idx < len(siblings)-1 else None
    list_href = f"../{p['cat']}.html"
    list_label = f"{cat_name} 목록"
    pn = '<div class="post-nav">'
    pn += f'<a class="post-nav-prev" href="{prev_p["id"]}.html">&larr; {html.escape(prev_p["title"])}</a>' if prev_p else '<span></span>'
    pn += f'<a class="post-nav-list" href="{list_href}">{list_label}</a>'
    pn += f'<a class="post-nav-next" href="{next_p["id"]}.html">{html.escape(next_p["title"])} &rarr;</a>' if next_p else '<span></span>'
    pn += '</div>'

    rel = [siblings[(idx+k) % len(siblings)] for k in range(1, 4) if len(siblings) > 1][:3]
    rel = [r for r in rel if r['id'] != p['id']][:3]
    rel_cards = "\n                    ".join(card(r, "../") for r in rel)
    related = f'''
            <section class="related">
                <h2 class="related-title">관련 글</h2>
                <div class="card-grid">
                    {rel_cards}
                </div>
            </section>''' if rel else ''

    out = head(f"{p['title']} - {SITE_NAME}", desc, url, "../", og, jsonld=ld)
    out += nav(p['cat'], "../")
    out += f'''
    <main class="main-content">
        <div class="container post-page">
            <nav class="breadcrumb"><a href="../index.html">홈</a> &rsaquo; <a href="{list_href}">{cat_name}</a> &rsaquo; <span>{html.escape(p['title'])}</span></nav>
            {p['html']}
            {pn}{related}
        </div>
    </main>'''
    out += footer("../")
    write(f"posts/{p['id']}.html", out)

build_home()
for c in active_cats:
    list_page(c)
    for i, p in enumerate(bycat[c["key"]]):
        post_page(p, i, bycat[c["key"]])

# ---------- favicon.svg ----------
write("favicon.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#e63946"/>
  <text x="32" y="42" font-size="34" text-anchor="middle" fill="#fff">&#9992;</text>
</svg>
''')

# ---------- 404.html ----------
nf = head("페이지를 찾을 수 없습니다 - " + SITE_NAME, "요청하신 페이지를 찾을 수 없습니다.", BASE+"404.html", "")
nf += nav("", "")
nf += '''
    <main class="main-content">
        <div class="container" style="text-align:center;padding:80px 24px;">
            <h1 style="font-size:72px;margin-bottom:8px;color:#e63946;">404</h1>
            <p style="font-size:20px;font-weight:700;margin-bottom:8px;">페이지를 찾을 수 없습니다</p>
            <p style="color:#888;margin-bottom:28px;">주소가 바뀌었거나 삭제된 페이지일 수 있어요.</p>
            <a class="btn btn-primary" href="/">홈으로 돌아가기</a>
        </div>
    </main>'''
nf += footer("")
write("404.html", nf)

# ---------- sitemap.xml ----------
static = [(BASE, "1.0")] + [(BASE+f"{c['key']}.html", "0.8") for c in active_cats] + \
         [(BASE+"about.html", "0.5"), (BASE+"privacy.html", "0.5"), (BASE+"contact.html", "0.5")]
newest = max((p['iso'] for p in posts), default="2026-07-01")
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, pr in static:
    sm += f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{newest}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{pr}</priority>\n  </url>\n'
for p in posts:
    sm += f'  <url>\n    <loc>{BASE}posts/{p["id"]}.html</loc>\n    <lastmod>{p["iso"]}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
sm += '</urlset>\n'
write("sitemap.xml", sm)

print(f"DONE: {len(posts)} posts across {len(active_cats)} categories regenerated.")
