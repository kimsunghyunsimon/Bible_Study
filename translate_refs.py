import json
import re

# 1. 파일 이름 설정
INPUT_FILE = 'english_refs.json'  # 방금 다운받은 영어 파일
OUTPUT_FILE = 'bible_refs.json'   # 결과로 나올 한글 파일

# 2. 영어 -> 한글 변환표
ENG_TO_KOR = {
    "Genesis": "창세기", "Exodus": "출애굽기", "Leviticus": "레위기", "Numbers": "민수기", "Deuteronomy": "신명기",
    "Joshua": "여호수아", "Judges": "사사기", "Ruth": "룻기", "1 Samuel": "사무엘상", "2 Samuel": "사무엘하",
    "1 Kings": "열왕기상", "2 Kings": "열왕기하", "1 Chronicles": "역대상", "2 Chronicles": "역대하", "Ezra": "에스라",
    "Nehemiah": "느헤미야", "Esther": "에스더", "Job": "욥기", "Psalms": "시편", "Proverbs": "잠언",
    "Ecclesiastes": "전도서", "Song of Solomon": "아가", "Isaiah": "이사야", "Jeremiah": "예레미야", "Lamentations": "예레미야애가",
    "Ezekiel": "에스겔", "Daniel": "다니엘", "Hosea": "호세아", "Joel": "요엘", "Amos": "아모스",
    "Obadiah": "오바댜", "Jonah": "요나", "Micah": "미가", "Nahum": "나훔", "Habakkuk": "하박국",
    "Zephaniah": "스바냐", "Haggai": "학개", "Zechariah": "스가랴", "Malachi": "말라기",
    "Matthew": "마태복음", "Mark": "마가복음", "Luke": "누가복음", "John": "요한복음", "Acts": "사도행전",
    "Romans": "로마서", "1 Corinthians": "고린도전서", "2 Corinthians": "고린도후서", "Galatians": "갈라디아서", "Ephesians": "에베소서",
    "Philippians": "빌립보서", "Colossians": "골로새서", "1 Thessalonians": "데살로니가전서", "2 Thessalonians": "데살로니가후서",
    "1 Timothy": "디모데전서", "2 Timothy": "디모데후서", "Titus": "디도서", "Philemon": "빌레몬서", "Hebrews": "히브리서",
    "James": "야고보서", "1 Peter": "베드로전서", "2 Peter": "베드로후서", "1 John": "요한일서", "2 John": "요한이서",
    "3 John": "요한삼서", "Jude": "유다서", "Revelation": "요한계시록"
}

def translate_bible_refs():
    try:
        print("📂 영어 데이터 읽는 중...")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        new_data = {}
        count = 0

        print("🔄 한글로 변환 시작...")
        
        # 데이터 한 줄씩 꺼내서 변환
        for key, refs in data.items():
            # key 예시: "Genesis 1:1"
            # refs 예시: ["John 1:1", "Hebrews 11:3"]
            
            # 1. '키' 변환 (Genesis 1:1 -> 창세기 1:1)
            found_book = False
            for eng, kor in ENG_TO_KOR.items():
                if key.startswith(eng + " "): # "Genesis " 로 시작하면
                    new_key = key.replace(eng, kor, 1) # 창세기 1:1로 변경
                    
                    # 2. '내용' 변환 (John 1:1 -> 요한복음 1:1)
                    new_refs = []
                    for r in refs:
                        translated_ref = r
                        # 참조 구절 안에 있는 영어도 한글로 바꿈
                        for e_book, k_book in ENG_TO_KOR.items():
                            if e_book in translated_ref:
                                translated_ref = translated_ref.replace(e_book, k_book)
                        new_refs.append(translated_ref)
                    
                    new_data[new_key] = new_refs
                    found_book = True
                    count += 1
                    break
            
            if not found_book:
                # 매칭되는 책 이름이 없으면 그냥 둠 (디버깅용)
                pass

        # 저장
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 변환 완료! 총 {count}개 구절의 관주를 한글로 바꿨습니다.")
        print(f"👉 생성된 '{OUTPUT_FILE}' 파일을 GitHub에 업로드하세요.")

    except FileNotFoundError:
        print(f"❌ 오류: '{INPUT_FILE}'이 없습니다. 파일을 다운로드했는지 확인하세요.")

if __name__ == "__main__":
    translate_bible_refs()