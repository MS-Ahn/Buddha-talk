from flask import Flask, request, jsonify, render_template, session, Response, stream_with_context
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# 커스텀 모듈 import
from prompts import get_system_prompt, get_relevant_teaching
from emotion_tracker import EmotionTracker, get_tracker
from data_logger import ConversationLogger, get_logger

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
CORS(app)

# OpenAI 클라이언트 (서버 사이드 관리로 보안 강화)
openai_client = None

# 감정 트래커 및 데이터 로거 초기화
emotion_tracker = get_tracker()
data_logger = get_logger(consent_required=True)

@app.route('/')
def index():
    """메인 페이지"""
    # 세션 ID 생성 (없으면)
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['conversation_turn'] = 0
        session['session_start'] = datetime.now().isoformat()

    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup_api():
    """OpenAI API 키 설정 (서버 환경 변수로 관리 권장)"""
    global openai_client
    data = request.get_json()
    api_key = data.get('api_key')

    if not api_key:
        return jsonify({'error': 'API 키가 필요합니다'}), 400

    try:
        # OpenAI 클라이언트 설정
        openai_client = openai.OpenAI(api_key=api_key)

        # 간단한 테스트 요청
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "안녕"}],
            max_tokens=10
        )

        # 세션에 플래그만 저장 (API 키는 저장하지 않음 - 보안)
        session['api_configured'] = True

        return jsonify({'message': 'API 키가 성공적으로 설정되었습니다'})

    except Exception as e:
        return jsonify({'error': f'API 키 설정 실패: {str(e)}'}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    """부처님과의 대화 (일반 응답)"""
    global openai_client

    if not openai_client:
        return jsonify({'error': 'API 키를 먼저 설정해주세요'}), 400

    data = request.get_json()
    user_message = data.get('message')
    conversation_history = data.get('history', [])
    user_id = data.get('user_id', 'anonymous')

    if not user_message:
        return jsonify({'error': '메시지가 필요합니다'}), 400

    try:
        # 세션 정보
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['conversation_turn'] = session.get('conversation_turn', 0) + 1

        # 감정 분석
        emotion_result = emotion_tracker.analyze_emotion(user_message)

        # 위기 상황 감지
        if emotion_result.get('needs_crisis_support'):
            crisis_response = """
제자여, 당신이 지금 매우 깊은 고통 속에 있다는 것이 느껴집니다.

이런 때는 혼자 견디지 마세요. 전문가의 도움이 필요합니다:

• 자살예방상담전화: 1393 (24시간)
• 정신건강위기상담: 1577-0199 (24시간)
• 희망의 전화: 129 (24시간)

당신의 생명은 무한히 소중합니다. 지금 당장 위 번호로 전화해주세요.
당신은 혼자가 아닙니다. 🙏
            """
            return jsonify({
                'message': crisis_response.strip(),
                'timestamp': str(datetime.now()),
                'emotion': emotion_result,
                'crisis_alert': True
            })

        # 대화 맥락 구성
        context = _build_context(conversation_history, emotion_result)

        # 시스템 프롬프트 생성 (Few-shot 포함)
        system_prompt = get_system_prompt(context=context, include_few_shot=True)

        # 메시지 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # OpenAI API 호출
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=800,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )

        buddha_response = response.choices[0].message.content

        # 데이터 로깅 (사용자 동의 시)
        if data_logger.check_consent(user_id):
            data_logger.log_conversation(
                user_id=user_id,
                session_id=session_id,
                user_message=user_message,
                buddha_response=buddha_response,
                detected_emotions=emotion_result.get('all_emotions', []),
                conversation_turn=session['conversation_turn']
            )

        return jsonify({
            'message': buddha_response,
            'timestamp': str(datetime.now()),
            'emotion': emotion_result,
            'meditation_suggestion': emotion_tracker.suggest_meditation()
        })

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': f'대화 생성 실패: {str(e)}'}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """스트리밍 응답 (실시간 타이핑 효과)"""
    global openai_client

    if not openai_client:
        return jsonify({'error': 'API 키를 먼저 설정해주세요'}), 400

    data = request.get_json()
    user_message = data.get('message')
    conversation_history = data.get('history', [])

    if not user_message:
        return jsonify({'error': '메시지가 필요합니다'}), 400

    def generate():
        try:
            # 감정 분석
            emotion_result = emotion_tracker.analyze_emotion(user_message)

            # 맥락 구성
            context = _build_context(conversation_history, emotion_result)
            system_prompt = get_system_prompt(context=context, include_few_shot=True)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # 스트리밍 응답
            stream = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=800,
                temperature=0.8,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

            # 완료 신호
            yield f"data: {json.dumps({'done': True, 'emotion': emotion_result})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/consent', methods=['POST'])
def save_consent():
    """사용자 데이터 수집 동의 저장"""
    data = request.get_json()
    consent = data.get('consent', False)

    # 사용자 ID 생성 (IP 기반 해시)
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    user_id = data_logger.generate_user_id(user_ip, user_agent)

    data_logger.save_consent(user_id, consent)

    # 세션에 저장
    session['user_id'] = user_id
    session['data_consent'] = consent

    return jsonify({
        'message': '동의 정보가 저장되었습니다',
        'user_id': user_id
    })

@app.route('/api/session/summary')
def get_session_summary():
    """현재 세션 요약 정보"""
    try:
        summary = emotion_tracker.get_session_summary()
        meditation = emotion_tracker.suggest_meditation()

        return jsonify({
            'session_summary': summary,
            'recommended_meditation': meditation,
            'session_id': session.get('session_id', 'unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """전체 데이터 통계 (관리자용)"""
    try:
        stats = data_logger.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """API 상태 확인"""
    return jsonify({
        'api_configured': openai_client is not None,
        'status': 'active',
        'session_id': session.get('session_id', None),
        'data_consent': session.get('data_consent', False)
    })

@app.route('/api/meditation/daily')
def daily_meditation():
    """매일 다른 명상 가이드 제공"""
    meditations = [
        {
            "title": "호흡 명상",
            "quote": "숨을 관찰하는 것만으로도 마음은 고요해진다",
            "guide": "코로 들어오고 나가는 숨을 5분간 관찰해보세요."
        },
        {
            "title": "자비 명상",
            "quote": "모든 존재가 행복하기를",
            "guide": "자신과 타인에게 자비의 마음을 보내보세요."
        },
        {
            "title": "걷기 명상",
            "quote": "한 걸음 한 걸음이 평화다",
            "guide": "천천히 걸으며 발바닥의 감각을 느껴보세요."
        }
    ]

    # 날짜 기반으로 로테이션
    day_index = datetime.now().timetuple().tm_yday % len(meditations)

    return jsonify(meditations[day_index])

def _build_context(conversation_history, emotion_result):
    """대화 맥락 구성"""
    context_parts = []

    # 최근 대화 요약
    if conversation_history:
        recent = conversation_history[-3:]
        context_parts.append(
            "최근 대화: " + " | ".join([
                f"사용자: {h['user'][:50]}... 부처님: {h['buddha'][:50]}..."
                for h in recent
            ])
        )

    # 감정 정보
    if emotion_result:
        context_parts.append(
            f"현재 감정: {emotion_result.get('primary_emotion', '알 수 없음')} "
            f"(강도: {emotion_result.get('intensity', 'medium')})"
        )

    # 세션 정보
    session_summary = emotion_tracker.get_session_summary()
    if session_summary['total_messages'] > 1:
        context_parts.append(
            f"세션 주요 감정: {session_summary.get('dominant_emotion', '중립')} "
            f"(총 {session_summary['total_messages']}번 대화)"
        )

    return " | ".join(context_parts) if context_parts else "새로운 대화 시작"

if __name__ == '__main__':
    # 프로덕션 환경에서는 gunicorn 사용 권장
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'

    app.run(debug=debug, host='0.0.0.0', port=port)
