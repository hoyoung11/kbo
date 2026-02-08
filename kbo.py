import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정 (웹 브라우저 탭에 표시될 이름)
st.set_page_config(page_title="KBO 데이터 분석기", layout="wide")
st.title("⚾ KBO 공식 기록실 & 선수 검색")

# --- [섹션 1] 팀 순위표 ---
st.subheader("🏆 KBO 공식 팀 순위")
url_rank = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

try:
    # 팀 순위 가져오기
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url_rank, headers=headers)
    df_rank = pd.read_html(response.text)[0]
    
    # 상단 요약 지표 (Metric)
    col1, col2, col3 = st.columns(3)
    col1.metric("현재 1위", f"🏆 {df_rank.iloc[0]['팀명']}")
    col2.metric("리그 진행", f"{df_rank.iloc[0]['경기']} 경기")
    col3.metric("최고 승률", f"{df_rank.iloc[0]['승률']}")
    
    st.dataframe(df_rank, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("팀 순위 데이터를 불러오는 중 오류가 발생했습니다.")

st.markdown("---") # 구분선

# --- [섹션 2] 1군 선수 검색 기능 ---
st.header("🔍 1군 선수 검색")

@st.cache_data(ttl=3600) # 1시간 동안 데이터를 기억합니다.
def get_all_players():
    # KBO 팀 코드 매핑
    teams = {
        'OB':'두산', 'LG':'LG', 'SK':'SSG', 'LT':'롯데', 'SS':'삼성', 
        'HT':'KIA', 'HE':'한화', 'NC':'NC', 'KT':'KT', 'WO':'키움'
    }
    player_data = []
    
    # 접속 차단을 막기 위한 헤더 설정
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for code, team_name in teams.items():
        try:
            url = f"https://www.koreabaseball.com/Player/Search.aspx?teamCode={code}"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 선수 목록 테이블 행 찾기
            rows = soup.select('.tEx tbody tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 3:
                    p_name = cols[1].text.strip() # 이름
                    p_pos = cols[3].text.strip()  # 포지션
                    player_data.append({'팀': team_name, '이름': p_name, '포지션': p_pos})
        except:
            continue
    
    # 수집된 데이터가 없으면 빈 표 반환
    if not player_data:
        return pd.DataFrame(columns=['팀', '이름', '포지션'])
    
    return pd.DataFrame(player_data)

# 선수 데이터 로드 (로딩 바 표시)
with st.spinner('전체 10개 팀 선수 명단을 수집 중입니다. 잠시만 기다려 주세요...'):
    df_players = get_all_players()

# 검색창 입력
search_query = st.text_input("찾고 싶은 선수 이름을 입력하세요", placeholder="예: 김도영, 강백호, 구자욱")

if search_query:
    # 검색어 정제 (공백 제거 등)
    clean_query = search_query.strip()
    
    if not df_players.empty and '이름' in df_players.columns:
        # 이름에 검색어가 포함된 선수 필터링
        result = df_players[df_players['이름'].str.contains(clean_query)]
        
        if not result.empty:
            st.success(f"'{clean_query}' 검색 결과입니다.")
            st.dataframe(result, use_container_width=True, hide_index=True)
        else:
            st.warning(f"'{clean_query}' 선수를 찾을 수 없습니다. 성과 이름을 정확히 입력했는지 확인해 주세요.")
    else:
        st.error("현재 선수 데이터를 불러올 수 없는 상태입니다. 잠시 후 새로고침(F5)을 해주세요.")

st.snow() # 성공 기념 눈 내리기