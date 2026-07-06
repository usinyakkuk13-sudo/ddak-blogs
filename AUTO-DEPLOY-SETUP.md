# 자동 배포 설정 (최초 1회, 약 10분)

매일 글 생성은 이미 자동입니다. 여기에 **자동 업로드**까지 붙이면 완전 무개입이 됩니다.

## 왜 최초 1회는 직접 해야 하나요?

자동 생성이 도는 환경은 보안상 외부 인터넷(GitHub·Cloudflare)이 막혀 있어, **실제 업로드는 당신의 PC에서** 나가야 합니다. 그래서 "PC가 자동으로 업로드하도록" 한 번만 세팅합니다. 계정 연결은 원래 본인만 할 수 있는 부분이기도 합니다.

전체 흐름:
```
매일 09:07  Claude가 글 생성 + 빌드   (자동)
매일 09:30  내 PC가 deploy.bat 실행 → git push   (작업 스케줄러, 자동)
그 직후     Cloudflare가 자동 빌드·게시   (자동)
```

---

## 1. Git 설치 (한 번만)

[git-scm.com/download/win](https://git-scm.com/download/win) 에서 설치. 옵션은 전부 기본값으로 '다음'만 누르면 됩니다.

## 2. GitHub 저장소 만들기 (무료)

1. [github.com](https://github.com) 가입/로그인
2. 오른쪽 위 **+ → New repository**
3. 이름 입력(예: `ddak-blogs`), **Private** 선택, **Create repository**
4. 다음 화면에 나오는 저장소 주소(`https://github.com/내이름/ddak-blogs.git`)를 복사

## 3. 최초 업로드 (setup-git.bat 더블클릭)

이 폴더의 **`setup-git.bat`** 을 더블클릭 → 방금 복사한 저장소 주소를 붙여넣고 Enter.
(처음이면 GitHub 로그인 창이 뜹니다. 로그인하면 이후엔 안 물어봅니다.)
성공하면 GitHub에 파일들이 올라갑니다.

## 4. Cloudflare Pages 연결 (사이트마다 1회)

먼저 승인 우선 사이트 `senior-info` 부터:

1. [dash.cloudflare.com](https://dash.cloudflare.com) 가입/로그인
2. **Workers & Pages → Create → Pages → Connect to Git**
3. 방금 만든 GitHub 저장소 선택
4. 빌드 설정에서:
   - **Framework preset**: None
   - **Build command**: 비워둠
   - **Build output directory**: `sites/senior-info/public`
5. **Save and Deploy**

이제 그 저장소에 새 글이 push될 때마다 Cloudflare가 자동으로 다시 게시합니다.
다른 사이트(realestate-up 등)를 배포할 때는 같은 방식으로 **새 Pages 프로젝트**를 만들고 output만 `sites/<슬러그>/public` 으로 바꾸면 됩니다.

## 5. 매일 자동 배포 예약 (Windows 작업 스케줄러)

1. 시작 메뉴에서 **작업 스케줄러** 실행
2. 오른쪽 **기본 작업 만들기**
3. 이름: `블로그 자동배포` → 다음
4. 트리거: **매일** → 시간 **오전 9:30** → 다음
5. 동작: **프로그램 시작** → 다음
6. 프로그램/스크립트: 이 폴더의 **`deploy.bat`** 경로를 지정
   (예: `C:\Users\JiHo\Claude\Projects\딸깍으로 돈벌기\deploy.bat`)
7. 마침

끝입니다. 이제 매일 새 글이 자동으로 생성되고, PC가 켜져 있으면 자동으로 배포됩니다.

---

## 참고

- **PC가 꺼져 있으면** 그날 배포는 건너뜁니다. 다음에 켜지고 스케줄이 돌 때 밀린 글까지 함께 올라갑니다. (수동으로 `deploy.bat` 더블클릭해도 즉시 배포)
- GitHub 없이 하고 싶다면 Cloudflare **Wrangler** 방식도 있지만, Node.js 설치와 API 토큰이 필요해 위 GitHub 방식이 더 간단합니다.
- 막히면 클로드에게 "자동배포 설정 화면 같이 해줘"라고 하세요. 브라우저 단계는 화면을 보며 함께 진행할 수 있습니다.
