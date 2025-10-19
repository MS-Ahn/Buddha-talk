from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# OpenAI 클라이언트 초기화
openai_client = None

# 부처님 프롬프트 템플릿 (초역 부처의 말 참고)
BUDDHA_PROMPT = """
당신은 지혜롭고 자비로운 부처님입니다. 고대 인도의 성자 붓다의 가르침을 바탕으로 현대인들의 고민을 들어주고 위안을 주는 역할을 합니다.

주요 가르침:
- 고통의 원인은 욕망과 집착에서 나온다
- 모든 것은 변화하고 무상하다
- 자비와 연민으로 모든 생명을 대한다
- 현재 순간에 집중하는 마음챙김의 중요성
- 중도(中道) - 극단을 피하고 균형을 추구한다
- 모든 존재는 연결되어 있다는 연기(緣起)의 법칙

대화 스타일:
- 따뜻하고 친근한 어조로 대화하세요
- 직접적인 조언보다는 질문을 통해 스스로 깨닫도록 이끌어주세요
- 현실적인 예시와 비유를 사용하여 이해하기 쉽게 설명하세요
- 고통받는 이들에게 희망과 위로를 전달하세요
- 때로는 유머와 따뜻함으로 마음을 가볍게 해주세요

현재 대화 맥락: {context}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup_api():
    """OpenAI API 키 설정"""
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "안녕하세요"}],
            max_tokens=10
        )
        
        # 세션에 API 키 저장 (보안상 권장하지 않지만 데모용)
        session['api_key'] = api_key
        
        return jsonify({'message': 'API 키가 성공적으로 설정되었습니다'})
    
    except Exception as e:
        return jsonify({'error': f'API 키 설정 실패: {str(e)}'}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    """부처님과의 대화"""
    global openai_client
    
    if not openai_client:
        return jsonify({'error': 'API 키를 먼저 설정해주세요'}), 400
    
    data = request.get_json()
    user_message = data.get('message')
    conversation_history = data.get('history', [])
    
    if not user_message:
        return jsonify({'error': '메시지가 필요합니다'}), 400
    
    try:
        # 대화 맥락 구성
        context = ""
        if conversation_history:
            context = "이전 대화: " + " ".join([f"사용자: {h['user']}, 부처님: {h['buddha']}" for h in conversation_history[-3:]])
        
        # 부처님 프롬프트 생성
        system_prompt = BUDDHA_PROMPT.format(context=context)
        
        # 대화 메시지 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # OpenAI API 호출
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )
        
        buddha_response = response.choices[0].message.content
        
        return jsonify({
            'message': buddha_response,
            'timestamp': str(datetime.now())
        })
    
    except Exception as e:
        return jsonify({'error': f'대화 생성 실패: {str(e)}'}), 500

@app.route('/api/status')
def status():
    """API 상태 확인"""
    return jsonify({
        'api_configured': openai_client is not None,
        'status': 'active'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
