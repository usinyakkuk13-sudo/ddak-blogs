# -*- coding: utf-8 -*-
SITE = {
    "name": "오늘 뭐 보지",
    "tagline": "오늘의 방송·편성표·프로그램 정보 한눈에",
    "subtitle": "보고 싶은 방송을 놓치지 않도록 정리합니다.",
    "url": "https://example-tv-guide.pages.dev",
    "adsense_client": "",
    "author": "오늘 뭐 보지 편집부",
    "email": "usinyakkuk13@gmail.com",
}

CATEGORIES = [
    ("today", "오늘의 방송", "오늘 볼 만한 방송"),
    ("program", "프로그램 소개", "화제의 프로그램"),
    ("schedule", "편성표", "채널별 편성 안내"),
    ("cast", "출연자", "출연진 정보"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
