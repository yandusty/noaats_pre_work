# 현재 세션 상태.
# 세션 초기화 및 가져오기, 프로토타입의 시작
import streamlit as st

from .models import AppState, ChoiceBlock


def _default_state() -> AppState:
    s = AppState()
    s.choices = [
        ChoiceBlock("생산활동", 4.0),
        ChoiceBlock("인적자본 축적", 4.0),
        ChoiceBlock("회복,건강,여가", 2.0),
        ChoiceBlock("소비성 여가, 저생산 활동", 2.0)
    ]
    return s

def get_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state.app_state = _default_state()
    return st.session_state.app_state
