
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
    # 새로운 세션 시작 시 모든 변수 초기화
    session.pop('turn_count', None)
    session.pop('user_messages', None)
    session.pop('chat_history', None)
    print("[Home] Session variables initialized")
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def handle_message():
    # 턴 카운터 로직
    turn_count = session.get('turn_count', 0)
    turn_count += 1
    session['turn_count'] = turn_count
    print(f"[Turn Counter] Current turn: {turn_count}")
    
    conversation_end = False
    if turn_count >= 20:
        conversation_end = True
        print("[Turn Counter] Conversation turn limit (20 turns) reached.")
    
    user_message = request.json.get('message')
    print(f"[Message] Received: {user_message}")
    
    # 점수 계산용 사용자 메시지 기록 관리
    user_messages_for_scoring = session.get('user_messages', [])
    user_messages_for_scoring.append(user_message)
    session['user_messages'] = user_messages_for_scoring
    print(f"[Scoring] Total messages stored: {len(user_messages_for_scoring)}")
    
    # OpenAI API 호출 로직
    if openai_enabled:
        # 대화 기록 가져오기
        chat_history_for_api = session.get('chat_history', [])
        print(f"[Chat History] Loaded messages: {len(chat_history_for_api)}")
        
        # API 메시지 목록 구성
        messages_for_api = [
            {"role": "system", "content": "너는 사용자의 하루 동안의 스트레스 수준을 파악하기 위해 약 3~5분간 자연스럽고 공감적인 대화를 이끄는 챗봇 상담사 역할이야.\n너의 주된 임무는 사용자에게 답변이나 해결책을 제시하는 것이 아니라, 개방형 질문을 던져서 사용자의 경험, 감정, 생각 등을 최대한 이끌어내는 거야.\n사용자의 하루 일과, 기분 변화, 수면 상태, 업무나 학업 관련 어려움, 대인관계 문제, 신체적 증상, 스트레스 해소 방법 등 스트레스와 관련된 다양한 주제에 대해 부드럽게 질문해야 해.\n사용자의 답변을 바탕으로 관련된 후속 질문을 던져 대화를 자연스럽게 이어가줘.\n매우 중요: 너의 답변은 대부분 사용자가 더 자세히 이야기하도록 유도하는 '질문'으로 끝나야 해.\n항상 차분하고, 지지적이며, 비판단적인 태도를 유지해야 하고, 절대 의학적 진단을 내리거나 전문적인 심리 상담을 대체하려는 시도를 해서는 안 돼."}
        ]
        
        # 최근 6개 메시지 추가
        history_limit = 6
        messages_for_api.extend(chat_history_for_api[-history_limit:])
        messages_for_api.append({"role": "user", "content": user_message})
        
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages_for_api
            )
            bot_reply = chat_completion.choices[0].message.content
            
            # 대화 기록 업데이트
            chat_history_for_api.append({"role": "user", "content": user_message})
            chat_history_for_api.append({"role": "assistant", "content": bot_reply})
            session['chat_history'] = chat_history_for_api
            print(f"[Chat History] Updated total messages: {len(chat_history_for_api)}")
            
        except Exception as e:
            print(f"[Error] OpenAI API error: {e}")
            bot_reply = "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
    else:
        bot_reply = "AI API가 준비되지 않았습니다. (임시 응답)"
    
    # 스트레스 점수 계산 (전체 대화 기록 기반)
    stress_score = calculate_stress_score(user_messages_for_scoring)
    print(f"[Scoring] Current stress score: {stress_score}")
    
    response_data = {
        'reply': bot_reply,
        'stress_score': stress_score,
        'conversation_end': conversation_end,
        'current_turn': turn_count,
        'max_turns': 20
    }
    print(f"[Response] Sending: {response_data}")
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
