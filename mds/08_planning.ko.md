# Lesson 08  -  Planning as Data (Not Thoughts)
# 레슨 08 - 데이터로서의 계획 수립 (사고가 아니다)

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How can an agent solve multi-step tasks?"**
**"에이전트가 어떻게 여러 단계로 이루어진 작업을 해결할 수 있을까?"**

Complex tasks require multiple steps. Planning breaks down a goal into a sequence of actions that can be executed step by step.
> 복잡한 작업은 여러 단계를 필요로 합니다. 계획 수립은 목표를 단계별로 실행 가능한 일련의 행동으로 쪼개는 과정입니다.

## What You Will Build
## 무엇을 만들게 되나요?

A planning system that:
- Generates a step-by-step plan from a goal
- Separates planning from execution
- Stores plans as data structures
- Executes plans sequentially

> 다음을 수행하는 계획 수립 시스템을 만듭니다:
> - 목표로부터 단계별 계획을 생성한다
> - 계획 수립과 실행을 분리한다
> - 계획을 데이터 구조로 저장한다
> - 계획을 순서대로 실행한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Planning vs Execution
### 1. 계획 수립 vs 실행

**Planning** is generating the steps needed to achieve a goal. **Execution** is actually doing those steps. By separating them, you can:
- Inspect the plan before executing
- Modify the plan if needed
- Debug planning separately from execution

> **계획 수립**은 목표를 달성하는 데 필요한 단계들을 생성하는 것입니다. **실행**은 실제로 그 단계들을 수행하는 것입니다. 이 둘을 분리함으로써 다음이 가능해집니다:
> - 실행 전에 계획을 검토할 수 있다
> - 필요하면 계획을 수정할 수 있다
> - 계획 수립과 실행을 따로 디버깅할 수 있다

This separation is powerful - you can see what the agent "thinks" it should do before it does it.
> 이 분리는 강력합니다 — 에이전트가 실제로 행동하기 전에, 무엇을 해야 한다고 "생각"하는지 미리 볼 수 있습니다.

### 2. Step Ordering
### 2. 단계 순서(Step Ordering)

**Step ordering** determines the sequence of actions. Steps might depend on each other (step 2 needs step 1's output), or they might be independent.
> **단계 순서**는 행동들의 순서를 결정합니다. 단계들은 서로 의존적일 수도 있고(2단계가 1단계의 출력을 필요로 함), 서로 독립적일 수도 있습니다.

For now, we execute steps in order. Later lessons will handle dependencies more explicitly.
> 지금은 단계를 순서대로 실행합니다. 이후 레슨에서 의존관계를 더 명시적으로 다룰 것입니다.

### 3. Validation
### 3. 검증(Validation)

**Validation** checks plans before execution. Is the plan valid JSON? Does it have the required structure? Are the steps reasonable?
> **검증**은 실행 전에 계획을 확인하는 것입니다. 계획이 유효한 JSON인가? 필요한 구조를 갖추고 있는가? 단계들이 합리적인가?

Validating plans catches errors before wasting time on execution.
> 계획을 검증하면 실행에 시간을 낭비하기 전에 오류를 잡아낼 수 있습니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No dependency handling ([Lesson 10](10_atom_of_thought.md))
- No atomic action validation ([Lesson 09](09_atomic_actions.md))
- No parallel execution - steps run sequentially

> - 의존관계 처리는 다루지 않음 ([레슨 10](10_atom_of_thought.md))
> - 원자적 행동 검증은 다루지 않음 ([레슨 09](09_atomic_actions.md))
> - 병렬 실행은 다루지 않음 - 단계는 순차적으로 실행됨

## The Code
## 코드

Look at `agent/agent.py`, see `create_plan()` and `execute_plan()` methods:
> `agent/agent.py`의 `create_plan()`과 `execute_plan()` 메서드를 살펴보세요:

```python
def create_plan(self, goal: str) -> dict | None:
    """
    Generate a plan to achieve a goal.
    
    Lesson 08 version.
    
    Args:
        goal: The goal to achieve
        
    Returns:
        Plan with steps
    """
    plan = create_plan(self.llm, goal)
    
    if plan:
        self.state.current_plan = plan
    
    return plan

def execute_plan(self, plan: dict) -> list:
    """
    Execute a plan step by step.
    
    Args:
        plan: Plan dictionary with "steps" list
        
    Returns:
        List of execution results
    """
    if not plan or "steps" not in plan:
        return []
    
    results = []
    
    for step in plan["steps"]:
        # Simple execution - in reality you'd call tools, etc.
        result = {
            "step": step,
            "executed": True
        }
        results.append(result)
        self.state.increment_step()
    
    return results
```

And the planner implementation in `agent/planner.py`:
> 그리고 `agent/planner.py`의 플래너 구현:

```python
def create_plan(llm: LocalLLM, goal: str) -> dict | None:
    """
    Generate a plan to achieve a goal.
    
    Used in: Lesson 08
    
    Args:
        llm: The language model to use
        goal: The goal to achieve
        
    Returns:
        Plan as a dictionary with a "steps" list, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Create a step-by-step plan to achieve the goal. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{"steps": ["step1", "step2", "step3"]}}

Goal: {goal}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        plan = extract_json_from_text(response)
        
        if plan and "steps" in plan and isinstance(plan["steps"], list):
            return plan
    
    return None
```

Notice:
- **Structured output** - Plans are JSON data structures
- **Validation** - We check that plans have the expected structure
- **Retry logic** - Multiple attempts to get a valid plan
- **Simple execution** - Steps are executed in order (actual execution logic comes later)

> 다음을 확인하세요:
> - **구조화된 출력** - 계획은 JSON 데이터 구조임
> - **검증** - 계획이 기대되는 구조를 갖추고 있는지 확인함
> - **재시도 로직** - 유효한 계획을 얻기 위한 여러 번의 시도
> - **단순한 실행** - 단계들이 순서대로 실행됨 (실제 실행 로직은 이후에 추가됨)

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_08_planning()` method:
> `complete_example.py`의 `lesson_08_planning()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

plan = agent.create_plan("Write a blog post about AI agents")
print(f"Plan: {plan}")

if plan:
    results = agent.execute_plan(plan)
    print(f"Execution results: {results}")
```

## Compare to Lesson 07
## 레슨 07과 비교하기

**Lesson 07 (Memory):**
> **레슨 07 (메모리):**
```
User: "My name is Alice" -> Save to memory
User: "What's my name?" -> Retrieve from memory
```
> 사용자: "제 이름은 Alice예요" -> 메모리에 저장
> 사용자: "제 이름이 뭐죠?" -> 메모리에서 검색

Stores and retrieves facts.
> 사실을 저장하고 검색합니다.

**Lesson 08 (Planning):**
> **레슨 08 (계획 수립):**
```
Goal: "Write article" -> Plan: ["Research", "Outline", "Write", "Review"]
Plan -> Execute each step -> Results
```
> 목표: "글쓰기" -> 계획: ["조사", "개요 작성", "본문 작성", "검토"]
> 계획 -> 각 단계 실행 -> 결과

Generates and executes a sequence of steps.
> 일련의 단계를 생성하고 실행합니다.

![Planning Flow](../diagrams/lesson-08-planning.png)

## Key Insights
## 핵심 통찰

### Plans Aren't Thoughts
### 계획은 사고가 아니다

Plans aren't thoughts - they're **data structures**. This makes them inspectable, modifiable, and safe. You can see, edit, and validate them before execution.
> 계획은 사고가 아니라 **데이터 구조**입니다. 그래서 들여다보고, 수정하고, 안전하게 다룰 수 있습니다. 실행하기 전에 확인하고, 편집하고, 검증할 수 있습니다.

### Planning = Data Generation
### 계획 수립 = 데이터 생성

Planning is not sophisticated reasoning - it's structured data generation. The model generates a list of steps, just like it generates any other structured output.
> 계획 수립은 정교한 추론이 아니라 구조화된 데이터 생성입니다. 모델은 다른 구조화된 출력을 생성할 때와 마찬가지로 단계 목록을 생성할 뿐입니다.

### Separate Phases
### 단계를 분리하기

Separating planning from execution lets you:
- Debug plans without executing
- Modify plans before running
- Reuse plans for similar goals
- Test planning independently

> 계획 수립과 실행을 분리하면 다음이 가능해집니다:
> - 실행 없이 계획을 디버깅하기
> - 실행 전에 계획을 수정하기
> - 비슷한 목표에 계획을 재사용하기
> - 계획 수립을 독립적으로 테스트하기

### Simple Execution
### 단순한 실행

For now, execution is simple - just iterate through steps. Later lessons will add more sophisticated execution with dependencies and validation.
> 지금은 실행이 단순합니다 — 단계를 순회할 뿐입니다. 이후 레슨에서 의존관계와 검증을 포함한 더 정교한 실행을 추가할 것입니다.

## Common Issues
## 자주 발생하는 문제

**"The plan is too vague"**
- Make the goal more specific
- Provide examples of good plans in the prompt
- Consider breaking down very general goals

> **"계획이 너무 모호해요"**
> - 목표를 더 구체적으로 만드세요
> - 프롬프트에 좋은 계획의 예시를 제공하세요
> - 매우 일반적인 목표는 더 잘게 쪼개는 것을 고려하세요

**"Steps are in wrong order"**
- The model determines order - validate if needed
- Consider adding dependency information
- Review and reorder steps before execution if necessary

> **"단계 순서가 잘못됐어요"**
> - 모델이 순서를 정합니다 - 필요하면 검증하세요
> - 의존관계 정보를 추가하는 것을 고려하세요
> - 필요하다면 실행 전에 단계를 검토하고 재정렬하세요

**"Execution doesn't do anything"**
- This lesson's execution is a placeholder
- In practice, you'd call tools or other functions
- The pattern is more important than the implementation

> **"실행해도 아무 일도 안 일어나요"**
> - 이 레슨의 실행 부분은 자리표시자(placeholder)일 뿐입니다
> - 실제로는 도구나 다른 함수를 호출하게 됩니다
> - 구현 자체보다 이 패턴이 더 중요합니다

## Exercises
## 연습 문제

1. Generate plans for different types of goals
2. Modify plans manually before executing
3. Compare plans for the same goal across multiple runs
4. Try to validate plans for completeness

> 1. 다양한 유형의 목표에 대한 계획을 생성해보세요
> 2. 실행 전에 계획을 직접 수정해보세요
> 3. 같은 목표에 대해 여러 번 실행한 계획들을 비교해보세요
> 4. 계획이 완전한지 검증을 시도해보세요

## What's Next?
## 다음 단계는?

In [Lesson 09](09_atomic_actions.md), we'll make execution safer by converting plan steps into **atomic actions** with validated schemas.
> [레슨 09](09_atomic_actions.md)에서는 계획 단계를 검증된 스키마를 가진 **원자적 행동(atomic actions)**으로 변환해서 실행을 더 안전하게 만듭니다.

---

**Key Takeaway:** Planning = data generation, not reasoning. Plans are inspectable data structures that enable multi-step execution.
> **핵심 요약:** 계획 수립 = 추론이 아니라 데이터 생성. 계획은 다단계 실행을 가능하게 하는, 들여다볼 수 있는 데이터 구조입니다.
