# Lesson 02  -  Giving the Model a Role
# 레슨 02 - 모델에게 역할 부여하기

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"Why does the same model behave differently?"**
**"같은 모델인데 왜 행동이 다르게 나타날까?"**

You've probably noticed that LLMs can act like different personas - technical expert, creative writer, helpful assistant. How does that work?
> LLM이 기술 전문가, 창작 작가, 친절한 비서처럼 서로 다른 페르소나로 행동하는 걸 본 적이 있을 겁니다. 이게 어떻게 가능한 걸까요?

## What You Will Build
## 무엇을 만들게 되나요?

A script that uses **system prompts** to:
- Assign the model a specific role
- Stabilize its behavior
- Control tone and format

> **시스템 프롬프트**를 사용해 다음을 수행하는 스크립트를 만듭니다:
> - 모델에게 특정 역할을 부여한다
> - 모델의 행동을 안정화시킨다
> - 어조와 형식을 제어한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. System Prompts
### 1. 시스템 프롬프트

A **system prompt** is an instruction that shapes how the model responds. It's like giving someone a role before a conversation.
> **시스템 프롬프트**는 모델이 어떻게 응답할지를 형성하는 지시문입니다. 대화를 시작하기 전에 상대에게 역할을 미리 부여하는 것과 비슷합니다.

Example system prompts:
> 시스템 프롬프트 예시:
```
"You are a calm, precise teacher who explains concepts simply."
```
> "당신은 개념을 간단하게 설명하는, 차분하고 정확한 교사입니다."

```
"You are a creative writer who uses vivid imagery."
```
> "당신은 생생한 이미지를 사용하는 창작 작가입니다."

```
"You are a code reviewer who finds bugs and suggests improvements."
```
> "당신은 버그를 찾아내고 개선점을 제안하는 코드 리뷰어입니다."

### 2. Instruction Hierarchy
### 2. 지시문의 위계

Most models understand this hierarchy:
1. **System prompt** - Overall behavior and role
2. **User prompt** - The actual question or request

> 대부분의 모델은 다음과 같은 위계를 이해합니다:
> 1. **시스템 프롬프트** - 전반적인 행동과 역할
> 2. **사용자 프롬프트** - 실제 질문이나 요청

The system prompt has higher "priority" - it guides how the model interprets the user prompt.
> 시스템 프롬프트가 더 높은 "우선순위"를 가지며, 모델이 사용자 프롬프트를 어떻게 해석할지를 이끕니다.

### 3. Behavior Shaping
### 3. 행동 형성하기

Behavior ≠ intelligence. Behavior = instructions.
> 행동 ≠ 지능. 행동 = 지시.

The same model can:
- Be technical or casual (tone)
- Be verbose or concise (length)
- Be creative or factual (style)

All based on the system prompt.

> 같은 모델도 다음과 같이 달라질 수 있습니다:
> - 기술적이거나 캐주얼하게 (어조)
> - 장황하거나 간결하게 (길이)
> - 창의적이거나 사실적으로 (스타일)
>
> 이 모든 것이 시스템 프롬프트에 따라 결정됩니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No structured outputs ([Lesson 03](03_structured_output.md))
- No decisions ([Lesson 04](04_decision_making.md))
- No tools ([Lesson 05](05_tools.md))
- No memory ([Lesson 07](07_memory.md))

> - 구조화된 출력은 다루지 않음 ([레슨 03](03_structured_output.md))
> - 의사결정은 다루지 않음 ([레슨 04](04_decision_making.md))
> - 도구(tools)는 다루지 않음 ([레슨 05](05_tools.md))
> - 메모리는 다루지 않음 ([레슨 07](07_memory.md))

## The Code
## 코드

Look at `agent/agent.py`, see `generate_with_role()` method:
> `agent/agent.py`의 `generate_with_role()` 메서드를 살펴보세요:

```python
def generate_with_role(self, user_input: str) -> str:
    """
    Generate with a system prompt to shape behavior.
    """
    # Use a format that doesn't confuse the model
    prompt = f"""{self.system_prompt}

User: {user_input}
Assistant:"""
    
    response = self.llm.generate(prompt)
    # Clean up any potential tag artifacts
    response = response.replace('<SYSTEM>', '').replace('</SYSTEM>', '')
    response = response.replace('<USER>', '').replace('</USER>', '')
    return response.strip()
```

Notice we've added:
- The system prompt at the beginning
- A simple "User:" / "Assistant:" format for the conversation
- Cleanup code to remove any tag artifacts that might appear

> 다음이 추가된 것을 확인하세요:
> - 맨 앞에 붙는 시스템 프롬프트
> - 대화를 위한 단순한 "User:" / "Assistant:" 포맷
> - 나타날 수 있는 태그 잔여물을 제거하는 정리 코드

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_02_with_role()` method:
> `complete_example.py`의 `lesson_02_with_role()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# The agent has a default system prompt:
# "You are a calm, precise, and helpful AI assistant..."

response = agent.generate_with_role("What is an AI agent?")
print(response)
```

## Compare to Lesson 01
## 레슨 01과 비교하기

**Without system prompt ([Lesson 01](01_basic_llm_chat.md)):**
> **시스템 프롬프트가 없을 때 ([레슨 01](01_basic_llm_chat.md)):**
```
Input: "What is an AI agent?"
Output: "An AI agent is a system that perceives its environment and acts autonomously to achieve specified goals. It processes information, makes decisions, and can adapt to changing conditions using machine learning algorithms..."
```
> 입력: "AI 에이전트란 무엇인가?"
> 출력: "AI 에이전트는 환경을 인식하고 지정된 목표를 달성하기 위해 자율적으로 행동하는 시스템입니다. 정보를 처리하고, 의사결정을 내리며, 머신러닝 알고리즘을 사용해 변화하는 상황에 적응할 수 있습니다..."

**With system prompt:**
> **시스템 프롬프트가 있을 때:**
```
Input: "What is an AI agent?"
Output: "Think of an AI agent as a helpful assistant that can observe what's happening around it and take actions to help you accomplish tasks. Like how a thermostat watches the temperature and adjusts heating automatically - but much more sophisticated."
```
> 입력: "AI 에이전트란 무엇인가?"
> 출력: "AI 에이전트를 주변 상황을 관찰하고 여러분의 작업 수행을 돕는 행동을 취하는 친절한 비서라고 생각해보세요. 온도조절기가 온도를 감시하고 자동으로 난방을 조절하는 것과 비슷하지만, 훨씬 더 정교합니다."

Same question. Same model. Different behavior.
> 같은 질문. 같은 모델. 다른 행동.

## The Power of System Prompts
## 시스템 프롬프트의 힘

### Example 1: Technical Expert
### 예시 1: 기술 전문가
```python
agent.system_prompt = "You are a senior software engineer who explains concepts with code examples."
```
> "당신은 코드 예시를 통해 개념을 설명하는 시니어 소프트웨어 엔지니어입니다."

### Example 2: ELI5 (Explain Like I'm 5)
### 예시 2: ELI5 (다섯 살 아이에게 설명하듯)
```python
agent.system_prompt = "You explain complex topics using simple words and everyday analogies."
```
> "당신은 쉬운 단어와 일상적인 비유를 사용해 복잡한 주제를 설명합니다."

### Example 3: Concise Responder
### 예시 3: 간결한 응답자
```python
agent.system_prompt = "You give accurate answers in 1-2 sentences maximum. No elaboration unless asked."
```
> "당신은 최대 1~2문장으로 정확한 답변을 제공합니다. 요청이 없는 한 부연 설명을 하지 않습니다."

## Key Insights
## 핵심 통찰

### Behavior is Configurable
### 행동은 설정 가능하다

You're not changing the model - you're changing the **constraints** on its output. The model still predicts tokens; the system prompt just shifts probabilities.
> 모델 자체를 바꾸는 것이 아니라, 출력에 대한 **제약 조건**을 바꾸는 것입니다. 모델은 여전히 토큰을 예측할 뿐이며, 시스템 프롬프트는 그 확률을 이동시킬 뿐입니다.

### Consistency Improves
### 일관성이 향상된다

Without a system prompt, the model might be:
- Formal one response, casual the next
- Verbose sometimes, terse other times
- Inconsistent in tone

A system prompt creates **behavioral consistency**.

> 시스템 프롬프트가 없으면 모델은 다음처럼 될 수 있습니다:
> - 이번엔 격식체, 다음엔 캐주얼한 어조
> - 어떤 때는 장황하고, 어떤 때는 짧게
> - 일관성 없는 톤
>
> 시스템 프롬프트는 **행동의 일관성**을 만들어냅니다.

### Still Probabilistic
### 여전히 확률적이다

Even with a system prompt, responses vary. But they vary **within the constraints** you set.
> 시스템 프롬프트가 있어도 응답은 여전히 달라집니다. 다만 여러분이 설정한 **제약 범위 안에서** 달라질 뿐입니다.

## Common System Prompt Patterns
## 자주 쓰이는 시스템 프롬프트 패턴

### 1. Role Definition
### 1. 역할 정의
```
You are a [role] who [behavior].
```
> "당신은 [행동]을(를) 하는 [역할]입니다."

### 2. Constraint Setting
### 2. 제약 조건 설정
```
You must [requirement]. You never [prohibition].
```
> "당신은 반드시 [요구사항]을(를) 해야 합니다. 절대 [금지사항]을(를) 하지 않습니다."

### 3. Output Format
### 3. 출력 형식
```
Always respond with [format]. Use [style].
```
> "항상 [형식]으로 응답하세요. [스타일]을(를) 사용하세요."

### 4. Combination
### 4. 조합
```
You are a helpful assistant. 
You explain concepts clearly using examples.
You keep responses under 100 words unless asked to elaborate.
```
> "당신은 친절한 비서입니다.
> 예시를 사용해 개념을 명확하게 설명합니다.
> 부연 설명 요청이 없는 한 응답을 100단어 이내로 유지합니다."

## Common Issues
## 자주 발생하는 문제

**"The model ignores my system prompt"**
- Some models follow system prompts better than others
- Try being more explicit and specific
- Use stronger language ("You MUST..." instead of "Try to...")

> **"모델이 시스템 프롬프트를 무시해요"**
> - 모델마다 시스템 프롬프트를 따르는 정도가 다릅니다
> - 더 명시적이고 구체적으로 작성해보세요
> - 더 강한 표현을 쓰세요 ("Try to..." 대신 "You MUST...")

**"Responses are still inconsistent"**
- This is normal - LLMs are probabilistic
- Lower the `temperature` for more consistency
- We'll add validation in [Lesson 03](03_structured_output.md)

> **"응답이 여전히 일관성이 없어요"**
> - 정상입니다 — LLM은 확률적으로 동작합니다
> - `temperature`를 낮추면 일관성이 높아집니다
> - [레슨 03](03_structured_output.md)에서 검증(validation)을 추가할 것입니다

**"The system prompt is too long"**
- Keep it under 100-200 words
- More tokens = less room for user input + response

> **"시스템 프롬프트가 너무 길어요"**
> - 100~200단어 이내로 유지하세요
> - 토큰이 많아질수록 사용자 입력과 응답에 쓸 여유가 줄어듭니다

## Exercises
## 연습 문제

1. Try different system prompts and observe behavior changes
2. Create a system prompt that makes responses extremely concise
3. Create a system prompt that makes responses highly detailed
4. Experiment with conflicting instructions (what wins?)

> 1. 다양한 시스템 프롬프트를 시도하며 행동 변화를 관찰해보세요
> 2. 응답을 극도로 간결하게 만드는 시스템 프롬프트를 작성해보세요
> 3. 응답을 매우 상세하게 만드는 시스템 프롬프트를 작성해보세요
> 4. 서로 충돌하는 지시를 넣어 실험해보세요 (어느 쪽이 이길까요?)

## What's Next?
## 다음 단계는?

In [Lesson 03](03_structured_output.md), we'll add **structured outputs** to make responses reliable and parseable. Instead of free text, we'll get validated JSON.
> [레슨 03](03_structured_output.md)에서는 응답을 신뢰할 수 있고 파싱 가능하게 만들기 위해 **구조화된 출력**을 추가합니다. 자유 텍스트 대신 검증된 JSON을 받게 됩니다.

---

**Key Takeaway:** Behavior is not intelligence. It's constraints. System prompts turn a general model into a specific assistant.
> **핵심 요약:** 행동은 지능이 아닙니다. 제약 조건입니다. 시스템 프롬프트는 범용 모델을 특정한 비서로 바꿔줍니다.
