import streamlit as st

from src.state import get_state
from src.calc import calc_discretionary_hours
from src.ui.sidebar import render_sidebar
from src.ui.onboarding_page import render_onboarding_page  # ✅ 추가
from src.ui.input_page import render_input_page
from src.ui.results_page import render_results_page
from src.ui.support_page import render_support_page
from src.ui.export_page import render_export_page


def main():
    # ✅ 메인 화면 시작 앵커
    st.markdown('<div id="main_top"></div>', unsafe_allow_html=True)

    # ✅ 온보딩에서 "스크롤 점프 요청"이 있으면 처리
    if st.session_state.get("scroll_to") == "main_top":
        st.components.v1.html(
            """
            <script>
            const el = window.parent.document.getElementById("main_top");
            if (el) el.scrollIntoView({behavior: "smooth"});
            </script>
            """,
            height=0,
        )
        st.session_state["scroll_to"] = None
    
    st.set_page_config(page_title="시간=돈(기회비용)", layout="wide")

    s = get_state()
    render_sidebar(s)

    st.title("시간 = 돈(기회비용)")
    st.caption("사람을 평가하지 않는다. 선택을 비난하지 않는다. 선택의 가치를 ‘보여준다’.")

    # ✅ 온보딩이 먼저
    if not s.onboarding_completed:
        render_onboarding_page(s)
        return

    with st.expander(f"{s.persona_name}의 상황(설계 철학)", expanded=True):
        st.write(s.persona_note)

    discretionary, fixed = calc_discretionary_hours(s.basics)

    tab1, tab2, tab3, tab4 = st.tabs(["입력", "선택 활동 가치 환산 결과", "의사 결정 지원", "내보내기(틀)"])
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
