# 앱 아이콘 가이드

## 현재 상태
- `icon.svg` 파일이 생성되었습니다 (기본 부처님 아이콘)

## 필요한 PNG 아이콘 크기
PWA로 작동하려면 다음 크기의 PNG 파일들이 필요합니다:

- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

## 아이콘 생성 방법

### 방법 1: 온라인 도구 사용 (가장 쉬움)
1. https://www.pwabuilder.com/imageGenerator 방문
2. 512x512 PNG 이미지 업로드
3. 모든 크기 자동 생성 및 다운로드
4. 다운로드한 파일들을 `/static/icons/` 폴더에 복사

### 방법 2: Figma/Photoshop 사용
1. 512x512 크기로 디자인
2. 각 크기로 Export
3. `/static/icons/` 폴더에 저장

### 방법 3: Python 스크립트 사용
```bash
pip install pillow
python generate_icons.py
```

## 디자인 가이드라인
- **배경색**: #D4AF37 (금색)
- **메인 색상**: #F5DEB3 (베이지)
- **강조 색상**: #FF8C00 (오렌지)
- **심플하고 명확한 디자인** (작은 크기에서도 인식 가능)
- **안전 영역**: 가장자리 10% 여백 유지

## 임시 해결책
현재는 icon.svg를 여러 크기의 PNG로 변환해야 합니다.
온라인 도구나 디자인 툴을 사용하여 변환하세요.
