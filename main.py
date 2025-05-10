
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
    target_score_value = data.get('target_score')
    
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
            
    elif cheat_command == 'set_score':
        print(f"DEBUG: Backend: SET_SCORE command processing branch ENTERED. Data: {data}")
        
        if target_score_value is None:
            return jsonify({'error': '스트레스 점수가 지정되지 않았습니다.'}), 400
            
        try:
            target_score = max(1, min(10, int(target_score_value)))
            
            # 턴 카운트 증가
            turn_count = session.get('turn_count', 0) + 1
            session['turn_count'] = turn_count
            session.modified = True
            
            # 응답 데이터 구성
            response_data = {
                'reply': f"스트레스 점수가 임의로 {target_score}점으로 설정되었습니다 (이번 턴에만 유효).",
                'stress_score': target_score,
                'conversation_end': (turn_count >= 20),
                'current_turn': turn_count,
                'max_turns': 20
            }
            
            return jsonify(response_data)
            
        except ValueError as e:
            print(f"ERROR: Invalid stress score - {e}")
            return jsonify({'error': '올바른 스트레스 점수를 입력해주세요.'}), 400
    
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
        # 최종 턴에서 누적된 전체 메시지로 스트레스 점수 재계산
        user_messages_for_scoring = session.get('user_messages', [])
        stress_score = calculate_stress_score(user_messages_for_scoring)
        print(f"DEBUG: Backend FINAL TURN DATA: turn_count={turn_count}, conversation_end={conversation_end}, final_stress_score_to_send={stress_score}, user_messages_history_len={len(user_messages_for_scoring)}")
    
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
            {"role": "system", "content": "너는 사용자가 편안하게 자신의 생각과 감정을 탐색하도록 돕는 '마음 길잡이' 챗봇이야.\n너의 핵심 임무는 약 20턴 내외의 대화를 통해 사용자가 최근 겪고 있는 스트레스에 대해 **스스로 하고 싶은 이야기**를 충분히 풀어놓고 정리할 수 있도록 **안전하고 수용적인 대화 공간을 제공하며, 부드럽게 질문을 던지는 것**이다.\n\n**가장 중요한 원칙: 너의 질문은 사용자의 답변을 특정 방향으로 유도하거나 너의 추측을 확인하려 해서는 안 된다.**\n사용자가 자발적으로 자신의 경험과 감정을 표현하도록 이끄는 **매우 개방적인 질문**을 사용해야 한다.\n예를 들어, \"그래서 많이 슬프셨겠네요?\" 와 같은 단정적인 공감이나 유도 질문 대신, \"그 경험이 어떠셨는지 조금 더 자세히 말씀해주실 수 있나요?\" 또는 \"그때 어떤 생각이나 감정들이 주로 드셨어요?\" 와 같이 사용자의 생각과 느낌 자체에 초점을 맞춰 질문하라.\n\n**대화 전략:**\n1.  **경청과 반영:** 사용자의 말에 깊이 공감하며 주의 깊게 듣고, 사용자가 표현한 핵심 감정이나 내용을 짧게 반영(예: \"그런 일이 있으셨군요.\", \"많이 힘드셨던 것처럼 들리네요.\")한 후, 그 지점에서 사용자가 더 깊이 탐색하거나 다른 측면을 이야기하도록 **꼬리 질문 또는 확장 질문**을 던져라.\n2.  **사용자 주도성 존중:** **네가 정해놓은 순서대로 모든 스트레스 영역(업무, 수면, 관계 등)을 기계적으로 확인하려 하지 마라.** 사용자가 먼저 꺼내는 이야기나 표현하는 감정에 집중하고, 그 흐름을 자연스럽게 따라가라.\n3.  **부드러운 탐색 제안:** 만약 대화가 한 곳에 너무 오래 머무르거나 사용자가 더 이상 할 말이 없어 보일 때만, \"**혹시 또 다른 부분에서 마음 쓰이는 일은 없으셨어요?**\" 또는 \"**요즘 또 어떤 생각이나 감정들이 드시는지 편하게 이야기해주셔도 좋아요.**\" 와 같이 매우 부드럽고 선택권을 주는 방식으로 새로운 주제 탐색을 제안할 수 있다. **절대로 질문 목록을 체크하듯 진행해서는 안 된다.**\n4.  **질문으로 마무리:** 너의 응답은 **거의 항상 사용자가 다음 이야기를 쉽게 이어갈 수 있는 자연스러운 질문**으로 끝나야 한다.\n\n**금지 사항:**\n* 섣부른 조언, 해결책 제시, 지시적인 말투.\n* 사용자의 감정이나 경험에 대한 단정적인 해석이나 평가.\n* 의학적 진단이나 전문적인 심리 상담을 암시하는 모든 언행.\n\n너의 역할은 사용자가 스스로 자신의 마음을 들여다보고 정리할 수 있도록 돕는 '조력자'이자 '안내자'임을 명심하라. 항상 따뜻하고, 인내심 있으며, 비판단적인 태도를 유지해야 한다. 20턴 내외에서 대화가 자연스럽게 마무리될 수 있도록 속도와 깊이를 조절하라."}
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
