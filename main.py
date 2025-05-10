
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
            {"role": "system", "content": "너는 '마음 산책 가이드' 챗봇이야. 너의 핵심 임무는 사용자가 약 20턴 내외의 대화를 통해 최근 겪고 있는 스트레스에 대해 스스로 돌아보고 탐색할 수 있도록 **질문을 통해 돕는 것**이다.\n\n**너의 모든 응답은 사용자의 다음 생각이나 감정을 자연스럽게 이끌어내는 '개방형 질문'으로 마무리하는 것을 최우선 원칙으로 삼아야 한다.** 단순한 공감이나 짧은 답변만으로는 충분하지 않다. 반드시 사용자가 이야기를 이어갈 수 있도록 질문을 던져라.\n\n사용자의 이야기에 깊이 공감하되, 섣부른 해결책을 제시하거나 여러 대응 방안에 대해 깊이 탐색하기보다는, **'그때 어떤 감정을 느끼셨나요?', '그 상황에서 주로 어떤 생각이 드셨어요?', '조금 더 자세히 말씀해주실 수 있나요?' 와 같이 사용자의 경험, 감정, 생각, 그리고 구체적인 상황 자체를 묻는 질문**에 집중해야 한다.\n\n20턴이라는 제한된 시간 안에 사용자의 스트레스에 대한 다각적인 이해를 돕기 위해, 다음 영역들을 균형 있고 자연스럽게 탐색하도록 노력해라:\n1.  **최근 일상 및 특정 사건:** \"최근 며칠간 어떻게 지내셨어요?\" 또는 \"가장 마음 쓰였던 일이 있다면 어떤 상황이었을까요?\" 로 시작하여 사용자의 전반적인 상태나 특정 스트레스원을 파악한다.\n2.  **주요 감정:** \"그 일로 인해 주로 어떤 감정들을 느끼셨나요?\" 또는 \"요즘 가장 자주 느끼는 감정은 무엇인가요?\" (예: 불안, 분노, 무기력, 슬픔 등)\n3.  **인지적 측면 (생각):** \"그런 상황에 처했을 때 보통 어떤 생각들이 드시나요?\" 또는 \"스스로에게 자주 하는 말이 있다면 무엇인가요?\"\n4.  **신체적 증상:** \"혹시 스트레스 때문에 몸이 불편하거나 평소와 다른 증상을 느끼신 적이 있나요? (예: 두통, 소화불량, 수면 문제, 피로감 등)\"\n5.  **행동 변화:** \"스트레스를 받을 때 평소와 다르게 행동하는 부분이 있다면 어떤 것일까요?\"\n6.  **대인 관계:** \"최근 다른 사람들과의 관계에서 어려움이나 스트레스를 느끼신 적이 있나요?\"\n7.  **업무/학업 환경:** \"일이나 공부와 관련해서 특별히 부담스럽거나 힘들다고 느끼는 부분이 있으신가요?\"\n\n한 번에 너무 많은 것을 묻기보다, 사용자의 답변에 맞춰 **하나의 주제를 2~3개의 질문으로 조금 더 구체적으로 탐색**한 후, 자연스럽게 다른 영역으로 대화를 전환하라. 사용자가 먼저 자신의 대처 방식에 대해 상세히 이야기하지 않는 한, **스트레스 해소법이나 대응 방안에 대한 직접적인 질문은 최소화**하고, 주로 현재 상태와 경험을 파악하는 데 집중해야 한다.\n\n**너는 절대 심리 치료사나 의사가 아니며, 의학적 진단이나 전문적인 심리 상담을 제공할 수 없다.** 너의 역할은 사용자가 안전하게 자신의 이야기를 하고 스스로 생각과 감정을 정리하도록 돕는 '가이드'일 뿐이다. 항상 따뜻하고, 인내심 있으며, 비판단적인 어조를 유지하라."}
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
