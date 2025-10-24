# 🚀 Buddha Talk 배포 가이드

Buddha Talk을 Vercel에 배포하여 전 세계 어디서나 접속 가능하게 만드는 방법입니다.

## 📋 배포 전 체크리스트

✅ Git 저장소 초기화 완료
✅ .gitignore 설정 완료
✅ vercel.json 설정 완료
⬜ GitHub 계정 필요
⬜ Vercel 계정 필요 (무료)

---

## 🎯 배포 방법 (2가지)

### **방법 1: GitHub + Vercel 연동** (추천 ⭐)
가장 쉽고 자동화된 방법

### **방법 2: Vercel CLI**
명령어로 바로 배포

---

## 📦 방법 1: GitHub + Vercel (추천)

### Step 1: GitHub에 코드 업로드

#### 1-1. GitHub 저장소 생성
1. https://github.com 접속 및 로그인
2. 우측 상단 **+ → New repository** 클릭
3. 저장소 이름: `buddha-talk` (원하는 이름)
4. **Public** 또는 **Private** 선택
5. **Create repository** 클릭

#### 1-2. 로컬 코드를 GitHub에 푸시

터미널에서 다음 명령어 실행:

```bash
# Buddha Talk 프로젝트 폴더로 이동
cd "C:\Users\82107\OneDrive\바탕 화면\Buddha talk"

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Buddha Talk PWA"

# GitHub 저장소 연결 (YOUR_USERNAME를 본인 것으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/buddha-talk.git

# main 브랜치로 변경
git branch -M main

# GitHub에 푸시
git push -u origin main
```

> 💡 **GitHub 인증이 필요한 경우:**
> - Personal Access Token 생성: GitHub → Settings → Developer settings → Personal access tokens
> - 또는 GitHub Desktop 사용

---

### Step 2: Vercel에 배포

#### 2-1. Vercel 계정 생성
1. https://vercel.com 접속
2. **Sign Up** 클릭
3. **Continue with GitHub** 선택 (GitHub 계정으로 로그인)

#### 2-2. 프로젝트 배포
1. Vercel 대시보드에서 **Add New... → Project** 클릭
2. GitHub 저장소 목록에서 **buddha-talk** 찾기
3. **Import** 클릭
4. 설정 확인:
   - **Framework Preset**: Other (자동 감지됨)
   - **Root Directory**: `./` (기본값)
   - **Build Command**: (비워두기)
   - **Output Directory**: (비워두기)

#### 2-3. 환경 변수 설정 (중요! ⚠️)
**Environment Variables** 섹션에서:

```
SECRET_KEY = [랜덤한 긴 문자열 - 아래 생성 방법 참고]
```

**SECRET_KEY 생성 방법:**
```bash
# Python으로 생성
python -c "import secrets; print(secrets.token_hex(32))"
```

또는 온라인 도구: https://generate-secret.vercel.app/32

> ⚠️ **주의:** OpenAI API 키는 **서버에 저장하지 마세요!**
> 사용자가 웹에서 직접 입력하는 현재 방식이 더 안전합니다.

#### 2-4. 배포 시작
1. **Deploy** 버튼 클릭
2. 2-3분 대기 (빌드 과정 확인 가능)
3. 배포 완료! 🎉

---

### Step 3: 배포된 앱 확인

배포가 완료되면:
- **도메인**: `https://buddha-talk-xxxxx.vercel.app`
- 자동으로 HTTPS 적용됨 (PWA 필수!)
- 전 세계 어디서나 접속 가능

#### 테스트:
1. 제공된 URL로 접속
2. PWA 설치 버튼 확인
3. 모바일에서 접속 및 홈 화면 추가 테스트

---

## 🛠 방법 2: Vercel CLI로 배포

### Step 1: Vercel CLI 설치

```bash
npm install -g vercel
```

### Step 2: 로그인

```bash
vercel login
```

### Step 3: 배포

```bash
cd "C:\Users\82107\OneDrive\바탕 화면\Buddha talk"
vercel
```

대화형 질문에 답변:
- Set up and deploy? **Y**
- Which scope? (본인 계정 선택)
- Link to existing project? **N**
- What's your project's name? **buddha-talk**
- In which directory is your code located? **./**
- Want to modify these settings? **N**

배포 완료! URL이 표시됩니다.

---

## 🎨 커스텀 도메인 설정 (선택)

무료로 커스텀 도메인 연결 가능:

1. Vercel 프로젝트 → **Settings** → **Domains**
2. 도메인 입력 (예: `buddhatalk.com`)
3. DNS 설정 (도메인 제공업체에서 설정)

**무료 도메인 추천:**
- Freenom: https://freenom.com
- InfinityFree: https://infinityfree.net

---

## 🔄 자동 배포 설정

GitHub + Vercel 연동 시:
- **main 브랜치에 푸시** → 자동 배포
- **Pull Request** → 미리보기 배포

### 업데이트 방법:
```bash
git add .
git commit -m "Update: 새로운 기능 추가"
git push
```

→ 자동으로 Vercel에 배포됨!

---

## 📱 배포 후 공유 방법

### 1. URL 공유
```
https://buddha-talk-xxxxx.vercel.app
```

### 2. QR 코드 생성
- https://qr-code-generator.com
- URL 입력 후 QR 코드 다운로드
- 지인들에게 공유

### 3. 카카오톡/SNS 공유
- 링크 붙여넣기
- 미리보기 이미지 자동 생성됨 (Open Graph 태그)

### 4. PWA 설치 안내
```
📱 Buddha Talk 앱 설치 방법:

1. 링크 접속: https://buddha-talk-xxxxx.vercel.app
2. 모바일: 우측 하단 "앱으로 설치" 버튼 클릭
3. iPhone: Safari → 공유 → 홈 화면에 추가
4. Android: Chrome → 메뉴 → 앱 설치

이제 앱처럼 사용 가능! 🙏
```

---

## ⚠️ 주의사항

### 1. API 키 보안
- 사용자가 직접 입력하는 현재 방식 유지 (안전)
- 서버에 API 키 저장 금지

### 2. 비용
- Vercel 무료 플랜:
  - 월 100GB 대역폭
  - 무제한 요청
  - 취미 프로젝트에 충분

### 3. 데이터베이스
- 현재는 CSV 파일로 저장
- 사용자 많아지면 PostgreSQL/MongoDB 고려

### 4. 성능
- Vercel은 서버리스 (Serverless)
- 처음 요청 시 약간 느릴 수 있음 (Cold Start)
- 자주 사용하면 빠름

---

## 🐛 문제 해결

### 배포 실패 시
1. Vercel 대시보드 → Deployments → 실패한 배포 클릭
2. Logs 확인
3. 오류 메시지 검색 또는 문의

### 자주 발생하는 오류

#### "No Python version specified"
→ `runtime.txt` 파일 확인:
```
python-3.10.6
```

#### "Module not found"
→ `requirements.txt` 확인 및 수정

#### "PORT already in use"
→ 로컬 서버 중지 후 재시도

### HTTPS 문제
- Vercel은 자동 HTTPS 제공
- 문제 없음!

---

## 📊 배포 후 모니터링

### Vercel 대시보드에서 확인 가능:
- 방문자 수
- 요청 수
- 에러 로그
- 성능 분석

### Google Analytics 추가 (선택)
`templates/index.html`의 `<head>` 태그에 추가:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## 🎉 다음 단계

배포 완료 후:

1. ✅ 지인들에게 URL 공유
2. ✅ PWA 설치 테스트
3. ✅ 피드백 수집
4. ✅ 기능 개선 및 업데이트

### 향후 개선 사항:
- 사용자 인증 (로그인)
- 대화 기록 저장 (데이터베이스)
- 푸시 알림
- 다국어 지원
- 앱스토어 등재 (React Native)

---

## 📞 도움이 필요하신가요?

문제가 있거나 질문이 있으시면:
- Vercel 공식 문서: https://vercel.com/docs
- GitHub Issues 생성
- Discord/Slack 커뮤니티

---

**Buddha Talk을 전 세계와 공유하세요! 🙏✨**
