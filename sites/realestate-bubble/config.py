# -*- coding: utf-8 -*-
SITE = {
    "name": "부동산 거품이다",
    "tagline": "지금이 고점인 이유 — 거품론의 논리를 데이터로",
    "subtitle": "소득 대비 가격·가계부채·인구, 하락 신호를 짚습니다.",
    "url": "https://example-realestate-bubble.pages.dev",
    "adsense_client": "",
    "author": "부동산 거품이다 편집부",
    "email": "usinyakkuk13@gmail.com",
}

CATEGORIES = [
    ("signals", "거품 신호", "고평가를 알리는 지표들"),
    ("market", "시장 데이터", "거래량·가격·공급 지표 읽기"),
    ("policy", "금리·정책", "정책과 금리가 시장에 미치는 영향"),
    ("prepare", "하락기 대비", "무리한 매수를 피하는 법"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
