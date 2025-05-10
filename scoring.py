import math

# Comprehensive stress-related keywords dictionary
KEYWORDS = {
    "정서적 어려움": {
        # 불안/걱정
        "불안해": 1.5, "불안하다": 1.5, "불안감": 2.0, "걱정돼": 1.5, "걱정된다": 1.5, 
        "걱정스러워": 1.5, "초조해": 1.5, "안절부절": 2.0, "불안불안": 1.8, "조마조마": 1.5,
        "두렵다": 1.5, "두려워": 1.5, "겁나": 1.5, "무섭다": 1.5, "무서워": 1.5,
        "떨린다": 1.2, "긴장된다": 1.2, "마음이 무거워": 1.8,
        # 우울/슬픔
        "우울해": 2.0, "우울하다": 2.0, "우울증": 2.5, "눈물나": 1.5, "울고싶어": 2.0,
        "울적해": 1.8, "슬퍼": 1.5, "슬프다": 1.5, "서럽다": 2.0, "마음아파": 2.0, 
        "가슴아파": 2.0, "괴로워": 2.0, "눈물이나": 1.5, "쓸쓸해": 1.8, "허전해": 1.5,
        # 무기력/절망
        "무기력해": 2.0, "희망없어": 2.5, "절망적": 2.5, "끝난것같아": 2.0, "포기하고싶어": 2.5,
        "의미없어": 2.0, "살기싫어": 3.0, "죽고싶다": 3.0, "자살하고싶": 3.0,
        "의욕상실": 2.2, "아무것도하기싫어": 2.3, "삶이힘들어": 2.5, "앞이안보여": 2.3,
        # 분노/짜증
        "화난다": 1.5, "화가나": 1.5, "짜증나": 1.0, "짜증난다": 1.0, "빡쳐": 2.0,
        "열받아": 1.5, "미치겠다": 2.0, "미칠것같아": 2.0, "폭발할것같아": 2.0,
        "짜증쟁이": 1.2, "부들부들": 1.8, "화가치밀어": 2.0, "속이터져": 1.8,
        # 압도감/스트레스
        "벅차": 1.5, "벅차다": 1.5, "너무많아": 1.5, "감당안돼": 2.0, "힘들어": 1.5,
        "힘들다": 1.5, "힘드네": 1.5, "버거워": 1.5, "지친다": 1.5, "지쳐": 1.5,
        "압박감": 2.0, "스트레스받아": 1.8, "한계야": 2.2, "숨막혀": 2.0
    },

    "업무 및 학업 부담": {
        # 과도한 업무량
        "일많아": 1.5, "일이많아": 1.5, "업무과다": 2.0, "할일많아": 1.5, "산더미야": 2.0,
        "과제폭탄": 2.0, "과제많아": 1.5, "밀린일": 1.5, "밀린과제": 1.5, "업무초과": 2.0,
        "일이넘쳐": 1.8, "처리못해": 1.8, "업무압박": 2.0, "과제못했어": 1.5,
        # 시간 압박
        "마감임박": 2.0, "데드라인": 2.0, "시간없어": 1.5, "늦어서": 1.5, "늦었다": 1.5,
        "촉박해": 1.5, "급하다": 1.5, "시간부족": 1.5, "야근": 2.0, "밤샘": 2.0,
        "시간이모자라": 1.8, "마감못맞춰": 2.0, "초과근무": 1.8, "야근중": 1.8,
        # 성과/평가 관련
        "성과압박": 2.0, "실적부진": 2.0, "평가불안": 1.5, "발표떨려": 1.5, "시험불안": 2.0,
        "면접긴장": 2.0, "성적걱정": 1.5, "등수걱정": 1.5, "실적미달": 2.0,
        "평가받기싫어": 1.8, "시험망쳤어": 2.0, "성적떨어져": 1.8,
        # 능력/역량 불안
        "능력부족": 2.0, "실력부족": 2.0, "자신없어": 1.5, "못하겠어": 1.5, "어려워": 1.0,
        "버거워": 1.5, "잘못했어": 1.0, "실수했어": 1.0, "역량부족": 2.0,
        "따라가기힘들어": 1.8, "성장못해": 1.8, "부족한것같아": 1.5,
        # 의욕상실/소진
        "하기싫어": 1.5, "포기하고싶어": 2.0, "관두고싶다": 2.0, "그만두고싶어": 2.0,
        "번아웃": 2.5, "소진됐어": 2.0, "지쳤어": 1.5, "의욕상실": 2.0,
        "동기부족": 1.8, "일이재미없어": 1.5, "집중안돼": 1.5
    },

    "대인 관계 갈등 및 어려움": {
        # 직접적 갈등
        "싸웠어": 2.0, "다퉜어": 1.5, "갈등있어": 1.5, "트러블": 1.5, "말다툼": 1.5,
        "대판싸움": 2.5, "폭언": 2.5, "욕했어": 2.0, "험담": 2.0, "감정싸움": 2.0,
        "오해생겼어": 1.8, "얘기가안통해": 1.8, "대화가안돼": 1.8,
        # 관계 단절/손상
        "절교했어": 2.5, "관계끊었어": 2.5, "차단했어": 2.0, "연락끊었어": 2.0,
        "손절했어": 2.0, "거절당했어": 1.5, "무시당했어": 2.0, "관계정리": 2.0,
        "더이상못봐": 2.0, "관계가깨졌어": 2.2, "신뢰잃었어": 2.0,
        # 소외감/외로움
        "외로워": 1.5, "혼자인것같아": 2.0, "따돌림": 2.5, "소외감": 2.0, "뒤처지는": 1.5,
        "친구없어": 2.0, "혼자밥먹어": 1.5, "아싸됐어": 1.5, "낀것같지않아": 1.8,
        "소속감없어": 1.8, "이방인같아": 2.0, "공동체에서밀려나": 2.0,
        # 가족/연인 관계
        "가족갈등": 2.0, "부모님이랑": 1.5, "형제랑": 1.5, "애인이랑": 1.5, "이혼": 2.5,
        "헤어졌어": 2.0, "이별했어": 2.0, "깨졌어": 1.5, "가족불화": 2.0,
        "집안분위기": 1.8, "부모님답답해": 1.8, "집안일때문에": 1.5
    },

    "신체적 증상 및 건강 문제": {
        # 수면 문제
        "잠못자": 2.0, "불면증": 2.5, "뒤척여": 1.5, "뒤척이": 1.5, "악몽꿨어": 1.5,
        "새벽까지": 1.5, "밤새": 2.0, "잠들기힘들어": 2.0, "불면": 2.0,
        "뒤척거려": 1.5, "잠안와": 1.8, "수면부족": 1.8, "꿈많이꿔": 1.5,
        # 두통/어지럼
        "두통": 1.5, "머리아파": 1.5, "머리痛": 1.5, "어지러워": 1.5, "현기증": 1.5,
        "편두통": 2.0, "메스꺼워": 1.5, "구역질": 2.0, "머리가깨질것": 1.8,
        "속이울렁거려": 1.5, "어지럽다": 1.5, "현기증나": 1.5,
        # 소화기 증상
        "속쓰려": 1.5, "체했어": 1.0, "배아파": 1.5, "설사": 1.5, "변비": 1.0,
        "속불편해": 1.0, "소화불량": 1.5, "위장장애": 2.0, "속이안좋아": 1.5,
        "위가아파": 1.5, "배가불편해": 1.2, "속이쓰려": 1.5,
        # 근골격계
        "어깨아파": 1.5, "허리아파": 1.5, "목아파": 1.5, "관절통": 1.5, "근육통": 1.5,
        "손목아파": 1.5, "거북목": 1.5, "허리디스크": 2.0, "목디스크": 2.0,
        "근육경직": 1.8, "관절이아파": 1.5, "몸이뻣뻣해": 1.5,
        # 전신 증상
        "피곤해": 1.5, "무기력해": 2.0, "기운없어": 1.5, "면역력": 1.5, "아프다": 1.0,
        "몸살": 1.5, "감기": 1.0, "열나": 1.5, "온몸이아파": 2.0,
        "컨디션난조": 1.8, "체력저하": 1.8, "면역력약해": 1.8
    },

    "긍정적 자원 및 대처": {
        # 긍정적 감정
        "행복해": -2.0, "좋아": -1.0, "기뻐": -1.5, "신나": -1.5, "설레": -1.5,
        "즐거워": -1.5, "감사해": -1.5, "만족스러워": -1.5, "뿌듯해": -1.5,
        "기분좋아": -1.8, "상쾌해": -1.5, "마음이편해": -1.8, "평온해": -2.0,
        # 휴식/여가 활동
        "쉬었어": -1.0, "푹잤어": -1.5, "여행갔다": -1.5, "운동했어": -1.0,
        "산책했어": -1.0, "맛있는거": -1.0, "영화봤어": -1.0, "휴식했어": -1.5,
        "여유있어": -1.8, "힐링했어": -1.5, "재충전했어": -1.8,
        # 관계 개선/지지
        "화해했어": -2.0, "대화했어": -1.0, "이해했어": -1.5, "도와줬어": -1.5,
        "응원받았어": -1.5, "칭찬받았어": -1.5, "위로받았어": -1.5, "지지받았어": -1.8,
        "마음이통해": -1.8, "이해받았어": -1.5, "공감받았어": -1.5,
        # 성취/극복
        "해냈어": -2.0, "성공했어": -2.0, "합격했어": -2.0, "이겨냈어": -2.0,
        "극복했어": -2.0, "해결했어": -1.5, "발전했어": -1.5, "성장했어": -1.8,
        "목표달성": -2.0, "성과냈어": -1.8, "진전있어": -1.5,
        # 긍정적 태도
        "괜찮아질거야": -1.0, "잘될거야": -1.0, "희망있어": -1.5, "자신있어": -1.5,
        "할수있어": -1.0, "긍정적으로": -1.0, "감사하게": -1.0, "이겨낼거야": -1.5,
        "극복할수있어": -1.5, "해결할거야": -1.2, "노력하면돼": -1.0
    }
}

def calculate_stress_score(user_messages):
    """
    Calculate stress score based on keywords found in user messages.
    Includes diminishing returns for repeated keywords.

    Args:
        user_messages (list): List of strings containing user messages

    Returns:
        dict: Stress scores including overall and category scores
    """
    if not user_messages:
        print("[Scoring] No user messages provided.")
        return {
            "overall_score": 5.0,
            "category_scores": {category: 5.0 for category in KEYWORDS.keys()},
            "raw_category_details": {
                category: {"keywords_found": [], "score": 0} 
                for category in KEYWORDS.keys()
            }
        }

    category_scores = {category: 5.0 for category in KEYWORDS.keys()}
    raw_category_details = {
        category: {"keywords_found": [], "score": 0} 
        for category in KEYWORDS.keys()
    }

    print(f"\n--- [Scoring] Start analyzing {len(user_messages)} messages ---")
    for category, keywords in KEYWORDS.items():
        print(f"\n--- [Scoring] Analyzing for category '{category}' ---")
        found_keywords = {}

        # Count keyword occurrences across all messages
        for message in user_messages:
            for keyword, weight in keywords.items():
                if keyword in message.lower():
                    found_keywords[keyword] = found_keywords.get(keyword, 0) + 1
                    raw_category_details[category]["keywords_found"].append(keyword)

        # Calculate category score with diminishing returns
        category_raw_score = 0
        for keyword, count in found_keywords.items():
            base_weight = keywords[keyword]
            diminishing_factor = 1.0
            for _ in range(count):
                category_raw_score += base_weight * diminishing_factor
                diminishing_factor *= 0.6

        raw_category_details[category]["score"] = category_raw_score
        print(f"[Scoring] Raw score for {category}: {category_raw_score}")

        # Normalize category score (1-10 scale)
        if category == "긍정적 자원 및 대처":
            # For positive resources, higher raw score means lower stress
            normalized_score = max(1, min(10, 5 - category_raw_score))
        else:
            # For other categories, higher raw score means higher stress
            normalized_score = max(1, min(10, 5 + category_raw_score))

        category_scores[category] = round(normalized_score, 1)
        print(f"[Scoring] Normalized score for {category}: {normalized_score}")

    # Calculate overall score (average of all categories)
    overall_score = round(sum(category_scores.values()) / len(category_scores), 1)
    print(f"[Scoring] Overall score: {overall_score}")

    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "raw_category_details": raw_category_details
    }

if __name__ == '__main__':
    print("Running scoring module self-test...")
    
    test_messages_1 = ["오늘 너무 피곤하고 머리가 아파요", "일이 너무 많아서 스트레스 받아요"]
    test_messages_2 = ["잘 지내고 있어요", "오늘은 정말 행복한 하루였어요!"]
    test_messages_3 = ["시험기간이라 불안하고 잠도 못자고 있어요"]
    
    score1 = calculate_stress_score(test_messages_1)
    score2 = calculate_stress_score(test_messages_2)
    score3 = calculate_stress_score(test_messages_3)
    
    print(f"Test Case 1 Score: {score1['overall_score']}")
    print(f"Test Case 2 Score: {score2['overall_score']}")
    print(f"Test Case 3 Score: {score3['overall_score']}")