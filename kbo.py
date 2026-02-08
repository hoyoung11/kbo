import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- 팀 순위표 ---
st.subheader("🏆 KBO 공식 팀 순위")
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

try:
    response = requests.get(url_rank, headers=headers)
    df_rank = pd.read_html(response.text)[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"팀 순위 로딩 실패: {e}")

st.markdown("---")

# --- 선수 검색 ---
st.header("🔍 1군 선수 검색")

@st.cache_data(ttl=600)
def get_all_players():
    teams = {'OB':'두산', 'LG':'LG', 'SK':'SSG', 'LT':'롯데', 'SS':'삼성', 'HT':'KIA', 'HE':'한화', 'NC':'NC', 'KT':'KT', 'WO':'키움'}
    player_data = []
    errors = []

    for code, team_name in teams.items():
        try:
            url = f"https://www.koreabaseball.com/Player/Search.aspx?teamCode={code}"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('.tEx tbody tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 3:
                    p_name = cols[1].text.strip()
                    p_pos = cols[3].text.strip()
                    player_data.append({'팀': team_name, '이름': p_name, '포지션': p_pos})
        except Exception as e:
            errors.append(f"{team_name}: {str(e)}")
            continue
    
    return pd.DataFrame(player_data), errors

with st.spinner('선수 명단을 불러오는 중...'):
    df_players, err_list = get_all_players()

# 만약 에러가 있었다면 화면에 작게 표시 (진단용)
if err_list:
    with st.expander("⚠️ 데이터 수집 중 발생한 기술적 문제 보기"):
        for err in err_list:
            st.write(err)

search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요")

if search_query:
    if not df_players.empty:
        result = df_players[df_players['이름'].str.contains(search_query.strip())]
        if not result.empty:
            st.success(f"검색 결과")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning("선수를 찾을 수 없습니다.")
    else:
        st.error("선수 명단 데이터가 비어있습니다. KBO 서버에서 접속을 차단했을 수 있습니다.")

st.snow()