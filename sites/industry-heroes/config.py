# -*- coding: utf-8 -*-
SITE = {
    "name": "그 시절 우리는",
    "tagline": "대한민국을 일으킨 산업역군의 이야기",
    "subtitle": "땀과 눈물로 시대를 건너온 분들의 이야기를 나눕니다.",
    "url": "https://example-industry-heroes.pages.dev",
    "adsense_client": "",
    "author": "그 시절 우리는 편집부",
    "email": "geusijeol.story@gmail.com",
    "accept_stories": True,
}

CATEGORIES = [
    ("memories", "그때 그 시절", "추억과 기록"),
    ("history", "산업화 이야기", "시대의 현장"),
    ("comfort", "위로와 공감", "마음을 토닥이는 글"),
    ("life", "인생 이야기", "살아온 이야기"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
