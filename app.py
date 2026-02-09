import streamlit as st
import pandas as pd
import requests
import datetime
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="AI 습관 트래커", page_icon="📊")

# 2. 세션 상태 초기화 (습관 데이터 저장용)
if 'history_data' not in st.session_state:
    # 데모용 7일치 성취도 데이터 (기본 라이브러리용 구조)
    st.session_state.history_data = [60, 80, 40, 100, 20, 80]

# 3. 사이드바 - API 설정
with st.sidebar:
    st.header("⚙️ 설정")
    openai_key = st.text_input("OpenAI API Key", type="password")
    weather_key = st.text_input("OpenWeatherMap API Key", type="password")
    
    st.divider()
    city = st.selectbox("📍 도시 선택", ["Seoul", "Busan", "Incheon", "Jeju"])
    coach_style = st.radio("🧠 코치 스타일", ["스파르타 코치", "따뜻한 멘토", "게임 마스터"])

# 4. API 함수 (최대한 단순하게 유지)
def get_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        res = requests.get(url, timeout=5).json()
        return {"temp": res['main']['temp'], "desc": res['weather'][0]['description']}
    except:
        return None

def get_dog_image():
    try:
        res = requests.get("https://dog.ceo/api/breeds/image/random", timeout=5).json()
        breed = res['message'].split('/')[4].capitalize()
        return {"url": res['message'], "breed": breed}
    except:
        return None

# 5. 메인 UI
st.title("📊 AI 습관 트래커")

# 습관 체크박스 (2열 배치)
st.subheader("✅ 오늘의 습관")
cols = st.columns(2)
with cols[0]:
    h1 = st.checkbox("🌅 기상 미션")
    h2 = st.checkbox("💧 물 마시기")
    h3 = st.checkbox("📚 공부/독서")
with cols[1]:
    h4 = st.checkbox("💪 운동하기")
    h5 = st.checkbox("😴 수면 관리")

mood = st.slider("오늘의 기분 점수", 1, 10, 5)

# 계산
done_count = sum([h1, h2, h3, h4, h5])
rate = (done_count / 5) * 100

st.divider()

# 메트릭 & 차트 (Plotly 대신 Streamlit 기본 차트 사용)
m1, m2, m3 = st.columns(3)
m1.metric("오늘의 달성률", f"{rate}%")
m2.metric("완료 개수", f"{done_count}/5")
m3.metric("기분", f"{mood}/10")

st.subheader("📈 최근 7일 성취도")
# 오늘 데이터 포함하여 차트 그리기
chart_data = st.session_state.history_data + [rate]
st.bar_chart(chart_data)

st.divider()

# 6. 리포트 생성 및 결과
if st.button("🚀 컨디션 리포트 생성"):
    if not openai_key:
        st.error("OpenAI API 키를 입력해주세요!")
    else:
        with st.spinner("AI 분석 중..."):
            weather = get_weather(city, weather_key)
            dog = get_dog_image()
            
            # 정보 표시
            c1, c2 = st.columns(2)
            with c1:
                if weather:
                    st.info(f"🌡️ {city}: {weather['temp']}도, {weather['desc']}")
                else:
                    st.warning("날씨 API 키를 확인해주세요.")
            with c2:
                if dog:
                    st.image(dog['url'], caption=f"오늘의 강아지: {dog['breed']}", use_container_width=True)

            # OpenAI 리포트 생성
            try:
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"당신은 {coach_style}입니다."},
                        {"role": "user", "content": f"습관 {done_count}개 완료, 기분 {mood}점, 날씨 {weather}, 강아지 {dog['breed']}. 컨디션 등급(S~D)을 포함한 분석 리포트를 써줘."}
                    ]
                )
                report = response.choices[0].message.content
                st.markdown("### 🤖 AI 코치 리포트")
                st.write(report)
                st.code(report, language="text") # 복사용
            except Exception as e:
                st.error(f"OpenAI 연결 오류: {e}")

with st.expander("ℹ️ 안내"):
    st.write("Plotly 라이브러리 없이 Streamlit 기본 기능만 사용한 버전입니다.")
