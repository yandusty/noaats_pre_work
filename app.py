import streamlit as st

from src.state import get_state
from src.calc import calc_discretionary_hours
from src.ui.sidebar import render_sidebar
from src.ui.input_page import render_input_page
from src.ui.results_page import render_results_page
from src.ui.support_page import render_support_page
from src.ui.export_page import render_export_page


def main():
    st.set_page_config(
        page_title="시간=돈(기회비용) — 선택을 보여주는 도구",
        layout="wide",
    )

    s = get_state()
    render_sidebar(s)

    st.title("시간 = 돈(기회비용)")
    st.caption("사람을 평가하지 않는다. 선택을 비난하지 않는다. 선택의 무게를 ‘보여준다’.")

    with st.expander(f"{s.persona_name}의 상황(설계 철학)", expanded=True):
        st.write(s.persona_note)

    discretionary, fixed = calc_discretionary_hours(s.basics)

    tab1, tab2, tab3, tab4 = st.tabs(["입력", "기회비용 결과", "의사결정 지원", "내보내기(틀)"])

    with tab1:
        render_input_page(s, discretionary)

    with tab2:
        render_results_page(s, discretionary, fixed)

    with tab3:
        render_support_page(s)

    with tab4:
        render_export_page(s)


if __name__ == "__main__":
    main()
