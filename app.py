import streamlit as st
import pandas as pd
import requests
import datetime
from openai import OpenAI

# 1. 페이지 설정 및 커스텀 CSS (카드 스타일 UI)
st.set_page_config(page_title="AI Habit Diary", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 및 폰트 설정 */
    .main { background-color: #fcfcfc; }
    h1, h2, h3 { color: #4A4A4A; font-family: 'Nanum Gothic', sans-serif; }
    
    /* 카드 스타일 컨테이너 */
    .st-emotion-cache-1r6slb0 {
        padding: 20px;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 체크박스 색상 변경 */
    div[data-testid="stCheckbox"] {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 상태 초기화
if 'history_data' not in st.session_state:
    st.session_state.history_data = [70, 85, 50, 100, 40, 80]
if 'habit_list' not in st.session_state:
    st.session_state.habit_list = ["🌅 기상 미션", "💧 물 마시기", "📚 독서", "💪 운동"]

# 3. 사이드바 (설정창 숨기기 가능)
with st.sidebar:
    st.title("🌿 My Zen Settings")
    openai_key = st.text_input("OpenAI API Key", type="password")
    weather_key = st.text_input("Weather API Key", type="password")
    city = st.selectbox("📍 나의 도시", ["Seoul", "Jeju", "Busan", "Tokyo", "London"])
    coach_style = st.radio("🧠 분석 무드", ["따뜻한 멘토", "스파르타 코치", "게임 마스터"])

# 4. API 함수
def get_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        res = requests.get(url, timeout=5).json()
        return {"temp": res['main']['temp'], "desc": res['weather'][0]['description']}
    except: return None

def get_dog_image():
    try:
        res = requests.get("https://dog.ceo/api/breeds/image/random", timeout=5).json()
        return res['message']
    except: return None

def get_tarot_card():
    try:
        url = "https://tarotapi.dev/api/v1/cards/random?n=1"
        res = requests.get(url, timeout=5).json()
        return res['cards'][0]
    except: return None

# 5. 메인 레이아웃 시작
st.title("✨ 오늘의 마음 기록")
st.caption(f"{datetime.date.today().strftime('%Y년 %m월 %d일')} | 평온한 하루를 시작하세요.")

# --- 섹션 1: 습관 리스트 ---
with st.container():
    st.subheader("📝 오늘 꼭 하고 싶은 일")
    
    # 습관 추가/삭제 에디터 (깔끔하게 Expander로 숨김)
    with st.expander("습관 목록 편집"):
        new_h = st.text_input("새 습관 입력")
        if st.button("추가"):
            st.session_state.habit_list.append(new_h); st.rerun()
        for idx, h in enumerate(st.session_state.habit_list):
            if st.button(f"삭제: {h}", key=f"del_{idx}"):
                st.session_state.habit_list.remove(h); st.rerun()

    # 체크박스 리스트
    checked = []
    c1, c2 = st.columns(2)
    for i, h in enumerate(st.session_state.habit_list):
        col = c1 if i % 2 == 0 else c2
        if col.checkbox(h, key=f"chk_{i}"): checked.append(h)

# --- 섹션 2: 통계 및 달성률 ---
total = len(st.session_state.habit_list)
done = len(checked)
rate = (done / total * 100) if total > 0 else 0

st.divider()
st.subheader("📊 오늘의 성취")
col_m1, col_m2 = st.columns([1, 2])
with col_m1:
    st.metric("오늘의 달성률", f"{rate:.0f}%")
    mood = st.select_slider("오늘의 기분", options=range(1, 11), value=5)
with col_m2:
    st.area_chart(st.session_state.history_data + [rate])

if rate == 100:
    st.balloons()
    st.success("완벽한 하루네요! 모든 미션을 완료했습니다. ✨")

# --- 섹션 3: 분석 리포트 (버튼 클릭 시 카드 형태 출력) ---
st.divider()
if st.button("🚀 하루 마무리 리포트 생성", use_container_width=True):
    if not openai_key:
        st.error("설정에서 OpenAI API 키를 입력해주세요.")
    else:
        with st.spinner("평온한 마음으로 분석 중입니다..."):
            weather = get_weather(city, weather_key)
            dog_url = get_dog_image()
            tarot = get_tarot_card()
            
            # 카드형 결과 배치
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown(f"""
                <div style="background-color:#E3F2FD; padding:15px; border-radius:10px;">
                    <p style="margin:0; font-size:14px; color:#1976D2;"><b>📍 {city} 날씨</b></p>
                    <h3 style="margin:0; color:#1565C0;">{weather['temp'] if weather else '?'}°C</h3>
                    <p style="margin:0; font-size:12px;">{weather['desc'] if weather else '연결 안됨'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background-color:#F3E5F5; padding:15px; border-radius:10px;">
                    <p style="margin:0; font-size:14px; color:#7B1FA2;"><b>🃏 오늘의 카드</b></p>
                    <h4 style="margin:0; color:#4A148C;">{tarot['name'] if tarot else '신비로운 카드'}</h4>
                    <p style="margin:0; font-size:11px;">{tarot['meaning_up'][:60] if tarot else ''}...</p>
                </div>
                """, unsafe_allow_html=True)

            with res_col2:
                if dog_url: st.image(dog_url, caption="오늘의 행운", use_container_width=True)

            # AI 분석 리포트
            try:
                client = OpenAI(api_key=openai_key)
                prompt = f"사용자 습관 {done}/{total} 완료, 기분 {mood}/10, 날씨 {weather}, 타로카드 {tarot['name']}. {coach_style} 스타일로 리포트 써줘."
                res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                
                st.markdown("### 🤖 분석 리포트")
                st.info(res.choices[0].message.content)
            except Exception as e:
                st.error(f"연결 오류: {e}")
