import streamlit as st
import json
import os

# 1. 페이지 설정 (넓게 보기)
st.set_page_config(layout="wide", page_title="Bible Study Tool")

# 2. 스타일 정의 (스크롤바 및 디자인)
st.markdown("""
<style>
    /* 성경 본문 스타일 */
    .verse-box { padding: 10px; border-bottom: 1px solid #eee; font-size: 16px; }
    .verse-selected { background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 10px; font-weight: bold;}
    
    /* [핵심] 관주 영역 스크롤 박스 (높이 700px로 확대) */
    .ref-container {
        height: 700px;          /* 높이를 넉넉하게 잡았습니다 */
        overflow-y: auto;       /* 내용이 넘치면 스크롤바 생성 */
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    
    /* 관주 아이템 카드 디자인 */
    .ref-item { 
        background-color: #ffffff; 
        padding: 12px; 
        margin-bottom: 10px; 
        border-radius: 5px; 
        border-left: 5px solid #4caf50; /* 초록색 포인트 */
        font-size: 15px; 
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
    }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 (주석 데이터는 이제 안 읽어옵니다)
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

# 4. 탐정 함수 (주소 -> 내용 변환)
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
                    # 포장지 뜯기
                    if isinstance(raw_data, dict):
                        text = raw_data.get('text', str(raw_data))
                    else:
                        text = raw_data
                    return f"<b>{ref_string}</b><br>{text}" # 줄바꿈 추가해서 가독성 높임
        
        return ref_string + " (데이터 없음)"
    except:
        return ref_string

st.title("📖 성경 관주 연구 (Deep References)")
st.markdown("---")

if not bible_data:
    st.error("성경 데이터(bible_data.json)가 필요합니다.")
else:
    # 사이드바 설정
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

    # === [변경된 레이아웃] 3단 -> 2단 (50:50 비율) ===
    col_text, col_ref = st.columns([1, 1])
    
    search_key = f"{selected_book} {selected_chapter}:{selected_verse_num}"

    # [왼쪽] 성경 본문
    with col_text:
        st.subheader(f"📜 {selected_book} {selected_chapter}장")
        for v_num in verse_keys:
            raw_data = verses_in_chapter[v_num]
            if isinstance(raw_data, dict):
                text = raw_data.get('text', str(raw_data))
            else:
                text = raw_data

            if v_num == selected_verse_num:
                st.markdown(f"<div id='target' class='verse-selected'>{v_num}. {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='verse-box'>{v_num}. {text}</div>", unsafe_allow_html=True)

    # [오른쪽] 관주 (넓어진 화면 + 스크롤바)
    with col_ref:
        st.subheader("🔗 연결된 관주 (References)")
        st.caption(f"기준 구절: {search_key}")
        
        found_ref_links = refs_data.get(search_key, [])
        
        # 스크롤 박스 시작
        html_content = "<div class='ref-container'>"
        
        if found_ref_links:
            count = len(found_ref_links)
            html_content += f"<div style='margin-bottom:10px; color:#666;'>총 <b>{count}</b>개의 연결 구절을 찾았습니다.</div>"
            
            for link in found_ref_links:
                full_text = get_verse_text(link)
                html_content += f"<div class='ref-item'>{full_text}</div>"
        else:
            html_content += "<div style='padding:20px; text-align:center;'>💡 연결된 관주가 없습니다.</div>"
            
        html_content += "</div>"
        # 스크롤 박스 끝
        
        st.markdown(html_content, unsafe_allow_html=True)
