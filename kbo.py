import streamlit as st
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- [섹션 1] 팀 순위표 (이건 잘 나오죠?) ---
st.subheader("🏆 KBO 공식 팀 순위")
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

try:
    response = requests.get(url_rank, headers=headers, timeout=10)
    df_rank = pd.read_html(response.text)[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except:
    st.error("팀 순위 로딩에 실패했습니다.")

st.markdown("---")

# --- [섹션 2] 1군 선수 검색 (API 방식 필살기) ---
st.header("🔍 1군 선수 검색")

@st.cache_data(ttl=3600)
def get_players_api():
    # KBO의 검색 데이터를 관리하는 내부 주소입니다.
    # HTML을 긁는게 아니라 데이터만 쏙 가져옵니다.
    api_url = "https://www.koreabaseball.com/ws/Player/PlayerSearch.ashx"
    
    # 10개 팀의 데이터를 한 번에 가져오기 위한 설정
    teams = ['OB', 'LG', 'SK', 'LT', 'SS', 'HT', 'HE', 'NC', 'KT', 'WO']
    all_players = []

    for team in teams:
        try:
            # 팀별로 데이터를 요청합니다.
            params = {'teamCode': team}
            res = requests.post(api_url, data=params, headers=headers, timeout=10)
            data = res.json() # 결과가 JSON(데이터 덩어리)으로 옵니다.
            
            # 받아온 데이터에서 필요한 정보만 추출
            for p in data['rows']:
                all_players.append({
                    '팀': p['TEAM_NM'],
                    '이름': p['PLAYER_NM'],
                    '포지션': p['POSITION']
                })
        except:
            continue
            
    return pd.DataFrame(all_players)

# 데이터 불러오기
with st.spinner('KBO 서버에서 선수 명단을 직접 가져오는 중...'):
    df_players = get_players_api()

# 검색창
search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요 (예: 강백호)")

if search_query:
    if not df_players.empty:
        # 검색 결과 필터링
        result = df_players[df_players['이름'].str.contains(search_query.strip())]
        if not result.empty:
            st.success(f"'{search_query}' 검색 결과")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning("선수를 찾을 수 없습니다.")
    else:
        st.error("KBO 서버가 접속을 거부했습니다. 이 기능은 현재 질문자님 컴퓨터(로컬)에서만 작동할 수 있습니다.")

st.snow()