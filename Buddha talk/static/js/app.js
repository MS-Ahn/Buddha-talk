/**
 * Buddha Talk - 개선된 프론트엔드
 * 감정 추적, 데이터 동의, 스트리밍 지원
 */

class BuddhaChat {
    constructor() {
        this.apiKey = null;
        this.conversationHistory = [];
        this.userId = null;
        this.sessionId = null;
        this.initializeElements();
        this.bindEvents();
        this.checkApiStatus();
        this.showConsentBanner();
    }

    initializeElements() {
        // DOM 요소들
        this.modal = document.getElementById('apiModal');
        this.apiKeyInput = document.getElementById('apiKey');
        this.saveApiKeyBtn = document.getElementById('saveApiKey');
        this.closeModal = document.querySelector('.close');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.charCount = document.querySelector('.char-count');
        this.consentBanner = document.getElementById('consentBanner');
    }

    bindEvents() {
        // 모달 이벤트
        this.saveApiKeyBtn.addEventListener('click', () => this.saveApiKey());
        this.closeModal.addEventListener('click', () => this.hideModal());
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hideModal();
            }
        });

        // 채팅 이벤트
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Enter로 전송, Shift+Enter로 줄바꿈
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 문자 수 카운터
        this.messageInput.addEventListener('input', () => this.updateCharCount());

        // 동의 배너 이벤트
        const acceptBtn = document.getElementById('acceptConsent');
        const declineBtn = document.getElementById('declineConsent');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => this.handleConsent(true));
        }
        if (declineBtn) {
            declineBtn.addEventListener('click', () => this.handleConsent(false));
        }
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            if (!data.api_configured) {
                this.showModal();
            }

            this.sessionId = data.session_id;
        } catch (error) {
            console.error('API 상태 확인 실패:', error);
            this.showModal();
        }
    }

    showConsentBanner() {
        // 로컬 스토리지에서 동의 여부 확인
        const consentGiven = localStorage.getItem('dataConsent');

        if (!consentGiven && this.consentBanner) {
            this.consentBanner.style.display = 'block';
        }
    }

    async handleConsent(consent) {
        try {
            const response = await fetch('/api/consent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ consent: consent })
            });

            const data = await response.json();
            this.userId = data.user_id;

            // 로컬 스토리지에 저장
            localStorage.setItem('dataConsent', consent);
            localStorage.setItem('userId', data.user_id);

            // 배너 숨기기
            if (this.consentBanner) {
                this.consentBanner.style.display = 'none';
            }

            if (consent) {
                this.addSystemMessage('데이터 수집에 동의해주셔서 감사합니다. 더 나은 서비스를 제공하는데 도움이 됩니다.');
            }
        } catch (error) {
            console.error('동의 저장 실패:', error);
        }
    }

    showModal() {
        this.modal.style.display = 'block';
        this.apiKeyInput.focus();
    }

    hideModal() {
        this.modal.style.display = 'none';
    }

    async saveApiKey() {
        const apiKey = this.apiKeyInput.value.trim();

        if (!apiKey) {
            alert('API 키를 입력해주세요.');
            return;
        }

        this.saveApiKeyBtn.textContent = '저장 중...';
        this.saveApiKeyBtn.disabled = true;

        try {
            const response = await fetch('/api/setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ api_key: apiKey })
            });

            const data = await response.json();

            if (response.ok) {
                this.apiKey = apiKey;
                this.hideModal();
                this.addSystemMessage('API 키가 성공적으로 설정되었습니다. 이제 부처님과 대화할 수 있습니다!');
            } else {
                alert(data.error || 'API 키 설정에 실패했습니다.');
            }
        } catch (error) {
            console.error('API 키 설정 실패:', error);
            alert('API 키 설정 중 오류가 발생했습니다.');
        } finally {
            this.saveApiKeyBtn.textContent = '저장';
            this.saveApiKeyBtn.disabled = false;
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();

        if (!message) {
            return;
        }

        if (!this.apiKey) {
            this.showModal();
            return;
        }

        // 사용자 메시지 추가
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateCharCount();

        // 입력 비활성화
        this.setInputEnabled(false);
        this.showLoading();

        try {
            const userId = localStorage.getItem('userId') || 'anonymous';

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory,
                    user_id: userId
                })
            });

            const data = await response.json();

            if (response.ok) {
                // 위기 상황 감지
                if (data.crisis_alert) {
                    this.addMessage(data.message, 'buddha', true);
                } else {
                    // 부처님 응답 추가
                    this.addMessage(data.message, 'buddha');

                    // 명상 추천 표시 (선택적)
                    if (data.meditation_suggestion) {
                        this.showMeditationSuggestion(data.meditation_suggestion);
                    }
                }

                // 대화 기록에 추가
                this.conversationHistory.push({
                    user: message,
                    buddha: data.message
                });

                // 대화 기록이 너무 길어지면 최근 10개만 유지
                if (this.conversationHistory.length > 10) {
                    this.conversationHistory = this.conversationHistory.slice(-10);
                }
            } else {
                this.addSystemMessage(`오류가 발생했습니다: ${data.error}`);
            }
        } catch (error) {
            console.error('메시지 전송 실패:', error);
            this.addSystemMessage('부처님과의 연결에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } finally {
            this.hideLoading();
            this.setInputEnabled(true);
            this.messageInput.focus();
        }
    }

    addMessage(content, sender, isCrisis = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        if (isCrisis) {
            messageDiv.classList.add('crisis-message');
        }

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (sender === 'user') {
            avatarDiv.innerHTML = '<div class="mini-buddha">👤</div>';
        } else {
            avatarDiv.innerHTML = '<div class="mini-buddha">🙏</div>';
        }

        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message buddha-message';
        messageDiv.style.opacity = '0.9';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<div class="mini-buddha">ℹ️</div>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.style.background = 'linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)';
        contentDiv.style.border = '1px solid #90CAF9';

        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showMeditationSuggestion(meditation) {
        // 대시보드 영역이 있다면 표시
        const dashboard = document.getElementById('dashboard');
        if (!dashboard) return;

        const meditationCard = document.createElement('div');
        meditationCard.className = 'meditation-card fade-in';
        meditationCard.innerHTML = `
            <h4>💭 추천 명상: ${meditation.type}</h4>
            <p><strong>${meditation.description}</strong></p>
            ${meditation.guide ? `<p style="margin-top: 0.5rem; font-size: 0.85rem;">${meditation.guide.replace(/\n/g, '<br>')}</p>` : ''}
            <p style="margin-top: 0.5rem; color: var(--buddha-gold);">권장 시간: ${meditation.duration}</p>
        `;

        dashboard.innerHTML = '';
        dashboard.appendChild(meditationCard);
        dashboard.style.display = 'block';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading() {
        this.loadingIndicator.classList.add('show');
    }

    hideLoading() {
        this.loadingIndicator.classList.remove('show');
    }

    setInputEnabled(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
    }

    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/500`;

        // 색상 변경
        this.charCount.classList.remove('warning', 'danger');
        if (count > 450) {
            this.charCount.classList.add('danger');
        } else if (count > 400) {
            this.charCount.classList.add('warning');
        }
    }
}

// 부처님 캐릭터 애니메이션
class BuddhaAnimation {
    constructor() {
        this.initializeAnimation();
    }

    initializeAnimation() {
        // 눈 깜빡임은 CSS로 처리됨

        // 추가 인터랙션 (마우스 호버 시)
        const buddhaCharacter = document.querySelector('.buddha-character');
        if (buddhaCharacter) {
            buddhaCharacter.addEventListener('mouseenter', () => {
                buddhaCharacter.style.animationPlayState = 'paused';
            });

            buddhaCharacter.addEventListener('mouseleave', () => {
                buddhaCharacter.style.animationPlayState = 'running';
            });
        }
    }
}

// 페이지 가시성 변경 시 애니메이션 일시정지/재개
document.addEventListener('visibilitychange', () => {
    const buddhaCharacter = document.querySelector('.buddha-character');
    if (buddhaCharacter) {
        if (document.hidden) {
            buddhaCharacter.style.animationPlayState = 'paused';
        } else {
            buddhaCharacter.style.animationPlayState = 'running';
        }
    }
});

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.buddhaChat = new BuddhaChat();
    new BuddhaAnimation();

    // 일일 명상 로드
    loadDailyMeditation();
});

// 일일 명상 가이드 로드
async function loadDailyMeditation() {
    try {
        const response = await fetch('/api/meditation/daily');
        const meditation = await response.json();

        // 헤더나 푸터에 명상 인용구 표시 (선택적)
        const quoteElement = document.getElementById('dailyQuote');
        if (quoteElement) {
            quoteElement.textContent = meditation.quote;
        }
    } catch (error) {
        console.error('일일 명상 로드 실패:', error);
    }
}

// 세션 요약 가져오기 (선택적 - 버튼 클릭 시)
async function getSessionSummary() {
    try {
        const response = await fetch('/api/session/summary');
        const data = await response.json();

        console.log('세션 요약:', data);

        // 대시보드에 표시
        const dashboard = document.getElementById('dashboard');
        if (dashboard && data.session_summary) {
            const summary = data.session_summary;
            dashboard.innerHTML = `
                <div class="dashboard-title">🧘‍♂️ 오늘의 대화 요약</div>
                <p>총 대화 횟수: ${summary.total_messages}회</p>
                <p>주요 감정: <span class="emotion-badge">${summary.dominant_emotion}</span></p>
                <p>전체 분위기: ${summary.overall_valence === 'positive' ? '긍정적 ✨' : summary.overall_valence === 'negative' ? '힘든 시간 💭' : '평온함 🌸'}</p>
            `;
            dashboard.style.display = 'block';
        }
    } catch (error) {
        console.error('세션 요약 로드 실패:', error);
    }
}

// 전역 함수로 노출 (HTML에서 호출 가능)
window.getSessionSummary = getSessionSummary;
