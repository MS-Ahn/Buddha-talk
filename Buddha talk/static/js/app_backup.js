class BuddhaChat {
    constructor() {
        this.apiKey = null;
        this.conversationHistory = [];
        this.initializeElements();
        this.bindEvents();
        this.checkApiStatus();
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
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 문자 수 카운터
        this.messageInput.addEventListener('input', () => this.updateCharCount());

        // Enter 키로 전송, Shift+Enter로 줄바꿈
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                if (e.shiftKey) {
                    return; // 줄바꿈 허용
                } else {
                    e.preventDefault();
                    this.sendMessage();
                }
            }
        });
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (!data.api_configured) {
                this.showModal();
            }
        } catch (error) {
            console.error('API 상태 확인 실패:', error);
            this.showModal();
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
                this.addSystemMessage('API 키가 성공적으로 설정되었습니다. 이제 부처님과 대화할 수 있습니다! 🙏');
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
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.conversationHistory
                })
            });

            const data = await response.json();

            if (response.ok) {
                // 부처님 응답 추가
                this.addMessage(data.message, 'buddha');
                
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

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

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
        messageDiv.style.opacity = '0.8';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<div class="mini-buddha">ℹ️</div>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.style.background = 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)';
        contentDiv.style.border = '1px solid #90caf9';

        const p = document.createElement('p');
        p.textContent = content;
        contentDiv.appendChild(p);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
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
        
        if (count > 450) {
            this.charCount.style.color = '#ff5722';
        } else if (count > 400) {
            this.charCount.style.color = '#ff9800';
        } else {
            this.charCount.style.color = '#999';
        }
    }
}

// 부처님 캐릭터 애니메이션
class BuddhaAnimation {
    constructor() {
        this.initializeAnimation();
    }

    initializeAnimation() {
        // 눈 깜빡임 애니메이션
        const eyes = document.querySelectorAll('.eye');
        setInterval(() => {
            eyes.forEach(eye => {
                eye.style.transform = 'scaleY(0.1)';
                setTimeout(() => {
                    eye.style.transform = 'scaleY(1)';
                }, 100);
            });
        }, 3000);

        // 미소 애니메이션
        const smile = document.querySelector('.smile');
        setInterval(() => {
            smile.style.transform = 'translateX(-50%) scaleY(1.2)';
            setTimeout(() => {
                smile.style.transform = 'translateX(-50%) scaleY(1)';
            }, 500);
        }, 5000);
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    new BuddhaChat();
    new BuddhaAnimation();
});

// 페이지 가시성 변경 시 부처님 캐릭터 애니메이션 일시정지/재개
document.addEventListener('visibilitychange', () => {
    const buddhaCharacter = document.querySelector('.buddha-character');
    if (document.hidden) {
        buddhaCharacter.style.animationPlayState = 'paused';
    } else {
        buddhaCharacter.style.animationPlayState = 'running';
    }
});
