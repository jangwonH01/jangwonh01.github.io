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

# Firebase-backed comments. The section stays hidden until comments.js confirms
# a valid Firebase config (edit firebase-config.js), then it reveals + loads.
def comments_html(post_id, prefix):
    return f'''
            <section class="comments" id="comments" data-post-id="{post_id}" hidden>
                <h2 class="related-title">댓글 <span id="c-count"></span></h2>
                <form id="comment-form" class="comment-form">
                    <input id="c-name" class="c-name" maxlength="20" placeholder="이름" autocomplete="name" required>
                    <textarea id="c-text" class="c-text" maxlength="500" placeholder="댓글을 남겨주세요" required></textarea>
                    <div class="c-actions"><button type="submit" class="c-submit">댓글 남기기</button></div>
                    <p id="c-msg" class="c-msg"></p>
                </form>
                <div id="comment-list" class="comment-list"></div>
                <div id="comment-pagination" class="comment-pagination"></div>
            </section>
            <script type="module" src="{prefix}comments.js"></script>'''

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

    comments = comments_html(p['id'], "../")

    out = head(f"{p['title']} - {SITE_NAME}", desc, url, "../", og, jsonld=ld)
    out += nav(p['cat'], "../")
    out += f'''
    <main class="main-content">
        <div class="container post-page">
            <nav class="breadcrumb"><a href="../index.html">홈</a> &rsaquo; <a href="{list_href}">{cat_name}</a> &rsaquo; <span>{html.escape(p['title'])}</span></nav>
            {p['html']}
            {pn}{related}{comments}
        </div>
    </main>'''
    out += footer("../")
    write(f"posts/{p['id']}.html", out)

build_home()
for c in active_cats:
    list_page(c)
    for i, p in enumerate(bycat[c["key"]]):
        post_page(p, i, bycat[c["key"]])

# ---------- static pages (about / privacy / contact) ----------
def build_page(fname, title, desc, active, body):
    out = head(f"{title} - {SITE_NAME}", desc, BASE + fname, "")
    out += nav(active, "")
    out += body
    out += footer("")
    write(fname, out)

ABOUT_BODY = '''
    <main class="main-content">
        <div class="container">
                <div class="about-card">
                    <h1>여행하는 요리사 JUHWANDAD</h1>
                    <p class="about-tagline">세계를 여행하고, 그 맛을 재현하고, 세상을 읽습니다.</p>
                    <div class="about-body">
                        <p>안녕하세요! 여행과 요리를 사랑하는 블로거입니다. 새로운 도시를 걷고, 현지의 맛을 경험하고, 그 레시피를 집에서 재현하는 것이 저의 가장 큰 즐거움입니다.</p>
                        <p>10년간 20개국 이상을 여행하며, 각 나라의 음식 문화를 직접 체험했습니다. 교토의 골목길에서 만난 말차의 향기, 바르셀로나 시장에서 맛본 하몬의 감칠맛, 치앙마이 야시장의 카오소이 한 그릇까지 - 모든 여행은 미각의 기억으로 남아있습니다.</p>
                        <p>이 블로그에서는 제가 직접 다녀온 여행지의 솔직한 후기와, 여행에서 영감받은 레시피를 공유합니다. 화려한 레스토랑보다는 현지인이 사랑하는 소박한 맛집을, 복잡한 레시피보다는 집에서 쉽게 따라 할 수 있는 요리를 소개해드립니다.</p>
                        <p>여기에 더해, <strong>부동산·금융·정책 등 경제 이슈에 대한 개인적인 견해</strong>를 담은 <strong>경제 칼럼</strong>도 연재합니다. 여행과 요리로 일상을 즐기는 한편, 세상 돌아가는 흐름도 함께 짚어보려 합니다.</p>
                        <h3>이 블로그에서 만날 수 있는 것들</h3>
                        <ul>
                            <li>세계 각국의 여행 후기와 현지 팁</li>
                            <li>여행지에서 영감받은 홈쿠킹 레시피</li>
                            <li>초보자도 따라 할 수 있는 단계별 요리법</li>
                            <li>부동산·금융·정책을 다루는 경제 칼럼</li>
                        </ul>
                    </div>
                </div>

                <div class="about-card">
                    <h2>경제 칼럼에 대하여</h2>
                    <div class="about-body">
                        <p>경제 칼럼은 부동산·금융·정책 등 우리 삶에 직접 영향을 주는 이슈를 다룹니다. 단순한 뉴스 요약이 아니라, 시장의 흐름을 저 나름의 시각으로 해석하고 앞으로를 전망하는 글입니다. 2주에 한 번을 목표로 꾸준히 연재하려 합니다.</p>
                        <p>다만 모든 칼럼은 <strong>필자 개인의 견해와 전망</strong>이며, 특정 투자나 매매를 권유하지 않습니다. 시장은 예측과 다르게 움직일 수 있으니, 투자 판단은 반드시 본인 책임하에 최신 정보를 확인해 결정하시기 바랍니다.</p>
                        <p><a href="column.html">경제 칼럼 전체 보기 &rarr;</a></p>
                    </div>
                </div>
        </div>
    </main>'''

PRIVACY_BODY = '''
    <main class="main-content">
        <div class="container">
                <div class="about-card" id="privacy">
                    <h1>개인정보처리방침</h1>
                    <div class="about-body">
                        <p>본 웹사이트는 방문자의 개인정보를 소중히 여기며, 관련 법률을 준수합니다.</p>
                        <h3>수집하는 정보</h3>
                        <p>본 웹사이트는 Google Analytics 및 Google AdSense를 통해 비개인적인 방문 데이터(페이지 조회수, 체류 시간, 기기 정보 등)를 수집할 수 있습니다. 이 데이터는 웹사이트 개선 및 맞춤형 광고 제공을 위해 사용됩니다.</p>
                        <h3>쿠키 사용</h3>
                        <p>본 웹사이트는 서비스 제공 및 광고 표시를 위해 쿠키를 사용합니다. 브라우저 설정에서 쿠키 사용을 관리할 수 있습니다.</p>
                        <h3>댓글 기능</h3>
                        <p>본 사이트의 댓글은 Google Firebase(Firestore)에 저장되며, 작성 시 입력한 이름과 내용이 공개적으로 표시됩니다. 개인정보(전화번호·주소 등)는 댓글에 남기지 마세요.</p>
                        <h3>Google AdSense 및 제3자 광고</h3>
                        <p>Google을 포함한 제3자 광고 사업자는 쿠키를 사용하여 사용자의 이전 방문 기록에 기반한 광고를 게재합니다. Google이 광고 쿠키를 사용함으로써 사용자에게 관심 기반 광고를 제공할 수 있습니다. 사용자는 <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google 광고 설정</a>에서 맞춤 광고를 비활성화할 수 있으며, <a href="https://www.aboutads.info" target="_blank" rel="noopener">www.aboutads.info</a>에서 제3자 쿠키 사용을 거부할 수 있습니다.</p>
                        <h3>문의</h3>
                        <p>개인정보처리방침에 관한 문의사항이 있으시면 <a href="contact.html">문의하기</a> 페이지 또는 이메일(jang1red@naver.com)로 연락해주세요.</p>
                        <p><em>최종 수정일: 2026년 7월 2일</em></p>
                    </div>
                </div>

                <div class="about-card" id="site-policy">
                    <h2>운영정책 · 광고 고지 · 이용안내</h2>
                    <div class="about-body">
                        <h3>광고 및 제휴 고지</h3>
                        <p>본 사이트는 운영비 충당을 위해 Google AdSense 등 광고를 포함할 수 있습니다. 일부 링크는 제휴 링크일 수 있으며, 해당 링크를 통한 구매 시 일정 수수료를 받을 수 있습니다. 단, 콘텐츠의 평가와 의견은 독립적으로 작성됩니다.</p>
                        <h3>콘텐츠 이용 안내</h3>
                        <p>본 사이트의 글/이미지/코드는 저작권 보호를 받습니다. 사전 동의 없는 무단 복제, 재배포, 상업적 이용을 금지합니다. 인용 시에는 출처를 명시해 주세요.</p>
                        <h3>면책 조항</h3>
                        <p>여행·요리·경제·생활 정보는 개인 경험과 조사 기반이며, 정확성을 위해 노력하지만 절대적 완전성을 보장하지 않습니다. 특히 부동산·금융·정책 등 경제 칼럼은 필자 개인의 견해이며 투자 권유가 아닙니다. 투자·건강·법률 등 의사결정은 반드시 본인 판단과 전문가 자문을 병행해 주세요.</p>
                        <h3>문의 채널</h3>
                        <p>정책 및 콘텐츠 관련 문의는 <a href="contact.html">문의하기</a> 페이지 또는 이메일(jang1red@naver.com)로 연락해 주세요.</p>
                        <p><em>최종 수정일: 2026년 7월 2일</em></p>
                    </div>
                </div>
        </div>
    </main>'''

CONTACT_BODY = '''
    <main class="main-content">
        <div class="page-hero contact-hero">
            <h1>문의하기</h1>
            <p>궁금한 점이나 제안이 있으시면 편하게 연락해주세요</p>
        </div>
        <div class="container">
            <div class="contact-grid">
                <div class="contact-card">
                    <h2>메시지 보내기</h2>
                    <p>아래 양식을 작성하면 메일 앱으로 연결됩니다.</p>
                    <form id="contact-form">
                        <div class="form-group">
                            <label for="contact-name">이름 *</label>
                            <input type="text" id="contact-name" required placeholder="이름을 입력하세요">
                        </div>
                        <div class="form-group">
                            <label for="contact-email">이메일 *</label>
                            <input type="email" id="contact-email" required placeholder="example@email.com">
                        </div>
                        <div class="form-group">
                            <label for="contact-subject">문의 유형</label>
                            <select id="contact-subject">
                                <option value="일반 문의">일반 문의</option>
                                <option value="여행 관련">여행 관련</option>
                                <option value="레시피 관련">레시피 관련</option>
                                <option value="경제 칼럼 관련">경제 칼럼 관련</option>
                                <option value="협업/제휴">협업/제휴</option>
                                <option value="기타">기타</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="contact-message">메시지 *</label>
                            <textarea id="contact-message" required placeholder="문의 내용을 자세히 적어주세요"></textarea>
                        </div>
                        <button type="submit" class="submit-btn" id="contact-submit">보내기</button>
                        <div id="contact-form-message" class="form-message"></div>
                    </form>
                </div>
                <div class="contact-card">
                    <h2>연락처 정보</h2>
                    <p>다양한 채널로 소통하고 있습니다.</p>
                    <div class="contact-info-item">
                        <div class="contact-info-icon">&#9993;</div>
                        <div class="contact-info-text">
                            <h4>이메일</h4>
                            <p><a href="mailto:jang1red@naver.com">jang1red@naver.com</a></p>
                        </div>
                    </div>
                    <div class="contact-info-item">
                        <div class="contact-info-icon">&#9998;</div>
                        <div class="contact-info-text">
                            <h4>블로그 운영 시간</h4>
                            <p>월~금 10:00 - 18:00<br>문의 답변은 24시간 이내</p>
                        </div>
                    </div>
                    <div class="contact-info-item">
                        <div class="contact-info-icon">&#127758;</div>
                        <div class="contact-info-text">
                            <h4>협업 문의</h4>
                            <p>여행/요리/경제 관련 브랜드 협업, 원고 기고, 영상 출연 등 다양한 협업을 환영합니다.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>'''

build_page("about.html", "소개", "여행하는 요리사 JUHWANDAD 소개 — 여행·요리 이야기와 부동산·금융·정책 경제 칼럼을 연재합니다.", "about", ABOUT_BODY)
build_page("privacy.html", "개인정보처리방침", "개인정보처리방침, 쿠키·댓글·Google AdSense 광고 고지 및 운영정책 안내.", "", PRIVACY_BODY)
build_page("contact.html", "문의하기", "여행·요리·경제 칼럼 관련 문의와 협업 제안은 이메일 또는 문의 양식으로 연락주세요.", "contact", CONTACT_BODY)

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
