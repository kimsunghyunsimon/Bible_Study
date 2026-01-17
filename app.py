import streamlit as st
import json
import os
import re

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. 스타일 정의
st.markdown("""
<style>
    /* [1] 선택된 절 (맨 위 고정) */
    .verse-selected { 
        background-color: #e3f2fd; 
        border-left: 5px solid #2196F3; 
        padding: 15px; 
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 5px;
        font-size: 16px;
        line-height: 1.6;
        text-align: left !important;
        color: #000000;
        display: block;
    }
    
    /* [2] 버튼 스타일 (왼쪽 정렬) */
    div.stButton > button {
        width: 100% !important;
        background-color: #fff;
        border: 1px solid #f0f0f0;
        padding: 12px 15px;
        height: auto !important;
        white-space: normal !important;
        margin-bottom: 0px;
        
        display: flex !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }

    div.stButton > button * {
        text-align: left !important;
        justify-content: flex-start !important;
        display: block !important;
        margin-left: 0 !important;
    }
    
    div.stButton > button:hover {
        border-color: #4caf50;
        background-color: #f1f8e9;
        color: #2e7d32;
    }
    
    .ref-item {
        font-size: 14px;
        margin-bottom: 5px;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 및 [★핵심 수정] 이름표 수선하기
@st.cache_data
def load_data():
    bible_data = {}
    refs_data = {}
    if os.path.exists('bible_data.json'):
        with open('bible_data.json', 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
            
            # [수선 작업] "눅"이라고 되어 있으면 "누가복음"으로 고칩니다.
            if "눅" in bible_data:
                bible_data["누가복음"] = bible_data.pop("눅")
                
    if os.path.exists('bible_refs.json'):
        with open('bible_refs.json', 'r', encoding='utf-8') as f:
            refs_data = json.load(f)
            
    return bible_data, refs_data

bible_data, refs_data = load_data()

# 영어/약어 -> 한글 책 이름 변환기 (누가복음 'Luk' 포함)
book_map = {
    "Gen": "창세기", "Exo": "출애굽기", "Lev": "레위기", "Num": "민수기", "Deu": "신명기",
    "Jos": "여호수아", "Jdg": "사사기", "Rut": "룻기", "1Sa": "사무엘상", "2Sa": "사무엘하",
    "1Ki": "열왕기상", "2Ki": "열왕기하", "1Ch": "역대상", "2Ch": "역대하", "Ezr": "에스라",
    "Neh": "느헤미야", "Est": "에스더", "Job": "욥기", "Psa": "시편", "Pro": "잠언",
    "Ecc": "전도서", "Son": "아가", "Isa": "이사야", "Jer": "예레미야", "Lam": "예레미야애가",
    "Eze": "에스겔", "Dan": "다니엘", "Hos": "호세아", "Joe": "요엘", "Amo": "아모스",
    "Oba": "오바댜", "Jon": "요나", "Mic": "미가", "Nah": "나훔", "Hab": "하박국",
    "Zep": "스바냐", "Hag": "학개", "Zec": "스가랴", "Zech": "스가랴", "Mal": "말라기",
    "Mat": "마태복음", "Mar": "마가복음", "Luk": "누가복음", "Luke": "누가복음", "Joh": "요한복음", "Act": "사도행전",
    "Rom": "로마서", "1Co": "고린도전서", "2Co": "고린도후서", "Gal": "갈라디아서", "Eph": "에베소서",
    "Phi": "빌립보서", "Col": "골로새서", "1Th": "데살로니가전서", "2Th": "데살로니가후서",
    "1Ti": "디모데전서", "2Ti": "디모데후서", "Tit": "디도서", "Phm": "빌레몬서", "Heb": "히브리서",
    "Jam": "야고보서", "1Pe": "베드로전서", "2Pe": "베드로후서", "1Jo": "요한일서", "2Jo": "요한이서",
    "3Jo": "요한삼서", "Jud": "유다서", "Rev": "요한계시록",
    # 혹시 모를 한글 약어 처리
    "눅": "누가복음"
}

# 똑똑한 텍스트 찾기 함수
def find_text_safe(book, chapter, verse):
    clean_book = book.strip()
    # 영어면 한글로 변환
    if clean_book in book_map:
        clean_book = book_map[clean_book]
    
    # 절 번호 청소 (1-Zech -> 1)
    clean_verse = re.split(r'[-a-zA-Z]', str(verse))[0].strip()
    
    try:
        if clean_book in bible_data:
            if str(chapter) in bible_data[clean_book]:
                if str(clean_verse) in bible_data[clean_book][str(chapter)]:
                    raw = bible_data[clean_book][str(chapter)][str(clean_verse)]
                    return raw.get('text', str(raw)) if isinstance(raw, dict) else raw
    except:
        pass
    return ""

# 4. 기능 함수들
def go_to_verse(ref_string):
    try:
        parts = ref_string.split(':')
        if len(parts) < 2: return
        
        raw_verse = parts[1].strip()
        verse_num = re.split(r'[-a-zA-Z]', raw_verse)[0].strip()
        
        temp = parts[0].rsplit(' ', 1)
        book_raw = temp[0].strip()
        book_name = book_map.get(book_raw, book_raw) # 영문->한글 변환
        
        chapter_num = temp[1].strip()
        
        st.session_state['current_book'] = book_name
        st.session_state['current_chapter'] = chapter_num
        st.session_state['current_verse'] = verse_num
        st.session_state['sb_book'] = book_name
        st.session_state['sb_chapter'] = chapter_num
        st.session_state['sb_verse'] = verse_num
    except: pass

def change_verse_only(v_num):
    st.session_state['current_verse'] = v_num
    st.session_state['sb_verse'] = v_num

# 5. 초기값 설정
if 'current_book' not in st.session_state:
    st.session_state['current_book'] = list(bible_data.keys())[0] if bible_data else "창세기"
if 'current_chapter' not in st.session_state:
    st.session_state['current_chapter'] = "1"
if 'current_verse' not in st.session_state:
    st.session_state['current_verse'] = "1"

st.title("📖 성경 관주 연구 (Deep References)")
st.markdown("---")

if not bible_data:
    st.error("성경 데이터(bible_data.json)가 필요합니다.")
else:
    # === 사이드바 ===
    with st.sidebar:
        st.header("🔍 성경 찾기")
        book_list = list(bible_data.keys())
        
        # [안전장치] 현재 선택된 책이 리스트에 없으면(이름이 바뀐 경우) 첫번째 책으로
        if st.session_state['current_book'] not in book_list:
             # 만약 "눅"을 보고 있었다면 "누가복음"으로 자동 연결 시도
            if st.session_state['current_book'] == "눅" and "누가복음" in book_list:
                st.session_state['current_book'] = "누가복음"
            else:
                st.session_state['current_book'] = book_list[0]

        try: b_idx = book_list.index(st.session_state['current_book'])
        except: b_idx = 0
        selected_book = st.selectbox("성경", book_list, index=b_idx, key='sb_book')
        
        chapter_keys = list(bible_data[selected_book].keys())
        chapter_keys.sort(key=lambda x: int(x))
        try: c_idx = chapter_keys.index(st.session_state['current_chapter'])
        except: c_idx = 0
        selected_chapter = st.selectbox("장", chapter_keys, index=c_idx, key='sb_chapter')
        
        verses_in_chapter = bible_data[selected_book][selected_chapter]
        verse_keys = list(verses_in_chapter.keys())
        verse_keys.sort(key=lambda x: int(x))
        try: v_idx = verse_keys.index(st.session_state['current_verse'])
        except: v_idx = 0
        selected_verse_num = st.selectbox("절", verse_keys, index=v_idx, key='sb_verse')

        if selected_book != st.session_state['current_book']:
            st.session_state['current_book'] = selected_book
            st.session_state['current_chapter'] = "1"
            st.session_state['current_verse'] = "1"
            st.rerun()
        if selected_chapter != st.session_state['current_chapter']:
            st.session_state['current_chapter'] = selected_chapter
            st.session_state['current_verse'] = "1"
            st.rerun()
        if selected_verse_num != st.session_state['current_verse']:
            st.session_state['current_verse'] = selected_verse_num
            st.rerun()

    # === 메인 화면 ===
    col_text, col_ref = st.columns([1, 1])
    current_b = st.session_state['current_book']
    current_c = st.session_state['current_chapter']
    current_v = st.session_state['current_verse']
    search_key = f"{current_b} {current_c}:{current_v}"

    # [왼쪽] 성경 본문
    with col_text:
        st.subheader(f"📜 {current_b} {current_c}장")
        
        if current_b in bible_data and current_c in bible_data[current_b]:
            verses = bible_data[current_b][current_c]
            v_keys = list(verses.keys())
            v_keys.sort(key=lambda x: int(x))

            try:
                target_v_int = int(current_v)
                display_keys = [k for k in v_keys if int(k) >= target_v_int]
            except:
                display_keys = v_keys

            for v_num in display_keys:
                raw_data = verses[v_num]
                text = raw_data.get('text', str(raw_data)) if isinstance(raw_data, dict) else raw_data

                display_label = f"▶ {v_num}. {text}"

                if v_num == current_v:
                    st.markdown(f"<div class='verse-selected'><b>{v_num}.</b> {text}</div>", unsafe_allow_html=True)
                else:
                    st.button(
                        label=display_label, 
                        key=f"v_btn_{v_num}", 
                        use_container_width=True,
                        on_click=change_verse_only,
                        args=(v_num,)
                    )
        else:
            st.error("데이터 없음")

    # [오른쪽] 관주
    with col_ref:
        st.subheader("🔗 연결된 관주 (References)")
        st.caption(f"기준: {search_key}")
        found_ref_links = refs_data.get(search_key, [])
        
        with st.container(height=700):
            if found_ref_links:
                for idx, link in enumerate(found_ref_links):
                    preview_text = ""
                    try:
                        parts = link.split(':')
                        raw_verse = parts[1].strip()
                        raw_book_chapter = parts[0].rsplit(' ', 1)
                        
                        b = raw_book_chapter[0].strip()
                        c = raw_book_chapter[1].strip()
                        v = raw_verse 
                        
                        preview_text = find_text_safe(b, c, v)
                        
                    except: pass

                    btn_label = f"🔗 {link}\n{preview_text}"
                    
                    st.button(
                        btn_label, 
                        key=f"ref_btn_{idx}", 
                        use_container_width=True,
                        on_click=go_to_verse,
                        args=(link,)
                    )
            else:
                st.info(f"💡 {search_key}에 대한 관주가 없습니다.")
