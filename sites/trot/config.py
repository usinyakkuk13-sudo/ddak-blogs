# -*- coding: utf-8 -*-
SITE = {
    "name": "트로트 한마당",
    "tagline": "트로트 가수와 무대, 그 모든 이야기",
    "subtitle": "좋아하는 가수와 무대 소식을 한곳에서.",
    "url": "https://example-trot.pages.dev",
    "adsense_client": "",
    "author": "트로트 한마당 편집부",
    "email": "geusijeol.story@gmail.com",
}

CATEGORIES = [
    ("singers", "가수 이야기", "가수 소개와 활동"),
    ("stage", "무대·방송", "공연과 방송 소식"),
    ("history", "트로트 역사", "트로트의 어제와 오늘"),
    ("info", "공연 정보", "공연·행사 안내"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
