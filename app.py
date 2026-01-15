import streamlit as st
import json
import os

# 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 스타일 정의
st.markdown("""
<style>
    .verse-box { padding: 10px; border-bottom: 1px solid #eee; font-size: 16px; }
    .verse-selected { background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 10px; font-weight: bold;}
    .ref-item { background-color: #f1f8e9; padding: 10px; margin-bottom: 8px; border-radius: 5px; border-left: 4px solid #4caf50; font-size: 14px;}
    .comm-box { background-color: #fff8e1; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; font-size: 15px; line-height: 1.6; }
    .comm-title { font-weight: bold; color: #d32f2f; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    bible_data = {}
    refs_data = {}
    comm_data = {}
    
    if os.path.exists('bible_data.json'):
        with open('bible_data.json', 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
    if os.path.exists('bible_refs.json'):
        with open('bible_refs.json', 'r', encoding='utf-8') as f:
            refs_data = json.load(f)
    if os.path.exists('bible_comm.json'):
        with open('bible_comm.json', 'r', encoding='utf-8') as f:
            comm_data = json.load(f)
            
    return bible_data, refs_data, comm_data

bible_data, refs_data, comm_data = load_data()

# [핵심 기능] 주소를 주면 내용을 찾아오는 탐정 함수 (포장지 뜯기 기능 추가!)
def get_verse_text(ref_string):
    try:
        parts = ref_string.split(':')
        if len(parts) < 2: return ref_string

        verse_num = parts[1].strip()
        temp = parts[0].rsplit(' ', 1)
        book_name = temp[0].strip()
        chapter_num = temp[1].strip()
        
        if book_name in bible_data:
            if chapter_num in bible_data[book_name]:
                if verse_num in bible_data[book_name][chapter_num]:
                    raw_data = bible_data[book_name][chapter_num][verse_num]
                    
                    # [수정된 부분] 데이터가 포장(dict)되어 있으면 'text'만 꺼냄
                    if isinstance(raw_data, dict):
                        text = raw_data.get('text', str(raw_data))
                    else:
                        text = raw_data
                        
                    return f"<b>{ref_string}</b> - {text}"
        
        return ref_string + " (데이터 없음)"
    except:
        return ref_string

st.title("📖 통합 성경 연구 도구")
st.markdown("---")

if not bible_data:
    st.error("성경 데이터(bible_data.json)가 필요합니다.")
else:
    with st.sidebar:
        st.header("🔍 성경 찾기")
        book_list = list(bible_data.keys())
        selected_book = st.selectbox("성경", book_list)
        
        chapter_keys = list(bible_data[selected_book].keys())
        chapter_keys.sort(key=lambda x: int(x))
        selected_chapter = st.selectbox("장", chapter_keys)
        
        verses_in_chapter = bible_data[selected_book][selected_chapter]
        verse_keys = list(verses_in_chapter.keys())
        verse_keys.sort(key=lambda x: int(x))
        selected_verse_num = st.selectbox("절", verse_keys)

    col_text, col_ref, col_comm = st.columns([2, 1, 1])
    search_key = f"{selected_book} {selected_chapter}:{selected_verse_num}"

    # [1열] 성경 본문
    with col_text:
        st.subheader(f"📜 {selected_book} {selected_chapter}장")
        for v_num in verse_keys:
            raw_data = verses_in_chapter[v_num]
            
            # [수정된 부분] 여기서도 'text'만 쏙 뽑아냅니다
            if isinstance(raw_data, dict):
                text = raw_data.get('text', str(raw_data))
            else:
                text = raw_data

            if v_num == selected_verse_num:
                st.markdown(f"<div id='target' class='verse-selected'>{v_num}. {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)

    # [2열] 관주
    with col_ref:
        st.subheader("🔗 관주 (References)")
        st.caption(f"기준: {search_key}")
        
        found_ref_links = refs_data.get(search_key, [])
        
        if found_ref_links:
            for link in found_ref_links:
                full_text = get_verse_text(link)
                st.markdown(f"<div class='ref-item'>{full_text}</div>", unsafe_allow_html=True)
        else:
            st.info("💡 관주 데이터가 없습니다.")

    # [3열] 주석
    with col_comm:
        st.subheader("📚 주석 (Commentary)")
        found_comm = comm_data.get(search_key, "")
        if found_comm:
            st.markdown(f"<div class='comm-box'><div class='comm-title'>매튜 헨리 주석</div>{found_comm}</div>", unsafe_allow_html=True)
        else:
            st.warning("이 구절에 대한 주석이 없습니다.")
