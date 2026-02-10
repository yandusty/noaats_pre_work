# 격언, 문구
import random
from typing import List


def get_quotes() -> List[str]:
    return [
        "당신의 시간 가치는 숫자로만 정의되지 않는다.",
        "쉬는 것도 선택이다. 선택에는 무게가 있다.",
        "오늘의 한 시간이 미래의 방향을 만든다.",
        "비교는 사람 대신 선택을 대상으로 하자.",
        "완벽한 계획보다, 가능한 한 걸음.",
    ]
# 이부분은 생성형 ai의 도움을 받던지, 그냥 유명한 격언으로 채워도 가능.

def pick_quote() -> str:
    return random.choice(get_quotes())
