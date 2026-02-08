import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정
st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- [섹션 1] 팀 순위표 ---
st.subheader("🏆 KBO 공식 팀 순위")
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

try:
    response = requests.get(url_rank, headers={'User-Agent': 'Mozilla/5.0'})
    df_rank = pd.read_html(response.text)[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"순위 데이터를 가져오지 못했습니다.")

st.markdown("---") # 화면에 구분선을 긋습니다.

# --- [섹션 2] 1군 선수 검색 (여기서부터 검색 기능입니다!) ---
st.header("🔍 1군 선수 검색")

@st.cache_data
def get_all_players():
    # 팀 코드와 이름 매칭
    teams = {
        'OB':'두산', 'LG':'LG', 'SK':'SSG', 'LT':'롯데', 'SS':'삼성', 
        'HT':'KIA', 'HE':'한화', 'NC':'NC', 'KT':'KT', 'WO':'키움'
    }
    player_data = []

    for code, name in teams.items():
        try:
            url = f"https://www.koreabaseball.com/Player/Search.aspx?teamCode={code}"
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 선수 테이블 행(tr) 찾기
            rows = soup.select('.tEx tbody tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 3:
                    p_name = cols[1].text.strip() # 이름
                    p_pos = cols[3].text.strip()  # 포지션
                    player_data.append({'팀': name, '이름': p_name, '포지션': p_pos})
        except:
            continue
    
    # 데이터가 없으면 빈 표라도 반환해서 에러 방지
    if not player_data:
        return pd.DataFrame(columns=['팀', '이름', '포지션'])
    return pd.DataFrame(player_data)

# 선수 데이터 가져오기
with st.spinner('전체 선수 명단을 불러오는 중...'):
    df_players = get_all_players()

# 검색창 UI
search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요", placeholder="예: 김도영, 강백호")

if search_query:
    # '이름' 컬럼이 있는지 확인 후 검색 (KeyError 방지)
    if not df_players.empty and '이름' in df_players.columns:
        result = df_players[df_players['이름'].str.contains(search_query)]
        if not result.empty:
            st.success(f"'{search_query}' 검색 결과입니다.")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning("선수를 찾을 수 없습니다.")
    else:
        st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")