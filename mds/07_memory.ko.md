# Lesson 07  -  Memory (Short and Long)
# 레슨 07 - 메모리 (단기와 장기)

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How does an agent remember things?"**
**"에이전트는 어떻게 무언가를 기억할까?"**

Agents need to remember information across multiple interactions. Without memory, each conversation starts from scratch. Memory lets agents build on previous conversations and maintain context.
> 에이전트는 여러 번의 상호작용에 걸쳐 정보를 기억할 필요가 있습니다. 메모리가 없으면 매 대화가 처음부터 다시 시작됩니다. 메모리는 에이전트가 이전 대화를 바탕으로 쌓아가며 맥락을 유지할 수 있게 해줍니다.

## What You Will Build
## 무엇을 만들게 되나요?

A memory system that:
- Stores facts across interactions
- Retrieves relevant memories when needed
- Integrates memory into the agent's context
- Allows explicit memory management

> 다음을 수행하는 메모리 시스템을 만듭니다:
> - 여러 상호작용에 걸쳐 사실을 저장한다
> - 필요할 때 관련된 기억을 가져온다
> - 메모리를 에이전트의 컨텍스트에 통합한다
> - 명시적인 메모리 관리를 허용한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Context vs Memory
### 1. 컨텍스트 vs 메모리

**Context** is what's in the current prompt - everything the model can see right now. **Memory** is persistent storage that survives across interactions.
> **컨텍스트**는 현재 프롬프트 안에 있는 것 — 즉 모델이 지금 당장 볼 수 있는 모든 것입니다. **메모리**는 여러 상호작용을 넘어 살아남는 영속적인 저장소입니다.

Context is temporary. Memory persists. Memory gets loaded into context when needed.
> 컨텍스트는 일시적입니다. 메모리는 지속됩니다. 필요할 때 메모리가 컨텍스트로 불러와집니다.

### 2. Persistence
### 2. 영속성(Persistence)

**Persistence** means saving facts across turns. When a user says "My name is Alice," that fact should be stored and available in future interactions.
> **영속성**이란 여러 턴에 걸쳐 사실을 저장해두는 것을 뜻합니다. 사용자가 "제 이름은 Alice예요"라고 말하면, 그 사실은 저장되어 앞으로의 상호작용에서도 사용할 수 있어야 합니다.

Without persistence, the agent forgets everything after each interaction.
> 영속성이 없다면 에이전트는 매 상호작용이 끝날 때마다 모든 것을 잊어버립니다.

### 3. Retrieval
### 3. 검색(Retrieval)

**Retrieval** is getting relevant memories when needed. When the user asks "What's my name?", the agent retrieves "User's name is Alice" from memory and uses it to respond.
> **검색**은 필요할 때 관련된 기억을 가져오는 것입니다. 사용자가 "제 이름이 뭐죠?"라고 물으면, 에이전트는 메모리에서 "사용자의 이름은 Alice"라는 정보를 가져와 응답에 사용합니다.

Simple retrieval might mean "get all memories." More sophisticated retrieval finds relevant memories based on the current query.
> 단순한 검색은 "모든 기억을 가져온다"는 의미일 수 있습니다. 더 정교한 검색은 현재 질의를 바탕으로 관련된 기억만 찾아냅니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No planning ([Lesson 08](08_planning.md))
- No sophisticated memory retrieval - just simple "get all" retrieval
- No memory decay or prioritization

> - 계획 수립은 다루지 않음 ([레슨 08](08_planning.md))
> - 정교한 메모리 검색은 다루지 않음 - 단순히 "전부 가져오기"만 다룸
> - 메모리의 감쇠(decay)나 우선순위화는 다루지 않음

## The Code
## 코드

Look at `agent/agent.py`, see `run_with_memory()` method:
> `agent/agent.py`의 `run_with_memory()` 메서드를 살펴보세요:

```python
def run_with_memory(self, user_input: str) -> dict | None:
    """
    Run agent with memory context.
    
    Lesson 07 version.
    
    Args:
        user_input: User's input
        
    Returns:
        Response with potential memory update
    """
    memory_context = self.memory.get_all()
    
    # Build memory context string
    if memory_context:
        memory_str = "You remember the following:\n" + "\n".join(f"- {item}" for item in memory_context)
    else:
        memory_str = "You have no memories yet."
    
    prompt = f"""{self.system_prompt}

You are an agent with memory. You must respond with ONLY valid JSON.

{memory_str}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}
4. If the user tells you information (like their name), save it to memory
5. If the user asks about something you remember, USE YOUR MEMORY to answer

Required JSON format:
{{"reply": "your response text", "save_to_memory": "fact to remember" or null}}

Examples:
- User says "My name is Alice" -> {{"reply": "Nice to meet you, Alice!", "save_to_memory": "User's name is Alice"}}
- User asks "What's my name?" and you remember "User's name is Alice" -> {{"reply": "Your name is Alice", "save_to_memory": null}}

User input: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "reply" in parsed:
            # Save to memory if requested
            if parsed.get("save_to_memory"):
                self.memory.add(parsed["save_to_memory"])
            
            self.state.increment_step()
            return parsed
    
    return None
```

Notice:
- **Memory retrieval** - `memory.get_all()` loads all stored memories
- **Context integration** - Memories are included in the prompt
- **Explicit storage** - The agent explicitly says what to save via JSON
- **Automatic persistence** - When `save_to_memory` is provided, it's automatically stored

> 다음을 확인하세요:
> - **메모리 검색** - `memory.get_all()`이 저장된 모든 기억을 불러옴
> - **컨텍스트 통합** - 기억들이 프롬프트에 포함됨
> - **명시적 저장** - 에이전트가 JSON을 통해 무엇을 저장할지 명시적으로 말함
> - **자동 영속화** - `save_to_memory`가 제공되면 자동으로 저장됨

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_07_memory()` method:
> `complete_example.py`의 `lesson_07_memory()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# First interaction - store name
response1 = agent.run_with_memory("My name is Alice")
if response1 and "reply" in response1:
    print(f"Response 1: {response1['reply']}")

# Second interaction - recall name
response2 = agent.run_with_memory("What's my name?")
if response2 and "reply" in response2:
    print(f"Response 2: {response2['reply']}")

print(f"Memory contents: {agent.memory.get_all()}")
```

![Memory System](../diagrams/lesson-07-memory.png)

## Compare to Lesson 06
## 레슨 06과 비교하기

**Lesson 06 (Agent Loop):**
> **레슨 06 (에이전트 루프):**
```
Loop -> Step 1 -> Step 2 -> Step 3 -> Done
         |         |        |
       Action   Action   Action
```
> 루프 -> 1단계 -> 2단계 -> 3단계 -> 완료
>          |         |        |
>        행동      행동      행동

State persists within the loop but resets when the loop ends.
> 상태는 루프 안에서는 지속되지만 루프가 끝나면 초기화됩니다.

**Lesson 07 (Memory):**
> **레슨 07 (메모리):**
```
Interaction 1 -> Save "name is Alice" -> Memory stores it
Interaction 2 -> Load memory -> "Your name is Alice"
```
> 상호작용 1 -> "이름은 Alice"를 저장 -> 메모리에 저장됨
> 상호작용 2 -> 메모리를 불러옴 -> "당신의 이름은 Alice입니다"

Memory persists across completely separate interactions.
> 메모리는 완전히 분리된 상호작용을 넘어서도 지속됩니다.

## Key Insights
## 핵심 통찰

### Memory is Explicit Storage
### 메모리는 명시적인 저장소다

Memory is **explicit storage**, not consciousness. It's data you can inspect, modify, and delete. There's no hidden reasoning - just stored facts.
> 메모리는 의식이 아니라 **명시적인 저장소**입니다. 여러분이 들여다보고, 수정하고, 삭제할 수 있는 데이터입니다. 숨겨진 추론 같은 것은 없으며, 그저 저장된 사실들일 뿐입니다.

### Simple is Powerful
### 단순함이 강력하다

This memory system is simple: store strings, retrieve all of them. Yet it's incredibly useful. More sophisticated retrieval can come later, but this foundation works.
> 이 메모리 시스템은 단순합니다: 문자열을 저장하고, 전부 가져오는 것뿐입니다. 그런데도 놀랍도록 유용합니다. 더 정교한 검색은 나중에 추가할 수 있지만, 이 토대만으로도 잘 작동합니다.

### The Agent Controls Storage
### 에이전트가 저장을 통제한다

The agent decides what to save via the `save_to_memory` field. You could automate this, but explicit control keeps things predictable.
> 에이전트는 `save_to_memory` 필드를 통해 무엇을 저장할지 스스로 결정합니다. 이를 자동화할 수도 있지만, 명시적으로 통제하면 예측 가능성이 유지됩니다.

### Context Loading
### 컨텍스트에 불러오기

Memories are loaded into the prompt context. The model doesn't have direct access to memory - it only sees what you include in the prompt.
> 기억들은 프롬프트 컨텍스트 안으로 불러와집니다. 모델은 메모리에 직접 접근할 수 없으며, 오직 여러분이 프롬프트에 포함시킨 내용만 볼 수 있습니다.

## Common Issues
## 자주 발생하는 문제

**"The agent doesn't save information"**
- Check that the response includes `save_to_memory`
- Verify the memory.add() is being called
- Make sure the prompt clearly explains when to save

> **"에이전트가 정보를 저장하지 않아요"**
> - 응답에 `save_to_memory`가 포함되어 있는지 확인하세요
> - `memory.add()`가 호출되고 있는지 확인하세요
> - 프롬프트가 언제 저장해야 하는지를 명확히 설명하고 있는지 확인하세요

**"The agent forgets things"**
- Verify memory is being loaded into the prompt
- Check that memory persists across calls
- Ensure the memory context string is being included

> **"에이전트가 자꾸 잊어버려요"**
> - 메모리가 프롬프트에 불러와지고 있는지 확인하세요
> - 호출 간에 메모리가 유지되는지 확인하세요
> - 메모리 컨텍스트 문자열이 포함되고 있는지 확인하세요

**"Memory gets too large"**
- This simple system stores all memories forever
- Consider adding memory limits or deletion
- More sophisticated systems can prioritize or summarize memories

> **"메모리가 너무 커져요"**
> - 이 단순한 시스템은 모든 기억을 영원히 저장합니다
> - 메모리 제한이나 삭제 기능 추가를 고려하세요
> - 더 정교한 시스템은 기억에 우선순위를 매기거나 요약할 수 있습니다

## Exercises
## 연습 문제

1. Save multiple facts and see how they accumulate
2. Try asking about something not in memory
3. Manually inspect `agent.memory.get_all()` to see stored data
4. Modify the memory format and see how it affects behavior

> 1. 여러 개의 사실을 저장하고 어떻게 누적되는지 관찰해보세요
> 2. 메모리에 없는 것에 대해 물어보세요
> 3. `agent.memory.get_all()`을 직접 확인해서 저장된 데이터를 살펴보세요
> 4. 메모리 형식을 수정하고 행동에 어떤 영향을 주는지 관찰해보세요

## What's Next?
## 다음 단계는?

In [Lesson 08](08_planning.md), we'll add **planning** - the ability to break down complex goals into a sequence of steps.
> [레슨 08](08_planning.md)에서는 **계획 수립**을 추가합니다 — 복잡한 목표를 일련의 단계들로 쪼개는 능력입니다.

---

**Key Takeaway:** Memory = data storage, not thoughts. It's explicit, inspectable, and gives agents continuity across interactions.
> **핵심 요약:** 메모리 = 사고가 아니라 데이터 저장소. 명시적이고, 들여다볼 수 있으며, 에이전트에게 상호작용 간의 연속성을 부여합니다.
