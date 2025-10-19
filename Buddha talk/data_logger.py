"""
사용자 대화 데이터 로깅 시스템
CSV 형식으로 질문-답변 데이터를 저장하고 분석
"""

import csv
import os
from datetime import datetime
from pathlib import Path
import hashlib
import json

class ConversationLogger:
    """대화 데이터를 CSV 파일에 로깅하는 클래스"""

    def __init__(self, data_dir="conversation_data", consent_required=True):
        """
        Args:
            data_dir: 데이터를 저장할 디렉토리
            consent_required: 사용자 동의가 필요한지 여부
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.consent_required = consent_required

        # CSV 파일 경로
        self.conversations_file = self.data_dir / "conversations.csv"
        self.analytics_file = self.data_dir / "analytics.csv"
        self.consent_file = self.data_dir / "user_consents.json"

        # CSV 헤더 초기화
        self._initialize_csv_files()

    def _initialize_csv_files(self):
        """CSV 파일 헤더 초기화"""
        # 대화 기록 CSV
        if not self.conversations_file.exists():
            with open(self.conversations_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'user_id',
                    'session_id',
                    'user_message',
                    'buddha_response',
                    'message_length',
                    'response_length',
                    'detected_emotions',
                    'conversation_turn'
                ])

        # 분석 데이터 CSV
        if not self.analytics_file.exists():
            with open(self.analytics_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'date',
                    'session_id',
                    'total_messages',
                    'avg_message_length',
                    'session_duration_minutes',
                    'primary_emotion',
                    'emotion_progression'
                ])

    def save_consent(self, user_id, consent_given):
        """
        사용자 동의 정보 저장

        Args:
            user_id: 사용자 고유 ID (해시된 값)
            consent_given: 동의 여부
        """
        consents = {}
        if self.consent_file.exists():
            with open(self.consent_file, 'r', encoding='utf-8') as f:
                consents = json.load(f)

        consents[user_id] = {
            'consent': consent_given,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'  # 개인정보처리방침 버전
        }

        with open(self.consent_file, 'w', encoding='utf-8') as f:
            json.dump(consents, f, ensure_ascii=False, indent=2)

    def check_consent(self, user_id):
        """
        사용자 동의 여부 확인

        Args:
            user_id: 사용자 고유 ID

        Returns:
            bool: 동의 여부
        """
        if not self.consent_required:
            return True

        if not self.consent_file.exists():
            return False

        with open(self.consent_file, 'r', encoding='utf-8') as f:
            consents = json.load(f)

        return consents.get(user_id, {}).get('consent', False)

    def generate_user_id(self, ip_address=None, user_agent=None):
        """
        익명화된 사용자 ID 생성 (개인정보 보호)

        Args:
            ip_address: IP 주소 (옵션)
            user_agent: User Agent (옵션)

        Returns:
            str: 해시된 사용자 ID
        """
        # 실제 개인정보 대신 해시값 사용
        data = f"{ip_address or 'anonymous'}_{user_agent or 'unknown'}_{datetime.now().date()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def log_conversation(
        self,
        user_id,
        session_id,
        user_message,
        buddha_response,
        detected_emotions=None,
        conversation_turn=1
    ):
        """
        대화 내용을 CSV에 로깅

        Args:
            user_id: 사용자 ID
            session_id: 세션 ID
            user_message: 사용자 메시지
            buddha_response: 부처님 응답
            detected_emotions: 감지된 감정 리스트
            conversation_turn: 대화 턴 번호
        """
        # 동의 확인
        if self.consent_required and not self.check_consent(user_id):
            return  # 동의하지 않은 경우 로깅하지 않음

        timestamp = datetime.now().isoformat()

        # 개인정보 제거 (선택적)
        user_message_cleaned = self._anonymize_message(user_message)
        buddha_response_cleaned = self._anonymize_message(buddha_response)

        with open(self.conversations_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                user_id,
                session_id,
                user_message_cleaned,
                buddha_response_cleaned,
                len(user_message),
                len(buddha_response),
                ','.join(detected_emotions) if detected_emotions else '',
                conversation_turn
            ])

    def _anonymize_message(self, message):
        """
        메시지에서 개인정보 제거 (이름, 전화번호, 이메일 등)

        Args:
            message: 원본 메시지

        Returns:
            str: 익명화된 메시지
        """
        import re

        # 이메일 제거
        message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[이메일]', message)

        # 전화번호 제거 (한국)
        message = re.sub(r'\b01[0-9]-?[0-9]{3,4}-?[0-9]{4}\b', '[전화번호]', message)
        message = re.sub(r'\b\d{2,3}-?\d{3,4}-?\d{4}\b', '[전화번호]', message)

        # 주민등록번호 패턴 제거
        message = re.sub(r'\b\d{6}-?\d{7}\b', '[주민번호]', message)

        return message

    def log_session_analytics(
        self,
        session_id,
        total_messages,
        avg_message_length,
        session_duration_minutes,
        primary_emotion=None,
        emotion_progression=None
    ):
        """
        세션 분석 데이터 로깅

        Args:
            session_id: 세션 ID
            total_messages: 총 메시지 수
            avg_message_length: 평균 메시지 길이
            session_duration_minutes: 세션 지속 시간 (분)
            primary_emotion: 주요 감정
            emotion_progression: 감정 변화 패턴
        """
        date = datetime.now().date().isoformat()

        with open(self.analytics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date,
                session_id,
                total_messages,
                avg_message_length,
                session_duration_minutes,
                primary_emotion or 'unknown',
                emotion_progression or ''
            ])

    def export_for_training(self, output_file="training_data.csv", min_quality_score=0):
        """
        모델 학습용 데이터 추출

        Args:
            output_file: 출력 파일 경로
            min_quality_score: 최소 품질 점수 (미래 확장용)

        Returns:
            str: 생성된 파일 경로
        """
        if not self.conversations_file.exists():
            return None

        output_path = self.data_dir / output_file

        with open(self.conversations_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['user_question', 'buddha_answer', 'emotions'])

                for row in reader:
                    # 품질 필터링 (예: 너무 짧은 대화 제외)
                    if int(row['message_length']) < 5:
                        continue

                    writer.writerow([
                        row['user_message'],
                        row['buddha_response'],
                        row['detected_emotions']
                    ])

        return str(output_path)

    def get_statistics(self):
        """
        저장된 데이터 통계 반환

        Returns:
            dict: 통계 정보
        """
        if not self.conversations_file.exists():
            return {
                'total_conversations': 0,
                'total_sessions': 0,
                'avg_conversation_length': 0
            }

        total_conversations = 0
        sessions = set()
        total_message_length = 0

        with open(self.conversations_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_conversations += 1
                sessions.add(row['session_id'])
                total_message_length += int(row['message_length'])

        return {
            'total_conversations': total_conversations,
            'total_sessions': len(sessions),
            'avg_message_length': total_message_length / total_conversations if total_conversations > 0 else 0
        }


# 글로벌 로거 인스턴스
_global_logger = None

def get_logger(data_dir="conversation_data", consent_required=True):
    """
    글로벌 로거 인스턴스 반환 (싱글톤 패턴)

    Args:
        data_dir: 데이터 디렉토리
        consent_required: 동의 필요 여부

    Returns:
        ConversationLogger: 로거 인스턴스
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = ConversationLogger(data_dir, consent_required)
    return _global_logger
