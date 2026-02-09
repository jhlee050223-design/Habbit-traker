import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="AI 습관 트래커", page_icon="📊", layout="wide")

# 2. 세션 상태 초기화 (습관 데이터 저장용)
if 'history' not in st.session_state:
    # 데모용 6일치 샘플 데이터
    dates = [(datetime.date.today() - datetime.timedelta(days=i)) for i in range(6, 0, -1)]
    st.session_state.history = pd.DataFrame({
        '날짜': dates,
        '달성률': [60, 80, 40, 100, 20, 80]
    })

# 3. 사이드바 - API 설정
with st.sidebar:
    st.header("⚙️ 설정")
    openai_key = st.text_input("OpenAI API Key", type="password")
    weather_key = st.text_input("OpenWeatherMap API Key", type="password")
    
    st.divider()
    city = st.selectbox("📍 도시 선택", ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan", "Suwon", "Sejong", "Jeju"])
    coach_style = st.radio("🧠 코치 스타일", ["스파르타 코치", "따뜻한 멘토", "게임 마스터"])

# 4. API 함수 정의
def get_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data['main']['temp'],
                "desc": data['weather'][0]['description']
            }
    except:
        return None

def get_dog_image():
    try:
        response = requests.get("https://dog.ceo/api/breeds/image/random", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # URL에서 품종 추출 (예: /breeds/hound-english/...)
            breed = data['message'].split('/')[4].replace('-', ' ').title()
            return {"url": data['message'], "breed": breed}
    except:
        return None

def generate_report(data):
    if not openai_key:
        return "OpenAI API 키를 입력해주세요."
    
    client = OpenAI(api_key=openai_key)
    
    # 스타일별 프롬프트 설정
    system_prompts = {
        "스파르타 코치": "당신은 엄격하고 강력하게 동기를 부여하는 스파르타 코치입니다. 짧고 강한 말투를 사용하세요.",
        "따뜻한 멘토": "당신은 다정하고 공감 능력이 뛰어난 따뜻한 멘토입니다. 존댓말을 사용하고 따뜻하게 격려하세요.",
        "게임 마스터": "당신은 판타지 RPG의 게임 마스터입니다. 사용자의 습관을 퀘스트로, 상태를 스탯으로 비유하여 흥미롭게 말하세요."
    }

    prompt = f"""
    사용자의 오늘 습관 데이터: {data['habits']}
    오늘의 기분 점수: {data['mood']}/10
    현재 날씨: {data['weather']}
    오늘의 동반견 품종: {data['dog_breed']}

    위 데이터를 바탕으로 아래 형식의 리포트를 작성해줘:
    1. 컨디션 등급 (S~D)
    2. 습관 분석
    3. 날씨 코멘트
    4. 내일 미션
    5. 오늘의 한마디 (강아지 품종 언급 포함)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # gpt-5-mini 부재 시 대체 가능한 최신 모델
            messages=[
                {"role": "system", "content": system_prompts[coach_style]},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"리포트 생성 중 오류 발생: {str(e)}"

# 5. 메인 UI
st.title("📊 AI 습관 트래커")

# 습관 체크인 섹션
st.subheader("✅ 오늘의 습관 체크인")
col1, col2 = st.columns(2)
with col1:
    h1 = st.checkbox("🌅 기상 미션")
    h2 = st.checkbox("💧 물 마시기")
    h3 = st.checkbox("📚 공부/독서")
with col2:
    h4 = st.checkbox("💪 운동하기")
    h5 = st.checkbox("😴 수면 관리")

mood = st.slider("오늘의 기분은 어떤가요? (1~10)", 1, 10, 5)

# 계산 로직
habit_list = [h1, h2, h3, h4, h5]
done_count = sum(habit_list)
achievement_rate = (done_count / 5) * 100

st.divider()

# 메트릭 카드
m1, m2, m3 = st.columns(3)
m1.metric("오늘의 달성률", f"{achievement_rate}%")
m2.metric("달성 습관 개수", f"{done_count} / 5")
m3.metric("기분 점수", f"{mood}/10")

# 차트 섹션
st.subheader("📈 최근 7일 성취도")
today_data = pd.DataFrame({'날짜': [datetime.date.today()], '달성률': [achievement_rate]})
chart_df = pd.concat([st.session_state.history, today_data]).tail(7)
fig = px.bar(chart_df, x='날짜', y='달성률', range_y=[0, 100], color='달성률', color_continuous_scale='Blues')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# 리포트 생성 버튼
if st.button("🚀 컨디션 리포트 생성"):
    with st.spinner("AI 코치가 데이터를 분석 중입니다..."):
        weather_data = get_weather(city, weather_key) if weather_key else "날씨 정보 없음"
        dog_data = get_dog_image()
        
        # 2열 레이아웃 (날씨 + 강아지)
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"🌡️ **{city} 날씨**")
            if weather_data and isinstance(weather_data, dict):
                st.write(f"온도: {weather_data['temp']}°C / 상태: {weather_data['desc']}")
            else:
                st.write("날씨 정보를 불러올 수 없습니다.")
        
        with c2:
            if dog_data:
                st.image(dog_data['url'], caption=f"오늘의 행운견: {dog_data['breed']}", use_container_width=True)
            else:
                st.write("강아지 이미지를 불러올 수 없습니다.")

        # AI 리포트 생성
        input_data = {
            "habits": f"{done_count}개 완료",
            "mood": mood,
            "weather": weather_data,
            "dog_breed": dog_data['breed'] if dog_data else "Unknown"
        }
        report = generate_report(input_data)
        
        st.subheader(f"🤖 {coach_style}의 분석")
        st.markdown(report)
        
        # 공유용 텍스트
        st.subheader("🔗 공유하기")
        share_text = f"[AI 습관 트래커 리포트]\n- 달성률: {achievement_rate}%\n- 기분: {mood}/10\n\n{report}"
        st.code(share_text, language='text')

# 6. 하단 안내
with st.expander("ℹ️ API 및 사용 안내"):
    st.write("""
    - **OpenAI:** GPT 모델을 통해 개인화된 리포트를 생성합니다. (현재 gpt-4o-mini 사용)
    - **OpenWeatherMap:** 사용자의 위치 정보를 기반으로 실시간 날씨를 반영합니다.
    - **Dog API:** 습관 달성 동기부여를 위해 랜덤 강아지 이미지를 제공합니다.
    - 본 앱은 세션이 유지되는 동안만 기록이 저장됩니다.
    """)
