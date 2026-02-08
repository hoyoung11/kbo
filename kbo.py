import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 페이지 설정
st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- [기본 기능] 팀 순위표 ---
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

try:
    response = requests.get(url_rank, headers={'User-Agent': 'Mozilla/5.0'})
    df_rank = pd.read_html(response.text)[0]
    
    st.subheader("🏆 KBO 공식 팀 순위")
    st.dataframe(df_rank, use_container_width=True, hide_index=True)

    # 상단 카드 표시 (Metric)
    col1, col2, col3 = st.columns(3)
    col1.metric("현재 1위", f"🏆 {df_rank.iloc[0]['팀명']}")
    col2.metric("리그 진행", f"{df_rank.iloc[0]['경기']} 경기")
    col3.metric("최고 승률", f"{df_rank.iloc[0]['승률']}")

except Exception as e:
    st.error(f"순위 데이터를 가져오지 못했습니다: {e}")

st.markdown("---")

# --- [추가 기능] 1군 선수 검색 ---
st.header("🔍 1군 선수 검색")

@st.cache_data # 데이터를 한 번만 가져오도록 저장(캐싱)
def get_all_players():
    # KBO 팀 코드 (각 팀의 페이지 주소용)
    teams = {
        'OB':'두산', 'LG':'LG', 'SK':'SSG', 'LT':'롯데', 'SS':'삼성', 
        'HT':'KIA', 'HE':'한화', 'NC':'NC', 'KT':'KT', 'WO':'키움'
    }
    player_data = []

    # 10개 팀을 돌면서 선수 이름을 가져옵니다.
    for code, name in teams.items():
        url = f"https://www.koreabaseball.com/Player/Search.aspx?teamCode={code}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 선수 이름이 들어있는 셀(td) 추출
        rows = soup.select('.tEx tbody tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                p_name = cols[1].text.strip()
                p_pos = cols[3].text.strip()
                player_data.append({'팀': name, '이름': p_name, '포지션': p_pos})
    
    return pd.DataFrame(player_data)

# 선수 데이터 로딩
with st.spinner('전체 선수 명단을 불러오는 중입니다...'):
    df_players = get_all_players()

# 검색창
search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요", placeholder="예: 김도영")

if search_query:
    result = df_players[df_players['이름'].str.contains(search_query)]
    if not result.empty:
        st.success(f"'{search_query}' 검색 결과입니다.")
        st.dataframe(result, use_container_width=True, hide_index=True)
    else:
        st.warning("선수를 찾을 수 없습니다. 이름을 확인해 주세요.")