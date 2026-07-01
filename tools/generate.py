#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEO pass: JSON-LD structured data, related-posts internal links, favicon, 404.
Idempotent — reads the <article> content from posts/*.html and fully regenerates
each page from templates (structured data lives outside the article block)."""
import re, os, glob, html, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root, portable
BASE = "https://jangwonh01.github.io/"
SITE_NAME = "여행하는 요리사 JUHWANDAD"
LOGO = BASE + "favicon.svg"

css = open(os.path.join(REPO, "style.css"), encoding="utf-8").read()
img_urls = {}
for m in re.finditer(r"\.((?:travel|food)-img-\d+)\s*\{[^}]*url\('([^']+)'\)", css):
    img_urls[m.group(1)] = m.group(2)

def to_iso(kdate):
    m = re.match(r'(\d+)년\s*(\d+)월\s*(\d+)일', kdate)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

def strip(t): return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()

def num(pid): return int(pid.split('-')[1])

posts = []
for f in glob.glob(os.path.join(REPO, "posts", "*.html")):
    src = open(f, encoding="utf-8").read()
    a = re.search(r'<article class="post.*?</article>', src, re.S).group(0)
    pid = re.search(r'id="([^"]+)"', a).group(1)
    imgcls = f"{'travel' if pid.startswith('travel') else 'food'}-img-{int(pid.split('-')[1])}"
    tag = re.search(r'<span class="post-tag[^"]*">([^<]+)</span>', a).group(1)
    title = re.search(r'<h2 class="post-title">([^<]+)</h2>', a).group(1)
    date = re.search(r'<time>([^<]+)</time>', a).group(1)
    first_p = re.search(r'<p>(.*?)</p>', a, re.S).group(1)
    excerpt = strip(first_p)
    cat = 'travel' if pid.startswith('travel') else 'food'
    is_recipe = 'recipe-post' in a
    ingredients = [strip(x) for x in re.findall(r'<div class="ingredient-box">.*?</div>', a, re.S) for x in re.findall(r'<li>(.*?)</li>', x, re.S)]
    steps = [strip(x) for block in re.findall(r'<ol class="recipe-steps">(.*?)</ol>', a, re.S) for x in re.findall(r'<li>(.*?)</li>', block, re.S)]
    posts.append(dict(id=pid, img=imgcls, tag=tag, title=title, date=date, iso=to_iso(date),
                      excerpt=excerpt, cat=cat, html=a, is_recipe=is_recipe,
                      ingredients=ingredients, steps=steps))

posts.sort(key=lambda p: (p['cat'], num(p['id'])))
travel = [p for p in posts if p['cat'] == 'travel']
food = [p for p in posts if p['cat'] == 'food']

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
    <meta name="keywords" content="여행 블로그, 요리 레시피, 세계여행, 홈쿠킹, 맛집, 여행 팁, JUHWANDAD">
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
                {link("travel.html","여행","travel")}
                {link("food.html","요리","food")}
                {link("about.html","소개","about")}
                {link("contact.html","문의","contact")}
            </div>
        </div>
    </nav>
'''

def footer(prefix):
    return f'''
    <footer class="site-footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <h4>{SITE_NAME}</h4>
                    <p>세계를 여행하고, 그 맛을 요리합니다.</p>
                </div>
                <div class="footer-col">
                    <h4>카테고리</h4>
                    <ul>
                        <li><a href="{prefix}travel.html">여행 블로그</a></li>
                        <li><a href="{prefix}food.html">요리 레시피</a></li>
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
    badge_cls = "card-badge badge-food" if p['cat'] == 'food' else "card-badge"
    ex = html.escape(p['excerpt'][:75]) + ("…" if len(p['excerpt']) > 75 else "")
    return f'''<a class="card" href="{prefix}posts/{p['id']}.html">
                        <div class="card-img {p['img']}"><span class="{badge_cls}">{p['tag']}</span></div>
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
    feat_t = "\n                    ".join(card(p, "") for p in travel[:3])
    feat_f = "\n                    ".join(card(p, "") for p in food[:3])
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": BASE,
         "description": "여행과 요리를 사랑하는 블로거의 세계 여행기와 홈쿠킹 레시피"},
        {"@context": "https://schema.org", "@type": "ItemList",
         "itemListElement": [{"@type": "ListItem", "position": i+1, "url": BASE+f"posts/{p['id']}.html", "name": p['title']}
                             for i, p in enumerate(travel[:3] + food[:3])]},
    ]
    out = head(f"{SITE_NAME} - 세계를 여행하고, 그 맛을 요리합니다",
               "여행과 요리를 사랑하는 블로거의 세계 여행기와 홈쿠킹 레시피를 만나보세요.", BASE, "", jsonld=ld)
    out += nav("home", "")
    out += f'''
    <main class="main-content">
        <section class="page-block">
            <div class="hero">
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <p class="hero-sub">Travel &amp; Cook</p>
                    <h1 class="hero-title">세계를 여행하고,<br>그 맛을 요리합니다</h1>
                    <p class="hero-desc">전 세계 곳곳의 여행 이야기와<br>집에서 재현하는 현지 레시피를 공유합니다.</p>
                    <div class="hero-buttons">
                        <a class="btn btn-primary" href="travel.html">여행 블로그</a>
                        <a class="btn btn-outline" href="food.html">요리 레시피</a>
                    </div>
                </div>
            </div>
            <div class="container">
                <div class="section-header">
                    <h2>최신 여행기</h2>
                    <a href="travel.html" class="see-all">전체보기 &rarr;</a>
                </div>
                <div class="card-grid">
                    {feat_t}
                </div>
                <div class="section-header">
                    <h2>인기 레시피</h2>
                    <a href="food.html" class="see-all">전체보기 &rarr;</a>
                </div>
                <div class="card-grid">
                    {feat_f}
                </div>
            </div>
        </section>
    </main>'''
    out += footer("")
    write("index.html", out)

# ---------- LIST ----------
def list_page(cat, items, hero_cls, h1, sub, active):
    cards = "\n                    ".join(card(p, "") for p in items)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{h1} - {SITE_NAME}",
          "url": BASE+f"{cat}.html",
          "hasPart": [{"@type": "Article", "headline": p['title'], "url": BASE+f"posts/{p['id']}.html",
                       "datePublished": p['iso']} for p in items]}
    out = head(f"{h1} - {SITE_NAME}", f"{SITE_NAME}의 {h1} 모음. {sub}", BASE + f"{cat}.html", "", jsonld=ld)
    out += nav(active, "")
    out += f'''
    <main class="main-content">
        <div class="page-hero {hero_cls}">
            <h1>{h1}</h1>
            <p>{sub}</p>
        </div>
        <div class="container">
            <div class="card-grid card-grid-list">
                    {cards}
            </div>
        </div>
    </main>'''
    out += footer("")
    write(f"{cat}.html", out)

# ---------- POST ----------
def post_page(p, idx, siblings):
    desc = p['excerpt'][:150]
    og = img_urls.get(p['img'])
    url = BASE + f"posts/{p['id']}.html"
    cat_name = "여행" if p['cat'] == 'travel' else "요리"
    cat_url = BASE + ("travel.html" if p['cat'] == 'travel' else "food.html")
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
    list_href = "../travel.html" if p['cat'] == 'travel' else "../food.html"
    list_label = "여행 목록" if p['cat'] == 'travel' else "요리 목록"
    pn = '<div class="post-nav">'
    pn += f'<a class="post-nav-prev" href="{prev_p["id"]}.html">&larr; {html.escape(prev_p["title"])}</a>' if prev_p else '<span></span>'
    pn += f'<a class="post-nav-list" href="{list_href}">{list_label}</a>'
    pn += f'<a class="post-nav-next" href="{next_p["id"]}.html">{html.escape(next_p["title"])} &rarr;</a>' if next_p else '<span></span>'
    pn += '</div>'

    # related: up to 3 other same-category posts (cyclic)
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

    crumb = list_label.replace(" 목록", "")
    out = head(f"{p['title']} - {SITE_NAME}", desc, url, "../", og, jsonld=ld)
    out += nav(p['cat'], "../")
    out += f'''
    <main class="main-content">
        <div class="container post-page">
            <nav class="breadcrumb"><a href="../index.html">홈</a> &rsaquo; <a href="{list_href}">{crumb}</a> &rsaquo; <span>{html.escape(p['title'])}</span></nav>
            {p['html']}
            {pn}{related}
        </div>
    </main>'''
    out += footer("../")
    write(f"posts/{p['id']}.html", out)

build_home()
list_page("travel", travel, "travel-hero", "여행 블로그", "발길 닿는 곳마다 새로운 이야기", "travel")
list_page("food", food, "food-hero", "요리 레시피", "집에서 만드는 전 세계의 맛", "food")
for i, p in enumerate(travel): post_page(p, i, travel)
for i, p in enumerate(food): post_page(p, i, food)

# ---------- favicon.svg ----------
favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#e63946"/>
  <text x="32" y="42" font-size="34" text-anchor="middle" fill="#fff">&#9992;</text>
</svg>
'''
write("favicon.svg", favicon)

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

print(f"DONE: JSON-LD + related + favicon + 404 applied to {len(posts)} posts and all pages.")
