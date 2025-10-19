"""
감정 추적 및 분석 시스템
사용자 메시지에서 감정을 추출하고 대화 흐름 분석
"""

from typing import List, Dict, Tuple
from datetime import datetime
import json
from collections import Counter

class EmotionTracker:
    """사용자의 감정 상태를 추적하고 분석하는 클래스"""

    # 감정 키워드 사전
    EMOTION_KEYWORDS = {
        "슬픔": [
            "슬프", "우울", "눈물", "외로", "쓸쓸", "허전", "공허",
            "상실", "그리움", "아쉬움", "애처로", "비참", "암울"
        ],
        "분노": [
            "화", "짜증", "분노", "열받", "미움", "원망", "억울",
            "불쾌", "약올", "배신", "복수", "증오"
        ],
        "불안": [
            "불안", "걱정", "두렵", "무서", "초조", "긴장", "떨림",
            "공포", "혼란", "패닉", "조급", "근심"
        ],
        "스트레스": [
            "스트레스", "힘들", "지쳐", "피곤", "압박", "부담", "벅차",
            "버거", "견딜", "감당", "포기", "한계"
        ],
        "자기비난": [
            "부족", "못나", "한심", "쓸모없", "실패", "자책", "후회",
            "죄책감", "미안", "창피", "부끄", "수치"
        ],
        "고통": [
            "아프", "고통", "괴롭", "힘들", "견디", "극복", "상처",
            "트라우마", "악몽", "시달"
        ],
        "외로움": [
            "외로", "혼자", "고립", "단절", "소외", "버림", "이해받지",
            "무시", "따돌림"
        ],
        "행복": [
            "행복", "기쁘", "즐거", "감사", "만족", "뿌듯", "설레",
            "좋아", "사랑", "평화", "편안"
        ],
        "희망": [
            "희망", "기대", "긍정", "나아질", "좋아질", "발전", "성장",
            "가능", "할 수 있"
        ]
    }

    # 고통 강도 키워드
    INTENSITY_KEYWORDS = {
        "high": ["너무", "정말", "진짜", "완전", "엄청", "극도로", "심하게", "못 견딜"],
        "medium": ["좀", "조금", "약간", "꽤", "상당히"],
        "low": ["살짝", "가끔", "때때로", "조금씩"]
    }

    def __init__(self):
        self.session_emotions = []  # 세션별 감정 기록
        self.session_start_time = datetime.now()

    def analyze_emotion(self, message: str) -> Dict[str, any]:
        """
        메시지에서 감정 분석

        Args:
            message: 사용자 메시지

        Returns:
            dict: 감정 분석 결과
        """
        detected_emotions = []
        emotion_scores = {}

        # 각 감정별 키워드 매칭
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score
                detected_emotions.append(emotion)

        # 고통 강도 분석
        intensity = self._analyze_intensity(message)

        # 주요 감정 추출 (가장 높은 스코어)
        primary_emotion = max(emotion_scores, key=emotion_scores.get) if emotion_scores else "중립"

        # 긍정/부정 판단
        valence = self._analyze_valence(detected_emotions)

        result = {
            "primary_emotion": primary_emotion,
            "all_emotions": detected_emotions,
            "emotion_scores": emotion_scores,
            "intensity": intensity,
            "valence": valence,  # positive, negative, neutral
            "needs_crisis_support": self._check_crisis_keywords(message),
            "timestamp": datetime.now().isoformat()
        }

        # 세션 기록에 추가
        self.session_emotions.append(result)

        return result

    def _analyze_intensity(self, message: str) -> str:
        """
        감정의 강도 분석

        Args:
            message: 메시지

        Returns:
            str: high, medium, low
        """
        for intensity, keywords in self.INTENSITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message:
                    return intensity
        return "medium"

    def _analyze_valence(self, emotions: List[str]) -> str:
        """
        감정의 긍정/부정 판단

        Args:
            emotions: 감지된 감정 리스트

        Returns:
            str: positive, negative, neutral
        """
        positive_emotions = {"행복", "희망"}
        negative_emotions = {"슬픔", "분노", "불안", "스트레스", "자기비난", "고통", "외로움"}

        positive_count = sum(1 for e in emotions if e in positive_emotions)
        negative_count = sum(1 for e in emotions if e in negative_emotions)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _check_crisis_keywords(self, message: str) -> bool:
        """
        위기 상황 키워드 체크 (자살, 자해 등)

        Args:
            message: 메시지

        Returns:
            bool: 위기 상황 여부
        """
        crisis_keywords = [
            "자살", "죽고싶", "죽어버리", "살기싫", "사라지고싶",
            "자해", "칼", "손목", "투신", "목매", "끝내고싶"
        ]

        return any(keyword in message for keyword in crisis_keywords)

    def get_emotion_progression(self) -> List[str]:
        """
        세션 동안의 감정 변화 추이 반환

        Returns:
            list: 감정 변화 리스트
        """
        return [emotion["primary_emotion"] for emotion in self.session_emotions]

    def get_session_summary(self) -> Dict[str, any]:
        """
        현재 세션의 감정 요약

        Returns:
            dict: 세션 요약 정보
        """
        if not self.session_emotions:
            return {
                "total_messages": 0,
                "dominant_emotion": "중립",
                "emotion_distribution": {},
                "overall_valence": "neutral",
                "session_duration_minutes": 0
            }

        # 가장 많이 나타난 감정
        all_primary_emotions = [e["primary_emotion"] for e in self.session_emotions]
        emotion_counter = Counter(all_primary_emotions)
        dominant_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "중립"

        # 전체 valence 계산
        valences = [e["valence"] for e in self.session_emotions]
        valence_counter = Counter(valences)
        overall_valence = valence_counter.most_common(1)[0][0] if valence_counter else "neutral"

        # 세션 지속 시간
        duration = (datetime.now() - self.session_start_time).total_seconds() / 60

        return {
            "total_messages": len(self.session_emotions),
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": dict(emotion_counter),
            "overall_valence": overall_valence,
            "session_duration_minutes": round(duration, 2),
            "emotion_progression": self.get_emotion_progression()
        }

    def suggest_meditation(self) -> Dict[str, str]:
        """
        현재 감정 상태에 맞는 명상법 추천

        Returns:
            dict: 명상법 정보
        """
        if not self.session_emotions:
            return {
                "type": "호흡 명상",
                "description": "기본적인 호흡 관찰로 마음을 안정시킵니다.",
                "duration": "5-10분"
            }

        summary = self.get_session_summary()
        dominant_emotion = summary["dominant_emotion"]

        meditation_map = {
            "분노": {
                "type": "자비 명상 (Metta)",
                "description": "자신과 타인에게 자비의 마음을 보내는 명상입니다.",
                "guide": "1. 편안히 앉아 눈을 감습니다.\n2. '나 자신이 평화롭기를' 마음속으로 말합니다.\n3. 분노의 대상에게도 같은 마음을 보냅니다.\n4. 모든 존재에게 확장합니다.",
                "duration": "10-15분"
            },
            "불안": {
                "type": "호흡 명상 (Anapanasati)",
                "description": "호흡에 집중하여 현재 순간에 머물러 불안을 가라앉힙니다.",
                "guide": "1. 코로 들어오고 나가는 숨을 관찰합니다.\n2. 마음이 흩어지면 부드럽게 호흡으로 돌아옵니다.\n3. '지금 이 순간은 괜찮다'고 느껴봅니다.",
                "duration": "10-20분"
            },
            "슬픔": {
                "type": "수용 명상",
                "description": "슬픔을 있는 그대로 받아들이고 관찰하는 명상입니다.",
                "guide": "1. 슬픔이 몸 어디에 느껴지는지 관찰합니다.\n2. 그것을 밀어내지 않고 그냥 지켜봅니다.\n3. '이것도 지나갈 것이다'라고 느껴봅니다.",
                "duration": "10-15분"
            },
            "스트레스": {
                "type": "바디 스캔",
                "description": "몸의 긴장을 풀어주는 명상입니다.",
                "guide": "1. 누워서 발끝부터 머리까지 천천히 관찰합니다.\n2. 긴장된 부분을 발견하면 숨을 내쉬며 이완합니다.\n3. 온몸이 편안해지는 것을 느낍니다.",
                "duration": "15-20분"
            },
            "자기비난": {
                "type": "자애 명상",
                "description": "자신에게 친절하고 자비로운 마음을 갖는 명상입니다.",
                "guide": "1. 손을 가슴에 대고 따뜻함을 느낍니다.\n2. '나는 충분히 가치 있는 사람이다'라고 말합니다.\n3. 자신의 노력을 인정하고 격려합니다.",
                "duration": "10분"
            }
        }

        return meditation_map.get(
            dominant_emotion,
            {
                "type": "호흡 명상",
                "description": "기본적인 호흡 관찰로 마음을 안정시킵니다.",
                "guide": "1. 편안히 앉아 호흡에 집중합니다.\n2. 생각이 떠오르면 판단하지 않고 흘려보냅니다.\n3. 현재 순간에 머뭅니다.",
                "duration": "5-10분"
            }
        )

    def reset_session(self):
        """새로운 세션 시작 (데이터 초기화)"""
        self.session_emotions = []
        self.session_start_time = datetime.now()


# 글로벌 트래커 인스턴스
_global_tracker = None

def get_tracker():
    """
    글로벌 감정 트래커 반환

    Returns:
        EmotionTracker: 트래커 인스턴스
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = EmotionTracker()
    return _global_tracker
