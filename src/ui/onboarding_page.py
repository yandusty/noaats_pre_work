import streamlit as st
from ..models import AppState

def render_onboarding_page(s: AppState) -> None:
    st.header("먼저, 당신의 기준을 정해볼까요?")

    # ✅ 폼 밖: 실시간 전환용
    mode = st.radio("입력 방식", ["직접 입력", "질문으로 환산"], horizontal=True, key="onboarding_mode")

    with st.form("onboarding_form"):
        st.subheader("어떤 시점의 나를 기준으로 볼까요?")
        s.value_reference = st.radio(
            "기준 시점",
            ["전성기", "현재", "미래"],
            index=["전성기", "현재", "미래"].index(s.value_reference) if s.value_reference in ["전성기", "현재", "미래"] else 1,
            horizontal=True,
        )

        st.subheader("당신이 생각하는 ‘내 시간의 가치’ 기준")

        if mode == "직접 입력":
            basis = st.number_input("내 시간가치 기준(원/시간)", min_value=0.0, value=float(s.basis_hour_value), step=500.0)
            note = st.text_area("설명(선택)", value=s.basis_note, height=60)
        else:
            month_value = st.number_input("내가 생각하는 한 달의 나의 가치(원)", min_value=0.0, value=2000000.0, step=100000.0)
            days_per_week = st.slider("주당 기준 일수", 1, 7, 6)
            hours_per_day = st.slider("하루 선택 가능한 시간(대략)", 0.0, 16.0, 8.0, 0.5)

            # (환산 함수는 기존 그대로)
            derived = month_value / max(1.0, (days_per_week * 4.345) * max(0.5, hours_per_day))
            st.info(f"→ 환산된 시간가치 기준(참고): 약 {derived:,.0f}원/시간")
            basis = st.slider("최종 시간가치 기준(원/시간) 조정", 0.0, max(100000.0, derived * 2), float(derived), 500.0)
            note = "자기 인식 기반 환산값(공식 통계 아님)."

        st.subheader("활동 중요도(가중치)")
        new_weights = {k: st.slider(k, 0, 100, int(v)) for k, v in s.weights.items()}

        apply = st.form_submit_button("설정 완료! 다음 단계로", type="primary", use_container_width=True)

    if apply:
        s.basis_hour_value = float(basis)
        s.basis_note = str(note)
        s.weights = new_weights
        s.onboarding_completed = True

        st.session_state["scroll_to"] = "main_top"  # ✅ 메인 상단으로 자동 점프
        st.rerun()