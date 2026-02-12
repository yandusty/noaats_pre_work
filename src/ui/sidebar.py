#첫 설정한 내용 수정용으로 사용!
import streamlit as st
from ..models import AppState


def render_sidebar(s: AppState) -> None:
    st.sidebar.header("설정")

    # 온보딩 상태 표시 + 재시작 버튼
    if s.onboarding_completed:
        st.sidebar.success("온보딩 완료")
        if st.sidebar.button("온보딩 다시하기"):
            s.onboarding_completed = False
            st.rerun()
    else:
        st.sidebar.warning("온보딩 진행 전")

    s.persona_name = st.sidebar.text_input("인물 이름", value=s.persona_name)

    st.sidebar.subheader("기준 시점")
    s.value_reference = st.sidebar.selectbox("전성기/현재/미래", ["전성기", "현재", "미래"], index=["전성기", "현재", "미래"].index(s.value_reference))

    st.sidebar.subheader("시간가치 기준(원/시간)")
    s.basis_hour_value = st.sidebar.number_input("기준 시간가치", min_value=0.0, value=float(s.basis_hour_value), step=500.0)
    s.basis_note = st.sidebar.text_area("기준 설명(선택)", value=s.basis_note, height=70)

    st.sidebar.subheader("활동 중요도(가중치)")
    with st.sidebar.expander("가중치 수정", expanded=False):
        for k in list(s.weights.keys()):
            s.weights[k] = st.slider(k, 0, 100, int(s.weights[k]), key=f"sb_w_{k}")
