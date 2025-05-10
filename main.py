
import os
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, session
from scoring import calculate_stress_score

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 실제 운영 환경에서는 안전한 키로 변경해야 합니다

# 대화 종료 조건 관련 상수
MAX_SCORE_CHANGES = 10
MAX_CONVERSATION_TURNS = 25

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
    # 세션 변수 초기화
    session.pop('turn_count', None)
    session.pop('user_messages', None)
    session.pop('chat_history', None)
    session['score_change_count'] = 0
    session['previous_score'] = 5.0
    print("[Home] Session variables initialized")
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def handle_message():
    print("--- handle_message START ---")
    
    # 세션 변수 가져오기
    turn_count = session.get('turn_count', 0) + 1
    session['turn_count'] = turn_count
    score_change_count = session.get('score_change_count', 0)
    previous_score = session.get('previous_score', 5.0)
    user_messages_history = session.get('user_messages', [])
    chat_history_for_api = session.get('chat_history', [])
    
    print(f"DEBUG: Turn {turn_count}, PrevScore: {previous_score}, ScoreChanges: {score_change_count}")
    
    # 치트 코드 처리
    data = request.json
    cheat_command = data.get('cheat_command')
    target_turn_value = data.get('target_turn')
    target_score_value = data.get('target_score')
    
    if cheat_command == 'set_turn' and target_turn_value is not None:
        try:
            target_turn = max(1, int(target_turn_value))
            session['turn_count'] = target_turn - 1
            session['user_messages'] = []
            session['chat_history'] = []
            session.modified = True
            
            print(f"CHEAT: Turn set to effectively start at {target_turn}.")
            response_data = {
                'reply': f"대화 상태가 {target_turn}번째 턴으로 설정되었습니다. 다음 메시지를 입력해주세요.",
                'stress_score': calculate_stress_score([]),
                'conversation_end': (target_turn >= MAX_CONVERSATION_TURNS),
                'current_turn': target_turn,
                'max_turns': MAX_CONVERSATION_TURNS,
                'score_changes': score_change_count,
                'max_score_changes': MAX_SCORE_CHANGES
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
            
            response_data = {
                'reply': f"스트레스 점수가 임의로 {target_score}점으로 설정되었습니다 (이번 턴에만 유효).",
                'stress_score': target_score,
                'conversation_end': (turn_count >= MAX_CONVERSATION_TURNS),
                'current_turn': turn_count,
                'max_turns': MAX_CONVERSATION_TURNS,
                'score_changes': score_change_count,
                'max_score_changes': MAX_SCORE_CHANGES
            }
            
            return jsonify(response_data)
            
        except ValueError as e:
            print(f"ERROR: Invalid stress score - {e}")
            return jsonify({'error': '올바른 스트레스 점수를 입력해주세요.'}), 400

    # 일반 메시지 처리
    user_message = data.get('message')
    if user_message is None:
        return jsonify({'error': 'No message provided'}), 400

    # 사용자 메시지 기록 관리
    user_messages_history.append(user_message)
    session['user_messages'] = user_messages_history
    print(f"DEBUG: user_messages saved to session: {len(user_messages_history)} messages")

    # 현재 스트레스 점수 계산
    current_stress_result = calculate_stress_score(user_messages_history)
    current_overall_score = current_stress_result['overall_score']
    print(f"DEBUG: Current calculated score: {current_overall_score}")

    # 점수 변동 감지 및 카운트 업데이트
    if abs(current_overall_score - previous_score) > 0.01:
        score_change_count += 1
        session['score_change_count'] = score_change_count
        print(f"DEBUG: Score CHANGED! New score: {current_overall_score}, Change count: {score_change_count}")
    session['previous_score'] = current_overall_score

    # OpenAI API 호출
    if openai_enabled:
        messages_for_api = [
            {"role": "system", "content": "너는 사용자가 편안하게 자신의 생각과 감정을 탐색하도록 돕는 '마음 길잡이' 챗봇이야.\n너의 핵심 임무는 약 20턴 내외의 대화를 통해 사용자가 최근 겪고 있는 스트레스에 대해 **스스로 하고 싶은 이야기**를 충분히 풀어놓고 정리할 수 있도록 **안전하고 수용적인 대화 공간을 제공하며, 부드럽게 질문을 던지는 것**이다.\n\n**가장 중요한 원칙: 너의 질문은 사용자의 답변을 특정 방향으로 유도하거나 너의 추측을 확인하려 해서는 안 된다.**\n사용자가 자발적으로 자신의 경험과 감정을 표현하도록 이끄는 **매우 개방적인 질문**을 사용해야 한다.\n예를 들어, \"그래서 많이 슬프셨겠네요?\" 와 같은 단정적인 공감이나 유도 질문 대신, \"그 경험이 어떠셨는지 조금 더 자세히 말씀해주실 수 있나요?\" 또는 \"그때 어떤 생각이나 감정들이 주로 드셨어요?\" 와 같이 사용자의 생각과 느낌 자체에 초점을 맞춰 질문하라."}
        ]
        
        history_limit = 6
        messages_for_api.extend(chat_history_for_api[-history_limit:])
        messages_for_api.append({"role": "user", "content": user_message})
        
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages_for_api
            )
            bot_reply = chat_completion.choices[0].message.content
            
            chat_history_for_api.append({"role": "user", "content": user_message})
            chat_history_for_api.append({"role": "assistant", "content": bot_reply})
            session['chat_history'] = chat_history_for_api
            
        except Exception as e:
            print(f"[Error] OpenAI API error: {e}")
            bot_reply = "죄송합니다. AI 응답 생성 중 오류가 발생했습니다."
    else:
        bot_reply = "AI API가 준비되지 않았습니다. (임시 응답)"

    # 대화 종료 조건 체크
    conversation_end = False
    if score_change_count >= MAX_SCORE_CHANGES or turn_count >= MAX_CONVERSATION_TURNS:
        conversation_end = True
        print(f"DEBUG: Conversation END condition met. ScoreChanges: {score_change_count}, Turn: {turn_count}")

    response_data = {
        'reply': bot_reply,
        'stress_score': current_overall_score,
        'conversation_end': conversation_end,
        'current_turn': turn_count,
        'max_turns': MAX_CONVERSATION_TURNS,
        'score_changes': score_change_count,
        'max_score_changes': MAX_SCORE_CHANGES
    }
    print(f"[Response] Sending: {response_data}")
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
