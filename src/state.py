# 현재 세션 상태.
# 세션 초기화 및 가져오기, 프로토타입의 시작
import streamlit as st

from .models import AppState, ChoiceBlock


def _default_state() -> AppState:
    s = AppState()
    s.choices = [
        ChoiceBlock("휴식/멍때리기(아무것도 안함)", 3.0),
        ChoiceBlock("탐색/정보수집(진로, 관심사, 상담 등)", 1.0),
        ChoiceBlock("학습/포트폴리오(작은 실행 포함)", 2.0),
        ChoiceBlock("운동/회복(컨디션 관리)", 1.0),
    ]
    return s


def get_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state.app_state = _default_state()
    return st.session_state.app_state
