#사이드바
import streamlit as st

from ..models import AppState


def render_sidebar(s: AppState) -> None:
    st.sidebar.header("설정(강요 없음)")

    s.persona_name = st.sidebar.text_input("인물 이름", value=s.persona_name)

    st.sidebar.subheader("시간가치 기준(원/시간)")
    s.basis_hour_value = st.sidebar.number_input(
        "기준 시간가치",
        min_value=0.0,
        value=float(s.basis_hour_value),
        step=500.0,
        help="v0에서는 사용자 입력 기준만 사용. v1에서 공식통계 프리셋 연결 가능.",
    )
    s.basis_note = st.sidebar.text_area("기준 설명(선택)", value=s.basis_note, height=70)
