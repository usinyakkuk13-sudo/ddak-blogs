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

# ---------- 공식 출처(확인처) 매핑 ----------
# YMYL(연금·복지·건강·금융) 글은 근거가 되는 공식 기관 링크를 반드시 노출한다.
# 사이트 config.py 에 SOURCE_PACK = "senior" 가 있을 때만 적용된다.
SOURCE_PACKS = {
    "senior": {
        # 키워드 -> [(기관명, URL, 안내문)]
        "keywords": [
            (("기초연금",), ("보건복지부 기초연금", "https://basicpension.mohw.go.kr/", "선정기준액·모의계산·신청")),
            (("국민연금", "노령연금", "유족연금", "분할연금", "반납", "추납", "임의가입"),
             ("국민연금공단", "https://www.nps.or.kr/", "내 연금 조회·상담 국번없이 1355")),
            (("장기요양", "요양보호사", "요양등급", "재가급여", "가족요양"),
             ("국민건강보험공단 노인장기요양보험", "https://www.longtermcare.or.kr/", "등급신청·급여 안내 1577-1000")),
            (("건강보험", "본인부담", "피부양자", "임의계속"),
             ("국민건강보험공단", "https://www.nhis.or.kr/", "자격·보험료 상담 1577-1000")),
            (("건강검진", "국가검진"), ("건강iN 검진 안내", "https://www.nhis.or.kr/", "검진 대상 조회")),
            (("암검진", "암 검진", "국가암"), ("국가암정보센터", "https://www.cancer.go.kr/", "검진 주기·비용")),
            (("치매",), ("중앙치매센터", "https://www.nid.or.kr/", "치매상담콜센터 1899-9988")),
            (("예방접종", "백신", "대상포진", "독감", "인플루엔자", "폐렴구균"),
             ("질병관리청 예방접종도우미", "https://nip.kdca.go.kr/", "무료 접종 대상·지정 의료기관 찾기")),
            (("생계급여", "의료급여", "주거급여", "기초생활", "차상위", "긴급복지"),
             ("복지로", "https://www.bokjiro.go.kr/", "복지 모의계산·온라인 신청, 129")),
            (("주택연금",), ("한국주택금융공사", "https://www.hf.go.kr/", "예상 월지급금 조회 1688-8114")),
            (("농지연금",), ("농지은행 농지연금", "https://www.fbo.or.kr/", "가입 조건·수령액 조회 1577-7770")),
            (("주민등록", "정부24", "등본", "인감"), ("정부24", "https://www.gov.kr/", "민원 발급·정부 서비스 1588-2188")),
            (("법률", "상속", "유언", "후견"), ("대한법률구조공단", "https://www.klac.or.kr/", "무료 법률상담 132")),
            (("문화누리",), ("문화누리카드", "https://www.mnuri.kr/", "발급·잔액 조회 1544-3412")),
            (("코레일", "기차", "철도"), ("코레일", "https://www.letskorail.com/", "경로 할인·예매")),
            (("알뜰폰",), ("알뜰폰 허브", "https://www.mvnohub.kr/", "요금제 비교")),
            (("디지털배움터",), ("디지털배움터", "https://www.디지털배움터.kr/", "무료 교육 신청 1800-0096")),
            (("에너지바우처",), ("에너지바우처", "https://www.energyv.or.kr/", "신청·잔액 조회 1600-3190")),
            (("보이스피싱", "사기", "명의도용", "금융"), ("금융감독원", "https://www.fss.or.kr/", "금융 민원·상담 1332")),
            (("노인일자리", "일자리"), ("노인일자리 여기", "https://www.seniorro.or.kr/", "지역별 일자리 조회")),
            (("연명의료", "사전연명"), ("국립연명의료관리기관", "https://www.lst.go.kr/", "등록기관 찾기 1855-0075")),
        ],
        # 카테고리 기본 출처(키워드가 안 걸려도 최소 1개는 붙는다)
        "defaults": {
            "연금·복지": ("복지로", "https://www.bokjiro.go.kr/", "복지 모의계산·온라인 신청, 보건복지상담센터 129"),
            "건강": ("질병관리청 국가건강정보포털", "https://health.kdca.go.kr/", "질환별 표준 건강정보"),
            "스마트폰": ("디지털배움터", "https://www.디지털배움터.kr/", "어르신 무료 스마트폰 교육 1800-0096"),
            "생활정보": ("정부24", "https://www.gov.kr/", "정부 민원·혜택 통합 안내 1588-2188"),
        },
    }
}

def sources_html(p):
    """글 내용에 맞는 공식 확인처 목록을 만든다."""
    pack = SOURCE_PACKS.get(SITE.get("source_pack") or "")
    if not pack:
        return ""
    haystack = (p.get("title", "") + " " + p.get("description", "") + " "
                + " ".join(p.get("tags", [])) + " " + p.get("body_html", ""))
    picked, seen = [], set()
    for words, src in pack["keywords"]:
        if any(w in haystack for w in words) and src[1] not in seen:
            seen.add(src[1]); picked.append(src)
    d = pack["defaults"].get(p.get("category"))
    if d and d[1] not in seen:
        seen.add(d[1]); picked.append(d)
    if not picked:
        return ""
    lis = "".join(
        f'<li><a href="{u}" target="_blank" rel="noopener nofollow">{html.escape(n)}</a>'
        f' — {html.escape(memo)}</li>' for n, u, memo in picked[:5])
    return ('<section class="sources"><h2>정확한 내용은 여기서 확인하세요</h2>'
            '<p>금액·기준은 해마다 바뀝니다. 신청 전에 아래 공식 기관에서 최신 내용을 꼭 확인해 주세요.</p>'
            f'<ul>{lis}</ul></section>')

def related_html(p, posts):
    """같은 분야 글 4개를 연결한다."""
    same = [q for q in posts if q["category"] == p["category"] and q["slug"] != p["slug"]]
    if len(same) < 2:
        same = [q for q in posts if q["slug"] != p["slug"]]
    if not same:
        return ""
    pick = same[:4]
    lis = "".join(f'<li><a href="/posts/{q["slug"]}/">{html.escape(q["title"])}</a></li>' for q in pick)
    return (f'<section class="related"><h2>함께 보면 좋은 글</h2><ul>{lis}</ul>'
            f'<p><a href="/category/{CAT_NAME_TO_SLUG.get(p["category"], "")}/">'
            f'{html.escape(p["category"])} 글 전체 보기 →</a></p></section>')

def load_site(site_dir):
    global SITE, CATEGORIES, CAT_NAME_TO_SLUG, CONTENT_DIR, STATIC_DIR, OUT
    spec = importlib.util.spec_from_file_location("sitecfg", os.path.join(site_dir, "config.py"))
    cfg = importlib.util.module_from_spec(spec); spec.loader.exec_module(cfg)
    SITE = cfg.SITE; CATEGORIES = cfg.CATEGORIES; CAT_NAME_TO_SLUG = getattr(cfg, "CAT_NAME_TO_SLUG", None) or {n: sl for sl, n, _ in cfg.CATEGORIES}
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
    ga = ""
    if SITE.get("ga_id"):
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={SITE["ga_id"]}"></script>\n'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
              f"gtag('js',new Date());gtag('config','{SITE['ga_id']}');</script>")
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
{ga}
{ads}
</head>
<body>
<header class="site-header"><div class="container">
<a href="/" class="site-title">{SITE['name']}</a>
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
    # 드립 공개: 오늘 날짜가 된 글만 게시(미래 날짜 글은 대기)
    _today = datetime.date.today()
    posts = [p for p in posts if p["date_obj"] <= _today]
    # 안전장치: config에 없는 카테고리는 첫 카테고리로 자동 교정(폐지된 카테고리 방지)
    _valid = {n for _, n, _ in CATEGORIES}
    for _p in posts:
        if _p.get("category") not in _valid:
            _p["category"] = CATEGORIES[0][1]
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
        cat_slug = CAT_NAME_TO_SLUG.get(p["category"], "")
        body = (head(p["title"], p["description"], f'/posts/{p["slug"]}/', "article", iso)
                + jsonld
                + '<div class="container"><article class="post">'
                + f'<a class="cat" href="/category/{cat_slug}/">{p["category"]}</a>'
                + f'<h1>{html.escape(p["title"])}</h1>'
                + f'<div class="meta">📅 {d} 작성 · 최종 확인 {_today.strftime("%Y년 %m월 %d일")}'
                  f' · <a href="/about/">{html.escape(SITE["author"])}</a></div>'
                + p["body_html"]
                + ad_block()
                + sources_html(p)
                + '<p class="disclaimer">※ 이 글은 일반적인 정보 제공을 위한 것으로, 제도·금액·기준은 개인 상황과 시점에 따라 달라집니다. '
                  '의료·법률·금융에 관한 개별 판단은 담당 기관이나 전문가와 상의하세요. '
                  '내용에 잘못된 부분이 있으면 <a href="/contact/">문의 페이지</a>로 알려주시면 확인 후 바로잡겠습니다.</p>'
                + related_html(p, posts)
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
    write("about/index.html", static_page("소개", f"{SITE['name']} 소개", ABOUT_HTML()))
    write("contact/index.html", static_page("문의", f"{SITE['name']} 문의", CONTACT_HTML()))
    write("privacy/index.html", static_page("개인정보처리방침", "개인정보처리방침 및 광고 안내", PRIVACY_HTML()))

    # sitemap / rss / robots / css
    write_sitemap(posts)
    write_rss(posts)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    # ads.txt : 애드센스 승인·수익화에 필요 (client가 ca-pub-XXXX 형태일 때만 출력)
    if SITE.get("adsense_client"):
        pub_id = SITE["adsense_client"].replace("ca-", "")  # ca-pub-XXX -> pub-XXX
        open(os.path.join(OUT, "ads.txt"), "w", encoding="utf-8").write(
            f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n")

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

def ABOUT_HTML():
    cats = "".join(f"<li><strong>{n}</strong> — {d}</li>" for _, n, d in CATEGORIES)
    mission = SITE.get("about_mission") or (
        f"<p><strong>{SITE['name']}</strong>는 {SITE['tagline']}를 목표로 하는 1인 운영 정보 사이트입니다. "
        f"{SITE['subtitle']}</p>")
    return f'''<h1>{SITE['name']} 소개</h1>
{mission}
<h2>다루는 분야</h2>
<ul>{cats}</ul>
<h2>글을 쓰는 원칙</h2>
<ol>
<li><strong>검색은 많은데 제대로 정리된 글이 없는 주제를 먼저 씁니다.</strong> 이미 잘 정리된 주제를 한 번 더 쓰는 대신,
흩어져 있어 찾기 어려운 제도·절차를 한 편에 모으는 데 집중합니다.</li>
<li><strong>공식 자료를 근거로 삼습니다.</strong> 금액·자격 요건·신청 절차는 소관 부처와 공공기관 자료를 확인해 쓰고,
모든 글 아래에 <em>확인처</em>로 해당 기관 링크와 전화번호를 함께 답니다.</li>
<li><strong>읽는 분의 다음 행동까지 적습니다.</strong> "어디에 전화해서, 무엇을 들고, 언제까지" 가 없으면 글을 올리지 않습니다.</li>
<li><strong>큰 글씨와 쉬운 말을 씁니다.</strong> 행정 용어는 처음 나올 때 풀어 쓰고, 표와 번호 목록으로 눈이 덜 피로하게 만듭니다.</li>
<li><strong>과장하지 않습니다.</strong> "무조건 받는다", "누구나 가능" 같은 표현을 쓰지 않고, 감액·제외 조건도 함께 밝힙니다.</li>
</ol>
<h2>정확성 관리</h2>
<p>제도는 해마다 바뀝니다. 각 글에는 작성일과 <strong>최종 확인일</strong>을 표시하고, 기준이 바뀌면 본문을 고쳐 최종 확인일을 갱신합니다.
그럼에도 시점 차이나 개인별 사정으로 실제 결과가 다를 수 있으므로, 신청 전에는 글 아래 확인처에서 최신 기준을 다시 확인해 주세요.</p>
<h2>틀린 내용을 발견하셨다면</h2>
<p>정정 요청은 언제든 환영합니다. <a href="/contact/">문의 페이지</a>나
<a href="mailto:{SITE['email']}">{SITE['email']}</a>로 알려주시면 확인 후 본문을 수정하고 최종 확인일을 갱신합니다.</p>
<h2>수익 안내</h2>
<p>이 사이트는 운영비를 충당하기 위해 광고를 게재합니다. 광고는 글의 내용과 무관하게 자동으로 표시되며,
특정 상품·기관을 홍보하는 대가를 받고 글을 쓰지 않습니다.</p>
<p style="color:#888">운영·편집: {SITE['author']} · 연락처: <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>'''

def CONTACT_HTML():
    return f'''<h1>문의하기</h1>
<p>아래 이메일로 보내주시면 확인 후 답변드립니다. 1인이 운영하는 사이트라 답변에 며칠 걸릴 수 있는 점 양해 부탁드립니다.</p>
<p style="font-size:22px"><strong>이메일:</strong> <a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
<h2>이런 문의를 받습니다</h2>
<ul>
<li><strong>내용 정정 요청</strong> — 금액·기준·절차가 바뀌었거나 잘못된 부분을 알려주세요.
어느 글(제목 또는 주소)의 어느 부분인지 적어주시면 훨씬 빠르게 고칠 수 있습니다.</li>
<li><strong>다뤄줬으면 하는 주제</strong> — 찾아봐도 잘 정리된 글이 없는 주제를 알려주시면 우선 검토합니다.</li>
<li><strong>제휴·인용 문의</strong> — 본문 인용은 출처와 링크를 밝히시면 자유롭게 하셔도 됩니다.</li>
<li><strong>개인정보·광고 관련 문의</strong> — <a href="/privacy/">개인정보처리방침</a>을 함께 참고해 주세요.</li>
</ul>
<h2>답변드리기 어려운 문의</h2>
<p>개인별 수급 자격 판정, 진단·치료 상담, 법률 자문은 이 사이트에서 판단해 드릴 수 없습니다.
각 글 아래 <strong>확인처</strong>에 적어둔 담당 기관 전화번호로 문의하시는 편이 정확하고 빠릅니다.</p>
<p style="color:#888">운영·편집: {SITE['author']}</p>'''

def PRIVACY_HTML():
    return f'''<h1>개인정보처리방침</h1>
<p>{SITE['name']}(이하 '사이트')는 이용자의 개인정보를 소중히 다룹니다. 본 방침은 사이트가 정보를 어떻게 수집·이용하는지 안내합니다.</p>
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
