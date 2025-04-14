
import math

# Keyword categories with their respective weights
KEYWORDS = {
    "negative_emotion": {
        "짜증": 1, "힘들다": 1, "힘들어": 1, "불안": 2, "우울": 2,
        "화나": 1, "슬프다": 1, "슬퍼": 1, "죽겠다": 3, "미치겠다": 2, "걱정": 1.5
    },
    "positive_emotion": {
        "괜찮아": -1, "좋아": -1, "재밌었어": -1, "재미있었어": -1,
        "행복": -2, "편안": -1, "기분전환": -1.5, "즐거웠어": -1.5, "다행이다": -1
    },
    "sleep_issues": {
        "못잤어": 2, "잠설쳤어": 2, "졸려": 0.5,
        "잠 부족": 1.5, "불면증": 2.5
    },
    "workload_issues": {
        "바빠": 1, "바쁘다": 1, "일많아": 1.5, "공부많아": 1.5,
        "야근": 1.5, "마감": 2, "시험": 2, "과제": 1, "벅차다": 1.5
    },
    "physical_symptoms": {
        "두통": 1, "머리아파": 1, "소화안돼": 1, "소화 안돼": 1,
        "어깨결려": 0.5, "피곤": 1.5, "피곤해": 1.5, "몸살": 1.5
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
