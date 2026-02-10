#결과 UI
import streamlit as st

from ..models import AppState
from ..calc import calc_opportunity_cost_table, krw


def render_results_page(s: AppState, discretionary: float, fixed: dict) -> None:
    st.subheader("3) 기회비용(가능성 가치) 결과")
    st.caption("‘손해’가 아니라, 다른 선택으로 전환될 수 있었던 가능성의 크기를 보여준다.")

    fixed_sum = sum(fixed.values())
    st.write(f"- 필수 시간 합계: **{fixed_sum:.1f}시간**")
    st.write(f"- 선택 가능한 시간(추정): **{discretionary:.1f}시간**")
    st.write(f"- 시간가치 기준: **{krw(s.basis_hour_value)}/시간**")
    st.caption(s.basis_note)

    if not s.choices:
        st.info("선택지(시간 배분)가 아직 없어. 입력 탭에서 추가해줘.")
        return

    df = calc_opportunity_cost_table(s.choices, s.basis_hour_value)
    df_show = df.copy()
    df_show["가치환산(원)"] = df_show["가치환산(원)"].apply(krw)
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    total_equiv = float(df["가치환산(원)"].sum()) if not df.empty else 0.0
    st.success(f"오늘 선택들의 ‘가능성 가치 환산 합계’는 **{krw(total_equiv)}** 정도로 표현될 수 있어.")

    st.markdown(
        "- 이 숫자는 **평가가 아니라 가시화**야.\n"
        "- 휴식도 선택이고 실행도 선택이야. 중요한 건 **내가 지금 어떤 선택을 하고 있는지**를 인식하는 것."
    )
