# Lesson 01  -  Talking to a Model
# 레슨 01 - 모델과 대화하기

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How do I talk to a language model at all?"**
**"언어 모델과 어떻게 대화를 시작할 수 있을까?"**

This is the absolute foundation. Before we can build agents, we need to understand the simplest possible interaction: text in, text out.
> 이것은 가장 근본적인 출발점입니다. 에이전트를 만들기 전에, 가장 단순한 상호작용 — 텍스트를 넣으면 텍스트가 나오는 것 — 을 먼저 이해해야 합니다.

## What You Will Build
## 무엇을 만들게 되나요?

A minimal interaction that:
- Loads a local LLM
- Sends text to it
- Receives text back

> 다음과 같은 최소한의 상호작용을 만듭니다:
> - 로컬 LLM을 불러온다
> - 텍스트를 모델에 보낸다
> - 텍스트 응답을 받는다

That's it. No magic. No frameworks. Just the basics.
> 이게 전부입니다. 마법도, 프레임워크도 없습니다. 그저 기본기입니다.

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Prompts
### 1. 프롬프트(Prompts)

A **prompt** is just text you send to the model. It can be a question like "What is an AI agent?", an instruction like "Explain quantum computing", or a request like "Write a poem about the ocean". The model completes or responds to this text based on patterns it learned during training.
> **프롬프트**는 모델에 보내는 텍스트일 뿐입니다. "AI 에이전트란 무엇인가?" 같은 질문일 수도, "양자컴퓨팅을 설명해줘" 같은 지시일 수도, "바다에 대한 시를 써줘" 같은 요청일 수도 있습니다. 모델은 학습 과정에서 익힌 패턴을 바탕으로 이 텍스트를 이어쓰거나 응답합니다.

### 2. Tokens
### 2. 토큰(Tokens)

Models don't see text as words - they see **tokens**. Tokens are pieces of text (often words or subwords). For example, "Hello world" might be 2 tokens, while "artificial intelligence" could be 2-4 tokens depending on the model.
> 모델은 텍스트를 단어 단위로 보지 않습니다 — **토큰** 단위로 봅니다. 토큰은 텍스트의 조각(대개 단어나 그보다 작은 단위)입니다. 예를 들어 "Hello world"는 토큰 2개일 수 있고, "artificial intelligence"는 모델에 따라 2~4개의 토큰이 될 수 있습니다.

This matters because models have token limits (context windows), generation is measured in tokens per second, and longer prompts use more tokens, leaving less room for responses.
> 이것이 중요한 이유는, 모델마다 토큰 제한(컨텍스트 윈도우)이 있고, 생성 속도는 초당 토큰 수로 측정되며, 프롬프트가 길수록 더 많은 토큰을 사용해서 응답에 쓸 수 있는 여유가 줄어들기 때문입니다.

### 3. Context
### 3. 컨텍스트(Context)

The **context** is everything the model can "see" at once. It includes your prompt, any previous conversation, and system instructions. Models have a **context window** (e.g., 2048 tokens). If you exceed it, the model can't see the earlier text.
> **컨텍스트**는 모델이 한 번에 "볼 수 있는" 모든 것을 의미합니다. 여기에는 프롬프트, 이전 대화 내용, 시스템 지시사항이 포함됩니다. 모델에는 **컨텍스트 윈도우**(예: 2048 토큰)가 있으며, 이를 초과하면 모델은 앞부분의 텍스트를 더 이상 볼 수 없습니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No system prompts ([Lesson 02](02_system_prompt.md))
- No structured outputs ([Lesson 03](03_structured_output.md))
- No tools ([Lesson 05](05_tools.md))
- No agents ([Lesson 06](06_agent_loop.md))
- No memory ([Lesson 07](07_memory.md))

> - 시스템 프롬프트는 다루지 않음 ([레슨 02](02_system_prompt.md))
> - 구조화된 출력은 다루지 않음 ([레슨 03](03_structured_output.md))
> - 도구(tools)는 다루지 않음 ([레슨 05](05_tools.md))
> - 에이전트는 다루지 않음 ([레슨 06](06_agent_loop.md))
> - 메모리는 다루지 않음 ([레슨 07](07_memory.md))

This lesson is intentionally minimal.
> 이번 레슨은 의도적으로 최소한의 내용만 다룹니다.

## The Code
## 코드

Look at `agent/agent.py`, see `simple_generate()` method:
> `agent/agent.py`의 `simple_generate()` 메서드를 살펴보세요:

```python
def simple_generate(self, user_input: str) -> str:
    """
    Simplest possible interaction - just pass text to the LLM.
    """
    return self.llm.generate(user_input)
```

That's it. One line. No complexity.
> 이게 전부입니다. 단 한 줄. 복잡함은 없습니다.

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_01_basic_chat()` method:
> `complete_example.py`의 `lesson_01_basic_chat()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

response = agent.simple_generate("What is an AI agent?")
print(response)
```

## What's Happening Internally?
## 내부에서는 무슨 일이 일어나나요?

1. Your text is converted to tokens
2. Tokens are sent to the model
3. The model predicts the next token
4. Repeat until a stop condition (end token, max length, etc.)
5. Tokens are converted back to text
6. Text is returned to you

> 1. 입력한 텍스트가 토큰으로 변환됩니다
> 2. 토큰이 모델로 전달됩니다
> 3. 모델이 다음 토큰을 예측합니다
> 4. 종료 조건(종료 토큰, 최대 길이 등)이 될 때까지 이를 반복합니다
> 5. 토큰이 다시 텍스트로 변환됩니다
> 6. 텍스트가 사용자에게 반환됩니다

## Key Insights
## 핵심 통찰

### There is No "Understanding"
### "이해"라는 것은 없다

The model doesn't "understand" your question. Instead, it recognizes patterns in the tokens, predicts likely continuations, and generates probabilistic text. This is important: **models are pattern matchers, not minds.**
> 모델은 여러분의 질문을 "이해"하지 않습니다. 대신 토큰 속의 패턴을 인식하고, 그럴듯한 다음 내용을 예측하며, 확률적으로 텍스트를 생성할 뿐입니다. 이 점이 중요합니다: **모델은 사고하는 정신이 아니라 패턴 매칭 장치입니다.**

### It's Probabilistic
### 확률적으로 작동한다

Run the same prompt twice and you might get different responses. This happens because models use randomness (temperature) in generation, and multiple plausible continuations exist. There's no single "correct" answer - just probabilistic outputs.
> 같은 프롬프트를 두 번 실행해도 다른 응답이 나올 수 있습니다. 이는 모델이 생성 과정에서 무작위성(temperature)을 사용하고, 그럴듯한 다음 내용이 여러 개 존재하기 때문입니다. 단 하나의 "정답"은 없으며, 확률적인 출력만 있을 뿐입니다.

### Text In = Text Out
### 텍스트를 넣으면 텍스트가 나온다

That's all this is. Everything else we build (agents, tools, memory) is built on top of this simple foundation.
> 이게 전부입니다. 앞으로 만들 나머지 모든 것(에이전트, 도구, 메모리)은 이 단순한 토대 위에 쌓아 올려집니다.

## Common Issues
## 자주 발생하는 문제

**"The response is cut off"**
- Increase `max_tokens` in `shared/llm.py`

> **"응답이 중간에 끊겨요"**
> - `shared/llm.py`에서 `max_tokens` 값을 늘리세요

**"The model repeats itself"**
- This is normal for completion models
- We'll fix it with better prompting in [Lesson 02](02_system_prompt.md)

> **"모델이 같은 말을 반복해요"**
> - completion 모델에서는 흔히 있는 일입니다
> - [레슨 02](02_system_prompt.md)에서 더 나은 프롬프팅으로 이를 개선합니다

**"The response doesn't match the prompt"**
- Some models need specific formatting
- We'll add structure in [Lesson 02](02_system_prompt.md) and [Lesson 03](03_structured_output.md)

> **"응답이 프롬프트 내용과 맞지 않아요"**
> - 일부 모델은 특정한 포맷을 필요로 합니다
> - [레슨 02](02_system_prompt.md)와 [레슨 03](03_structured_output.md)에서 구조를 추가할 것입니다

## Exercises
## 연습 문제

1. Try different prompts and observe the responses
2. Change the `temperature` in `shared/llm.py` (0.0 = deterministic, 1.0 = creative)
3. Use `max_tokens` to control response length

> 1. 다양한 프롬프트를 시도하며 응답을 관찰해보세요
> 2. `shared/llm.py`의 `temperature` 값을 바꿔보세요 (0.0 = 결정적, 1.0 = 창의적)
> 3. `max_tokens`로 응답 길이를 조절해보세요

## What's Next?
## 다음 단계는?

In [Lesson 02](02_system_prompt.md), we'll add a **system prompt** to shape the model's behavior. This turns random completions into consistent, useful responses.
> [레슨 02](02_system_prompt.md)에서는 모델의 행동을 다듬기 위한 **시스템 프롬프트**를 추가합니다. 이를 통해 무작위적인 텍스트 생성이 일관되고 유용한 응답으로 바뀝니다.

---

**Key Takeaway:** An LLM is just a text completion engine. Everything we build is structured interaction with this simple mechanism.
> **핵심 요약:** LLM은 그저 텍스트 완성 엔진일 뿐입니다. 우리가 만드는 모든 것은 이 단순한 메커니즘과의 구조화된 상호작용입니다.
