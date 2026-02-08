import streamlit as st
import pandas as pd
import requests

st.title("⚾ KBO 공식 기록실 데이터 분석")

# KBO 공식 홈페이지 순위 주소
url = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"

try:
    # 1. KBO 페이지의 표(table) 데이터 읽어오기
    # header={'User-Agent':...} 는 "나 사람이에요!"라고 알려주는 최소한의 예의입니다.
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    # 2. HTML 안의 표를 데이터프레임으로 변환
    dfs = pd.read_html(response.text)
    df = dfs[0] # 첫 번째 표가 보통 순위표입니다.

    # 3. 데이터 확인 및 출력
    st.subheader("🏆 KBO 공식 팀 순위")
    st.dataframe(df, width='stretch', hide_index=True)

    # 4. 간단한 시각화 (팀명과 승률)
    # KBO 표는 컬럼명이 '팀'이 아니라 '팀명'일 수 있으니 확인 후 그래프 그리기
    if '팀명' in df.columns:
        st.bar_chart(df.set_index("팀명")["승률"])

except Exception as e:
    st.error(f"KBO 공식 홈페이지 접속 중 오류가 발생했습니다: {e}")
    st.info("공식 홈페이지가 막혀있다면, 다음 단계인 '공공데이터 포털'로 넘어가 볼까요?")
    # 코드 하단에 추가
st.markdown("---")
target_team = st.multiselect("확인하고 싶은 팀을 선택하세요 (여러 팀 가능)", df['팀명'].unique())

if target_team:
    filtered_df = df[df['팀명'].isin(target_team)]
    st.write(f"🔍 선택하신 팀의 성적입니다.")
    st.dataframe(filtered_df, width='stretch')
    # 표 아래에 추가
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📂 KBO 순위표 CSV로 저장하기",
    data=csv,
    file_name='kbo_rank.csv',
    mime='text/csv',
)# 1. 사이드바 만들기 (휴대폰에서는 왼쪽 화살표로 숨겨져요)
with st.sidebar:
    st.header("⚾ 설정")
    st.write("KBO 실시간 순위 데이터입니다.")
    st.button("데이터 새로고침")

# 1. 실제 데이터에서 1위 팀 정보 추출
top_team = df.iloc[0]['팀명']       # 1등 팀 이름
top_win_rate = df.iloc[0]['승률']   # 1등 승률
game_count = df.iloc[0]['경기']     # 전체 경기 수

# 2. 화면에 카드 형태로 표시
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("현재 1위 팀", f"🏆 {top_team}")

with col2:
    st.metric("리그 진행도", f"{game_count} 경기", "2025 시즌")

with col3:
    st.metric("최고 승률", f"{top_win_rate}")
    st.markdown("---")
st.header("🔍 선수 검색 (준비 중)")

# 선수 데이터를 가져오려면 별도의 URL 크롤링이 필요하지만, 
# 우선 UI만 먼저 배치해서 구조를 잡아볼게요.
search_name = st.text_input("검색하고 싶은 선수 이름을 입력하세요", placeholder="예: 김도영")

if search_name:
    st.write(f"'{search_name}' 선수를 찾고 계시는군요!")
    st.info("💡 선수별 상세 기록(타율, 홈런 등)을 가져오려면 KBO의 '선수 페이지' 데이터를 추가로 연결해야 합니다.")
    
    # 맛보기로 보여줄 수 있는 기능: 해당 선수가 어느 팀인지 정도는 보여줄 수 있어요 (데이터가 있다면)
    # 현재는 팀 순위표만 있으니, 나중에 '선수 명단' 데이터를 추가하면 완벽해집니다!