#기회비용 계산 로직
from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd

from .models import ChoiceBlock, TimeBasics


def krw(x: float) -> str:
    try:
        return f"{x:,.0f}원"
    except Exception:
        return f"{x}원"


def calc_discretionary_hours(basics: TimeBasics) -> Tuple[float, Dict[str, float]]:
    fixed = {
        "수면": float(basics.sleep_h),
        "식사": float(basics.meals_h),
        "위생/용변/정리": float(basics.hygiene_h),
        "이동": float(basics.commute_h),
        "필수 집안일": float(basics.chores_h),
    }
    fixed_sum = sum(fixed.values())
    discretionary = 24.0 - fixed_sum
    return discretionary, fixed


def calc_opportunity_cost_table(choices: List[ChoiceBlock], basis_hour_value: float) -> pd.DataFrame:
    """
    기회비용(가능성 가치) 환산표
    - '돈을 잃는다'가 아니라, '다른 선택으로 전환될 수 있었던 가능성'을 숫자로 보여준다.
    - 활동 자체에 대한 평가/판정은 하지 않는다.
    """
    rows = []
    v = max(0.0, float(basis_hour_value))

    for c in choices:
        h = max(0.0, float(c.hours))
        rows.append(
            {
                "선택": c.label,
                "시간(시간)": h,
                "가치환산(원)": h * v,
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        df["시간(시간)"] = df["시간(시간)"].astype(float)
        df["가치환산(원)"] = df["가치환산(원)"].astype(float)
    return df


def sum_choice_hours(choices: List[ChoiceBlock]) -> float:
    return float(sum(max(0.0, float(c.hours)) for c in choices))
