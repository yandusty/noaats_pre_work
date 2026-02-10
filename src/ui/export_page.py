#부가적인 기능 내보내기 형식
import json
import streamlit as st
from dataclasses import asdict

from ..models import AppState


def render_export_page(s: AppState) -> None:
    st.subheader("5) 업데이트 가능 구조(저장/불러오기 틀)")
    st.caption("v0에서는 JSON을 ‘보여주기’까지만. v1에서 파일 업로드/다운로드로 확장하면 된다.")

    payload = {
        "persona_name": s.persona_name,
        "persona_note": s.persona_note,
        "basis_hour_value": s.basis_hour_value,
        "basis_note": s.basis_note,
        "basics": asdict(s.basics),
        "choices": [asdict(c) for c in (s.choices or [])],
    }

    st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")
