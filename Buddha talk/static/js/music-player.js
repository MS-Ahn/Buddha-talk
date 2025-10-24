/**
 * Buddha Talk - 명상 음악 플레이어
 * 불교 명상 BGM 재생
 */

class MeditationMusicPlayer {
    constructor() {
        this.audio = null;
        this.isPlaying = false;
        this.currentTrack = 0;
        this.volume = 0.3; // 기본 볼륨 30%

        // 무료 명상 음악 URL (YouTube Audio Library 등에서 가져온 것)
        // 실제 배포 시에는 저작권 걱정 없는 음원 사용
        this.tracks = [
            {
                name: "평온한 사찰",
                url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                duration: "5:00"
            },
            {
                name: "선 명상",
                url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                duration: "5:00"
            },
            {
                name: "연꽃의 평화",
                url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
                duration: "5:00"
            }
        ];

        this.initPlayer();
        this.bindEvents();
    }

    initPlayer() {
        // 오디오 엘리먼트 생성
        this.audio = new Audio();
        this.audio.volume = this.volume;
        this.audio.loop = true; // 무한 반복

        // 첫 번째 트랙 로드
        this.loadTrack(0);

        // 로컬 스토리지에서 설정 불러오기
        const savedVolume = localStorage.getItem('musicVolume');
        const musicEnabled = localStorage.getItem('musicEnabled');

        if (savedVolume) {
            this.volume = parseFloat(savedVolume);
            this.audio.volume = this.volume;
            this.updateVolumeUI();
        }

        if (musicEnabled === 'true') {
            // 자동 재생은 사용자 상호작용 후에만 가능
            // 처음 방문 시에는 수동으로 재생
        }
    }

    loadTrack(index) {
        if (index >= 0 && index < this.tracks.length) {
            this.currentTrack = index;
            this.audio.src = this.tracks[index].url;
            this.updateTrackInfoUI();
        }
    }

    bindEvents() {
        const playBtn = document.getElementById('musicPlayBtn');
        const volumeSlider = document.getElementById('volumeSlider');
        const prevBtn = document.getElementById('prevTrack');
        const nextBtn = document.getElementById('nextTrack');
        const musicToggle = document.getElementById('musicToggle');

        if (playBtn) {
            playBtn.addEventListener('click', () => this.togglePlay());
        }

        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                this.setVolume(e.target.value / 100);
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousTrack());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextTrack());
        }

        if (musicToggle) {
            musicToggle.addEventListener('click', () => this.toggleMusicPanel());
        }

        // 오디오 이벤트
        this.audio.addEventListener('ended', () => this.nextTrack());
        this.audio.addEventListener('error', (e) => {
            console.error('음악 로드 실패:', e);
            this.nextTrack(); // 다음 트랙으로
        });
    }

    togglePlay() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    play() {
        this.audio.play()
            .then(() => {
                this.isPlaying = true;
                this.updatePlayButtonUI();
                localStorage.setItem('musicEnabled', 'true');
            })
            .catch(error => {
                console.error('재생 실패:', error);
                alert('음악을 재생할 수 없습니다. 브라우저 설정을 확인해주세요.');
            });
    }

    pause() {
        this.audio.pause();
        this.isPlaying = false;
        this.updatePlayButtonUI();
        localStorage.setItem('musicEnabled', 'false');
    }

    setVolume(value) {
        this.volume = Math.max(0, Math.min(1, value));
        this.audio.volume = this.volume;
        this.updateVolumeUI();
        localStorage.setItem('musicVolume', this.volume);
    }

    nextTrack() {
        const wasPlaying = this.isPlaying;
        this.pause();
        this.currentTrack = (this.currentTrack + 1) % this.tracks.length;
        this.loadTrack(this.currentTrack);
        if (wasPlaying) {
            this.play();
        }
    }

    previousTrack() {
        const wasPlaying = this.isPlaying;
        this.pause();
        this.currentTrack = (this.currentTrack - 1 + this.tracks.length) % this.tracks.length;
        this.loadTrack(this.currentTrack);
        if (wasPlaying) {
            this.play();
        }
    }

    updatePlayButtonUI() {
        const playBtn = document.getElementById('musicPlayBtn');
        if (playBtn) {
            if (this.isPlaying) {
                playBtn.innerHTML = '⏸';
                playBtn.title = '일시정지';
            } else {
                playBtn.innerHTML = '▶';
                playBtn.title = '재생';
            }
        }
    }

    updateVolumeUI() {
        const volumeSlider = document.getElementById('volumeSlider');
        const volumeValue = document.getElementById('volumeValue');

        if (volumeSlider) {
            volumeSlider.value = this.volume * 100;
        }

        if (volumeValue) {
            volumeValue.textContent = Math.round(this.volume * 100) + '%';
        }
    }

    updateTrackInfoUI() {
        const trackName = document.getElementById('currentTrackName');
        if (trackName) {
            trackName.textContent = this.tracks[this.currentTrack].name;
        }
    }

    toggleMusicPanel() {
        const panel = document.getElementById('musicPanel');
        if (panel) {
            panel.classList.toggle('show');
        }
    }
}

// 전역 변수로 플레이어 인스턴스 생성
let musicPlayer;

document.addEventListener('DOMContentLoaded', () => {
    musicPlayer = new MeditationMusicPlayer();
});

// 전역 함수로 노출
window.toggleMusic = () => {
    if (musicPlayer) {
        musicPlayer.togglePlay();
    }
};
