
import os
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, session
from scoring import calculate_stress_score

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 실제 운영 환경에서는 안전한 키로 변경해야 합니다

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
    # 턴 카운터 로직
    turn_count = session.get('turn_count', 0)
    turn_count += 1
    session['turn_count'] = turn_count
    print(f"Current turn: {turn_count}")
    
    conversation_end = False
    if turn_count >= 20:
        conversation_end = True
        print("Conversation turn limit (20 turns) reached.")
    
    user_message = request.json.get('message')
    print(f"Received: {user_message}")
    
    # OpenAI API 호출 로직
    if openai_enabled:
        # 대화 기록 가져오기
        chat_history = session.get('chat_history', [])
        
        # API 메시지 목록 구성
        messages_for_api = [
            {"role": "system", "content": "너는 사용자의 하루 동안의 스트레스 수준을 파악하기 위해 약 3~5분간 자연스럽고 공감적인 대화를 이끄는 챗봇 상담사 역할이야.\n너의 주된 임무는 사용자에게 답변이나 해결책을 제시하는 것이 아니라, 개방형 질문을 던져서 사용자의 경험, 감정, 생각 등을 최대한 이끌어내는 거야.\n사용자의 하루 일과, 기분 변화, 수면 상태, 업무나 학업 관련 어려움, 대인관계 문제, 신체적 증상, 스트레스 해소 방법 등 스트레스와 관련된 다양한 주제에 대해 부드럽게 질문해야 해.\n사용자의 답변을 바탕으로 관련된 후속 질문을 던져 대화를 자연스럽게 이어가줘.\n매우 중요: 너의 답변은 대부분 사용자가 더 자세히 이야기하도록 유도하는 '질문'으로 끝나야 해.\n항상 차분하고, 지지적이며, 비판단적인 태도를 유지해야 하고, 절대 의학적 진단을 내리거나 전문적인 심리 상담을 대체하려는 시도를 해서는 안 돼."}
        ]
        
        # 최근 6개 메시지 추가
        history_limit = 6
        messages_for_api.extend(chat_history[-history_limit:])
        messages_for_api.append({"role": "user", "content": user_message})
        
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages_for_api
            )
            bot_reply = chat_completion.choices[0].message.content
            
            # 대화 기록 업데이트
            chat_history.append({"role": "user", "content": user_message})
            chat_history.append({"role": "assistant", "content": bot_reply})
            session['chat_history'] = chat_history
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            bot_reply = "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
    else:
        bot_reply = "AI API가 준비되지 않았습니다. (임시 응답)"
    
    # 사용자 메시지 기록 관리
    user_messages = session.get('user_messages', [])
    user_messages.append(user_message)
    session['user_messages'] = user_messages
    
    # 스트레스 점수 계산
    stress_score = calculate_stress_score(user_messages)
    
    return jsonify({
        'reply': bot_reply,
        'stress_score': stress_score,
        'conversation_end': conversation_end,
        'current_turn': turn_count,
        'max_turns': 20
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
