# 시작하기 — 블로그 수익 파이프라인

이 폴더는 **여러 개의 한국어 SEO 블로그 + 애드센스** 수익 파이프라인입니다.
글 생산은 자동화돼 있고(매일 자동 생성 예약됨), **돈이 실제로 오가는 단계(도메인 구매·애드센스 가입·배포 버튼)만 직접** 하시면 됩니다.

전체 사이트 목록과 전략은 `ROADMAP.md`를 보세요.

---

## 폴더 구조

```
딸깍으로 돈벌기/
├─ engine/generator.py     ← 공용 사이트 생성 엔진 (건드릴 필요 없음)
├─ build_all.py            ← 모든 사이트 다시 빌드
├─ sites/
│   ├─ ACTIVE_SITE.txt     ← 매일 자동 생성기가 집중할 사이트 (기본: senior-info)
│   ├─ senior-info/        ← 사이트 1개 = 폴더 1개
│   │   ├─ config.py       ← 이 사이트 설정(도메인·애드센스ID)
│   │   ├─ content/        ← 글(.md)
│   │   └─ public/         ← 완성된 사이트 ★배포는 이 폴더를 올림
│   ├─ realestate-up/ ...  ← 다른 사이트들
└─ ROADMAP.md
```

빌드 도구 설치 불필요. 파이썬만 있으면 됩니다. 다시 빌드: 폴더에서 `python3 build_all.py`.

---

## 지금 상태

- ✅ 사이트 8개 스캐폴드 완료, 총 글 28편, 전부 정상 빌드
- ✅ **`senior-info`(든든한 노후) = 글 19편, 애드센스 승인 준비 완료** ← 먼저 이걸로 승인
- ✅ SEO 풀세트(메타·canonical·OG·JSON-LD·sitemap·rss·robots), 60대 가독성 디자인, 개인정보처리방침 포함
- ✅ 매일 오전 9시 **활성 사이트에 원본 글 2편 자동 추가** 예약됨

---

## 해야 할 일 (senior-info 먼저)

### 1단계. 도메인 준비 (권장, 약 1~2만원/년)

무료 주소로도 신청 가능하지만, 직접 산 도메인이 승인·신뢰도에 유리합니다. 가비아·후이즈·Cloudflare 등에서 `.com` 구매.

### 2단계. 무료 배포 (Cloudflare Pages)

1. [dash.cloudflare.com](https://dash.cloudflare.com) 무료 가입
2. **Workers & Pages → Create → Pages → Upload assets**
3. **`sites/senior-info/public` 폴더 안의 내용물**을 드래그해서 업로드
4. `프로젝트명.pages.dev` 주소 생성 → (도메인 샀으면) Custom domains에서 연결

> 더 쉬운 대안: [app.netlify.com/drop](https://app.netlify.com/drop) 에 `sites/senior-info/public` 폴더를 끌어다 놓기.

### 3단계. 도메인을 코드에 반영

`sites/senior-info/config.py` 를 열어 한 줄 수정:

```python
"url": "https://내도메인.com",   # ← 실제 배포 주소
```

그다음 클로드에게 "다시 빌드해줘" 또는 직접 `python3 build_all.py` → `public/` 다시 업로드.

### 4단계. 애드센스 신청 (글 10편 이상, 이미 충족)

[www.google.com/adsense](https://www.google.com/adsense) 가입 → 사이트 주소 입력 → 받은 번호를 `config.py`의 `adsense_client`에 입력:

```python
"adsense_client": "ca-pub-여기에번호",
```

다시 빌드 → 업로드 → 애드센스에서 검토 요청. 승인까지 보통 3일~2주. 승인 후 대시보드에서 **자동 광고**를 켜면 광고가 붙습니다.

### 5단계. 검색 노출

- **구글 서치콘솔**([search.google.com/search-console](https://search.google.com/search-console)): 사이트맵 `https://내도메인.com/sitemap.xml` 제출
- **네이버 서치어드바이저**([searchadvisor.naver.com](https://searchadvisor.naver.com)): 사이트 등록 + 사이트맵 제출 (한국 시니어는 네이버 비중 큼)

---

## 매일 자동 생성 (이미 예약됨)

매일 오전 9시, `ACTIVE_SITE.txt`에 적힌 사이트에 **양질의 원본 글 2편**이 자동으로 추가되고 다시 빌드됩니다.
- 생성 후 **`public/` 폴더를 다시 업로드**해야 실제 사이트에 반영됩니다. (자동 배포를 원하면 GitHub+Cloudflare 연동을 요청하세요.)
- 승인 후 다음 사이트로 넘어가려면 `sites/ACTIVE_SITE.txt` 내용을 다음 슬러그(예: `ai-guide`)로 바꾸면 됩니다.

---

## 수익을 높이려면

- **한 사이트를 20편 이상으로 채워 먼저 승인**받고 다음으로. (얇은 여러 개보다 강함)
- 연금·복지·부동산은 검색량·광고단가가 특히 좋습니다.
- 승인 전엔 광고 없이 콘텐츠 품질에 집중.

막히는 건 언제든 클로드에게 물어보세요. ("서치콘솔 등록 도와줘", "ai-guide 글 10편 더 써줘" 등)
