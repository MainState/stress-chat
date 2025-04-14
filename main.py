
import os
from openai import OpenAI
from flask import Flask, render_template, request, jsonify
from scoring import calculate_stress_score

app = Flask(__name__)

# OpenAI 클라이언트 초기화
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. Secrets 메뉴를 확인하세요.")
    openai_enabled = False
    client = None
else:
    try:
        client = OpenAI(api_key=openai_api_key)
        openai_enabled = True
        print("OpenAI 클라이언트 초기화 성공.")
    except Exception as e:
        print(f"OpenAI 클라이언트 초기화 실패: {e}")
        openai_enabled = False
        client = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def handle_message():
    user_message = request.json.get('message')
    print(f"Received: {user_message}")
    
    bot_reply = f"'{user_message}' 잘 받았습니다!"
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
