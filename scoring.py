
import math

# Keyword categories with their respective weights
KEYWORDS = {
    "negative_emotion": {
        # 기본 부정 감정
        "짜증": 1, "화나": 1, "슬프": 1, "우울": 2, "불안": 2,
        "속상": 1, "답답": 1.5, "막막": 1.5, "허무": 1.5,
        # 강한 부정 감정
        "죽겠": 3, "미치겠": 2, "괴롭": 2, "좌절": 2,
        # 감정 소진
        "지친": 1.5, "지쳤": 1.5, "힘들": 1, "힘드네": 1,
        # 불안/두려움
        "무섭": 1.5, "두렵": 1.5, "걱정": 1.5,
        # 분노/실망
        "신경질": 1.5, "실망": 1, "후회": 1.5, "화가나": 1.5
    },
    
    "positive_emotion": {
        # 기본 긍정 감정
        "좋아": -1, "기쁘": -1, "즐겁": -1, "행복": -2,
        "뿌듯": -1.5, "감사": -1.5, "설레": -1,
        # 긍정적 대처
        "극복": -2, "해결": -1.5, "이해": -1, "수용": -1,
        # 휴식/안정
        "편안": -1, "평온": -1.5, "쉬었": -1, "여유": -1,
        # 수면 만족
        "잘잤": -1.5, "충분히 잤": -1.5, "개운": -1,
        # 성취감
        "성공": -2, "달성": -1.5, "해냈": -1.5
    },
    
    "sleep_issues": {
        # 수면 부족
        "못잤": 2, "잠설쳤": 2, "뒤척": 1.5, "불면": 2.5,
        # 수면 질 저하
        "잠 못들": 2, "얕은 잠": 1.5, "깊이 못자": 2,
        "뒤척이": 1.5, "악몽": 2, "새벽에 깨": 1.5,
        # 수면 패턴 붕괴
        "밤새": 2, "늦게잤": 1.5, "잠들기 힘들": 2,
        # 피로감
        "졸려": 1, "피곤": 1.5, "잠부족": 1.5
    },
    
    "workload_issues": {
        # 업무량
        "바쁘": 1, "일많": 1.5, "과제많": 1.5, "할일많": 1.5,
        # 시간 압박
        "마감": 2, "데드라인": 2, "늦어": 1.5, "급하": 1.5,
        # 업무 강도
        "야근": 2, "철야": 2.5, "overtime": 2,
        # 성과 압박
        "실적": 2, "성과": 1.5, "평가": 1.5, "경쟁": 2,
        # 학업 스트레스
        "시험": 2, "과제": 1.5, "공부": 1, "학점": 1.5
    },
    
    "physical_symptoms": {
        # 두통/어지럼
        "두통": 1.5, "머리아프": 1.5, "어지럽": 1.5,
        # 소화기 증상
        "속쓰림": 1.5, "소화불량": 1.5, "구역질": 2,
        "식욕없": 1.5, "과식": 1, "폭식": 2,
        # 근골격계 증상
        "어깨결림": 1, "목아프": 1, "허리아프": 1.5,
        # 심폐 증상
        "숨막힘": 2, "가슴답답": 2, "심장두근": 2,
        # 전신 증상
        "무기력": 2, "기운없": 1.5, "몸살": 1.5
    },
    
    "interpersonal_stress": {
        # 갈등 상황
        "싸웠": 2, "다툼": 2, "갈등": 1.5, "오해": 1.5,
        # 관계 불화
        "무시": 2, "따돌림": 2.5, "눈치": 1.5,
        # 관계별 스트레스
        "부모님이랑": 1.5, "친구랑": 1, "동료랑": 1,
        # 관계 단절
        "연락두절": 2, "차단": 2, "관계끊": 2.5,
        # 상처
        "배신": 2.5, "실망시켰": 2, "상처받": 2
    },
    
    "future_anxiety": {
        # 진로 불안
        "취업": 1.5, "진로": 1.5, "스펙": 1.5,
        # 미래 불확실성
        "불확실": 2, "미래가걱정": 2, "앞날이걱정": 2,
        # 경력 고민
        "경력": 1.5, "이직": 1.5, "퇴사": 2,
        # 인생 방향성
        "방향성": 1.5, "길잃": 2, "목표없": 2,
        # 재정 불안
        "돈걱정": 2, "빚": 2.5, "대출": 2
    },
    
    "low_self_esteem": {
        # 자기 비하
        "못난": 2, "부족해": 1.5, "한심해": 2,
        # 자신감 결여
        "자신없": 2, "자신감": 1.5, "무능해": 2,
        # 비교 불안
        "비교": 1.5, "뒤쳐져": 2, "열등감": 2,
        # 자책
        "자책": 2, "후회": 1.5, "내탓": 1.5,
        # 부정적 자아상
        "쓸모없": 2.5, "가치없": 2.5, "존재감없": 2.5
    }
}

def calculate_stress_score(user_messages):
    """
    Calculate stress score based on keywords found in user messages.
    
    Args:
        user_messages (list): List of strings containing user messages
        
    Returns:
        int: Final stress score (1-10 scale)
    """
    if not user_messages:
        print("[Scoring] No user messages...")
        return 5
    
    raw_score = 0
    found_keywords_details = []
    
    print(f"[Scoring] Start analyzing {len(user_messages)} messages ---")
    
    for i, message in enumerate(user_messages):
        print(f"[Scoring] Analyzing msg {i+1}: '{message[:50]}...'")
        found_in_this_message = set()
        
        for category, keywords in KEYWORDS.items():
            for keyword, weight in keywords.items():
                if keyword in message and keyword not in found_in_this_message:
                    print(f"  - Found: '{keyword}' (Cat: {category}, W: {weight})")
                    raw_score += weight
                    found_in_this_message.add(keyword)
                    found_keywords_details.append({'kw': keyword, 'wt': weight, 'msg_idx': i})
    
    print(f"[Scoring] Total Raw Score: {raw_score}")
    print(f"[Scoring] Found Keywords Details: {found_keywords_details}")
    
    normalized_score = round(raw_score + 5)
    final_score = max(1, min(10, normalized_score))
    
    print(f"[Scoring] Normalized Score (1-10): {final_score}")
    print("-" * 50)
    
    return final_score

if __name__ == '__main__':
    print("Running scoring module self-test...")
    
    test_messages_1 = ["오늘 너무 피곤하고 머리가 아파요", "일이 너무 많아서 스트레스 받아요"]
    test_messages_2 = ["잘 지내고 있어요", "오늘은 정말 행복한 하루였어요!"]
    test_messages_3 = ["시험기간이라 불안하고 잠도 못자고 있어요"]
    
    score1 = calculate_stress_score(test_messages_1)
    score2 = calculate_stress_score(test_messages_2)
    score3 = calculate_stress_score(test_messages_3)
    
    print(f"Test Case 1 Score: {score1}")
    print(f"Test Case 2 Score: {score2}")
    print(f"Test Case 3 Score: {score3}")
