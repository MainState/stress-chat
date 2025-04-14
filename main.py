
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
    
    # OpenAI API 호출 로직
    if openai_enabled:
        messages_for_api = [
            {"role": "system", "content": "너는 사용자의 스트레스에 대해 묻는 친절하고 공감 능력이 뛰어난 챗봇이야."},
            {"role": "user", "content": user_message}
        ]
        
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages_for_api
            )
            bot_reply = chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            bot_reply = "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
    else:
        bot_reply = "AI API가 준비되지 않았습니다. (임시 응답)"
    
    # 스트레스 점수 계산
    stress_score = calculate_stress_score([user_message])
    
    return jsonify({'reply': bot_reply, 'stress_score': stress_score})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
