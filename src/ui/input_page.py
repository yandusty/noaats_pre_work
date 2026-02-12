import streamlit as st

from ..models import AppState, ChoiceBlock


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
    st.subheader("2) 선택 가능한 시간 배분(6개 범주 고정)")
    st.caption("선택지는 온보딩에서 정한 6개 범주로 고정되어 있어. (범주 밖 활동 추가는 v1에서)")

    categories = list(s.weights.keys())

    # 기존 입력값 유지용 매핑
    existing = {c.label: float(c.hours) for c in (s.choices or [])}

    new_choices = []
    used = 0.0

    for i, cat in enumerate(categories):
        default_h = max(0.0, float(existing.get(cat, 0.0)))

        with st.container(border=True):
            c1, c2, c3 = st.columns([2.2, 1.2, 1.2])
            c1.markdown(f"**{cat}**")
            c2.caption(f"중요도: {int(s.weights.get(cat, 0))}/100")

            hours = c3.number_input(
                "시간(시간)",
                min_value=0.0,
                max_value=24.0,
                value=float(default_h),
                step=0.5,
                key=f"cat_hours_{i}",
            )

        used += float(hours)
        new_choices.append(ChoiceBlock(cat, float(hours)))

    # 저장(범주 고정)
    s.choices = new_choices

    st.info(f"선택 가능한 시간(추정): {discretionary:.1f}시간 / 현재 배분 합계: {used:.1f}시간")
    if used > discretionary + 0.25:
        st.warning("배분 시간이 선택 가능한 시간을 초과했어. 괜찮아—대략치니까. 필요하면 조금만 줄여봐.")
    elif used < max(0.0, discretionary - 2.0):
        st.caption("배분하지 않은 시간이 남아 있어. 일부러 비워두는 것도 하나의 선택이야.")