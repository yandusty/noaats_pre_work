# 핵심적인 기능
- 기회비용 계산 로직
- 사용할 데이터 형식
- 사용자들을 위한 격언 (부가적)

---
## 기술 흐름도
[사용자 입력]  
  ├─ (기본 생활 시간) sleep/meals/...  
  ├─ (선택 시간 배분) choice label + hours  
  └─ (시간가치 기준) 원/시간  
        ↓  
[session_state에 저장]  ← src/state.py  
        ↓  
[계산 로직]             ← src/calc.py  
  ├─ 필수시간 합계 계산  
  ├─ 선택가능시간 산출 (24 - 필수합)  
  └─ 선택별 가능성 가치 환산 (hours * 원/시간)  
        ↓  
[표/요약 출력]           ← src/ui/results_page.py  
        ↓
[의사결정 지원 질문 + 격려 문구] ← src/ui/support_page.py, src/quotes.py  
        ↓
[JSON 내보내기(틀)]      ← src/ui/export_page.py  
