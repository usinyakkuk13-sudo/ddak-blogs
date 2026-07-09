# -*- coding: utf-8 -*-
"""
든든한 노후 - 정적 사이트 생성기 (파이썬 표준 라이브러리만 사용)
사용법:  python3 build.py
결과:    public/ 폴더에 완성된 정적 HTML 사이트 생성 -> 그대로 배포
"""
import os, re, html, shutil, datetime, glob, sys, importlib.util

SITE = {}; CATEGORIES = []; CAT_NAME_TO_SLUG = {}
CONTENT_DIR = STATIC_DIR = OUT = ""

# 독자 사연 접수 구글 폼(모든 사이트 공용)
STORY_FORM_URL = "https://forms.gle/PZe2mrym4GFboeLX8"

def load_site(site_dir):
    global SITE, CATEGORIES, CAT_NAME_TO_SLUG, CONTENT_DIR, STATIC_DIR, OUT
    spec = importlib.util.spec_from_file_location("sitecfg", os.path.join(site_dir, "config.py"))
    cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
    SITE = cfg.SITE; CATEGORIES = cfg.CATEGORIES; CAT_NAME_TO_SLUG = cfg.CAT_NAME_TO_SLUG
    CONTENT_DIR = os.path.join(site_dir, "content")
    STATIC_DIR = os.path.join(site_dir, "static")
    OUT = os.path.join(site_dir, "public")

# ---------- 마크다운(부분집합) -> HTML ----------
def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text

def is_block_start(line):
    s = line.lstrip()
    return (line.startswith("#") or line.startswith(">") or line.startswith("|")
            or line.startswith("- ") or re.match(r"^\d+\.\s", line) or s.startswith("<"))

def md_to_html(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(md.split("\n"))
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1; continue
        # 제목
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:].strip())}</h3>"); i += 1; continue
        if line.startswith("## "):
            out.append(f"<h2>{inline(line[3:].strip())}</h2>"); i += 1; continue
        if line.startswith("# "):
            out.append(f"<h2>{inline(line[2:].strip())}</h2>"); i += 1; continue
        # 인용문
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            out.append("<blockquote><p>" + inline(" ".join(buf)) + "</p></blockquote>"); continue
        # 표
        if line.startswith("|"):
            buf = []
            while i < n and lines[i].startswith("|"):
                buf.append(lines[i]); i += 1
            rows = []
            for r in buf:
                if re.match(r"^\|[\s\-:|]+\|?\s*$", r):  # 구분선
                    continue
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                rows.append(cells)
            if rows:
                thead = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
                body = ""
                for r in rows[1:]:
                    body += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>")
            continue
        # 순서없는 목록
        if line.startswith("- "):
            buf = []
            while i < n and lines[i].startswith("- "):
                buf.append(f"<li>{inline(lines[i][2:].strip())}</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>"); continue
        # 순서있는 목록
        if re.match(r"^\d+\.\s", line):
            buf = []
            while i < n and re.match(r"^\d+\.\s", lines[i]):
                item = re.sub(r"^\d+\.\s", "", lines[i]).strip()
                buf.append(f"<li>{inline(item)}</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>"); continue
        # 원시 HTML (예: <div class=\"tip\">)
        if line.lstrip().startswith("<"):
            buf = []
            while i < n and lines[i].strip():
                buf.append(lines[i]); i += 1
            out.append("\n".join(buf)); continue
        # 문단
        buf = []
        while i < n and lines[i].strip() and not is_block_start(lines[i]):
            buf.append(lines[i].strip()); i += 1
        if buf:
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)

# ---------- front matter 파싱 ----------
def parse_post(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"front matter 없음: {path}")
    meta_block, body = m.group(1), m.group(2)
    meta = {}
    for ln in meta_block.split("\n"):
        if not ln.strip() or ":" not in ln:
            continue
        k, v = ln.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    meta["body_html"] = md_to_html(body.strip())
    meta["date_obj"] = datetime.date.fromisoformat(str(meta["date"]))
    return meta

# ---------- 템플릿 ----------
def nav_html():
    items = "".join(
        f'<a href="/category/{slug}/">{name}</a>' for slug, name, _ in CATEGORIES)
    return items

def head(title, description, path, og_type="website", published=None):
    full = title if title == SITE["name"] else f'{title} | {SITE["name"]}'
    canonical = SITE["url"] + path
    ads = ""
    if SITE["adsense_client"]:
        ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/'
               f'adsbygoogle.js?client={SITE["adsense_client"]}" crossorigin="anonymous"></script>\n'
               f'<meta name="google-adsense-account" content="{SITE["adsense_client"]}">')
    pub = f'<meta property="article:published_time" content="{published}">' if published else ""
    story_nav = (f'<a href="{STORY_FORM_URL}" class="nav-story" target="_blank" rel="noopener" style="border:1px solid currentColor;border-radius:999px;padding:4px 12px;font-weight:600;">✒️ 사연 보내기</a>') if SITE.get('accept_stories') else ''
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{html.escape(full)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:locale" content="ko_KR">
{pub}
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{SITE['name']}" href="/rss.xml">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/style.css">
{ads}
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="site-title">든든한 <span>노후</span></a>
<nav class="nav">{nav_html()}{story_nav}</nav>
</div></header>
<main>'''

def footer():
    story_foot = (f'<a href="{STORY_FORM_URL}" target="_blank" rel="noopener">✒️ 사연 보내기</a>') if SITE.get('accept_stories') else ''
    return f'''</main>
<footer class="site-footer"><div class="container">
<div class="fnav"><a href="/about/">소개</a><a href="/privacy/">개인정보처리방침</a><a href="/contact/">문의</a>{story_foot}</div>
<div>© {datetime.date.today().year} {SITE['name']}. 본 사이트 정보는 참고용이며, 정확한 내용은 관계 기관에 확인하시기 바랍니다.</div>
</div></footer>
</body></html>'''

def ad_block():
    if not SITE["adsense_client"]:
        return ""
    return ('<div class="ad-slot"><div class="ad-label">광고</div>'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{SITE["adsense_client"]}" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>')

def card(p):
    d = p["date_obj"].strftime("%Y년 %m월 %d일")
    return (f'<li class="post-card"><span class="cat">{p["category"]}</span>'
            f'<h2><a href="/posts/{p["slug"]}/">{html.escape(p["title"])}</a></h2>'
            f'<p>{html.escape(p["description"])}</p><div class="date">{d}</div></li>')

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

# ---------- 빌드 ----------
def build():
    if os.path.isdir(OUT):
        # 일부 마운트 파일시스템은 삭제(unlink)를 막지만 덮어쓰기는 허용한다.
        for f in os.listdir(OUT):
            fp = os.path.join(OUT, f)
            try:
                shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
            except (PermissionError, OSError):
                pass
    os.makedirs(OUT, exist_ok=True)

    posts = [parse_post(p) for p in glob.glob(os.path.join(CONTENT_DIR, "*.md"))]
    posts = [p for p in posts if p.get("draft", "false") != "true"]
    posts.sort(key=lambda p: p["date_obj"], reverse=True)

    # 개별 글
    for p in posts:
        d = p["date_obj"].strftime("%Y년 %m월 %d일")
        iso = p["date_obj"].isoformat()
        jsonld = (
            '<script type="application/ld+json">{'
            '"@context":"https://schema.org","@type":"Article",'
            f'"headline":{_j(p["title"])},"description":{_j(p["description"])},'
            f'"datePublished":"{iso}","dateModified":"{iso}",'
            f'"author":{{"@type":"Organization","name":{_j(SITE["author"])}}},'
            f'"publisher":{{"@type":"Organization","name":{_j(SITE["name"])}}},'
            f'"mainEntityOfPage":"{SITE["url"]}/posts/{p["slug"]}/"'
            '}</script>')
        body = (head(p["title"], p["description"], f'/posts/{p["slug"]}/', "article", iso)
                + jsonld
                + '<div class="container"><article class="post">'
                + f'<span class="cat">{p["category"]}</span>'
                + f'<h1>{html.escape(p["title"])}</h1>'
                + f'<div class="meta">📅 {d}</div>'
                + ad_block()
                + p["body_html"]
                + ad_block()
                + '<p class="disclaimer">※ 이 글은 일반적인 정보 제공을 위한 것으로, 개인별 상황에 따라 다를 수 있습니다. '
                  '정확한 내용은 관계 기관(정부24, 복지로, 국민연금공단 등)에서 확인하세요.</p>'
                + '<p style="margin-top:20px"><a href="/">← 다른 글 더 보기</a></p>'
                + '</article></div>' + footer())
        write(f'posts/{p["slug"]}/index.html', body)

    # 홈
    cards = "".join(card(p) for p in posts)
    home = (head(SITE["name"], SITE["tagline"], "/")
            + f'<section class="hero"><div class="container"><h1>{SITE["tagline"]}</h1>'
              f'<p>{SITE["subtitle"]}</p></div></section>'
            + f'<div class="container"><ul class="post-list">{cards}</ul></div>' + footer())
    write("index.html", home)

    # 카테고리
    for slug, name, desc in CATEGORIES:
        cp = [p for p in posts if p["category"] == name]
        cards = "".join(card(p) for p in cp) or "<p>아직 글이 없습니다.</p>"
        page = (head(name, desc, f"/category/{slug}/")
                + f'<section class="hero"><div class="container"><h1>{name}</h1><p>{desc}</p></div></section>'
                + f'<div class="container"><ul class="post-list">{cards}</ul></div>' + footer())
        write(f"category/{slug}/index.html", page)

    # 고정 페이지
    write("about/index.html", static_page("소개", "든든한 노후 사이트 소개", ABOUT_HTML))
    write("contact/index.html", static_page("문의", "든든한 노후 문의 안내", CONTACT_HTML()))
    write("privacy/index.html", static_page("개인정보처리방침", "개인정보처리방침 및 광고 안내", PRIVACY_HTML()))

    # sitemap / rss / robots / css
    write_sitemap(posts)
    write_rss(posts)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    shutil.copy(os.path.join(STATIC_DIR, "style.css"), os.path.join(OUT, "style.css"))
    # Cloudflare Pages가 .md 등을 건드리지 않도록 빈 파일 방지용 없음
    print(f"빌드 완료: 글 {len(posts)}개, 카테고리 {len(CATEGORIES)}개 -> public/")

def _j(s):
    import json
    return json.dumps(s, ensure_ascii=False)

def static_page(title, desc, inner):
    return (head(title, desc, f"/{_slug_of(title)}/")
            + '<div class="container"><article class="post">' + inner + "</article></div>" + footer())

def _slug_of(title):
    return {"소개": "about", "문의": "contact", "개인정보처리방침": "privacy"}[title]

def write_sitemap(posts):
    urls = ["/", "/about/", "/privacy/", "/contact/"]
    urls += [f"/category/{s}/" for s, _, _ in CATEGORIES]
    urls += [f'/posts/{p["slug"]}/' for p in posts]
    items = ""
    for u in urls:
        items += f"<url><loc>{SITE['url']}{u}</loc></url>\n"
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + items + "</urlset>\n")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(xml)

def write_rss(posts):
    items = ""
    for p in posts[:20]:
        pub = datetime.datetime.combine(p["date_obj"], datetime.time()).strftime("%a, %d %b %Y %H:%M:%S +0900")
        items += (f"<item><title>{html.escape(p['title'])}</title>"
                  f"<link>{SITE['url']}/posts/{p['slug']}/</link>"
                  f"<description>{html.escape(p['description'])}</description>"
                  f"<pubDate>{pub}</pubDate>"
                  f"<guid>{SITE['url']}/posts/{p['slug']}/</guid></item>\n")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
           f"<title>{SITE['name']}</title><link>{SITE['url']}</link>"
           f"<description>{SITE['tagline']}</description><language>ko</language>\n"
           + items + "</channel></rss>\n")
    open(os.path.join(OUT, "rss.xml"), "w", encoding="utf-8").write(xml)

ABOUT_HTML = '''<h1>사이트 소개</h1>
<p><strong>든든한 노후</strong>는 60대 이상 어르신과 그 가족을 위해 만든 생활정보 사이트입니다. 연금과 복지 혜택, 건강 관리, 스마트폰 사용법처럼 꼭 필요하지만 찾기 어려운 정보를 <strong>큰 글씨로, 쉬운 말로</strong> 정리해 드립니다.</p>
<h2>우리가 다루는 정보</h2>
<ul>
<li><strong>연금·복지</strong> — 기초연금, 국민연금, 정부지원금 신청 방법과 혜택</li>
<li><strong>건강</strong> — 노년 건강관리, 질병 예방, 국가건강검진</li>
<li><strong>스마트폰</strong> — 카카오톡, 유튜브, 유용한 앱을 쉽게 쓰는 법</li>
<li><strong>생활정보</strong> — 어르신 할인·혜택 등 실생활 정보</li>
</ul>
<p>모든 글은 공신력 있는 자료를 바탕으로 작성하되, 실제 신청·이용 전에는 반드시 관계 기관에서 최신 내용을 확인하시길 권합니다.</p>'''

def CONTACT_HTML():
    return f'''<h1>문의하기</h1>
<p>사이트 내용에 대한 문의, 정정 요청, 제휴 제안은 아래 이메일로 보내주세요.</p>
<p style="font-size:22px"><strong>이메일:</strong> <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
<p>정확하고 도움되는 정보를 전하기 위해 늘 노력하겠습니다.</p>'''

def PRIVACY_HTML():
    return f'''<h1>개인정보처리방침</h1>
<p>든든한 노후(이하 '사이트')는 이용자의 개인정보를 소중히 다룹니다. 본 방침은 사이트가 정보를 어떻게 수집·이용하는지 안내합니다.</p>
<h2>1. 수집하는 정보</h2>
<p>사이트는 회원가입 절차가 없으며 이름, 연락처 등 개인을 식별하는 정보를 직접 수집하지 않습니다. 다만 방문 통계 및 광고 제공을 위해 쿠키(cookie)와 접속 기록이 자동으로 수집될 수 있습니다.</p>
<h2>2. 광고 및 쿠키 (Google AdSense)</h2>
<p>본 사이트는 제3자 광고 서비스인 <strong>Google AdSense</strong>를 사용합니다. Google을 비롯한 제3자 공급업체는 쿠키를 사용하여 이용자의 이전 방문 기록을 바탕으로 광고를 게재합니다.</p>
<ul>
<li>Google은 광고 쿠키를 사용하여 이용자에게 맞춤형 광고를 제공합니다.</li>
<li>이용자는 <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google 광고 설정</a>에서 맞춤 광고를 해제할 수 있습니다.</li>
<li>제3자 공급업체의 쿠키 사용은 <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener">Google 광고 정책</a>에서 확인할 수 있습니다.</li>
</ul>
<h2>3. 접속 분석</h2>
<p>사이트는 서비스 개선을 위해 방문자 수, 페이지뷰 등 통계 정보를 익명으로 분석할 수 있습니다.</p>
<h2>4. 문의</h2>
<p>개인정보 관련 문의는 <a href="mailto:{SITE['email']}">{SITE['email']}</a>로 연락 주시기 바랍니다.</p>
<p style="color:#888;font-size:16px">시행일: 2026년 7월 6일</p>'''


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    load_site(target)
    build()
    print("빌드:", target)
