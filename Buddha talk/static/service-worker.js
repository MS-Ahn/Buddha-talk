/**
 * Buddha Talk - Service Worker
 * PWA 기능: 오프라인 지원, 캐싱, 백그라운드 동기화
 */

const CACHE_NAME = 'buddha-talk-v1.0.0';
const RUNTIME_CACHE = 'buddha-talk-runtime';

// 캐시할 정적 파일들
const STATIC_CACHE_URLS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/music-player.js',
  '/static/manifest.json',
  // 폰트는 Google Fonts CDN에서 로드되므로 제외
];

// 설치 이벤트 - 정적 파일 캐싱
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('[Service Worker] Skip waiting');
        return self.skipWaiting();
      })
  );
});

// 활성화 이벤트 - 오래된 캐시 정리
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Claiming clients');
      return self.clients.claim();
    })
  );
});

// Fetch 이벤트 - 네트워크 요청 처리
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API 요청은 항상 네트워크 우선 (OpenAI 호출)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // 정적 파일은 캐시 우선
  if (request.method === 'GET') {
    event.respondWith(cacheFirst(request));
  }
});

// 캐시 우선 전략 (정적 파일용)
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) {
    console.log('[Service Worker] Cache hit:', request.url);
    return cached;
  }

  try {
    const response = await fetch(request);

    // 성공적인 응답만 캐시
    if (response && response.status === 200) {
      const responseClone = response.clone();
      cache.put(request, responseClone);
    }

    return response;
  } catch (error) {
    console.error('[Service Worker] Fetch failed:', error);

    // 오프라인 폴백 (선택적)
    if (request.destination === 'document') {
      return cache.match('/');
    }

    throw error;
  }
}

// 네트워크 우선 전략 (API 요청용)
async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE);

  try {
    const response = await fetch(request);

    // API 응답은 짧은 시간만 캐시 (선택적)
    if (response && response.status === 200) {
      const responseClone = response.clone();
      cache.put(request, responseClone);
    }

    return response;
  } catch (error) {
    console.log('[Service Worker] Network failed, trying cache:', request.url);
    const cached = await cache.match(request);

    if (cached) {
      return cached;
    }

    throw error;
  }
}

// 푸시 알림 이벤트 (선택적 - 향후 확장)
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};

  const options = {
    body: data.body || '새로운 메시지가 있습니다',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '확인하기',
        icon: '/static/icons/checkmark.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/static/icons/close.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || '부처님과의 대화', options)
  );
});

// 알림 클릭 이벤트
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// 백그라운드 동기화 (선택적 - 향후 확장)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  // 오프라인 시 저장된 메시지를 서버와 동기화
  console.log('[Service Worker] Syncing messages...');
  // 구현 필요
}

// 주기적 백그라운드 동기화 (향후 확장)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'daily-meditation') {
    event.waitUntil(fetchDailyMeditation());
  }
});

async function fetchDailyMeditation() {
  console.log('[Service Worker] Fetching daily meditation...');
  // 구현 필요
}

console.log('[Service Worker] Loaded');
