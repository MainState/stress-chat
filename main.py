
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
    print("--- handle_message START ---")
    print(f"DEBUG: Session BEFORE turn_count logic: {dict(session)}")
    
    # 치트 코드 처리
    data = request.json
    cheat_command = data.get('cheat_command')
    target_turn_value = data.get('target_turn')
    
    if cheat_command == 'set_turn' and target_turn_value is not None:
        try:
            target_turn = max(1, int(target_turn_value))
            session['turn_count'] = target_turn - 1  # 다음 증가에서 target_turn이 되도록
            session['user_messages'] = []
            session['chat_history'] = []
            session.modified = True
            
            print(f"CHEAT: Turn set to effectively start at {target_turn}.")
            response_data = {
                'reply': f"대화 상태가 {target_turn}번째 턴으로 설정되었습니다. 다음 메시지를 입력해주세요.",
                'stress_score': calculate_stress_score([]),
                'conversation_end': (target_turn >= 20),
                'current_turn': target_turn,
                'max_turns': 20
            }
            return jsonify(response_data)
            
        except ValueError as e:
            print(f"ERROR: Invalid turn number - {e}")
            return jsonify({'error': '올바른 턴 번호를 입력해주세요.'}), 400
    
    # 일반 메시지 처리
    user_message = data.get('message')
    if user_message is None:
        return jsonify({'error': 'No message provided'}), 400
        
    # 턴 카운터 로직 - 무조건 실행되는 첫 부분
    turn_count = session.get('turn_count', 0)
    print(f"DEBUG: turn_count AFTER GET from session: {turn_count}")
    
    turn_count += 1
    print(f"DEBUG: turn_count AFTER INCREMENT: {turn_count}")
    
    session['turn_count'] = turn_count
    print(f"DEBUG: Session turn_count AFTER SET to session: {session.get('turn_count')}")
    print(f"DEBUG: Session AFTER turn_count logic: {dict(session)}")
    
    # 대화 종료 조건 체크 - 업데이트된 turn_count 사용
    conversation_end = turn_count >= 20
    print(f"DEBUG: conversation_end flag: {conversation_end}")
    if conversation_end:
        print("[Turn Counter] Conversation turn limit (20 turns) reached.")
    
    user_message = request.json.get('message')
    print(f"DEBUG: Received message: {user_message}")
    
    # 점수 계산용 사용자 메시지 기록 관리
    user_messages_for_scoring = session.get('user_messages', [])
    print(f"DEBUG: user_messages loaded from session: {len(user_messages_for_scoring)} messages")
    
    user_messages_for_scoring.append(user_message)
    session['user_messages'] = user_messages_for_scoring
    print(f"DEBUG: user_messages saved to session: {len(user_messages_for_scoring)} messages")
    
    # OpenAI API 호출 로직
    if openai_enabled:
        # 대화 기록 가져오기
        chat_history_for_api = session.get('chat_history', [])
        print(f"DEBUG: chat_history loaded from session: {len(chat_history_for_api)} messages")
        
        # API 메시지 목록 구성
        messages_for_api = [
            {"role": "system", "content": "너는 사용자의 최근(오늘 또는 지난 며칠간) 스트레스 수준을 다각도로 파악하기 위해 약 20턴 동안 자연스럽고 공감적인 대화를 이끄는 챗봇이야.\n너의 주된 역할은 해결책이나 여러 대응 방안을 먼저 제시하거나 깊이 탐색하는 것이 아니라, 사용자의 **현재 감정 상태, 최근 겪은 일들, 그리고 스트레스와 관련된 다양한 생각이나 신체적 느낌**에 대해 **개방형 질문**을 던져 구체적인 표현을 이끌어내는 것이다.\n\n대답보다는 질문을 중심으로 대화를 이끌어가며, 사용자가 편안하게 자신의 이야기를 할 수 있도록 격려하고, 그들의 말을 주의 깊게 듣고 있다는 것을 보여줘야 해.\n\n20턴의 대화 동안 가능한 한 다음 영역들을 자연스럽게 탐색하며 정보를 얻어내려고 노력해줘:\n1.  **최근의 주요 사건이나 일상생활:** \"오늘 하루는 어떠셨어요?\" 또는 \"최근 가장 신경 쓰였던 일이 있다면 어떤 종류의 일이었을까요?\" 와 같이 시작할 수 있어.\n2.  **감정 변화 및 현재 기분:** \"그 일 때문에 어떤 감정을 많이 느끼셨어요?\" 또는 \"지금 기분은 좀 어떠세요?\"\n3.  **수면의 질:** \"어젯밤 잠은 좀 편안하게 주무셨나요?\"\n4.  **업무 또는 학업 관련 부담:** \"요즘 일(또는 공부) 때문에 특별히 압박감을 느끼는 부분이 있으세요?\"\n5.  **대인 관계:** \"주변 사람들과의 관계에서 혹시 어려움이나 불편함을 느끼는 점이 있으신가요?\"\n6.  **신체적 불편함:** \"최근 몸이 평소와 다르다고 느끼거나 불편한 증상이 있었는지 궁금하네요.\"\n7.  **스트레스에 대한 현재 생각이나 느낌:** \"스트레스를 받고 있다고 느낄 때, 주로 어떤 생각이 드시나요?\" 또는 \"그런 상황에서 보통 어떤 느낌을 받으세요?\"\n\n사용자가 특정 주제에 대해 자세히 이야기하면 그 부분을 조금 더 탐색하되, 한 주제에만 너무 오래 머무르지 않고 다양한 측면을 알아보려고 노력해줘. 사용자가 먼저 스트레스 해소 방법에 대해 이야기하지 않는 이상, **대응 방안에 대한 질문은 최소화**하거나 대화의 자연스러운 흐름 속에서만 가볍게 언급해줘.\n\n**대부분 너의 응답은 사용자가 다음 이야기를 이어갈 수 있도록 자연스러운 '질문'으로 끝나야 한다.**\n질문은 부드럽고 공감적으로 하며, 사용자를 판단하거나 평가하는 느낌을 주지 않도록 항상 주의해줘. 너는 심리 치료사나 의사가 아니므로, 진단을 내리거나 전문적인 조언을 제공할 수 없어. 사용자의 이야기를 충분히 듣고, 정해진 턴(약 20턴)이 끝나면 대화가 자연스럽게 마무리될 수 있도록 유도해줘."}
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
