# 현재 세션 상태.
# 세션 초기화 및 가져오기, 프로토타입의 시작
import streamlit as st

from .models import AppState, ChoiceBlock


def _default_state() -> AppState:
    s = AppState()
    s.choices = [
        ChoiceBlock("휴식/회복", 3.0),
        ChoiceBlock("여가/취미", 1.0),
        ChoiceBlock("자기계발/공부", 2.0),
        ChoiceBlock("운동/건강", 1.0),
        ChoiceBlock("미래준비(탐색/계획)", 1.0),
        ChoiceBlock("관계/소통", 0.5),
    ]
    return s

def get_state() -> AppState:
    if "app_state" not in st.session_state:
        st.session_state.app_state = _default_state()
    return st.session_state.app_state
