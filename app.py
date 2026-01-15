import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. [초강력 스타일] 왼쪽 정렬을 위한 CSS
st.markdown("""
<style>
    /* [1] 선택된 절 (파란 박스) */
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
        display: block !important;
    }
    
    /* [2] 버튼 (선택 안 된 절) - 왼쪽 정렬 강제 적용 */
    /* Streamlit 버튼의 겉과 속을 모두 왼쪽으로 밀어버리는 코드입니다 */
    div.stButton > button {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important; /* 내용물 왼쪽 배치 */
        text-align: left !important;            /* 글자 왼쪽 정렬 */
        border: 1px solid #f0f0f0;
        background-color: #fff;
        margin-bottom: 0px;
        padding: 12px;
        height: auto !important;
        white-space: normal !important; /* 긴 글자 줄바꿈 허용 */
    }

    /* [3] 버튼 안의 글자(p 태그)까지 강제 왼쪽 정렬 */
    div.stButton > button p {
        text-align: left !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        margin: 0px !important;
        width: 100% !important;
    }
    
    /* 마우스 올렸을 때 */
    div.stButton > button:hover {
        border-color: #4caf50;
        background-color: #f1f8e9;
        color: #2e7d32;
    }
    
    /* 관주 아이템 */
    .ref-item {
        font-size: 14px;
        margin-bottom: 5px;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data
def load_data():
    bible_data = {}
    refs_data = {}
    
    if os.path.exists('bible_data.json'):
        with open('bible_data.json', 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
    if os.path.exists('bible_refs.json'):
        with open('bible_refs.json', 'r', encoding='utf-8') as f:
            refs_data = json.load(f)
            
    return bible_data, refs_data

bible_data, refs_data = load_data()

# 4. 기능 함수들
def go_to_verse(ref_string):
    try:
        parts = ref_string.split(':')
        if len(parts) < 2: return
        verse_num = parts[1].strip()
        temp = parts[0].rsplit(' ', 1)
        book_name = temp[0].strip()
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

            for v_num in v_keys:
                raw_data = verses[v_num]
                text = raw_data.get('text', str(raw_data)) if isinstance(raw_data, dict) else raw_data

                # [★핵심 수정] 절 번호를 강제로 붙이는 변수 생성
                label_with_num = f"{v_num}. {text}"

                if v_num == current_v:
                    # 선택된 절 (파란 박스)
                    st.markdown(f"<div id='target' class='verse-selected'>{label_with_num}</div>", unsafe_allow_html=True)
                else:
                    # 선택 안 된 절 (버튼)
                    # label=label_with_num 부분을 꼭 확인하세요!
                    st.button(
                        label=label_with_num, 
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
                        v = parts[1].strip()
                        temp = parts[0].rsplit(' ', 1)
                        b = temp[0].strip()
                        c = temp[1].strip()
                        raw = bible_data[b][c][v]
                        preview_text = raw.get('text', str(raw)) if isinstance(raw, dict) else raw
                    except: pass

                    # 관주 라벨에도 번호나 내용이 잘 들어가게 설정
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
