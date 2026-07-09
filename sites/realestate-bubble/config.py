# -*- coding: utf-8 -*-
SITE = {
    "name": "부동산 경고등",
    "tagline": "지금 사면 위험하다 — 심상치 않은 하락 신호를 데이터로 읽는다",
    "subtitle": "고평가·가계부채·금리, 위험 신호를 냉정하게 짚습니다.",
    "url": "https://example-realestate-bubble.pages.dev",
    "adsense_client": "",
    "author": "부동산 경고등 편집부",
    "email": "geusijeol.story@gmail.com",
}

CATEGORIES = [
    ("signals", "위험 신호", "지금이 위험하다고 보는 지표들"),
    ("market", "시장 데이터", "거래량·가격·공급 지표 읽기"),
    ("policy", "금리·정책", "정책과 금리가 시장에 미치는 영향"),
    ("prepare", "하락 대비", "무리한 매수를 피하는 법"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
