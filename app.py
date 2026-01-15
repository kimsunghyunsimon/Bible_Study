import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. 스타일 정의
st.markdown("""
<style>
    /* 성경 본문 스타일 */
    .verse-box { padding: 10px; border-bottom: 1px solid #eee; font-size: 16px; }
    .verse-selected { background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 10px; font-weight: bold;}
    
    /* 버튼 스타일 살짝 다듬기 (선택 사항) */
    div.stButton > button {
        width: 100%;
        text-align: left;
        border: 1px solid #ddd;
        background-color: #fff;
        margin-bottom: 5px;
    }
    div.stButton > button:hover {
        border-color: #4caf50;
        color: #4caf50;
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

# 4. [핵심] 이동 함수 (버튼 누르면 실행됨)
def go_to_verse(ref_string):
    try:
        # "요한복음 3:16" -> ["요한복음", "3", "16"] 분리 작업
        parts = ref_string.split(':')
        if len(parts) < 2: return

        verse_num = parts[1].strip()
        temp = parts[0].rsplit(' ', 1)
        book_name = temp[0].strip()
        chapter_num = temp[1].strip()

        # 앱의 '기억(State)'을 강제로 변경!
        st.session_state['current_book'] = book_name
        st.session_state['current_chapter'] = chapter_num
        st.session_state['current_verse'] = verse_num
    except:
        pass # 에러 나면 그냥 가만히 있음

# 5. [핵심] 초기값 설정 (처음 켰을 때 위치)
if 'current_book' not in st.session_state:
    st.session_state['current_book'] = list(bible_data.keys())[0] # 창세기
if 'current_chapter' not in st.session_state:
    st.session_state['current_chapter'] = "1"
if 'current_verse' not in st.session_state:
    st.session_state['current_verse'] = "1"

st.title("📖 성경 관주 연구 (Deep References)")
st.markdown("---")

if not bible_data:
    st.error("성경 데이터(bible_data.json)가 필요합니다.")
else:
    # === 사이드바 (Session State와 연결됨) ===
    with st.sidebar:
        st.header("🔍 성경 찾기")
        
        book_list = list(bible_data.keys())
        # index 찾기: 현재 기억된 책이 리스트의 몇 번째인지 찾아서 선택해줌
        try:
            b_idx = book_list.index(st.session_state['current_book'])
        except: b_idx = 0
            
        selected_book = st.selectbox("성경", book_list, index=b_idx, key='sb_book')
        
        # 장 선택
        chapter_keys = list(bible_data[selected_book].keys())
        chapter_keys.sort(key=lambda x: int(x))
        try:
            c_idx = chapter_keys.index(st.session_state['current_chapter'])
        except: c_idx = 0
            
        selected_chapter = st.selectbox("장", chapter_keys, index=c_idx, key='sb_chapter')
        
        # 절 선택
        verses_in_chapter = bible_data[selected_book][selected_chapter]
        verse_keys = list(verses_in_chapter.keys())
        verse_keys.sort(key=lambda x: int(x))
        try:
            v_idx = verse_keys.index(st.session_state['current_verse'])
        except: v_idx = 0
            
        selected_verse_num = st.selectbox("절", verse_keys, index=v_idx, key='sb_verse')

        # 사용자가 사이드바를 직접 바꿨을 때 기억 업데이트
        if selected_book != st.session_state['current_book']:
            st.session_state['current_book'] = selected_book
            st.session_state['current_chapter'] = "1" # 책 바꾸면 1장 1절로 리셋
            st.session_state['current_verse'] = "1"
            st.rerun() # 화면 새로고침
            
        if selected_chapter != st.session_state['current_chapter']:
            st.session_state['current_chapter'] = selected_chapter
            st.session_state['current_verse'] = "1" # 장 바꾸면 1절로 리셋
            st.rerun()

        if selected_verse_num != st.session_state['current_verse']:
            st.session_state['current_verse'] = selected_verse_num
            st.rerun()


    # === 메인 화면 ===
    col_text, col_ref = st.columns([1, 1])
    search_key = f"{st.session_state['current_book']} {st.session_state['current_chapter']}:{st.session_state['current_verse']}"

    # [왼쪽] 성경 본문
    with col_text:
        st.subheader(f"📜 {st.session_state['current_book']} {st.session_state['current_chapter']}장")
        
        # 본문 데이터 가져오기
        verses = bible_data[st.session_state['current_book']][st.session_state['current_chapter']]
        v_keys = list(verses.keys())
        v_keys.sort(key=lambda x: int(x))

        for v_num in v_keys:
            raw_data = verses[v_num]
            if isinstance(raw_data, dict):
                text = raw_data.get('text', str(raw_data))
            else:
                text = raw_data

            if v_num == st.session_state['current_verse']:
                st.markdown(f"<div id='target' class='verse-selected'>{v_num}. {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)

    # [오른쪽] 관주 (클릭 가능한 버튼으로 변신!)
    with col_ref:
        st.subheader("🔗 연결된 관주 (클릭하여 이동)")
        st.caption(f"기준: {search_key}")
        
        found_ref_links = refs_data.get(search_key, [])
        
        # [NEW] 파이썬 네이티브 스크롤 컨테이너 (높이 700px)
        with st.container(height=700):
            if found_ref_links:
                for idx, link in enumerate(found_ref_links):
                    # 1. 내용을 미리 찾습니다.
                    preview_text = "내용 없음"
                    try:
                        # 링크 파싱 (예: 요한복음 3:16)
                        parts = link.split(':')
                        v = parts[1].strip()
                        temp = parts[0].rsplit(' ', 1)
                        b = temp[0].strip()
                        c = temp[1].strip()
                        
                        # 데이터에서 찾기
                        raw = bible_data[b][c][v]
                        if isinstance(raw, dict):
                            preview_text = raw.get('text', str(raw))
                        else:
                            preview_text = raw
                    except:
                        pass

                    # 2. 버튼 라벨 만들기 ("요한복음 3:16 \n 태초에...")
                    btn_label = f"🔗 {link}\n{preview_text}"
                    
                    # 3. 버튼 생성 (누르면 go_to_verse 함수 실행!)
                    if st.button(btn_label, key=f"btn_{idx}", use_container_width=True):
                        go_to_verse(link)
                        st.rerun() # 화면 즉시 새로고침
            else:
                st.info("💡 연결된 관주가 없습니다.")
