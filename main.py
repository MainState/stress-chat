
import os
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, session
from scoring import update_category_score

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 실제 운영 환경에서는 안전한 키로 변경해야 합니다

# 스트레스 카테고리 정의
CATEGORY_ORDER = ["정서적 어려움", "업무 및 학업 부담", "대인 관계 갈등 및 어려움", "신체적 증상 및 건강 문제", "긍정적 자원 및 대처"]
NUM_CATEGORIES = len(CATEGORY_ORDER)
TURNS_PER_CATEGORY = 20 // NUM_CATEGORIES  # 각 카테고리당 4턴

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
    session.pop('chat_history', None)
    session['category_scores'] = {category: 5.0 for category in CATEGORY_ORDER}
    session['current_category_index'] = 0
    print("[Home] Session variables initialized with category scores")
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def handle_message():
    print("--- handle_message START ---")
    data = request.json
    user_message = data.get('message')
    if user_message is None:
        return jsonify({'error': 'No message provided'}), 400

    # 턴 카운터 및 현재 카테고리 로직
    turn_count = session.get('turn_count', 0) + 1
    session['turn_count'] = turn_count
    current_category_index = session.get('current_category_index', 0)
    current_category_name = CATEGORY_ORDER[current_category_index]
    
    print(f"DEBUG: Turn {turn_count}, Current Category: {current_category_name}")

    # 카테고리 점수 업데이트
    category_scores = session.get('category_scores', {cat: 5.0 for cat in CATEGORY_ORDER})
    current_score = category_scores.get(current_category_name, 5.0)
    updated_score = update_category_score(current_category_name, user_message, current_score)
    category_scores[current_category_name] = updated_score
    session['category_scores'] = category_scores
    print(f"DEBUG: Updated scores: {session['category_scores']}")

    # OpenAI API 호출 로직
    if openai_enabled:
        chat_history_for_api = session.get('chat_history', [])
        
        # 현재 카테고리에 맞는 시스템 프롬프트 구성
        system_prompt = {
            "role": "system",
            "content": f"""너는 사용자와 대화하는 '마음 길잡이' 챗봇이야. 현재 대화 주제는 '{current_category_name}' 관련 스트레스야.
이 주제에 대해 사용자가 자신의 경험이나 생각을 편안하게 이야기하도록 돕되, 다음 원칙을 반드시 지켜야 해:

1. 사용자의 이야기를 경청하고 공감하되, 단정적인 해석이나 평가는 하지 마.
2. 매우 개방적이고 자연스러운 질문으로 사용자가 스스로 자신의 경험과 감정을 탐색하도록 도와줘.
3. 섣부른 조언이나 해결책 제시는 절대 하지 마.
4. 응답은 항상 자연스러운 질문으로 마무리해야 해.

현재 주제인 '{current_category_name}'에 관해 사용자가 충분히 이야기할 수 있도록 도와줘."""
        }

        # API 메시지 목록 구성
        messages_for_api = [system_prompt]
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

    # 대화 종료 조건 체크 및 카테고리 전환
    conversation_end = (turn_count >= 20)
    if turn_count % TURNS_PER_CATEGORY == 0 and not conversation_end:
        session['current_category_index'] = (current_category_index + 1) % NUM_CATEGORIES
        print(f"DEBUG: Switching to next category: {CATEGORY_ORDER[session['current_category_index']]}")

    # 최종 점수 계산 (대화 종료 시)
    final_overall_score = 5.0
    if conversation_end:
        all_category_scores = list(category_scores.values())
        if all_category_scores:
            final_overall_score = round(sum(all_category_scores) / len(all_category_scores), 1)
        print(f"DEBUG: Final overall average score: {final_overall_score}")
    
    response_data = {
        'reply': bot_reply,
        'category_scores': category_scores,
        'current_category': current_category_name,
        'overall_score': final_overall_score if conversation_end else None,
        'conversation_end': conversation_end,
        'current_turn': turn_count,
        'max_turns': 20
    }
    print(f"[Response] Sending: {response_data}")
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
