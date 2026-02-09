import streamlit as st
import pandas as pd
import requests
import os

# 1. 페이지 설정
st.set_page_config(page_title="KBO 데이터 센터", layout="wide")
st.title("⚾ KBO 실시간 데이터 & 선수 검색")

# --- [섹션 1] 팀 순위표 ---
st.subheader("🏆 KBO 공식 팀 순위")
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

try:
    # 팀 순위는 비교적 차단이 덜하므로 실시간으로 가져옵니다.
    response = requests.get(url_rank, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    df_rank = pd.read_html(response.text)[0]
    st.dataframe(df_rank, use_container_width=True, hide_index=True)
except Exception as e:
    st.warning("순위 데이터를 실시간으로 가져오는 데 실패했습니다. 잠시 후 새로고침 해주세요.")

st.markdown("---")

# --- [섹션 2] 선수 검색 (GitHub Actions가 만든 파일 읽기) ---
st.header("🔍 선수 검색")

# 파일이 있는지 확인
if os.path.exists('players.csv'):
    try:
        # 인코딩 에러와 데이터 형식이 깨진 줄을 방지하며 읽기
        try:
            # 1순위: utf-8-sig (엑셀 호환 한글 인코딩)
            df_players = pd.read_csv('players.csv', encoding='utf-8-sig', on_bad_lines='skip')
        except:
            # 2순위: cp949 (윈도우 한글 인코딩)
            df_players = pd.read_csv('players.csv', encoding='cp949', on_bad_lines='skip')
        
        # 데이터가 정상적으로 로드되었는지 확인
        if not df_players.empty and '이름' in df_players.columns:
            search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요 (예: 강백호, 김도영)")
            
            if search_query:
                clean_name = search_query.strip()
                # 이름 컬럼에서 검색어 포함 여부 확인 (대소문자 무시 안 함, 한글 기준)
                result = df_players[df_players['이름'].str.contains(clean_name, na=False)]
                
                if not result.empty:
                    st.success(f"'{clean_name}' 검색 결과입니다.")
                    st.dataframe(result, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"'{clean_name}' 선수를 찾을 수 없습니다. 명단에 없는 신인이거나 이름 오타일 수 있습니다.")
        else:
            st.error("불러온 선수 명단 데이터가 올바르지 않습니다. GitHub Actions 설정을 확인해 주세요.")

    except Exception as e:
        # 에러 발생 시 구체적인 원인 출력
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
else:
    # 파일 자체가 없는 경우
    st.info("💡 선수 데이터 파일(players.csv)이 아직 생성되지 않았습니다.")
    st.write("GitHub Actions가 처음 실행되어 파일을 만들 때까지 약 1~2분 정도 걸릴 수 있습니다.")

st.snow()