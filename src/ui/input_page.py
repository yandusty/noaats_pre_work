#입력 UI
import streamlit as st

from ..models import AppState, ChoiceBlock
from ..calc import sum_choice_hours


def render_input_page(s: AppState, discretionary: float) -> None:
    st.subheader("1) 기본 생활 시간(필수)")
    st.caption("정확하지 않아도 괜찮아. 대략적으로만 적어도 계산은 돌아가게 만든다.")

    col1, col2, col3 = st.columns(3)
    s.basics.sleep_h = col1.number_input("수면(시간)", 0.0, 24.0, float(s.basics.sleep_h), 0.5)
    s.basics.meals_h = col1.number_input("식사(시간)", 0.0, 24.0, float(s.basics.meals_h), 0.5)

    s.basics.hygiene_h = col2.number_input("위생/용변/정리(시간)", 0.0, 24.0, float(s.basics.hygiene_h), 0.5)
    s.basics.chores_h = col2.number_input("필수 집안일(시간)", 0.0, 24.0, float(s.basics.chores_h), 0.5)

    s.basics.commute_h = col3.number_input("이동(시간)", 0.0, 24.0, float(s.basics.commute_h), 0.5)

    st.divider()
    st.subheader("2) 선택 가능한 시간 배분(선택)")
    st.caption("‘이 선택을 하면, 다른 선택을 못 한다’는 사실을 숫자로 보여준다.")

    if s.choices is None:
        s.choices = []

    # 선택지 편집
    for i, c in enumerate(s.choices):
        with st.container(border=True):
            cols = st.columns([3, 1.2, 0.8])
            c.label = cols[0].text_input("선택 이름", value=c.label, key=f"label_{i}")
            c.hours = cols[1].number_input("시간(시간)", 0.0, 24.0, float(c.hours), 0.5, key=f"hours_{i}")
            if cols[2].button("삭제", key=f"del_{i}"):
                s.choices.pop(i)
                st.rerun()

    with st.expander("선택지 추가", expanded=False):
        new_label = st.text_input("새 선택지 이름", value="새 선택지", key="new_label")
        new_hours = st.number_input("시간(시간)", 0.0, 24.0, 1.0, 0.5, key="new_hours")
        if st.button("추가"):
            s.choices.append(ChoiceBlock(new_label, float(new_hours)))
            st.rerun()

    used = sum_choice_hours(s.choices)
    st.info(f"선택 가능한 시간(추정): {discretionary:.1f}시간 / 현재 배분 합계: {used:.1f}시간")

    if used > discretionary + 0.25:
        st.warning("배분 시간이 선택 가능한 시간을 초과했어. 괜찮아—대략치니까. 필요하면 조금만 줄여봐.")
    elif used < max(0.0, discretionary - 2.0):
        st.caption("배분하지 않은 시간이 남아 있어. 일부러 비워두는 것도 하나의 선택이야.")
