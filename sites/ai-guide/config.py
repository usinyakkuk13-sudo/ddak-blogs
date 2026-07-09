# -*- coding: utf-8 -*-
SITE = {
    "name": "오늘의 AI",
    "tagline": "챗GPT부터 이미지 생성까지, AI를 쉽게 쓰는 법",
    "subtitle": "복잡한 AI를 실생활에 바로 쓰도록 쉽게 안내합니다.",
    "url": "https://example-ai-guide.pages.dev",
    "adsense_client": "",
    "author": "오늘의 AI 편집부",
    "email": "geusijeol.story@gmail.com",
}

CATEGORIES = [
    ("chatgpt", "챗GPT", "대화형 AI 활용법"),
    ("image", "이미지·영상", "그림·영상 만드는 AI"),
    ("work", "업무 활용", "일과 공부에 쓰는 법"),
    ("basic", "기초 개념", "AI 기본 이해"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
