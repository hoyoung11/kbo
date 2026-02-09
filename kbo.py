import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 실시간 데이터 센터")

# --- 팀 순위 ---
st.subheader("🏆 KBO 팀 순위")
try:
    df_rank = pd.read_html("https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx")[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except:
    st.write("순위 정보를 불러오는 중입니다...")

st.markdown("---")

# --- 선수 검색 (GitHub Action이 만든 파일 읽기) ---
st.header("🔍 선수 검색")

# 파일 읽기 시 에러 방지 옵션 추가
if os.path.exists('players.csv'):
    try:
        # on_bad_lines='skip'으로 에러 나는 줄은 건너뛰게 설정
        df_players = pd.read_csv('players.csv', encoding='utf-8-sig', on_bad_lines='skip')
        
        search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요")
        if search_query:
            result = df_players[df_players['이름'].str.contains(search_query.strip())]
            if not result.empty:
                st.dataframe(result, use_container_width=True, hide_index=True)
            else:
                st.warning("선수를 찾을 수 없습니다.")
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다.")
else:
    st.info("선수 데이터를 생성 중입니다. 잠시 후 다시 확인해 주세요.")