# Buddha Talk 배포 가이드

## 🚀 실제 웹사이트 배포하기

### 방법 1: Render.com (가장 쉬움, 무료 티어 있음)

#### 1단계: Render.com 계정 생성
- https://render.com 접속
- GitHub 계정으로 가입

#### 2단계: Web Service 생성
1. Dashboard에서 "New +" 클릭
2. "Web Service" 선택
3. GitHub 레포지토리 연결
4. 다음 설정 입력:
   ```
   Name: buddha-talk
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

#### 3단계: 환경 변수 설정
Settings > Environment에서 추가:
```
OPENAI_API_KEY = sk-your-actual-key
SECRET_KEY = your-secret-key-here
DEBUG = False
```

#### 4단계: 배포
- "Create Web Service" 클릭
- 자동으로 배포 시작
- 5-10분 후 URL 생성: `https://buddha-talk.onrender.com`

---

### 방법 2: Vercel (프론트엔드) + Render (백엔드)

#### Vercel (무료, 정적 사이트)
```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
cd "Buddha talk"
vercel
```

#### 백엔드는 Render에 별도 배포
- API 엔드포인트를 Vercel 프론트엔드에서 호출

---

### 방법 3: AWS Lightsail (VPS)

#### 비용: 월 $3.50~

1. **인스턴스 생성**
   - OS: Ubuntu 20.04
   - 플랜: $3.50/month

2. **SSH 접속**
   ```bash
   ssh ubuntu@your-lightsail-ip
   ```

3. **서버 설정**
   ```bash
   # Python 설치
   sudo apt update
   sudo apt install python3-pip python3-venv nginx -y

   # 프로젝트 클론
   git clone https://github.com/yourusername/buddha-talk.git
   cd buddha-talk

   # 가상환경 설정
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # 환경 변수 설정
   nano .env
   # OPENAI_API_KEY=sk-xxx 입력

   # Gunicorn으로 실행
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

4. **Nginx 설정 (리버스 프록시)**
   ```bash
   sudo nano /etc/nginx/sites-available/buddha-talk
   ```

   내용:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   활성화:
   ```bash
   sudo ln -s /etc/nginx/sites-available/buddha-talk /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **SSL 인증서 설정 (HTTPS)**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

---

### 방법 4: Railway.app (간편, 무료 티어)

1. https://railway.app 접속
2. "New Project" > "Deploy from GitHub repo"
3. 레포지토리 선택
4. 환경 변수 추가:
   - `OPENAI_API_KEY`
   - `SECRET_KEY`
5. 자동 배포 완료!

---

## 🔒 보안 체크리스트

배포 전 반드시 확인:

- [ ] `.env` 파일을 `.gitignore`에 추가
- [ ] API 키를 환경 변수로 관리
- [ ] `DEBUG=False` 설정
- [ ] HTTPS 적용 (SSL 인증서)
- [ ] CORS 설정 확인
- [ ] Rate Limiting 추가 (API 남용 방지)
- [ ] 데이터베이스 백업 설정

---

## 💰 비용 예상

### 최소 비용 (무료/저비용)
```
도메인: $12/년 (Namecheap)
호스팅: $0 (Render 무료 티어)
OpenAI API: $10-30/월 (사용량 기반)
───────────────────────
총 월 비용: $10-30
```

### 권장 비용 (안정적)
```
도메인: $12/년
호스팅: $7/월 (Render Pro)
OpenAI API: $50/월
CDN: $0 (Cloudflare 무료)
───────────────────────
총 월 비용: $60-80
```

### 프로 설정 (확장 가능)
```
도메인: $12/년
VPS: $20/월 (AWS Lightsail)
OpenAI API: $100/월
CDN: $20/월 (Cloudflare Pro)
모니터링: $10/월 (DataDog)
───────────────────────
총 월 비용: $150
```

---

## 📊 트래픽 대비 서버 스펙

| 일일 사용자 | 월 OpenAI 비용 | 권장 호스팅 |
|------------|---------------|------------|
| ~100명     | $10-20        | Render 무료 |
| ~1,000명   | $50-100       | Render Pro $7 |
| ~10,000명  | $500-1,000    | AWS EC2 t3.medium |
| 10,000명+  | $1,000+       | 로드밸런서 + 다중 서버 |

---

## 🔧 추가 개선사항 (배포 전 권장)

### 1. Rate Limiting 추가
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 2. 에러 로깅
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 3. 데이터베이스 (PostgreSQL)
- CSV 대신 DB 사용
- 더 빠른 쿼리
- 안전한 데이터 관리

### 4. 캐싱
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

---

## 📞 도움이 필요하면

- Render 문서: https://render.com/docs
- Flask 배포: https://flask.palletsprojects.com/en/2.3.x/deploying/
- OpenAI 가격: https://openai.com/pricing

---

## ✅ 배포 체크리스트

배포 완료 후:

- [ ] 웹사이트 접속 확인
- [ ] API 키 정상 작동 확인
- [ ] 대화 기능 테스트
- [ ] 모바일 반응형 확인
- [ ] HTTPS 적용 확인
- [ ] 에러 로그 모니터링 설정
- [ ] 백업 설정
- [ ] 도메인 DNS 연결
- [ ] Google Analytics 추가 (선택)
- [ ] SEO 최적화 (메타 태그)

Good luck! 🙏
