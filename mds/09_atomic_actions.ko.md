# Lesson 09  -  Atomic Steps & Safe Execution
# 레슨 09 - 원자적 단계와 안전한 실행

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How do I make plans safe and predictable?"**
**"계획을 어떻게 안전하고 예측 가능하게 만들 수 있을까?"**

Plan steps like "Write article" are vague and hard to validate. Atomic actions break steps into the smallest possible, well-defined operations that can be validated and executed safely.
> "글쓰기" 같은 계획 단계는 모호해서 검증하기 어렵습니다. 원자적 행동(atomic actions)은 단계를 가능한 한 가장 작고 명확하게 정의된 연산으로 쪼개서, 안전하게 검증하고 실행할 수 있게 합니다.

## What You Will Build
## 무엇을 만들게 되나요?

An atomic action system that:
- Converts vague plan steps into specific, typed actions
- Validates actions before execution
- Uses schemas to ensure correct parameters
- Makes execution predictable and debuggable

> 다음을 수행하는 원자적 행동 시스템을 만듭니다:
> - 모호한 계획 단계를 구체적이고 타입이 있는 행동으로 변환한다
> - 실행 전에 행동을 검증한다
> - 스키마를 사용해 올바른 파라미터를 보장한다
> - 실행을 예측 가능하고 디버깅하기 쉽게 만든다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Atomicity
### 1. 원자성(Atomicity)

**Atomicity** means breaking actions into the smallest possible units. Instead of "Write article," you get "generate_text" with specific parameters like topic and length.
> **원자성**이란 행동을 가능한 가장 작은 단위로 쪼개는 것을 뜻합니다. "글쓰기" 대신, topic과 length 같은 구체적인 파라미터를 가진 "generate_text"를 얻게 됩니다.

Atomic actions are indivisible - they either succeed completely or fail completely, with no partial states.
> 원자적 행동은 더 이상 나눌 수 없습니다 — 완전히 성공하거나 완전히 실패할 뿐, 중간 상태는 없습니다.

### 2. Determinism
### 2. 결정성(Determinism)

**Determinism** means predictable outcomes. Given the same atomic action with the same inputs, you should get similar results (accounting for LLM randomness).
> **결정성**이란 예측 가능한 결과를 의미합니다. 같은 입력으로 같은 원자적 행동을 실행하면 (LLM의 무작위성을 감안하더라도) 비슷한 결과를 얻어야 합니다.

Atomic actions make execution deterministic by removing ambiguity.
> 원자적 행동은 모호함을 제거함으로써 실행을 결정적으로 만듭니다.

### 3. Typed Execution
### 3. 타입이 있는 실행(Typed Execution)

**Typed execution** means actions have validated schemas. Each action specifies:
- Action name (e.g., "generate_text")
- Required inputs (e.g., {"topic": string, "length": string})
- Validation rules

> **타입이 있는 실행**이란 행동이 검증된 스키마를 가진다는 뜻입니다. 각 행동은 다음을 명시합니다:
> - 행동 이름 (예: "generate_text")
> - 필요한 입력 (예: {"topic": string, "length": string})
> - 검증 규칙

This catches errors before execution.
> 이는 실행 전에 오류를 잡아냅니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No dependency handling between actions ([Lesson 10](10_atom_of_thought.md))
- No parallel execution
- No action execution implementation - just conversion and validation

> - 행동 간의 의존관계 처리는 다루지 않음 ([레슨 10](10_atom_of_thought.md))
> - 병렬 실행은 다루지 않음
> - 행동의 실제 실행 구현은 다루지 않음 - 변환과 검증만 다룸

## The Code
## 코드

Look at `agent/planner.py`, see `create_atomic_action()` function:
> `agent/planner.py`의 `create_atomic_action()` 함수를 살펴보세요:

```python
def create_atomic_action(llm: LocalLLM, step: str) -> dict | None:
    """
    Convert a plan step into an atomic action.
    
    Used in: Lesson 09
    
    Args:
        llm: The language model to use
        step: A step from a plan
        
    Returns:
        Atomic action as a dictionary, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Convert this step into an atomic action. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{
  "action": "action_name",
  "inputs": {{"key": "value"}}
}}

The action should be a simple, atomic operation name.
The inputs should be a dictionary with the parameters needed for this action.

Step to convert:
{step}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        action = extract_json_from_text(response)
        
        if action and "action" in action:
            return action
    
    return None
```

And in `agent/agent.py`:
> 그리고 `agent/agent.py`에서:

```python
def create_atomic_action(self, step: str) -> dict | None:
    """
    Convert a plan step into an atomic action.
    
    Lesson 09 version.
    
    Args:
        step: A step from a plan (e.g., "Write an explanation of AI agents")
        
    Returns:
        Atomic action dictionary with "action" and "inputs", or None if generation failed
    """
    return create_atomic_action(self.llm, step)
```

Notice:
- **Step conversion** - Vague steps become specific actions with parameters
- **Schema validation** - Actions must have "action" and "inputs" fields
- **Structured output** - Uses the same JSON pattern from previous lessons
- **Retry logic** - Multiple attempts to get valid atomic actions

> 다음을 확인하세요:
> - **단계 변환** - 모호한 단계가 파라미터를 가진 구체적인 행동이 됨
> - **스키마 검증** - 행동은 반드시 "action"과 "inputs" 필드를 가져야 함
> - **구조화된 출력** - 이전 레슨과 동일한 JSON 패턴을 사용함
> - **재시도 로직** - 유효한 원자적 행동을 얻기 위한 여러 번의 시도

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_09_atomic_actions()` method:
> `complete_example.py`의 `lesson_09_atomic_actions()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# Convert a plan step into an atomic action
step = "Write an explanation of AI agents"
atomic_action = agent.create_atomic_action(step)
print(f"Step: {step}")
print(f"Atomic action: {atomic_action}")

# Example with a step from a plan
plan = agent.create_plan("Create a tutorial about Python")
if plan and "steps" in plan and plan["steps"]:
    first_step = plan["steps"][0]
    atomic_action_from_plan = agent.create_atomic_action(first_step)
    print(f"\nPlan step: {first_step}")
    print(f"Atomic action from plan step: {atomic_action_from_plan}")
```

## Compare to Lesson 08
## 레슨 08과 비교하기

**Lesson 08 (Planning):**
> **레슨 08 (계획 수립):**
```
Goal -> Plan: ["Research topic", "Create outline", "Write draft"]
```
> 목표 -> 계획: ["주제 조사", "개요 작성", "초안 작성"]

Plans are lists of vague step descriptions.
> 계획은 모호한 단계 설명들의 목록입니다.

**Lesson 09 (Atomic Actions):**
> **레슨 09 (원자적 행동):**
```
Step: "Write draft" -> Atomic: {"action": "generate_text", "inputs": {"topic": "...", "length": "..."}}
```
> 단계: "초안 작성" -> 원자적 행동: {"action": "generate_text", "inputs": {"topic": "...", "length": "..."}}

Steps become specific, typed actions with validated parameters.
> 단계들이 검증된 파라미터를 가진, 구체적이고 타입이 있는 행동으로 바뀝니다.

## Key Insights
## 핵심 통찰

### Small Steps = Safe Systems
### 작은 단계 = 안전한 시스템

The smaller the action, the safer the system. Atomic actions are:
- Easier to validate - you can check parameters before execution
- Easier to test - each action can be tested independently
- Easier to debug - failures are isolated to specific actions
- Harder to fail catastrophically - small actions have limited blast radius

> 행동이 작을수록 시스템은 더 안전해집니다. 원자적 행동은:
> - 검증하기 더 쉽습니다 - 실행 전에 파라미터를 확인할 수 있습니다
> - 테스트하기 더 쉽습니다 - 각 행동을 독립적으로 테스트할 수 있습니다
> - 디버깅하기 더 쉽습니다 - 실패가 특정 행동에 국한됩니다
> - 대규모로 실패하기 더 어렵습니다 - 작은 행동은 피해 범위가 제한적입니다

### Vague vs Specific
### 모호함 vs 구체성

"Write article" is vague. "generate_text(topic='AI agents', length='1000 words')" is specific. Specificity enables validation and predictable execution.
> "글쓰기"는 모호합니다. "generate_text(topic='AI 에이전트', length='1000단어')"는 구체적입니다. 구체성은 검증과 예측 가능한 실행을 가능하게 합니다.

### Validation Happens Early
### 검증은 일찍 일어난다

By validating actions before execution, you catch errors early. A plan with invalid actions can be rejected before any work is done.
> 실행 전에 행동을 검증함으로써 오류를 일찍 잡아낼 수 있습니다. 유효하지 않은 행동이 담긴 계획은 어떤 작업도 시작하기 전에 거부될 수 있습니다.

### Building Blocks
### building block (구성 요소)

Atomic actions are building blocks. Complex workflows are built from many simple atomic actions, each validated and safe.
> 원자적 행동은 구성 요소(building block)입니다. 복잡한 워크플로우는 검증되고 안전한 여러 개의 단순한 원자적 행동들로 이루어집니다.

## Common Issues
## 자주 발생하는 문제

**"Atomic action is still vague"**
- Provide clearer instructions in the prompt
- Give examples of good atomic actions
- Consider constraining the action names to a predefined set

> **"원자적 행동이 여전히 모호해요"**
> - 프롬프트에 더 명확한 지시문을 제공하세요
> - 좋은 원자적 행동의 예시를 제공하세요
> - 행동 이름을 미리 정해진 집합으로 제한하는 것을 고려하세요

**"Validation fails"**
- Check that the action has both "action" and "inputs" fields
- Verify the JSON structure is correct
- Consider adding schema validation for inputs

> **"검증이 실패해요"**
> - 행동이 "action"과 "inputs" 필드를 모두 가지고 있는지 확인하세요
> - JSON 구조가 올바른지 확인하세요
> - 입력에 대한 스키마 검증 추가를 고려하세요

**"Conversion fails"**
- Some steps might not map cleanly to atomic actions
- Consider multiple retry attempts (already implemented)
- Provide more context about what makes a good atomic action

> **"변환이 실패해요"**
> - 일부 단계는 원자적 행동으로 깔끔하게 대응되지 않을 수 있습니다
> - 여러 번의 재시도를 고려하세요 (이미 구현되어 있음)
> - 좋은 원자적 행동이 무엇인지에 대해 더 많은 맥락을 제공하세요

## Exercises
## 연습 문제

1. Convert different types of plan steps to atomic actions
2. Compare atomic actions for similar steps
3. Try to validate atomic actions before execution
4. Experiment with different input parameter structures

> 1. 다양한 유형의 계획 단계를 원자적 행동으로 변환해보세요
> 2. 비슷한 단계에 대한 원자적 행동들을 비교해보세요
> 3. 실행 전에 원자적 행동을 검증해보세요
> 4. 다양한 입력 파라미터 구조를 실험해보세요

## What's Next?
## 다음 단계는?

In [Lesson 10](10_atom_of_thought.md), we'll combine planning, atomic actions, and **dependencies** to create execution graphs that can run actions in the correct order and even in parallel.
> [레슨 10](10_atom_of_thought.md)에서는 계획 수립, 원자적 행동, 그리고 **의존관계**를 결합해서, 올바른 순서로 — 심지어 병렬로도 — 행동을 실행할 수 있는 실행 그래프를 만듭니다.

---

**Key Takeaway:** Small steps = safe systems. Atomic actions make execution predictable, debuggable, and safe by breaking vague plans into specific, validated operations.
> **핵심 요약:** 작은 단계 = 안전한 시스템. 원자적 행동은 모호한 계획을 구체적이고 검증된 연산으로 쪼갬으로써 실행을 예측 가능하고, 디버깅하기 쉽고, 안전하게 만듭니다.
