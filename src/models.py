#사용할 데이터 형식 ( 상태/입력 모델 )

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TimeBasics:
    sleep_h: float = 8.0
    meals_h: float = 2.0
    hygiene_h: float = 1.0
    commute_h: float = 0.0
    chores_h: float = 1.0


@dataclass
class ChoiceBlock:
    label: str
    hours: float


@dataclass
class AppState:
    persona_name: str = "노아"
    persona_note: str = (
        "지금은 쉬는 기간. 시간이 공짜처럼 느껴지고 결정을 미루기 쉬움.\n"
        "\n이 앱은 평가/비난을 하지 않고, 선택의 결과(기회비용)를 '보여주는' 데 목적이 있음."
    )

    # ✅ 온보딩 완료 여부
    onboarding_completed: bool = False

    # ✅ “내가 기준으로 삼는 나의 가치 시점”
    value_reference: str = "현재"  # "전성기" | "현재" | "미래"

    # 시간가치 기준(원/시간): v0에서는 사용자 입력만 사용
    basis_hour_value: float = 12000.0
    basis_note: str = "시간가치는 사용자 입력 기준(공식 통계값 아님)."

    # ✅ 핵심 수정: mutable default는 default_factory로
    basics: TimeBasics = field(default_factory=TimeBasics)

    # ✅ 활동 중요도(가중치): 0~100
    # 논문에 따르면 유지 필수활동까지 총 5분류로 사람들의 활동을 범주화 할 수 있다고 한다.
    # alpha 기본값 설정.
    weights: Dict[str, int] = field(
        default_factory=lambda: {
            "생산활동": 80,
            "인적자본 축적": 60,
            "회복,건강,여가": 60,
            "소비성 여가, 저생산 활동": 30,
        }
    )

    # choices는 리스트(가변)이므로 이것도 default_factory 추천
    choices: List[ChoiceBlock] = field(default_factory=list)
