import streamlit as st
import json
import os

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 스타일 정의 (가독성 향상)
st.markdown("""
<style>
    .verse-box { padding: 10px; border-bottom: 1px solid #ddd; }
    .verse-selected { background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 10px; }
    .ref-item { background-color: #f1f8e9; padding: 8px; margin-bottom: 5px; border-radius: 5px; border-left: 4px solid #4caf50; }
    .comm-box { background-color: #fff8e1; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    # 같은 폴더에 있는 bible_data.json 파일을 읽음
    file_path = 'bible_data.json'
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

st.title("📖 통합 성경 연구 도구")
st.markdown("---")

if data is None:
    st.error("데이터 파일(bible_data.json)을 찾을 수 없습니다.")
else:
    # 3. 사이드바 (책/장/절 선택)
    with st.sidebar:
        st.header("🔍 성경 찾기")
        
        # JSON 구조: 책 -> 장 -> 절
        book_list = list(data.keys())
        selected_book = st.selectbox("성경 (Book)", book_list)
        
        chapter_list = list(data[selected_book].keys())
        selected_chapter = st.selectbox("장 (Chapter)", chapter_list)
        
        # 선택된 장의 모든 절 가져오기
        verses_in_chapter = data[selected_book][selected_chapter]
        verse_list = list(verses_in_chapter.keys())
        
        # 기본적으로 1절 선택
        selected_verse_num = st.selectbox("집중 연구할 절 (Verse)", verse_list)

    # 4. 메인 화면 3단 분할
    col_text, col_ref, col_comm = st.columns([2, 1, 1])

    # [1열] 성경 본문 전체 표시
    with col_text:
        st.subheader(f"📜 {selected_book} {selected_chapter}장")
        for v_num, v_data in verses_in_chapter.items():
            text = v_data['text']
            # 선택된 절만 하이라이트 처리
            if v_num == selected_verse_num:
                st.markdown(f"<div class='verse-selected'><b>{v_num}. {text}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)

    # 선택된 절의 데이터 가져오기
    current_data = verses_in_chapter[selected_verse_num]

    # [2열] 관주 (References)
    with col_ref:
        st.subheader("🔗 관주 (References)")
        st.info(f"{selected_book} {selected_chapter}:{selected_verse_num} 관련")
        
        refs = current_data.get('refs', [])
        if refs:
            for ref in refs:
                st.markdown(f"<div class='ref-item'>{ref}</div>", unsafe_allow_html=True)
        else:
            st.caption("관련된 관주가 없습니다.")

    # [3열] 주석 (Commentary)
    with col_comm:
        st.subheader("📚 주석 (Commentary)")
        comm = current_data.get('comm', "작성된 주석이 없습니다.")
        
        st.markdown(f"""
        <div class='comm-box'>
            <b>{selected_book} {selected_chapter}:{selected_verse_num} 주석</b><br><br>
            {comm}
        </div>
        """, unsafe_allow_html=True)
