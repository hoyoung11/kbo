import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- [섹션 1] 팀 순위 (기존 방식 유지) ---
st.subheader("🏆 KBO 공식 팀 순위")
try:
    url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"
    df_rank = pd.read_html(url_rank)[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except:
    st.warning("순위 데이터는 실시간 연결이 필요합니다.")

st.markdown("---")

# --- [섹션 2] 선수 검색 (파일 로드 방식) ---
st.header("🔍 1군 선수 검색")

# players.csv 파일이 있는지 확인 후 읽어오기
if os.path.exists('players.csv'):
    df_players = pd.read_csv('players.csv')
    
    search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요")
    
    if search_query:
        result = df_players[df_players['이름'].str.contains(search_query.strip())]
        if not result.empty:
            st.success(f"검색 결과")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning("선수를 찾을 수 없습니다.")
else:
    st.error("선수 데이터 파일(players.csv)을 찾을 수 없습니다. 깃허브에 파일을 올려주세요!")

st.snow()