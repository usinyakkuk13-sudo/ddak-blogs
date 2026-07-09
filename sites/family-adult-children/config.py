# -*- coding: utf-8 -*-
SITE = {
    "name": "부모 마음",
    "tagline": "결혼·출산, 다 큰 자식을 바라보는 부모의 마음",
    "subtitle": "세대 사이의 거리를 이해와 대화로 좁혀갑니다.",
    "url": "https://example-family-adult-children.pages.dev",
    "adsense_client": "",
    "author": "부모 마음 편집부",
    "email": "geusijeol.story@gmail.com",
}

CATEGORIES = [
    ("marriage", "결혼", "비혼 시대의 자녀와 부모"),
    ("children", "출산·육아", "손주와 저출생 이야기"),
    ("heart", "부모 마음", "서운함과 사랑 사이"),
    ("talk", "소통", "대화하는 법"),
]

CAT_NAME_TO_SLUG = {name: slug for slug, name, _ in CATEGORIES}
