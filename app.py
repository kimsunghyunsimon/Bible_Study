import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. 스타일 정의 (왼쪽 정렬 + 깔끔한 디자인)
st.markdown("""
<style>
    /* [1] 선택된 절 (파란색 박스) - 맨 위에 고정됨 */
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

            # [핵심 로직 변경]
            # 전체 구절을 다 보여주는 게 아니라,
            # '현재 선택된 절(current_v)'보다 같거나 큰 절만 추려냅니다.
            # 이렇게 하면 선택된 절이 무조건 리스트의 1번 타자가 됩니다.
            try:
                target_v_int = int(current_v)
                display_keys = [k for k in v_keys if int(k) >= target_v_int]
            except:
                display_keys = v_keys

            # 스크롤 박스 제거! (그냥 쭉 보여줍니다)
            for v_num in display_keys:
                raw_data = verses[v_num]
                text = raw_data.get('text', str(raw_data)) if isinstance(raw_data, dict) else raw_data

                display_label = f"▶ {v_num}. {text}"

                if v_num == current_v:
                    # 선택된 절 (맨 위에 나옴)
                    st.markdown(f"<div class='verse-selected'><b>{v_num}.</b> {text}</div>", unsafe_allow_html=True)
                else:
                    # 그 다음 절들
                    st.button(
                        label=display_label, 
                        key=f"v_btn_{v_num}", 
                        use_container_width=True,
                        on_click=change_verse_only,
                        args=(v_num,)
                    )
        else:
            st.error("데이터 없음")

    # [오른쪽] 관주 (스크롤 박스 유지)
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
