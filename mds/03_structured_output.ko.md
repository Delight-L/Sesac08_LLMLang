# Lesson 03  -  Making Output Reliable
# 레슨 03 - 출력을 신뢰할 수 있게 만들기

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How do I stop parsing free-text?"**
**"자유 텍스트를 파싱하는 걸 어떻게 그만둘 수 있을까?"**

Free-text responses are unpredictable. Sometimes the model adds explanations, sometimes it uses different formats, sometimes it hallucinates. We need **structure**.
> 자유 텍스트 응답은 예측하기 어렵습니다. 모델이 설명을 덧붙이기도 하고, 형식이 매번 바뀌기도 하고, 없는 내용을 지어내기(hallucinate)도 합니다. 우리에게는 **구조**가 필요합니다.

## What You Will Build
## 무엇을 만들게 되나요?

A system that:
- Forces JSON output
- Validates the response
- Retries on failure

> 다음을 수행하는 시스템을 만듭니다:
> - JSON 출력을 강제한다
> - 응답을 검증한다
> - 실패하면 재시도한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Output Contracts
### 1. 출력 계약(Output Contracts)

An **output contract** is a specification for what the model must return. Instead of "answer the question," we say "return JSON matching this schema."
> **출력 계약**이란 모델이 반드시 반환해야 하는 형식을 명시한 규격입니다. "질문에 답하라"고 하는 대신, "이 스키마에 맞는 JSON을 반환하라"고 지시합니다.

```json
{
  "answer": string,
  "confidence": "high" | "medium" | "low"
}
```

### 2. Trust Boundaries
### 2. 신뢰 경계(Trust Boundaries)

Never trust LLM output directly. Always:
1. Parse it
2. Validate it
3. Handle failures

> LLM의 출력을 절대 그대로 신뢰하지 마세요. 항상 다음을 거쳐야 합니다:
> 1. 파싱한다
> 2. 검증한다
> 3. 실패를 처리한다

This is the first "engineering" moment - treating the LLM as a fallible component.
> 이것이 처음으로 등장하는 "엔지니어링"의 순간입니다 — LLM을 언제든 실패할 수 있는 하나의 컴포넌트로 취급하는 것입니다.

### 3. Validation
### 3. 검증(Validation)

Validation ensures the output matches your contract:
- Is it valid JSON?
- Does it have required fields?
- Are the values the right type?

> 검증은 출력이 계약(contract)에 부합하는지 확인하는 과정입니다:
> - 유효한 JSON인가?
> - 필수 필드가 있는가?
> - 값의 타입이 올바른가?

## The Code
## 코드

Look at `agent/agent.py`, see `generate_structured()` method:
> `agent/agent.py`의 `generate_structured()` 메서드를 살펴보세요:

```python
def generate_structured(self, user_input: str, schema: str) -> dict | None:
    """
    Generate structured JSON output with validation and retries.
    
    Lesson 03 version.
    
    Args:
        user_input: The user's question or request
        schema: JSON schema description
        
    Returns:
        Parsed JSON dictionary or None if all retries failed
    """
    prompt = f"""{self.system_prompt}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no extra text before or after the JSON
3. Start your response with {{ and end with }}

Schema you must follow:
{schema}

User request: {user_input}

Response (JSON only):"""
    
    # Try up to 3 times
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed is not None:
            return parsed
    
    return None
```

Notice we've added:
- **Strong instructions** - "CRITICAL INSTRUCTIONS" with explicit JSON-only requirements
- **Temperature control** - `temperature=0.0` for more deterministic, consistent output
- **JSON extraction** - `extract_json_from_text()` handles cases where the model adds extra text
- **Retry logic** - Up to 3 attempts to get valid JSON, turning probabilistic behavior into reliable results

> 다음이 추가된 것을 확인하세요:
> - **강한 지시문** - JSON만 출력하라는 명시적 요구사항을 담은 "CRITICAL INSTRUCTIONS"
> - **temperature 제어** - 더 결정적이고 일관된 출력을 위한 `temperature=0.0`
> - **JSON 추출** - `extract_json_from_text()`가 모델이 불필요한 텍스트를 덧붙이는 경우를 처리
> - **재시도 로직** - 유효한 JSON을 얻기 위해 최대 3번 시도하며, 확률적인 동작을 신뢰할 수 있는 결과로 바꿈

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_03_structured()` method:
> `complete_example.py`의 `lesson_03_structured()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

schema = '''
{
  "topic": string,
  "difficulty": "beginner" | "intermediate" | "advanced"
}
'''

result = agent.generate_structured(
    "Explain quantum computing",
    schema
)

print(result)
# {"topic": "'quantum computing", "difficulty": "advanced"}
```

## Why This Matters
## 이것이 중요한 이유

### Before (Free Text)
### 이전 (자유 텍스트)
```
Output: "Okay! This task is medium difficulty. I'd suggest building..."
```
> 출력: "좋아요! 이 작업은 중간 난이도네요. 이렇게 만들어보시길 추천합니다..."

- Can't parse
- Inconsistent
- Unreliable

> - 파싱할 수 없음
> - 일관성이 없음
> - 신뢰할 수 없음

### After (Structured)
### 이후 (구조화됨)
```
Output: {'topic': 'quantum computing', 'difficulty': 'advanced'}
```
- Parseable
- Predictable
- Validated

> - 파싱 가능함
> - 예측 가능함
> - 검증됨

## Key Insights
## 핵심 통찰

### LLMs Are Probabilistic
### LLM은 확률적으로 동작한다

They don't always output valid JSON on the first try. Retries turn probabilistic behavior into reliable behavior.
> 첫 시도에서 항상 유효한 JSON을 출력하는 것은 아닙니다. 재시도는 확률적인 동작을 신뢰할 수 있는 동작으로 바꿔줍니다.

### Structure Beats Cleverness
### 구조가 영리함을 이긴다

A simple prompt with validation beats a clever prompt without it.
> 검증이 있는 단순한 프롬프트가, 검증이 없는 영리한 프롬프트보다 낫습니다.

### This is Engineering
### 이것이 곧 엔지니어링이다

You're treating the LLM as a component in a system:
- Input: prompt + schema
- Output: validated data or error
- Retry: if validation fails

> LLM을 시스템 속 하나의 컴포넌트로 취급하는 것입니다:
> - 입력: 프롬프트 + 스키마
> - 출력: 검증된 데이터 또는 오류
> - 재시도: 검증에 실패했을 때

## Common Issues
## 자주 발생하는 문제

**"The model adds explanations before JSON"**
- Use `extract_json_from_text()` helper (finds JSON in text)
- Emphasize "ONLY valid JSON" in prompt

> **"모델이 JSON 앞에 설명을 덧붙여요"**
> - `extract_json_from_text()` 헬퍼를 사용하세요 (텍스트 속에서 JSON을 찾아냄)
> - 프롬프트에서 "오직 유효한 JSON만"이라는 점을 강조하세요

**"Still getting invalid responses"**
- Lower temperature for more deterministic output
- Be more specific about the schema
- Use models trained for structured output

> **"여전히 유효하지 않은 응답이 나와요"**
> - temperature를 낮춰 더 결정적인 출력을 얻으세요
> - 스키마를 더 구체적으로 명시하세요
> - 구조화된 출력에 특화되어 학습된 모델을 사용하세요

**"Retries use too many tokens"**
- 3 retries is usually enough
- Track retry counts to monitor model quality

> **"재시도가 토큰을 너무 많이 써요"**
> - 보통 3번의 재시도면 충분합니다
> - 재시도 횟수를 추적해서 모델 품질을 모니터링하세요

## What's Next?
## 다음 단계는?

In [Lesson 04](04_decision_making.md), we add **decision making** - the model chooses actions, not just answers questions.
> [레슨 04](04_decision_making.md)에서는 **의사결정**을 추가합니다 — 모델이 단순히 질문에 답하는 것을 넘어 행동을 스스로 선택하게 됩니다.

---

**Key Takeaway:** Structured outputs + validation = reliable agents.
> **핵심 요약:** 구조화된 출력 + 검증 = 신뢰할 수 있는 에이전트.
