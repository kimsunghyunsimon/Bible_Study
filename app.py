import streamlit as st
import json
import os

# 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

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

# [핵심 기능] 주소("요한복음 1:1")를 주면 성경 본문을 찾아오는 탐정 함수
def get_verse_text(ref_string):
    try:
        # "요한복음 1:1" -> ["요한복음 1", "1"] 로 분리
        parts = ref_string.split(':')
        if len(parts) < 2: return ref_string # 형식이 이상하면 그냥 주소만 리턴

        verse_num = parts[1].strip() # "1"
        
        # "요한복음 1" -> ["요한복음", "1"] 로 분리 (뒤에서 첫번째 공백 기준)
        temp = parts[0].rsplit(' ', 1)
        book_name = temp[0].strip() # "요한복음"
        chapter_num = temp[1].strip() # "1"
        
        # 성경 데이터에서 찾기
        if book_name in bible_data:
            if chapter_num in bible_data[book_name]:
                if verse_num in bible_data[book_name][chapter_num]:
                    text = bible_data[book_name][chapter_num][verse_num]
                    # 결과: "요한복음 1:1 - 태초에 말씀이..."
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

    with col_text:
        st.subheader(f"📜 {selected_book} {selected_chapter}장")
        for v_num in verse_keys:
            text = verses_in_chapter[v_num]
            if v_num == selected_verse_num:
                st.markdown(f"<div id='target' class='verse-selected'>{v_num}. {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)

    with col_ref:
        st.subheader("🔗 관주 (References)")
        st.caption(f"기준: {search_key}")
        
        # 주소 리스트만 가져옴 (예: ["요한복음 1:1", "히브리서 11:3"])
        found_ref_links = refs_data.get(search_key, [])
        
        if found_ref_links:
            for link in found_ref_links:
                # 여기서 함수를 써서 내용을 찾아옵니다!
                full_text = get_verse_text(link)
                st.markdown(f"<div class='ref-item'>{full_text}</div>", unsafe_allow_html=True)
        else:
            st.info("💡 관주 데이터가 없습니다.")

    with col_comm:
        st.subheader("📚 주석 (Commentary)")
        found_comm = comm_data.get(search_key, "")
        if found_comm:
            st.markdown(f"<div class='comm-box'><div class='comm-title'>매튜 헨리 주석</div>{found_comm}</div>", unsafe_allow_html=True)
        else:
            st.warning("주석 없음")
