# -*- coding: utf-8 -*-
SITE = {
    "name": "부동산 오른다",
    "tagline": "집값은 왜 오를 수밖에 없나 — 상승론의 근거를 데이터로",
    "subtitle": "공급·유동성·인구, 상승을 뒷받침하는 논리를 정리합니다.",
    "url": "https://example-realestate-up.pages.dev",
    "adsense_client": "",
    "author": "부동산 오른다 편집부",
    "email": "usinyakkuk13@gmail.com",
}

CATEGORIES = [
    ("reasons", "상승 근거", "집값 상승을 뒷받침하는 요인"),
    ("market", "시장 데이터", "거래량·가격·공급 지표 읽기"),
    ("policy", "금리·정책", "정책과 금리가 시장에 미치는 영향"),
    ("strategy", "내집마련 전략", "실수요자를 위한 접근법"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
