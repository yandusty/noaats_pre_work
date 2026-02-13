# 의사결정지원(회고록/대안가치) 페이지
import streamlit as st
from copy import deepcopy
from typing import Dict, List, Tuple, Any

from ..models import AppState
from ..calc import calc_opportunity_cost_table, krw


# -----------------------------
# 내부 유틸: choices에서 "라벨/카테고리/시간" 최대한 안전하게 뽑기
# -----------------------------
def _get_field(choice, keys, default=None):
    """choice가 dict든 객체든 field를 안전하게 가져오기"""
    # dict
    if isinstance(choice, dict):
        for k in keys:
            if k in choice and choice[k] not in (None, ""):
                return choice[k]
        return default

    # object (dataclass / pydantic / 일반 클래스)
    for k in keys:
        if hasattr(choice, k):
            v = getattr(choice, k)
            if v not in (None, ""):
                return v
    return default


def _set_field(choice, keys, value):
    """choice가 dict든 객체든 field를 안전하게 설정하기"""
    if isinstance(choice, dict):
        # 기존 키가 있으면 그 키에, 없으면 첫 키로 추가
        for k in keys:
            if k in choice:
                choice[k] = value
                return
        choice[keys[0]] = value
        return

    # object: 존재하는 속성에 우선 설정, 없으면 첫 키로 setattr
    for k in keys:
        if hasattr(choice, k):
            setattr(choice, k, value)
            return
    setattr(choice, keys[0], value)


def _get_choice_label(choice) -> str:
    return str(_get_field(choice, ("label", "name", "title", "activity"), default="선택지"))


def _get_choice_category(choice) -> str:
    # 프로젝트에서 실제로 쓰는 필드명에 맞춰 여기를 늘려도 됨
    cat = _get_field(choice, ("category", "cat", "type", "kind", "group"), default=None)
    if cat is None:
        return _get_choice_label(choice)  # fallback
    return str(cat)


def _get_choice_hours(choice) -> float:
    v = _get_field(choice, ("hours", "hour", "time", "duration", "h"), default=0.0)
    try:
        return float(v)
    except Exception:
        return 0.0


def _set_choice_hours(choice, new_hours: float) -> None:
    _set_field(choice, ("hours", "hour", "time", "duration", "h"), float(new_hours))


def _aggregate_hours_by_category(choices: List[dict]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for c in choices:
        cat = _get_choice_category(c)
        h = max(0.0, _get_choice_hours(c))
        out[cat] = out.get(cat, 0.0) + h
    return out


# -----------------------------
# 대안 시나리오: "A에서 Δh 빼서 B에 더하기"
# choices 구조를 최대한 유지하면서 "시간"만 수정
# -----------------------------
def _reallocate_time_between_categories(
    choices: List[dict],
    reduce_from_cat: str,
    add_to_cat: str,
    delta_h: float,
) -> Tuple[List[dict], float]:
    """
    returns: (new_choices, moved_hours)
    - reduce_from_cat에 속한 choice들의 시간을 합쳐서 delta_h만큼 줄이고
      add_to_cat에 속한 choice(들) 중 첫 번째에 delta_h만큼 더함(없으면 새 choice 생성)
    """
    delta_h = max(0.0, float(delta_h))
    if delta_h <= 0:
        return deepcopy(choices), 0.0

    new_choices = deepcopy(choices)

    # 1) reduce_from_cat에서 뺄 수 있는 시간 계산
    reducible = 0.0
    reduce_idxs = []
    for i, c in enumerate(new_choices):
        if _get_choice_category(c) == reduce_from_cat:
            reduce_idxs.append(i)
            reducible += max(0.0, _get_choice_hours(c))

    moved = min(delta_h, reducible)
    if moved <= 0:
        # 뺄 시간이 없다면 그대로
        return new_choices, 0.0

    # 2) reduce_from_cat의 choices에서 시간을 차감 (뒤에서부터 깎아도 되고, 여기선 순차적으로 깎음)
    remaining = moved
    for i in reduce_idxs:
        if remaining <= 0:
            break
        h = max(0.0, _get_choice_hours(new_choices[i]))
        cut = min(h, remaining)
        _set_choice_hours(new_choices[i], h - cut)
        remaining -= cut

    # 3) add_to_cat에 시간 추가: 해당 범주 choice가 있으면 첫번째에 더하고, 없으면 새로 만든다
    add_idx = None
    for i, c in enumerate(new_choices):
        if _get_choice_category(c) == add_to_cat:
            add_idx = i
            break

    if add_idx is not None:
        h = max(0.0, _get_choice_hours(new_choices[add_idx]))
        _set_choice_hours(new_choices[add_idx], h + moved)
    else:
        # 새로운 선택지 생성(최소 필드만)
        new_choice = {
            "category": add_to_cat,
            "label": f"{add_to_cat} (대안 추가)",
            "hours": moved,
        }
        new_choices.append(new_choice)

    return new_choices, moved


# -----------------------------
# "가능성" 블록: 1시간 재배분 시 가치 변화(가중치 기반)
# -----------------------------
def _shift_gain_per_hour(base_hour_value: float, w_add: float, w_reduce: float) -> float:
    return float(base_hour_value) * (float(w_add) - float(w_reduce))


def render_decision_support_page(s: AppState, discretionary: float, fixed: dict) -> None:
    st.subheader("의사결정 지원")
    st.caption("회고록(사후 가시화) / 대안가치(재배분 비교) 두 모드 중 선택")

    fixed_sum = sum(fixed.values())
    st.write(f"- 필수 시간 합계: **{fixed_sum:.1f}시간**")
    st.write(f"- 선택 가능한 시간(추정): **{discretionary:.1f}시간**")
    st.write(f"- 시간가치 기준: **{krw(s.basis_hour_value)}/시간**")
    st.caption(s.basis_note)

    if not s.choices:
        st.info("선택지(시간 배분)가 아직 없어. 입력 탭에서 추가해줘.")
        return

    mode = st.radio(
        "모드 선택",
        ["회고록 모드", "대안 가치 모드"],
        horizontal=True,
        key="support_mode_radio",  # ✅ 고유 key
    )

    # 공통: 현재 가치 테이블
    df_now = calc_opportunity_cost_table(s.choices, s.basis_hour_value, weights=s.weights)
    total_now = float(df_now["가치환산(원)"].sum()) if not df_now.empty else 0.0

    st.divider()
    st.subheader("현재 시간 배분 (가치 가시화)")
    df_show = df_now.copy()
    if "가치환산(원)" in df_show.columns:
        df_show["가치환산(원)"] = df_show["가치환산(원)"].apply(krw)
    st.dataframe(df_show, use_container_width=True, hide_index=True)
    st.success(f"현재 선택들의 ‘가능성 가치 환산 합계’는 **{krw(total_now)}** 정도로 표현될 수 있어.")

    if mode == "회고록 모드":
        st.divider()
        st.subheader("회고 질문 3개")
        st.write("비교/평가가 아니라 **정리/인식**을 돕는 질문이야.")

        st.text_area("1) 오늘 가장 의미 있었던 선택(순간)은 무엇이었나요?", height=90)
        st.text_area("2) 내일도 유지하고 싶은 선택은 무엇인가요? (이유 포함)", height=90)
        st.text_area("3) 내일 ‘1시간’만 바꿀 수 있다면, 어디에 쓰고 싶나요?", height=90)

        st.markdown(
            "- 이 숫자는 **평가가 아니라 가시화**야.\n"
            "- 휴식도 선택이고 실행도 선택이야. 중요한 건 **내가 지금 어떤 선택을 하고 있는지**를 인식하는 것."
        )
        return

    # -----------------------------
    # 대안 가치 모드
    # -----------------------------
    st.divider()
    st.subheader("대안 가치 모드: 재배분 비교")

    # 범주 후보: s.weights의 키(가장 확실) 우선, 없으면 choices에서 추출
    if isinstance(getattr(s, "weights", None), dict) and len(s.weights) > 0:
        categories = list(s.weights.keys())
    else:
        categories = sorted(_aggregate_hours_by_category(s.choices).keys())

    if len(categories) < 2:
        st.warning("대안 비교를 하려면 범주가 2개 이상 필요해.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        add_to = st.selectbox("늘릴 범주(+)", categories, index=0)
    with col2:
        reduce_from = st.selectbox("줄일 범주(-)", categories, index=min(1, len(categories) - 1))
    with col3:
        delta_h = st.number_input("이동 시간(시간)", min_value=0.0, max_value=24.0, value=1.0, step=0.5)

    alt_choices, moved = _reallocate_time_between_categories(
        s.choices,
        reduce_from_cat=reduce_from,
        add_to_cat=add_to,
        delta_h=delta_h,
    )

    df_alt = calc_opportunity_cost_table(alt_choices, s.basis_hour_value, weights=s.weights)
    total_alt = float(df_alt["가치환산(원)"].sum()) if not df_alt.empty else 0.0
    diff = total_alt - total_now

    cA, cB, cC = st.columns(3)
    cA.metric("현재 가치", f"{total_now:,.0f}원")
    cB.metric("대안 가치", f"{total_alt:,.0f}원")
    cC.metric("차이(대안-현재)", f"{diff:,.0f}원")

    if moved < float(delta_h) and float(delta_h) > 0:
        st.caption(f"※ 줄일 범주({reduce_from})에서 실제로 이동 가능한 시간이 부족해서 **{moved:.1f}시간**만 이동했어.")

    with st.expander("대안 시간 배분 테이블 보기", expanded=False):
        df_alt_show = df_alt.copy()
        if "가치환산(원)" in df_alt_show.columns:
            df_alt_show["가치환산(원)"] = df_alt_show["가치환산(원)"].apply(krw)
        st.dataframe(df_alt_show, use_container_width=True, hide_index=True)

    # -----------------------------
    # 가능성: 1시간 재배분 민감도 (calc.py 기반으로!)
    # -----------------------------
    st.divider()
    st.subheader("가능성: ‘1시간 재배분’ 시 가치 변화(시뮬레이션)")
    st.caption("각 조합마다 실제로 1시간을 옮긴 뒤 다시 계산해서 변화량을 보여줘.")

    hours_by_cat = _aggregate_hours_by_category(s.choices)

    rows: List[Tuple[str, str, float]] = []
    one_hour = 1.0

    for a in categories:
        for r in categories:
            if a == r:
                continue
            if hours_by_cat.get(r, 0.0) <= 0:
                continue  # 줄일 수 있는 시간이 없으면 제외

            sim_choices, moved = _reallocate_time_between_categories(
                s.choices,
                reduce_from_cat=r,
                add_to_cat=a,
                delta_h=one_hour,
            )
            if moved <= 0:
                continue

            df_sim = calc_opportunity_cost_table(sim_choices, s.basis_hour_value, weights=s.weights)
            total_sim = float(df_sim["가치환산(원)"].sum()) if not df_sim.empty else 0.0
            gain = total_sim - total_now
            rows.append((a, r, gain))

    if not rows:
        st.write("- 현재 시간 분포상 ‘줄일 수 있는 범주’가 부족해서 조합을 만들기 어려워.")
        return

    rows.sort(key=lambda x: x[2], reverse=True)

    top_n = st.slider("표시할 조합 개수", min_value=3, max_value=min(30, len(rows)), value=min(10, len(rows)))
    for i, (a, r, gain) in enumerate(rows[:top_n], start=1):
        if gain > 0:
            st.write(f"{i}. **{r} 1h → {a} 1h** : **+{gain:,.0f}원**")
        elif gain < 0:
            st.write(f"{i}. **{r} 1h → {a} 1h** : **{gain:,.0f}원**")
        else:
            st.write(f"{i}. **{r} 1h → {a} 1h** : 변화 없음")

    best_a, best_r, best_gain = rows[0]
    if best_gain > 0:
        st.success(f"**{best_r} → {best_a} (1시간)** 이동이 **약 +{best_gain:,.0f}원**로 가장 커.")
    else:
        st.info("큰 이득이 나는 1시간 재배분이 뚜렷하지 않아.")