import streamlit as st
import pandas as pd
import requests
import datetime
from openai import OpenAI

# 1. 페이지 설정
st.set_page_config(page_title="AI 습관 트래커", page_icon="🔮")

# 2. 세션 상태 초기화
if 'history_data' not in st.session_state:
    st.session_state.history_data = [60, 80, 40, 90, 30, 70]

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    openai_key = st.text_input("OpenAI API Key", type="password")
    weather_key = st.text_input("OpenWeatherMap API Key", type="password")
    
    st.divider()
    city = st.selectbox("📍 도시 선택", ["Seoul", "Busan", "Incheon", "Jeju", "Daegu"])
    coach_style = st.radio("🧠 코치 스타일", ["스파르타 코치", "따뜻한 멘토", "게임 마스터"])

# 4. API 함수 정의
def get_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        res = requests.get(url, timeout=5).json()
        return {"temp": res['main']['temp'], "desc": res['weather'][0]['description']}
    except: return None

def get_dog_image():
    try:
        res = requests.get("https://dog.ceo/api/breeds/image/random", timeout=5).json()
        return {"url": res['message'], "breed": res['message'].split('/')[4].capitalize()}
    except: return None

# [신규] 타로 API 연동
def get_tarot_card():
    try:
        # 요청하신 API 주소 사용
        url = "https://tarotapi.dev/api/v1/cards/random?n=1"
        res = requests.get(url, timeout=5).json()
        card = res['cards'][0]
        return {
            "name": card['name'],
            "meaning": card['meaning_up'],
            "desc": card['desc']
        }
    except: return None

# 5. 메인 UI
st.title("🔮 AI 습관 트래커 & 타로")

# 습관 체크박스
st.subheader("✅ 오늘의 습관 체크")
c1, c2 = st.columns(2)
with c1:
    h1 = st.checkbox("🌅 기상 미션")
    h2 = st.checkbox("💧 물 마시기")
    h3 = st.checkbox("📚 공부/독서")
with c2:
    h4 = st.checkbox("💪 운동하기")
    h5 = st.checkbox("😴 수면 관리")

mood = st.slider("오늘의 기분은?", 1, 10, 5)
done_count = sum([h1, h2, h3, h4, h5])
rate = (done_count / 5) * 100

# 대시보드 표시
st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("달성률", f"{rate}%")
m2.metric("완료", f"{done_count}/5")
m3.metric("기분", f"{mood}/10")

st.bar_chart(st.session_state.history_data + [rate])

# 6. 리포트 생성
if st.button("🚀 타로 뽑고 리포트 생성하기"):
    if not openai_key:
        st.error("OpenAI API 키를 입력해주세요!")
    else:
        with st.spinner("AI 코치가 카드를 섞고 날씨를 확인하는 중..."):
            weather = get_weather(city, weather_key)
            dog = get_dog_image()
            tarot = get_tarot_card() # 타로 카드 호출
            
            # 결과 카드 섹션
            st.divider()
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.write("🌡️ **오늘의 날씨**")
                if weather: st.info(f"{city}\n{weather['temp']}°C / {weather['desc']}")
                else: st.warning("날씨 정보 없음")
                
            with res_col2:
                st.write("🃏 **오늘의 타로**")
                if tarot: st.success(f"**{tarot['name']}**\n\n{tarot['meaning'][:50]}...")
                else: st.warning("카드를 뽑지 못했습니다.")
                
            with res_col3:
                st.write("🐶 **동기부여 멍멍**")
                if dog: st.image(dog['url'], use_container_width=True)

            # AI 분석 리포트
            try:
                client = OpenAI(api_key=openai_key)
                # 타로 데이터까지 포함한 프롬프트
                prompt = f"""
                사용자 데이터: 습관 {done_count}개 완료, 기분 {mood}/10, 날씨 {weather}.
                오늘 뽑은 타로 카드: {tarot['name']} (의미: {tarot['meaning']})
                강아지 품종: {dog['breed'] if dog else '알 수 없음'}

                위 데이터를 종합해서 {coach_style} 스타일로 리포트를 써줘.
                형식:
                - 컨디션 등급 (S~D)
                - 습관 & 기분 분석
                - **타로 카드 해석 (오늘의 운세와 연결)**
                - 내일의 미션 제안
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader(f"🤖 {coach_style}의 통합 리포트")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"AI 리포트 생성 실패: {e}")

with st.expander("ℹ️ 사용된 API 안내"):
    st.write("- **Tarot API**: tarotapi.dev (랜덤 카드 정보)")
    st.write("- **OpenWeatherMap**: 실시간 날씨 데이터")
    st.write("- **Dog API**: 랜덤 강아지 이미지")
    st.write("- **OpenAI**: 맞춤형 AI 코칭 리포트")
