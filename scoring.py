import math

KEYWORDS = {
    "정서적 어려움": {
        "불안": 1.5, "우울": 2.0, "힘들다": 1.0, "짜증": 1.0, "화나": 1.5,
        "슬프": 1.5, "답답": 1.2, "속상": 1.0, "괴로움": 1.8, "스트레스": 1.5,
        "두려움": 1.5, "걱정": 1.2, "무기력": 1.8, "무섭": 1.5, "후회": 1.2
    },
    "업무 및 학업 부담": {
        "야근": 1.5, "마감": 2.0, "과제": 1.5, "시험": 1.8, "발표": 1.5,
        "회의": 1.0, "업무": 1.2, "공부": 1.0, "시간부족": 1.8, "피곤": 1.2,
        "늦잠": 1.0, "졸림": 1.0, "실수": 1.5, "실패": 1.8, "부담": 1.5
    },
    "대인 관계 갈등 및 어려움": {
        "싸웠어": 1.5, "외로워": 1.0, "무시": 1.8, "갈등": 1.5, "오해": 1.2,
        "불화": 1.5, "다툼": 1.5, "비난": 1.8, "차별": 2.0, "따돌림": 2.0,
        "불신": 1.5, "배신": 2.0, "고립": 1.8, "소외": 1.5, "단절": 1.8
    },
    "신체적 증상 및 건강 문제": {
        "못잤어": 2.0, "두통": 1.0, "어지러움": 1.5, "위통": 1.5, "메스꺼움": 1.5,
        "근육통": 1.2, "허리통증": 1.5, "불면": 1.8, "식욕부진": 1.5, "체중": 1.0,
        "피로": 1.2, "무력감": 1.5, "질병": 2.0, "통증": 1.5, "아픔": 1.2
    },
    "긍정적 자원 및 대처": {
        "괜찮아": -1.0, "운동했어": -0.5, "좋아": -1.0, "행복": -1.5, "감사": -1.2,
        "극복": -1.5, "희망": -1.2, "성장": -1.0, "휴식": -1.0, "여유": -1.0,
        "성취": -1.5, "만족": -1.2, "기쁨": -1.5, "평온": -1.2, "즐거움": -1.0
    }
}

def update_category_score(category_name, user_message, current_category_score):
    if not user_message or category_name not in KEYWORDS:
        print(f"[Scoring] Invalid input - message: '{user_message}', category: '{category_name}'")
        return current_category_score

    print(f"\n--- [Scoring] Analyzing message for category '{category_name}' ---")
    print(f"[Scoring] Current score: {current_category_score}")
    print(f"[Scoring] Message: '{user_message}'")

    delta_score = 0.0
    keywords_found = []

    for keyword, base_weight in KEYWORDS[category_name].items():
        count = user_message.count(keyword)
        if count == 0:
            continue

        # 동일 키워드 반복 시 가중치 감소
        keyword_score = 0.0
        diminishing_factor = 1.0
        for _ in range(count):
            keyword_score += base_weight * diminishing_factor
            diminishing_factor *= 0.6

        if count > 0:
            keywords_found.append({
                "keyword": keyword,
                "count": count,
                "contribution": round(keyword_score, 2)
            })
        delta_score += keyword_score

    # 점수 변화 적용 및 범위 제한
    new_score = current_category_score + delta_score
    new_score = round(max(0.0, min(10.0, new_score)), 1)

    print(f"[Scoring] Keywords found: {keywords_found}")
    print(f"[Scoring] Delta score: {delta_score}")
    print(f"[Scoring] New score: {new_score}")

    return new_score

if __name__ == '__main__':
    # 테스트
    test_messages = [
        ("정서적 어려움", "너무 불안하고 우울해요", 5.0),
        ("업무 및 학업 부담", "야근하느라 너무 피곤해요", 5.0),
        ("긍정적 자원 및 대처", "운동하고 휴식했더니 좋아요", 5.0)
    ]

    for category, message, initial_score in test_messages:
        print(f"\nTesting category: {category}")
        final_score = update_category_score(category, message, initial_score)
        print(f"Final score: {final_score}")