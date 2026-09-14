# Lesson 04  -  Decision Making with LLMs
# 레슨 04 - LLM으로 의사결정하기

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"Can the model decide what to do, not just answer?"**
**"모델이 단순히 답하는 것을 넘어, 무엇을 할지 스스로 결정할 수 있을까?"**

This is the first moment of **agency**. Instead of responding with generated text, the model chooses actions from a finite set of options.
> 이것이 처음으로 등장하는 **행위 주체성(agency)**의 순간입니다. 모델이 텍스트를 생성해 응답하는 대신, 정해진 선택지 중에서 행동을 고릅니다.

## What You Will Build
## 무엇을 만들게 되나요?

A decision-making system that:
- Presents the model with a finite set of choices
- Forces the model to pick exactly one option
- Validates the decision and retries on failure
- Uses the decision to route execution

> 다음을 수행하는 의사결정 시스템을 만듭니다:
> - 모델에게 정해진 선택지 집합을 제시한다
> - 모델이 정확히 하나의 옵션을 고르도록 강제한다
> - 결정을 검증하고 실패하면 재시도한다
> - 그 결정으로 실행 흐름을 분기(route)한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Decision Schemas
### 1. 의사결정 스키마(Decision Schemas)

A **decision schema** is a finite set of choices the model must pick from. Instead of generating free text, the model selects from predefined actions like "answer_question", "summarize_text", or "translate".
> **의사결정 스키마**는 모델이 반드시 그중에서 골라야 하는, 정해진 선택지 집합입니다. 자유 텍스트를 생성하는 대신, 모델은 "answer_question", "summarize_text", "translate"처럼 미리 정의된 행동 중 하나를 선택합니다.

This constrains the output space dramatically - instead of infinite possible responses, there are only a few valid options.
> 이는 출력 공간을 극적으로 제한합니다 — 무한한 가능성의 응답 대신, 유효한 선택지 몇 개만 존재하게 됩니다.

### 2. Routing Logic
### 2. 라우팅 로직(Routing Logic)

Once a decision is made, your code can **route** execution based on it. If the model chooses "summarize_text", you call the summarization function. If it chooses "translate", you call the translation function.
> 결정이 내려지면, 여러분의 코드는 그 결정에 따라 실행을 **분기(route)**할 수 있습니다. 모델이 "summarize_text"를 선택하면 요약 함수를 호출하고, "translate"를 선택하면 번역 함수를 호출하는 식입니다.

This is how agents take different paths based on what they "decide" to do.
> 이것이 바로 에이전트가 스스로 "결정"한 바에 따라 서로 다른 경로를 취하는 방식입니다.

### 3. Intent Detection
### 3. 의도 파악(Intent Detection)

By framing user input as a decision problem, you're doing **intent detection**. The model analyzes what the user wants and maps it to one of your available actions.
> 사용자 입력을 의사결정 문제로 프레이밍함으로써, 여러분은 **의도 파악(intent detection)**을 수행하는 것입니다. 모델은 사용자가 원하는 바를 분석해서 여러분이 제공한 행동 중 하나에 매핑합니다.

This is simpler than trying to parse free text to understand intent.
> 이는 자유 텍스트를 파싱해서 의도를 파악하려는 것보다 훨씬 단순합니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No tools ([Lesson 05](05_tools.md))
- No agent loop ([Lesson 06](06_agent_loop.md))
- No memory ([Lesson 07](07_memory.md))
- No planning ([Lesson 08](08_planning.md))

> - 도구(tools)는 다루지 않음 ([레슨 05](05_tools.md))
> - 에이전트 루프는 다루지 않음 ([레슨 06](06_agent_loop.md))
> - 메모리는 다루지 않음 ([레슨 07](07_memory.md))
> - 계획 수립(planning)은 다루지 않음 ([레슨 08](08_planning.md))

## The Code
## 코드

Look at `agent/agent.py`, see `decide()` method:
> `agent/agent.py`의 `decide()` 메서드를 살펴보세요:

```python
def decide(self, user_input: str, choices: list[str]) -> str | None:
    """
    Make the model choose from a finite set of options.
    
    Lesson 04 version.
    
    Args:
        user_input: The input to make a decision about
        choices: List of possible actions/decisions
        
    Returns:
        The chosen action or None if decision failed
    """
    options = "\n".join(f"- {choice}" for choice in choices)
    
    prompt = f"""{self.system_prompt}

You must choose ONE of the following options. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Available choices:
{options}

Required JSON format:
{{"decision": "one_of_the_choices_above"}}

User request: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "decision" in parsed:
            decision = parsed["decision"]
            if decision in choices:
                return decision
    
    return None
```

Notice we've added:
- **Finite choice space** - The model must pick from a predefined list, not generate anything
- **Validation** - We check that the decision is actually in the list of choices
- **Structured output** - Using the same JSON extraction pattern from Lesson 03
- **Retry logic** - Up to 3 attempts to get a valid decision

> 다음이 추가된 것을 확인하세요:
> - **유한한 선택 공간** - 모델은 무언가를 생성하는 게 아니라 미리 정해진 목록에서 골라야 함
> - **검증** - 결정된 값이 실제로 선택지 목록 안에 있는지 확인
> - **구조화된 출력** - 레슨 03과 동일한 JSON 추출 패턴 사용
> - **재시도 로직** - 유효한 결정을 얻기 위해 최대 3번 시도

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_04_decisions()` method:
> `complete_example.py`의 `lesson_04_decisions()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

decision = agent.decide(
    "Can you summarize this article for me?",
    choices=["answer_question", "summarize_text", "translate"]
)

print(decision)
# Output: "summarize_text"
```

## Compare to Lesson 03
## 레슨 03과 비교하기

**Lesson 03 (Structured Output):**
> **레슨 03 (구조화된 출력):**
```
Input: "What is AI?"
Output: {"answer": "AI is...", "confidence": "high"}
```
> 입력: "AI란 무엇인가?"
> 출력: {"answer": "AI는...", "confidence": "high"}

The model generates structured data with values it creates.
> 모델이 스스로 만들어낸 값을 담아 구조화된 데이터를 생성합니다.

**Lesson 04 (Decision Making):**
> **레슨 04 (의사결정):**
```
Input: "Summarize this article"
Choices: ["answer_question", "summarize_text", "translate"]
Output: "summarize_text"
```
> 입력: "이 글을 요약해줘"
> 선택지: ["answer_question", "summarize_text", "translate"]
> 출력: "summarize_text"

The model selects from predefined options - no generation, just selection.
> 모델이 미리 정해진 옵션 중에서 고를 뿐, 생성이 아니라 선택만 합니다.

## Key Insights
## 핵심 통찰

### Selection vs Generation
### 선택 vs 생성

The model is no longer generating content - it's **selecting from a finite action space**. This is fundamentally different and much more predictable than free-text generation.
> 모델은 더 이상 콘텐츠를 생성하지 않습니다 — **유한한 행동 공간에서 선택**할 뿐입니다. 이는 자유 텍스트 생성과는 근본적으로 다르며, 훨씬 더 예측 가능합니다.

### Agency Begins Here
### 행위 주체성은 여기서 시작된다

This is where the agent starts to feel "agent-like". It's not just responding - it's choosing what to do. The choices might be simple, but the pattern is important.
> 바로 이 지점부터 에이전트가 "에이전트답게" 느껴지기 시작합니다. 단순히 응답하는 게 아니라 무엇을 할지 스스로 고르는 것입니다. 선택 자체는 단순할 수 있지만, 이 패턴이 중요합니다.

### Constrained = Reliable
### 제약이 곧 신뢰성이다

By limiting choices to a small, well-defined set, you make the system more reliable. The model can't hallucinate new actions - it must pick from your list.
> 선택지를 작고 명확하게 정의된 집합으로 제한함으로써 시스템의 신뢰성이 높아집니다. 모델은 새로운 행동을 지어낼(hallucinate) 수 없으며, 반드시 여러분이 정한 목록에서 골라야 합니다.

### Validation is Critical
### 검증이 결정적으로 중요하다

Always validate that the decision is actually in your choices list. The model might return something that looks like a decision but isn't in your allowed set.
> 결정된 값이 실제로 선택지 목록 안에 있는지 항상 검증하세요. 모델이 결정처럼 보이지만 허용된 집합에는 없는 값을 반환할 수도 있습니다.

## Common Issues
## 자주 발생하는 문제

**"The model returns a choice not in my list"**
- Validate against the choices list (the code does this)
- Make your choice names clear and unambiguous
- Consider adding a retry with more explicit instructions

> **"모델이 제 목록에 없는 선택지를 반환해요"**
> - 선택지 목록과 대조해서 검증하세요 (코드가 이미 이렇게 처리합니다)
> - 선택지 이름을 명확하고 모호하지 않게 만드세요
> - 더 명시적인 지시문으로 재시도를 추가하는 것도 고려하세요

**"All decisions seem random"**
- Check that your choices are semantically distinct
- Make sure the user input actually relates to the choices
- Lower temperature further for more deterministic selection

> **"모든 결정이 무작위처럼 보여요"**
> - 선택지들이 의미상 서로 뚜렷이 구분되는지 확인하세요
> - 사용자 입력이 선택지와 실제로 관련이 있는지 확인하세요
> - temperature를 더 낮춰 더 결정적인 선택을 유도하세요

**"The model adds explanations"**
- The `extract_json_from_text()` helper handles this
- Stronger instructions help (already in the code)
- Consider rejecting responses with extra text

> **"모델이 설명을 덧붙여요"**
> - `extract_json_from_text()` 헬퍼가 이를 처리합니다
> - 더 강한 지시문이 도움이 됩니다 (코드에 이미 반영됨)
> - 불필요한 텍스트가 섞인 응답을 거부하는 것도 고려하세요

## Exercises
## 연습 문제

1. Create a decision with 5+ choices and test different inputs
2. Try ambiguous inputs and see which choice the model picks
3. Add a "none_of_the_above" choice and see when it's selected
4. Compare decisions with temperature 0.0 vs 0.5

> 1. 선택지가 5개 이상인 의사결정을 만들고 다양한 입력으로 테스트해보세요
> 2. 모호한 입력을 시도해서 모델이 어떤 선택지를 고르는지 관찰해보세요
> 3. "none_of_the_above"(해당 없음) 선택지를 추가하고 언제 선택되는지 확인해보세요
> 4. temperature 0.0과 0.5일 때의 결정을 비교해보세요

## What's Next?
## 다음 단계는?

In [Lesson 05](05_tools.md), we'll introduce **tools** - capabilities the agent can request to extend beyond text generation.
> [레슨 05](05_tools.md)에서는 **도구(tools)**를 소개합니다 — 에이전트가 텍스트 생성을 넘어 요청할 수 있는 능력입니다.

---

**Key Takeaway:** Decisions = agency. Agents choose, not just respond. Constraining choices makes behavior predictable.
> **핵심 요약:** 결정 = 행위 주체성. 에이전트는 응답만 하는 것이 아니라 선택합니다. 선택지를 제약하면 행동이 예측 가능해집니다.
