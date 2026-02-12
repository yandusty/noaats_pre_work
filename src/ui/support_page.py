#의사 결정 지원 UI
import streamlit as st

from ..models import AppState
from ..quotes import pick_quote


def _sunk_cost_text() -> str:
    return (
        "### 매몰비용(과거) 안내\n"
        "- 이 앱은 **과거에 쓴 시간/돈(매몰비용)**을 '되찾아야 한다'는 근거로 쓰지 않습니다.\n"
        "- 다만, 과거가 지금의 판단을 흔들고 있다면 **왜 흔들리는지 설명하는 재료**로만 다룹니다.\n"
        "- 결론은 항상 **지금 이후의 선택**에 초점을 맞춥니다.\n"
    )


def render_support_page(s: AppState) -> None:
    st.subheader("의사결정 지원(비난 없음)")
    st.caption("선택을 ‘정답/오답’으로 판정하지 않고, 다음 질문을 던지는 형태로 돕는다.")

    st.markdown("#### 오늘의 선택을 더 편하게 만드는 질문(선택)")
    q1 = st.text_area("Q1. 오늘 가장 지키고 싶은 감정/상태는?", placeholder="예: 안정감, 회복, 성취감, 연결감 ...")
    q2 = st.text_area("Q2. 내일의 나에게 남기고 싶은 최소 결과물은?", placeholder="예: 30분 정리, 이력서 1줄, 전화 1통 ...")
    q3 = st.text_area("Q3. '아무것도 안함'을 선택했다면, 그 이유는?", placeholder="예: 회복 필요, 두려움, 막막함, 비교 스트레스 ...")

    st.markdown(_sunk_cost_text())

    with st.expander("내 답변 정리 보기", expanded=False):
        st.write(f"- 지키고 싶은 상태: {q1 if q1.strip() else '(비어있음)'}")
        st.write(f"- 최소 결과물: {q2 if q2.strip() else '(비어있음)'}")
        st.write(f"- 아무것도 안함의 이유: {q3 if q3.strip() else '(비어있음)'}")

    st.divider()
    st.subheader("오늘의 한 문장")
    st.write(pick_quote())
    st.caption("이 앱은 너를 몰아붙이기 위한 도구가 아니다. 시간을 ‘보여주기’ 위한 도구다.")
