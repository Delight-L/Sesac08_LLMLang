# Lesson 05  -  Introducing Tools 
# 레슨 05 - 도구(Tools) 소개하기

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"Can the model ask me to do something?"**
**"모델이 나에게 무언가를 해달라고 요청할 수 있을까?"**

Tools extend the agent's capabilities beyond text generation. Instead of only generating text, the agent can request actions like calculations, API calls, or file operations.
> 도구는 에이전트의 능력을 텍스트 생성 너머로 확장시켜줍니다. 텍스트만 생성하는 대신, 에이전트는 계산, API 호출, 파일 작업 같은 행동을 요청할 수 있습니다.

## What You Will Build
## 무엇을 만들게 되나요?

A tool-calling system that:
- Lets the agent request specific tools with structured parameters
- Validates tool requests before execution
- Separates tool requests from tool execution
- Extends agent capabilities without retraining the model

> 다음을 수행하는 도구 호출 시스템을 만듭니다:
> - 에이전트가 구조화된 파라미터와 함께 특정 도구를 요청하게 한다
> - 실행 전에 도구 요청을 검증한다
> - 도구 요청과 도구 실행을 분리한다
> - 모델을 재학습하지 않고도 에이전트의 능력을 확장한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Tool Interfaces
### 1. 도구 인터페이스(Tool Interfaces)

A **tool interface** is a defined API the agent can request. Tools have names and parameters, like `calculator(a, b, operation)`. The agent requests the tool, but the system executes it.
> **도구 인터페이스**란 에이전트가 요청할 수 있도록 정의된 API입니다. 도구는 `calculator(a, b, operation)`처럼 이름과 파라미터를 가집니다. 에이전트는 도구를 요청할 뿐이고, 실제 실행은 시스템이 담당합니다.

This separation is critical - the agent **describes** what it needs, but you **control** what actually happens.
> 이 분리가 결정적으로 중요합니다 — 에이전트는 필요한 것을 **기술(describe)**할 뿐이고, 실제로 무슨 일이 일어날지는 여러분이 **통제**합니다.

### 2. Structured Tool Calls
### 2. 구조화된 도구 호출(Structured Tool Calls)

Tool calls are **structured JSON specifications** for function calls. The model outputs JSON like `{"tool": "calculator", "arguments": {"a": 42, "b": 7, "operation": "multiply"}}`, and your code validates and executes it.
> 도구 호출은 함수 호출을 위한 **구조화된 JSON 명세**입니다. 모델은 `{"tool": "calculator", "arguments": {"a": 42, "b": 7, "operation": "multiply"}}`와 같은 JSON을 출력하고, 여러분의 코드가 이를 검증하고 실행합니다.

This is similar to Lesson 04's decision making, but instead of choosing an action, the agent is specifying a function call.
> 이는 레슨 04의 의사결정과 비슷하지만, 행동을 선택하는 대신 에이전트가 함수 호출을 명시한다는 점이 다릅니다.

### 3. Model-Chosen Actions
### 3. 모델이 선택하는 행동(Model-Chosen Actions)

The agent decides **which tool to use** and **what parameters to pass**. You define available tools, but the agent chooses which one fits the situation.
> 에이전트는 **어떤 도구를 쓸지**, 그리고 **어떤 파라미터를 넘길지**를 결정합니다. 여러분은 사용 가능한 도구들을 정의하지만, 상황에 맞는 도구를 고르는 것은 에이전트입니다.

This is agency at work - the agent is selecting and configuring actions.
> 이것이 바로 작동 중인 행위 주체성입니다 — 에이전트가 행동을 선택하고 구성하는 것입니다.

## Important Rule
## 중요한 규칙

The model **requests** tools. The system **executes** them. No autonomy yet. This separation gives you control and safety.
> 모델은 도구를 **요청**합니다. 시스템이 이를 **실행**합니다. 아직 자율성은 없습니다. 이 분리가 여러분에게 통제권과 안전성을 부여합니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No agent loop ([Lesson 06](06_agent_loop.md))
- No memory ([Lesson 07](07_memory.md))
- No automatic tool execution - you still manually execute tool calls

> - 에이전트 루프는 다루지 않음 ([레슨 06](06_agent_loop.md))
> - 메모리는 다루지 않음 ([레슨 07](07_memory.md))
> - 자동 도구 실행은 다루지 않음 - 여전히 도구 호출을 수동으로 실행함

## The Code
## 코드

Look at `agent/agent.py`, see `request_tool()` method:
> `agent/agent.py`의 `request_tool()` 메서드를 살펴보세요:

```python
def request_tool(self, user_input: str) -> dict | None:
    """
    Have the model request a tool call.
    
    Lesson 05 version.
    
    Args:
        user_input: The user's request
        
    Returns:
        Tool call specification or None if request failed
    """
    prompt = f"""{self.system_prompt}

You are a tool-calling assistant. When asked a math question, you must respond with ONLY valid JSON.

Available tool: calculator
- Parameters: a (number), b (number), operation ("add", "subtract", "multiply", or "divide")

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Example format:
{{"tool": "calculator", "arguments": {{"a": 42, "b": 7, "operation": "multiply"}}}}

User request: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "tool" in parsed and "arguments" in parsed:
            return parsed
    
    return None

def execute_tool_call(self, tool_call: dict) -> Any:
    """
    Execute a tool call requested by the model.
    
    Args:
        tool_call: Dictionary with "tool" and "arguments"
        
    Returns:
        Result of the tool execution
    """
    return execute_tool(tool_call["tool"], tool_call["arguments"])
```

Notice:
- **Structured output** - The tool call is validated JSON, similar to Lesson 03
- **Validation** - We check that both "tool" and "arguments" are present
- **Separation of concerns** - Request and execution are separate methods
- **Extensibility** - Easy to add new tools without changing the model

> 다음을 확인하세요:
> - **구조화된 출력** - 도구 호출은 레슨 03과 비슷하게 검증된 JSON임
> - **검증** - "tool"과 "arguments"가 둘 다 존재하는지 확인함
> - **관심사의 분리** - 요청과 실행이 서로 다른 메서드로 분리됨
> - **확장성** - 모델을 바꾸지 않고도 새 도구를 쉽게 추가할 수 있음

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_05_tools()` method:
> `complete_example.py`의 `lesson_05_tools()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

tool_call = agent.request_tool("What is 42 * 7?")
print(f"Tool request: {tool_call}")

if tool_call:
    result = agent.execute_tool_call(tool_call)
    print(f"Tool result: {result}")
```

![Tool Calling Flow](diagrams/lesson-05-tool-calling.png)

## Compare to Lesson 04
## 레슨 04와 비교하기

**Lesson 04 (Decision Making):**
> **레슨 04 (의사결정):**
```
Input: "What should I do?"
Choices: ["answer", "calculate", "translate"]
Output: "calculate"
```
> 입력: "내가 뭘 해야 할까?"
> 선택지: ["answer", "calculate", "translate"]
> 출력: "calculate"

The agent picks from a list of actions.
> 에이전트가 행동 목록 중에서 고릅니다.

**Lesson 05 (Tool Calling):**
> **레슨 05 (도구 호출):**
```
Input: "What is 42 * 7?"
Tool: calculator
Arguments: {"a": 42, "b": 7, "operation": "multiply"}
Result: 294
```
> 입력: "42 * 7은 얼마인가?"
> 도구: calculator
> 인자: {"a": 42, "b": 7, "operation": "multiply"}
> 결과: 294

The agent specifies a tool call with parameters and gets a result.
> 에이전트는 파라미터와 함께 도구 호출을 명시하고 결과를 받습니다.

## Key Insights
## 핵심 통찰

### Tools Are Interfaces, Not Abilities
### 도구는 능력이 아니라 인터페이스다

The agent doesn't have the ability - you do. The agent describes what it needs through a structured interface, and you provide the implementation. This keeps you in control.
> 에이전트에게 그 능력이 있는 게 아니라, 여러분에게 있는 것입니다. 에이전트는 구조화된 인터페이스를 통해 필요한 것을 기술할 뿐이고, 실제 구현은 여러분이 제공합니다. 이 덕분에 통제권은 여러분에게 남습니다.

### No Retraining Required
### 재학습이 필요 없다

To add new capabilities, you add new tools. The model doesn't need retraining - it just needs to understand the tool interface. This is powerful.
> 새로운 능력을 추가하려면 새로운 도구를 추가하면 됩니다. 모델을 재학습할 필요는 없습니다 — 도구 인터페이스를 이해하기만 하면 됩니다. 이것이 강력한 점입니다.

### Safety Through Separation
### 분리를 통한 안전성

By separating tool requests from execution, you can validate, log, and control what actually happens. The agent can't execute dangerous operations without your code allowing it.
> 도구 요청과 실행을 분리함으로써, 실제로 무슨 일이 일어나는지 검증하고 로그를 남기고 통제할 수 있습니다. 여러분의 코드가 허용하지 않는 한 에이전트는 위험한 작업을 실행할 수 없습니다.

### Structured = Reliable
### 구조화 = 신뢰성

Using the same structured JSON pattern from Lessons 03 and 04 makes tool calls reliable and parseable. The model outputs structured data, you validate it, then execute.
> 레슨 03과 04에서 쓰던 동일한 구조화된 JSON 패턴을 사용하면 도구 호출이 신뢰할 수 있고 파싱 가능해집니다. 모델이 구조화된 데이터를 출력하면, 여러분이 이를 검증한 뒤 실행합니다.

## Common Issues
## 자주 발생하는 문제

**"The model requests a tool that doesn't exist"**
- Validate the tool name against your available tools
- Provide clear examples of available tools in the prompt
- Handle invalid tool names gracefully

> **"모델이 존재하지 않는 도구를 요청해요"**
> - 도구 이름을 사용 가능한 도구 목록과 대조해서 검증하세요
> - 프롬프트에 사용 가능한 도구의 명확한 예시를 제공하세요
> - 잘못된 도구 이름을 우아하게 처리하세요

**"The arguments are the wrong type"**
- Validate argument types before execution
- Make the expected types clear in the tool description
- Consider using schema validation for complex tools

> **"인자의 타입이 잘못됐어요"**
> - 실행 전에 인자 타입을 검증하세요
> - 도구 설명에서 기대되는 타입을 명확히 하세요
> - 복잡한 도구에는 스키마 검증 사용을 고려하세요

**"The model doesn't request a tool when it should"**
- Make it clear when tools should be used
- Provide examples in the prompt
- Consider making tool use mandatory for certain request types

> **"모델이 도구를 써야 할 때 요청하지 않아요"**
> - 언제 도구를 써야 하는지 명확히 하세요
> - 프롬프트에 예시를 제공하세요
> - 특정 유형의 요청에는 도구 사용을 필수로 만드는 것도 고려하세요

## Exercises
## 연습 문제

1. Add a new tool (e.g., "weather" or "search") and test it
2. Try invalid tool calls and see how validation handles them
3. Modify the tool interface and see how the model adapts
4. Create tools with different parameter types (strings, numbers, booleans)

> 1. 새 도구(예: "weather" 또는 "search")를 추가하고 테스트해보세요
> 2. 잘못된 도구 호출을 시도해서 검증이 어떻게 처리하는지 확인해보세요
> 3. 도구 인터페이스를 수정하고 모델이 어떻게 적응하는지 관찰해보세요
> 4. 다양한 파라미터 타입(문자열, 숫자, 불리언)을 가진 도구를 만들어보세요

## What's Next?
## 다음 단계는?

In [Lesson 06](06_agent_loop.md), we'll create the **agent loop** - putting decision making and tool calling together into a repeating cycle.
> [레슨 06](06_agent_loop.md)에서는 **에이전트 루프**를 만듭니다 — 의사결정과 도구 호출을 하나의 반복되는 사이클로 결합합니다.

---

**Key Takeaway:** Tool calling = expanding capabilities without retraining. Tools are interfaces you control, not abilities the agent has.
> **핵심 요약:** 도구 호출 = 재학습 없이 능력을 확장하는 것. 도구는 에이전트가 가진 능력이 아니라, 여러분이 통제하는 인터페이스입니다.
