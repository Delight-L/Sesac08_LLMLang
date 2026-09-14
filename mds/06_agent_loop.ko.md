# Lesson 06  -  The Agent Loop
# 레슨 06 - 에이전트 루프

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How does this become an agent instead of a chatbot?"**
**"이것이 어떻게 챗봇이 아니라 에이전트가 되는 걸까?"**

Answer: When it can **observe, decide, act, and repeat**, with state. A chatbot responds once and stops. An agent takes multiple steps toward a goal.
> 답: **관찰하고, 결정하고, 행동하고, 반복**할 수 있으며 상태(state)를 가질 때입니다. 챗봇은 한 번 응답하고 멈추지만, 에이전트는 목표를 향해 여러 단계를 밟아갑니다.

## What You Will Build
## 무엇을 만들게 되나요?

An agent loop that:
- Runs multiple steps in sequence
- Maintains state across steps
- Decides actions based on current state
- Terminates when the goal is reached or max steps exceeded

> 다음을 수행하는 에이전트 루프를 만듭니다:
> - 여러 단계를 순서대로 실행한다
> - 단계마다 상태를 유지한다
> - 현재 상태를 바탕으로 행동을 결정한다
> - 목표에 도달하거나 최대 단계 수를 초과하면 종료한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Agent Loop
### 1. 에이전트 루프(Agent Loop)

The **agent loop** is the repeating cycle: observe, decide, act. Each iteration, the agent looks at the current situation, decides what to do, takes that action, and repeats until done.
> **에이전트 루프**는 관찰-결정-행동을 반복하는 사이클입니다. 매 반복마다 에이전트는 현재 상황을 살펴보고, 무엇을 할지 결정하고, 그 행동을 취한 뒤, 끝날 때까지 이를 반복합니다.

This is what separates agents from simple chatbots - agents don't stop after one response.
> 이것이 바로 에이전트를 단순한 챗봇과 구분 짓는 지점입니다 — 에이전트는 한 번의 응답 후에 멈추지 않습니다.

### 2. State Transitions
### 2. 상태 전이(State Transitions)

**State transitions** track how the agent's state changes with each step. The state might include step count, completion status, accumulated results, or other tracking information.
> **상태 전이**는 각 단계마다 에이전트의 상태가 어떻게 변하는지를 추적합니다. 상태에는 단계 수, 완료 상태, 누적된 결과, 또는 그 밖의 추적 정보가 포함될 수 있습니다.

State makes the loop aware of its progress and history.
> 상태 덕분에 루프는 자신의 진행 상황과 이력을 인지할 수 있습니다.

### 3. Termination Conditions
### 3. 종료 조건(Termination Conditions)

**Termination conditions** determine when the loop stops. Common conditions include:
- The agent decides it's "done"
- Maximum steps reached
- A goal is achieved
- An error occurs

> **종료 조건**은 루프가 언제 멈출지를 결정합니다. 흔히 쓰이는 조건은 다음과 같습니다:
> - 에이전트가 스스로 "완료됐다"고 판단할 때
> - 최대 단계 수에 도달했을 때
> - 목표가 달성됐을 때
> - 오류가 발생했을 때

Without termination, the loop would run forever.
> 종료 조건이 없다면 루프는 영원히 실행될 것입니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No memory across loops ([Lesson 07](07_memory.md))
- No planning ([Lesson 08](08_planning.md))
- No sophisticated reasoning - just simple step-by-step decisions

> - 루프 간의 메모리는 다루지 않음 ([레슨 07](07_memory.md))
> - 계획 수립은 다루지 않음 ([레슨 08](08_planning.md))
> - 정교한 추론은 다루지 않음 - 단순한 단계별 결정만 다룸

## The Code
## 코드

Look at `agent/agent.py`, see `agent_step()` and `run_loop()` methods:
> `agent/agent.py`의 `agent_step()`과 `run_loop()` 메서드를 살펴보세요:

```python
def agent_step(self, user_input: str) -> dict | None:
    """
    Execute one step of the agent loop: observe, decide, act.
    
    Lesson 06 version.
    
    Args:
        user_input: User's input or system observation
        
    Returns:
        Action decision or None if step failed
    """
    state_dict = self.state.to_dict()
    
    prompt = f"""{self.system_prompt}

You are an agent. You must decide the next action and respond with ONLY valid JSON.

Current state: steps={state_dict.get('steps', 0)}, done={state_dict.get('done', False)}

Available actions: analyze, research, summarize, answer, done

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{"action": "action_name", "reason": "explanation"}}

User input: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "action" in parsed:
            if "reason" not in parsed:
                parsed["reason"] = f"Taking action: {parsed['action']}"
            self.state.increment_step()
            return parsed
    
    return None

def run_loop(self, user_input: str, max_steps: int = 5):
    """
    Run the agent loop for multiple steps.
    
    Args:
        user_input: Initial user input
        max_steps: Maximum number of steps to execute
        
    Returns:
        List of action results
    """
    self.state.reset()
    results = []
    
    while not self.state.done and self.state.steps < max_steps:
        action = self.agent_step(user_input)
        
        if action:
            results.append(action)
            
            # Simple termination condition
            if action.get("action") == "done":
                self.state.mark_done()
        else:
            break
    
    return results
```

Notice:
- **State tracking** - Each step increments the step counter and checks completion
- **Loop structure** - `while not done` continues until termination
- **Action accumulation** - Results are collected across steps
- **Safety limits** - `max_steps` prevents infinite loops

> 다음을 확인하세요:
> - **상태 추적** - 매 단계마다 스텝 카운터를 증가시키고 완료 여부를 확인함
> - **루프 구조** - `while not done`이 종료될 때까지 계속 반복됨
> - **행동 누적** - 여러 단계에 걸쳐 결과가 수집됨
> - **안전장치** - `max_steps`가 무한 루프를 방지함

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_06_agent_loop()` method:
> `complete_example.py`의 `lesson_06_agent_loop()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

print("\nNote: Repetition in early iterations is expected.")
print("The agent refines its understanding step by step and may repeat analysis")
print("before converging on a clearer explanation.\n")

results = agent.run_loop("Help me understand loops", max_steps=3)

for i, result in enumerate(results, 1):
    print(f"Iteration {i}:")
    action = result.get("action", "unknown")
    reason = result.get("reason", "No reason provided")
    print(f"  Action: {action}")
    print(f"  Reason: {reason}")
    if i < len(results):
        print()
```

The output shows each iteration with the action taken and reason. Note that repetition in early iterations is expected - the agent refines its understanding step by step.
> 출력에는 각 반복마다 취해진 행동과 그 이유가 표시됩니다. 초반 반복에서 나타나는 반복(중복)은 정상입니다 — 에이전트가 단계적으로 이해를 다듬어가는 과정입니다.

## Compare to Lesson 05
## 레슨 05와 비교하기

**Lesson 05 (Tool Calling):**
> **레슨 05 (도구 호출):**
```
Request -> Tool call -> Result -> Done
```
> 요청 -> 도구 호출 -> 결과 -> 완료

Single interaction: request, execute, return.
> 한 번의 상호작용: 요청, 실행, 반환.

**Lesson 06 (Agent Loop):**
> **레슨 06 (에이전트 루프):**
```
Input -> Step 1 -> Step 2 -> Step 3 -> Done
          |        |        |
        Action   Action   Action
```
> 입력 -> 1단계 -> 2단계 -> 3단계 -> 완료
>            |        |        |
>          행동      행동      행동

Multiple steps in sequence, each deciding what to do next.
> 순서대로 이어지는 여러 단계, 각 단계마다 다음에 무엇을 할지 결정합니다.

![Agent Loop Flow](../diagrams/lesson-06-agent-loop.png)

## Key Insights
## 핵심 통찰

### An Agent is Not a Clever Prompt
### 에이전트는 영리한 프롬프트가 아니다

An agent is not a clever prompt. It's a **loop with state**. The magic isn't in the prompt - it's in the repeated cycle of observation, decision, and action.
> 에이전트는 영리한 프롬프트가 아닙니다. **상태를 가진 루프**입니다. 마법은 프롬프트 안에 있는 것이 아니라, 관찰-결정-행동이 반복되는 사이클 안에 있습니다.

### State Enables Continuity
### 상태가 연속성을 가능하게 한다

Without state, each step would be independent. With state, steps can build on each other and track progress toward a goal.
> 상태가 없다면 각 단계는 서로 독립적일 것입니다. 상태가 있으면 단계들이 서로의 위에 쌓여가며 목표를 향한 진행 상황을 추적할 수 있습니다.

### Termination is Critical
### 종료 조건이 결정적으로 중요하다

Always have termination conditions. Without them, loops can run forever or consume resources unnecessarily. `max_steps` is a simple but essential safety mechanism.
> 항상 종료 조건을 두세요. 종료 조건이 없으면 루프가 영원히 실행되거나 불필요하게 자원을 소모할 수 있습니다. `max_steps`는 단순하지만 필수적인 안전장치입니다.

### Simple is Better
### 단순한 것이 낫다

This loop is intentionally simple. Complex reasoning can come later - first, establish the pattern of repeated action.
> 이 루프는 의도적으로 단순하게 설계되었습니다. 복잡한 추론은 나중에 다뤄도 됩니다 — 먼저 반복되는 행동의 패턴을 확립하는 것이 우선입니다.

## Common Issues
## 자주 발생하는 문제

**"The loop runs forever"**
- Check that termination conditions are properly set
- Verify `max_steps` is being enforced
- Make sure the agent can signal "done"

> **"루프가 끝없이 실행돼요"**
> - 종료 조건이 제대로 설정되어 있는지 확인하세요
> - `max_steps`가 제대로 적용되고 있는지 확인하세요
> - 에이전트가 "완료" 신호를 보낼 수 있는지 확인하세요

**"Each step seems independent"**
- Include state information in the prompt
- Pass accumulated results to subsequent steps
- Make the state visible to the decision-making process

> **"각 단계가 서로 독립적인 것처럼 보여요"**
> - 프롬프트에 상태 정보를 포함시키세요
> - 누적된 결과를 다음 단계로 전달하세요
> - 의사결정 과정에서 상태가 보이도록 만드세요

**"The agent doesn't make progress"**
- Check that actions actually change something
- Verify state is being updated correctly
- Ensure the agent sees relevant state information

> **"에이전트가 진전을 보이지 않아요"**
> - 행동이 실제로 무언가를 바꾸는지 확인하세요
> - 상태가 올바르게 업데이트되는지 확인하세요
> - 에이전트가 관련된 상태 정보를 보고 있는지 확인하세요

## Exercises
## 연습 문제

1. Modify the available actions and see how the loop adapts
2. Change `max_steps` and observe how it affects behavior
3. Add state variables beyond step count
4. Experiment with different termination conditions

> 1. 사용 가능한 행동을 수정하고 루프가 어떻게 적응하는지 관찰해보세요
> 2. `max_steps`를 바꿔보고 행동에 어떤 영향을 주는지 관찰해보세요
> 3. 단계 수 외의 상태 변수를 추가해보세요
> 4. 다양한 종료 조건을 실험해보세요

## What's Next?
## 다음 단계는?

In [Lesson 07](07_memory.md), we'll add **memory** so the agent can remember information across multiple interactions, not just within a single loop.
> [레슨 07](07_memory.md)에서는 **메모리**를 추가해서, 에이전트가 하나의 루프 안에서뿐 아니라 여러 번의 상호작용에 걸쳐서도 정보를 기억할 수 있게 합니다.

---

**Key Takeaway:** Agent = loop + state. That's it. The loop enables multi-step behavior, state enables continuity.
> **핵심 요약:** 에이전트 = 루프 + 상태. 그게 전부입니다. 루프는 다단계 행동을 가능하게 하고, 상태는 연속성을 가능하게 합니다.
