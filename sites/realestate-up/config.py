# -*- coding: utf-8 -*-
SITE = {
    "name": "부동산 저평가",
    "tagline": "지금 집값이 싼 이유 — 저평가 근거를 데이터로 읽는다",
    "subtitle": "안전마진·저평가 관점으로 시장을 분석합니다.",
    "url": "https://example-realestate-up.pages.dev",
    "adsense_client": "",
    "author": "부동산 저평가 편집부",
    "email": "geusijeol.story@gmail.com",
}

CATEGORIES = [
    ("reasons", "저평가 근거", "집값이 저평가됐다고 보는 근거"),
    ("market", "시장 데이터", "거래량·가격·공급 지표 읽기"),
    ("policy", "금리·정책", "정책과 금리가 시장에 미치는 영향"),
    ("strategy", "내집마련 전략", "실수요자를 위한 접근법"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
