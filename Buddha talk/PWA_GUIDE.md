# 📱 Buddha Talk PWA 가이드

Buddha Talk이 이제 **Progressive Web App (PWA)**로 업그레이드되었습니다!

## ✨ PWA란?

PWA는 웹 기술로 만든 앱을 **네이티브 앱처럼** 사용할 수 있게 해주는 기술입니다.

**장점:**
- 홈 화면에 아이콘 추가 가능
- 오프라인에서도 일부 기능 사용 가능
- 빠른 로딩 속도 (캐싱)
- 앱스토어 없이 바로 설치
- 푸시 알림 지원 (향후 업데이트)

## 🚀 사용 방법

### 1. 웹사이트 접속
```
http://localhost:5000
```

### 2. PWA 설치

#### **Android (Chrome)**
1. 웹사이트 접속
2. 우측 하단에 나타나는 **"📱 앱으로 설치"** 버튼 클릭
3. 또는 Chrome 메뉴 (⋮) → "앱 설치" 또는 "홈 화면에 추가"
4. 확인 후 홈 화면에 Buddha Talk 아이콘 추가됨

#### **iPhone/iPad (Safari)**
1. Safari에서 웹사이트 접속
2. 하단 공유 버튼 (□↑) 탭
3. "홈 화면에 추가" 선택
4. 이름 확인 후 "추가" 탭
5. 홈 화면에 Buddha Talk 아이콘 추가됨

#### **Windows (Chrome/Edge)**
1. 웹사이트 접속
2. 주소창 우측의 설치 아이콘 (⊕) 클릭
3. 또는 우측 하단 **"📱 앱으로 설치"** 버튼 클릭
4. "설치" 확인
5. 독립 앱 창으로 실행됨

#### **Mac (Chrome/Safari)**
- Chrome: 주소창 우측 설치 아이콘 클릭
- Safari: Dock → "홈 화면에 추가"

### 3. 앱 실행
홈 화면이나 앱 목록에서 Buddha Talk 아이콘을 탭하면 **독립된 앱**으로 실행됩니다!

## 🔧 PWA 기능

### ✅ 현재 지원
- **오프라인 캐싱**: 정적 파일들이 캐시되어 빠른 로딩
- **홈 화면 설치**: 네이티브 앱처럼 설치 가능
- **독립 앱 모드**: 브라우저 UI 없이 앱처럼 실행
- **자동 업데이트**: 새 버전 자동 감지 및 알림
- **앱 아이콘**: 부처님 캐릭터 아이콘

### 🔜 향후 업데이트 예정
- **푸시 알림**: 명상 리마인더, 일일 명언
- **백그라운드 동기화**: 오프라인 메시지 자동 동기화
- **명상 타이머**: 오프라인 명상 세션

## 📊 개발자용 정보

### 파일 구조
```
Buddha talk/
├── static/
│   ├── manifest.json          # PWA 매니페스트
│   ├── service-worker.js      # Service Worker
│   ├── icons/                 # 앱 아이콘들
│   │   ├── icon-72x72.png
│   │   ├── icon-96x96.png
│   │   ├── ...
│   │   └── icon-512x512.png
│   └── js/
│       └── app.js            # PWA 등록 코드 포함
└── templates/
    └── index.html            # PWA 메타 태그 포함
```

### 테스트 방법

#### Chrome DevTools로 PWA 검증
1. Chrome에서 웹사이트 접속
2. F12 → "Lighthouse" 탭
3. "Progressive Web App" 체크
4. "Analyze page load" 클릭
5. PWA 점수 및 개선 사항 확인

#### Service Worker 확인
1. F12 → "Application" 탭
2. 좌측 "Service Workers" 클릭
3. 등록 상태 및 캐시 확인

#### Manifest 확인
1. F12 → "Application" 탭
2. 좌측 "Manifest" 클릭
3. 앱 정보 및 아이콘 확인

### 캐시 전략
- **정적 파일**: Cache First (HTML, CSS, JS, 이미지)
- **API 요청**: Network First (OpenAI API 호출)
- **캐시 버전**: `buddha-talk-v1.0.0`

### 아이콘 재생성
더 나은 디자인으로 아이콘을 교체하려면:

```bash
# Python 스크립트 사용
python generate_icons.py

# 또는 온라인 도구 사용
https://www.pwabuilder.com/imageGenerator
```

## 🌐 배포 시 주의사항

### HTTPS 필수
PWA는 **HTTPS**에서만 작동합니다 (localhost 제외).

배포 시:
- Heroku, Vercel, Netlify 등은 자동 HTTPS
- 커스텀 도메인 사용 시 SSL 인증서 필요

### manifest.json 수정
배포 전 `static/manifest.json`의 `start_url` 확인:
```json
{
  "start_url": "/",  // 또는 배포 URL
  ...
}
```

### Service Worker 스코프
현재 Service Worker는 전체 도메인을 커버합니다:
```javascript
scope: '/'
```

하위 경로에 배포하려면 수정 필요.

## 🎯 사용자 경험 팁

1. **첫 방문**: 사이트 로드 후 5초 뒤 설치 버튼이 깜빡입니다
2. **설치 권장**: 모바일에서 자주 사용한다면 설치 추천
3. **오프라인**: API 키 설정 후에는 일부 캐시된 내용 확인 가능
4. **업데이트**: 새 버전이 나오면 자동으로 알림 표시

## ❓ 문제 해결

### 설치 버튼이 안 보여요
- HTTPS 사용 중인지 확인 (localhost는 OK)
- 이미 설치되었는지 확인
- Chrome/Edge 사용 (Firefox는 제한적 지원)

### Service Worker가 등록 안 돼요
- F12 콘솔에서 에러 확인
- 파일 경로 확인: `/static/service-worker.js`
- 브라우저 캐시 삭제 후 재시도

### 아이콘이 안 보여요
- `/static/icons/` 폴더에 PNG 파일들 확인
- `python generate_icons.py` 재실행
- manifest.json 경로 확인

### 오프라인이 안 돼요
- PWA 설치 후 한 번 이상 방문 필요
- Service Worker가 정상 등록되었는지 확인
- API 요청은 네트워크 필요 (캐싱 X)

## 📞 지원

문제가 있거나 개선 제안이 있으시면 이슈를 등록해주세요!

---

**Buddha Talk PWA로 언제 어디서나 부처님과 대화하세요! 🙏**
