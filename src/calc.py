# opportunity_cost.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd

from .models import ChoiceBlock, TimeBasics


def krw(x: float) -> str:
    try:
        return f"{x:,.0f}원"
    except Exception:
        return f"{x}원"


def _clamp_nonneg(x: Any, default: float = 0.0) -> float:
    """None/문자/이상치가 들어와도 안전하게 0 이상 float로 정리."""
    try:
        v = float(x)
    except Exception:
        v = float(default)
    return max(0.0, v)


def _clamp_01(x: Any, default: float = 1.0) -> float:
    """확률용: 0~1로 클램프."""
    try:
        v = float(x)
    except Exception:
        v = float(default)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def calc_discretionary_hours(basics: TimeBasics) -> Tuple[float, Dict[str, float]]:
    fixed = {
        "수면": _clamp_nonneg(getattr(basics, "sleep_h", 0.0)),
        "식사": _clamp_nonneg(getattr(basics, "meals_h", 0.0)),
        "위생/용변/정리": _clamp_nonneg(getattr(basics, "hygiene_h", 0.0)),
        "이동": _clamp_nonneg(getattr(basics, "commute_h", 0.0)),
        "필수 집안일": _clamp_nonneg(getattr(basics, "chores_h", 0.0)),
    }
    fixed_sum = sum(fixed.values())
    discretionary = 24.0 - fixed_sum
    return discretionary, fixed


@dataclass(frozen=True)
class OCConfig:
    """
    기회비용 환산 설정(옵션)
    - alpha: 활동/선택 유형별 가중치
    - p_conv: 소득/목표로 전환될 확률(불확실성 반영)
    - multiplier: 제약/마감/컨디션 등의 상태 가중치
    """
    default_alpha: float = 1.0
    default_p_conv: float = 1.0
    default_multiplier: float = 1.0

    # label(선택 이름) 기준으로 덮어쓰기 하고 싶을 때 사용
    alpha_by_label: Optional[Dict[str, float]] = None
    p_conv_by_label: Optional[Dict[str, float]] = None
    multiplier_by_label: Optional[Dict[str, float]] = None


def _get_choice_factor(
    c: ChoiceBlock,
    key: str,
    *,
    label: str,
    override: Optional[Dict[str, float]],
    default_value: float,
    clamp_fn,
) -> float:
    """
    우선순위:
    1) override dict[label]
    2) ChoiceBlock.<key> 속성값
    3) default_value
    """
    if override and label in override:
        return clamp_fn(override[label], default_value)
    if hasattr(c, key):
        return clamp_fn(getattr(c, key), default_value)
    return clamp_fn(default_value, default_value)


def sum_choice_hours(choices: List[ChoiceBlock]) -> float:
    return float(sum(_clamp_nonneg(getattr(c, "hours", 0.0)) for c in choices))

def weight_to_alpha(weight: int, mode: str = "ratio") -> float:
    """
    weight(0~100) -> alpha 변환
    mode:
      - "ratio": alpha = w/100 (0~1)
      - "neutral_1": alpha = 0.5 + w/100 (0.5~1.5)  ✅ 추천
    """
    w = max(0, min(100, int(weight)))
    if mode == "ratio":
        return w / 100.0
    # neutral_1
    return 0.5 + (w / 100.0)

def build_alpha_by_label_from_weights(
    weights: Dict[str, int],
    *,
    mode: str = "neutral_1",
    default_weight: int = 50,
) -> Dict[str, float]:
    """
    온보딩 weights(0~100)를 label별 alpha로 변환.
    - mode="neutral_1": 0.5~1.5 (추천: 과격하지 않음)
    - label 누락 시 default_weight(중립 50)로 처리
    """
    alpha_by_label: Dict[str, float] = {}
    for label, w in (weights or {}).items():
        try:
            wi = int(w)
        except Exception:
            wi = default_weight
        alpha_by_label[str(label)] = float(weight_to_alpha(wi, mode=mode))
    return alpha_by_label


def calc_opportunity_cost_table(
    choices: List[ChoiceBlock],
    basis_hour_value: float,
    config: Optional[OCConfig] = None,
    weights: Optional[Dict[str, int]] = None,
    alpha_mode: str = "ratio",
) -> pd.DataFrame:
    """
    기회비용(가능성 가치) 환산표

    기본:
      V = basis_hour_value
      OC = hours * V

    옵션(노아 시나리오 확장):
      V = basis_hour_value * alpha * p_conv * multiplier
      OC = hours * V

    - 활동 자체에 대한 평가/판정은 하지 않는다.
    - '선택으로 전환될 수 있었던 가치'을 숫자로 보여준다.
    """
    cfg = config or OCConfig()

    if weights is not None:
        alpha_by_label = build_alpha_by_label_from_weights(weights, mode=alpha_mode)
        cfg = OCConfig(
            default_alpha=cfg.default_alpha,
            default_p_conv=cfg.default_p_conv,
            default_multiplier=cfg.default_multiplier,
            alpha_by_label=alpha_by_label,
            p_conv_by_label=cfg.p_conv_by_label,
            multiplier_by_label=cfg.multiplier_by_label,
        )

    v0 = _clamp_nonneg(basis_hour_value)

    rows: List[Dict[str, float | str]] = []
    for c in choices:
        label = str(getattr(c, "label", ""))
        h = _clamp_nonneg(getattr(c, "hours", 0.0))

        alpha = _get_choice_factor(
            c,
            "alpha",
            label=label,
            override=cfg.alpha_by_label,
            default_value=cfg.default_alpha,
            clamp_fn=_clamp_nonneg,
        )
        p_conv = _get_choice_factor(
            c,
            "p_conv",
            label=label,
            override=cfg.p_conv_by_label,
            default_value=cfg.default_p_conv,
            clamp_fn=_clamp_01,
        )
        mult = _get_choice_factor(
            c,
            "multiplier",
            label=label,
            override=cfg.multiplier_by_label,
            default_value=cfg.default_multiplier,
            clamp_fn=_clamp_nonneg,
        )

        v_effective = v0 * alpha * p_conv * mult
        oc = h * v_effective

        rows.append(
            {
                "선택": label,
                "시간(시간)": float(h),
                "기준가치(원/시간)": float(v0),
                "alpha": float(alpha),
                "p_conv": float(p_conv),
                "multiplier": float(mult),
                "유효가치(원/시간)": float(v_effective),
                "가치환산(원)": float(oc),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        # 수치형 강제
        num_cols = [
            "시간(시간)",
            "기준가치(원/시간)",
            "alpha",
            "p_conv",
            "multiplier",
            "유효가치(원/시간)",
            "가치환산(원)",
        ]
        for col in num_cols:
            df[col] = df[col].astype(float)
    return df
