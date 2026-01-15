import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. 스타일 정의
st.markdown("""
<style>
    .verse-box { padding: 10px; border-bottom: 1px solid #eee; font-size: 16px; }
    .verse-selected { background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 10px; font-weight: bold;}
    
    /* 버튼 스타일 */
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
        background-color: #f1f8e9;
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

# 4. [핵심] 이동 함수 (콜백 함수)
# 버튼을 누르는 순간 이 함수가 실행되어 '사이드바'의 값을 강제로 바꿔버립니다.
def go_to_verse(ref_string):
    try:
        # "요한복음 3:16" 분해
        parts = ref_string.split(':')
        if len(parts) < 2: return

        verse_num = parts[1].strip()
        temp = parts[0].rsplit(' ', 1)
        book_name = temp[0].strip()
        chapter_num = temp[1].strip()

        # [중요] 세션 상태(기억) 업데이트
        st.session_state['current_book'] = book_name
        st.session_state['current_chapter'] = chapter_num
        st.session_state['current_verse'] = verse_num
        
        # [더 중요] 사이드바 위젯(selectbox)의 값도 강제로 동기화!
        # 이걸 해줘야 사이드바가 딴청을 피우지 않고 바로 바뀝니다.
        st.session_state['sb_book'] = book_name
        st.session_state['sb_chapter'] = chapter_num
        st.session_state['sb_verse'] = verse_num
        
    except Exception as e:
        print(f"이동 오류: {e}")

# 5. 초기값 설정
if 'current_book' not in st.session_state:
    st.session_state['current_book'] = list(bible_data.keys())[0]
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
        
        # 책 선택
        book_list = list(bible_data.keys())
        # index 계산 (혹시 에러나면 0번으로)
        try: b_idx = book_list.index(st.session_state['current_book'])
        except: b_idx = 0
        
        # key='sb_book'을 주어서 위젯을 특정합니다.
        selected_book = st.selectbox(
            "성경", book_list, index=b_idx, key='sb_book'
        )
        
        # 장 선택
        chapter_keys = list(bible_data[selected_book].keys())
        chapter_keys.sort(key=lambda x: int(x))
        try: c_idx = chapter_keys.index(st.session_state['current_chapter'])
        except: c_idx = 0
            
        selected_chapter = st.selectbox(
            "장", chapter_keys, index=c_idx, key='sb_chapter'
        )
        
        # 절 선택
        verses_in_chapter = bible_data[selected_book][selected_chapter]
        verse_keys = list(verses_in_chapter.keys())
        verse_keys.sort(key=lambda x: int(x))
        try: v_idx = verse_keys.index(st.session_state['current_verse'])
        except: v_idx = 0
            
        selected_verse_num = st.selectbox(
            "절", verse_keys, index=v_idx, key='sb_verse'
        )

        # 사이드바를 손으로 조작했을 때의 동기화
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
    
    # 현재 보고 있는 구절 주소
    current_b = st.session_state['current_book']
    current_c = st.session_state['current_chapter']
    current_v = st.session_state['current_verse']
    search_key = f"{current_b} {current_c}:{current_v}"

    # [왼쪽] 성경 본문
    with col_text:
        st.subheader(f"📜 {current_b} {current_c}장")
        
        # 혹시 모를 에러 방지 (데이터가 없을 경우)
        if current_b in bible_data and current_c in bible_data[current_b]:
            verses = bible_data[current_b][current_c]
            v_keys = list(verses.keys())
            v_keys.sort(key=lambda x: int(x))

            for v_num in v_keys:
                raw_data = verses[v_num]
                if isinstance(raw_data, dict):
                    text = raw_data.get('text', str(raw_data))
                else:
                    text = raw_data

                if v_num == current_v:
                    st.markdown(f"<div id='target' class='verse-selected'>{v_num}. {text}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)
        else:
            st.error("해당 구절을 찾을 수 없습니다.")

    # [오른쪽] 관주 (클릭 이동 기능!)
    with col_ref:
        st.subheader("🔗 연결된 관주 (클릭하여 이동)")
        st.caption(f"기준: {search_key}")
        
        found_ref_links = refs_data.get(search_key, [])
        
        with st.container(height=700):
            if found_ref_links:
                for idx, link in enumerate(found_ref_links):
                    # 내용 미리보기 찾기
                    preview_text = "내용 없음"
                    try:
                        parts = link.split(':')
                        v = parts[1].strip()
                        temp = parts[0].rsplit(' ', 1)
                        b = temp[0].strip()
                        c = temp[1].strip()
                        
                        raw = bible_data[b][c][v]
                        if isinstance(raw, dict):
                            preview_text = raw.get('text', str(raw))
                        else:
                            preview_text = raw
                    except:
                        pass

                    btn_label = f"🔗 {link}\n{preview_text}"
                    
                    # [핵심 수정] args를 사용하여 클릭 시 go_to_verse 함수를 즉시 호출!
                    st.button(
                        btn_label, 
                        key=f"btn_{idx}", 
                        use_container_width=True,
                        on_click=go_to_verse,  # 클릭하면 이 함수 실행
                        args=(link,)           # 함수에 '링크 주소' 전달
                    )
            else:
                st.info("💡 연결된 관주가 없습니다.")
