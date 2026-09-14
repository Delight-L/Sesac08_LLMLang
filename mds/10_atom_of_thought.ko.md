# Lesson 10  -  AoT (Atom of Thought)  -  Now It Makes Sense
# 레슨 10 - AoT (사고의 원자) - 이제야 이해가 되다

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How do I scale planning without losing control?"**
**"통제력을 잃지 않으면서 계획 수립을 어떻게 확장할 수 있을까?"**

Complex tasks need many actions with dependencies. Some actions can run in parallel, others must wait. AoT (Atom of Thought) creates dependency graphs that enable safe, efficient execution of complex workflows.
> 복잡한 작업은 의존관계를 가진 여러 행동을 필요로 합니다. 어떤 행동은 병렬로 실행할 수 있고, 어떤 행동은 기다려야 합니다. AoT(사고의 원자)는 의존관계 그래프를 만들어 복잡한 워크플로우를 안전하고 효율적으로 실행할 수 있게 해줍니다.

## What You Will Build
## 무엇을 만들게 되나요?

An AoT system that:
- Creates dependency graphs with nodes and dependencies
- Validates graph structure before execution
- Executes actions respecting dependencies
- Enables parallel execution of independent actions

> 다음을 수행하는 AoT 시스템을 만듭니다:
> - 노드와 의존관계로 이루어진 의존관계 그래프를 생성한다
> - 실행 전에 그래프 구조를 검증한다
> - 의존관계를 준수하며 행동을 실행한다
> - 독립적인 행동들의 병렬 실행을 가능하게 한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Atomic Planning
### 1. 원자적 계획 수립(Atomic Planning)

**Atomic planning** means creating plans as dependency graphs where each node is an atomic action. Nodes can depend on other nodes, creating an explicit execution order.
> **원자적 계획 수립**이란 각 노드가 원자적 행동인 의존관계 그래프로 계획을 만드는 것을 뜻합니다. 노드는 다른 노드에 의존할 수 있으며, 이를 통해 명시적인 실행 순서가 만들어집니다.

This is the natural combination of Lesson 08's planning and Lesson 09's atomic actions, with added dependency tracking.
> 이는 레슨 08의 계획 수립과 레슨 09의 원자적 행동이 자연스럽게 결합된 것에, 의존관계 추적이 더해진 것입니다.

### 2. Dependency Resolution
### 2. 의존관계 해소(Dependency Resolution)

**Dependency resolution** determines the correct execution order. Actions with no dependencies can run immediately. Actions with dependencies wait for their dependencies to complete.
> **의존관계 해소**는 올바른 실행 순서를 결정하는 것입니다. 의존관계가 없는 행동은 즉시 실행될 수 있습니다. 의존관계가 있는 행동은 그 의존 대상이 완료될 때까지 기다립니다.

This enables parallel execution of independent actions while respecting ordering constraints.
> 이를 통해 순서 제약을 지키면서도 독립적인 행동들을 병렬로 실행할 수 있습니다.

### 3. Validated Execution
### 3. 검증된 실행(Validated Execution)

**Validated execution** means checking the graph structure before running it. Are all dependencies valid? Is there a circular dependency? Are all required nodes present?
> **검증된 실행**이란 실행하기 전에 그래프 구조를 확인하는 것입니다. 모든 의존관계가 유효한가? 순환 의존관계가 있는가? 필요한 노드가 모두 존재하는가?

Validation catches structural errors before execution begins.
> 검증은 실행이 시작되기 전에 구조적 오류를 잡아냅니다.

## The Code
## 코드

Look at `agent/planner.py`, see `create_aot_graph()` function:
> `agent/planner.py`의 `create_aot_graph()` 함수를 살펴보세요:

```python
def create_aot_graph(llm: LocalLLM, goal: str) -> dict | None:
    """
    Generate an AoT execution graph.
    
    Used in: Lesson 10
    
    Args:
        llm: The language model to use
        goal: The goal to achieve
        
    Returns:
        AoT graph with nodes and dependencies, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Create an execution graph to achieve the goal. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{
  "nodes": [
    {{"id": "1", "action": "action_name", "depends_on": []}},
    {{"id": "2", "action": "action_name", "depends_on": ["1"]}}
  ]
}}

Each node must have:
- "id": unique identifier (string)
- "action": what to do (string)
- "depends_on": list of node IDs that must complete first (list of strings)

Goal: {goal}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        graph = extract_json_from_text(response)
        
        if graph and "nodes" in graph and isinstance(graph["nodes"], list):
            # Validate node structure
            node_ids = set()
            for node in graph["nodes"]:
                if "id" not in node or "action" not in node or "depends_on" not in node:
                    break
                node_ids.add(node["id"])
            else:
                # All nodes valid, check dependencies reference valid nodes
                for node in graph["nodes"]:
                    for dep in node.get("depends_on", []):
                        if dep not in node_ids:
                            break
                    else:
                        continue
                    break
                else:
                    return graph
    
    return None
```

And in `agent/agent.py`:
> 그리고 `agent/agent.py`에서:

```python
def create_aot_plan(self, goal: str) -> dict | None:
    """
    Generate an AoT execution graph.
    
    Lesson 10 version.
    
    Args:
        goal: The goal to achieve
        
    Returns:
        AoT graph with atomic nodes and dependencies
    """
    return create_aot_graph(self.llm, goal)

def execute_aot_plan(self, graph: dict) -> list:
    """
    Execute an AoT graph respecting dependencies.
    
    Args:
        graph: AoT graph
        
    Returns:
        List of execution results
    """
    def execute_action(action: str):
        # Placeholder for actual action execution
        return f"Executed: {action}"
    
    return execute_graph(graph, execute_action)
```

Notice:
- **Graph structure** - Nodes with IDs, actions, and dependencies
- **Validation** - Checks that all dependencies reference valid nodes
- **Dependency resolution** - The execute_graph function handles ordering
- **Extensibility** - Easy to add parallel execution later

> 다음을 확인하세요:
> - **그래프 구조** - ID, 행동, 의존관계를 가진 노드들
> - **검증** - 모든 의존관계가 유효한 노드를 참조하는지 확인함
> - **의존관계 해소** - execute_graph 함수가 순서를 처리함
> - **확장성** - 이후 병렬 실행을 추가하기 쉬움

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_10_aot()` method:
> `complete_example.py`의 `lesson_10_aot()` 메서드를 살펴보세요:

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

graph = agent.create_aot_plan("Research and write article")
print(f"AoT graph: {graph}")

if graph:
    results = agent.execute_aot_plan(graph)
    print(f"Execution results: {results}")
```

![Atom of Thought Graph](../diagrams/lesson-10-atom-of-thoght.png)

## Compare to Lesson 09
## 레슨 09와 비교하기

**Lesson 09 (Atomic Actions):**
> **레슨 09 (원자적 행동):**
```
Step -> Atomic action: {"action": "...", "inputs": {...}}
```
> 단계 -> 원자적 행동: {"action": "...", "inputs": {...}}

Single step converted to atomic action.
> 단일 단계가 원자적 행동으로 변환됩니다.

**Lesson 10 (AoT):**
> **레슨 10 (AoT):**
```
Goal -> Graph: {
  nodes: [
    {id: "1", action: "...", depends_on: []},
    {id: "2", action: "...", depends_on: ["1"]}
  ]
}
```
> 목표 -> 그래프: {
>   nodes: [
>     {id: "1", action: "...", depends_on: []},
>     {id: "2", action: "...", depends_on: ["1"]}
>   ]
> }

Multiple atomic actions with explicit dependencies.
> 명시적인 의존관계를 가진 여러 개의 원자적 행동들입니다.

## Key Insights
## 핵심 통찰

### AoT is Inevitable
### AoT는 필연적이다

At this point, AoT feels **inevitable**, not advanced. It's the natural evolution of planning (Lesson 08), atomic actions (Lesson 09), and adding dependencies. Once you understand the pieces, the graph structure makes perfect sense.
> 이 지점에 이르면 AoT는 고급 기법이라기보다 **필연적**으로 느껴집니다. 계획 수립(레슨 08)과 원자적 행동(레슨 09)에 의존관계를 더한, 자연스러운 발전 과정입니다. 각 조각을 이해하고 나면 그래프 구조는 완벽하게 이치에 맞습니다.

### It's Not Advanced Reasoning
### 이것은 고급 추론이 아니다

AoT isn't smarter thinking - it's **better structure**:
- Each node is validated (from Lesson 09)
- Dependencies are explicit (new in this lesson)
- Execution is deterministic (respecting order)
- Failures are contained (to individual nodes)

> AoT는 더 똑똑한 사고가 아니라 **더 나은 구조**입니다:
> - 각 노드는 검증됩니다 (레슨 09에서 온 것)
> - 의존관계는 명시적입니다 (이번 레슨에서 새로 추가된 것)
> - 실행은 결정적입니다 (순서를 준수함)
> - 실패는 (개별 노드에) 국한됩니다

### Structure Enables Scale
### 구조가 확장을 가능하게 한다

By adding dependencies, you can handle complex workflows with many actions. Dependencies enable:
- Parallel execution of independent actions
- Clear execution order
- Easier debugging (know what depends on what)

> 의존관계를 추가함으로써 많은 행동으로 이루어진 복잡한 워크플로우를 다룰 수 있습니다. 의존관계는 다음을 가능하게 합니다:
> - 독립적인 행동들의 병렬 실행
> - 명확한 실행 순서
> - 더 쉬운 디버깅 (무엇이 무엇에 의존하는지 알 수 있음)

### Validation is Key
### 검증이 핵심이다

The graph structure must be validated before execution. Circular dependencies, missing nodes, or invalid references must be caught early.
> 그래프 구조는 실행 전에 반드시 검증되어야 합니다. 순환 의존관계, 누락된 노드, 유효하지 않은 참조는 일찍 잡아내야 합니다.

## Common Issues
## 자주 발생하는 문제

**"Circular dependencies"**
- The validation should catch this
- Check that dependencies form a directed acyclic graph (DAG)
- Consider adding cycle detection to validation

> **"순환 의존관계가 있어요"**
> - 검증이 이를 잡아내야 합니다
> - 의존관계가 방향성 비순환 그래프(DAG)를 이루는지 확인하세요
> - 검증에 순환 탐지 기능을 추가하는 것을 고려하세요

**"Dependencies reference non-existent nodes"**
- Validation checks for this
- Ensure all node IDs in dependencies exist in the graph
- Consider generating IDs more systematically

> **"의존관계가 존재하지 않는 노드를 참조해요"**
> - 검증이 이를 확인합니다
> - 의존관계 안의 모든 노드 ID가 그래프 안에 존재하는지 확인하세요
> - ID를 더 체계적으로 생성하는 것을 고려하세요

**"Execution order seems wrong"**
- Verify dependencies are correctly specified
- Check that execute_graph respects dependencies
- Consider adding execution logging to see order

> **"실행 순서가 잘못된 것 같아요"**
> - 의존관계가 올바르게 명시되어 있는지 확인하세요
> - execute_graph가 의존관계를 준수하는지 확인하세요
> - 순서를 확인하기 위해 실행 로그를 추가하는 것을 고려하세요

## Exercises
## 연습 문제

1. Create graphs with different dependency structures
2. Try to create a circular dependency and see if validation catches it
3. Compare execution order with and without dependencies
4. Experiment with parallel vs sequential execution

> 1. 다양한 의존관계 구조를 가진 그래프를 만들어보세요
> 2. 순환 의존관계를 만들어보고 검증이 이를 잡아내는지 확인해보세요
> 3. 의존관계가 있을 때와 없을 때의 실행 순서를 비교해보세요
> 4. 병렬 실행과 순차 실행을 실험해보세요

## Final Insight
## 마지막 통찰

You've now built an agent that:
1. Talks to an LLM ([Lesson 01](01_basic_llm_chat.md))
2. Has consistent behavior ([Lesson 02](02_system_prompt.md))
3. Produces validated outputs ([Lesson 03](03_structured_output.md))
4. Makes decisions ([Lesson 04](04_decision_making.md))
5. Uses tools ([Lesson 05](05_tools.md))
6. Runs in a loop ([Lesson 06](06_agent_loop.md))
7. Remembers things ([Lesson 07](07_memory.md))
8. Plans actions ([Lesson 08](08_planning.md))
9. Executes safely ([Lesson 09](09_atomic_actions.md))
10. Scales with dependencies ([Lesson 10](10_atom_of_thought.md))

> 여러분은 이제 다음과 같은 에이전트를 만들었습니다:
> 1. LLM과 대화한다 ([레슨 01](01_basic_llm_chat.md))
> 2. 일관된 행동을 보인다 ([레슨 02](02_system_prompt.md))
> 3. 검증된 출력을 만든다 ([레슨 03](03_structured_output.md))
> 4. 의사결정을 내린다 ([레슨 04](04_decision_making.md))
> 5. 도구를 사용한다 ([레슨 05](05_tools.md))
> 6. 루프 안에서 동작한다 ([레슨 06](06_agent_loop.md))
> 7. 무언가를 기억한다 ([레슨 07](07_memory.md))
> 8. 행동을 계획한다 ([레슨 08](08_planning.md))
> 9. 안전하게 실행한다 ([레슨 09](09_atomic_actions.md))
> 10. 의존관계로 확장한다 ([레슨 10](10_atom_of_thought.md))

And you understand **exactly how it all works**. No magic, no hidden reasoning - just structure, validation, and explicit execution.
> 그리고 여러분은 이 모든 것이 **정확히 어떻게 작동하는지** 이해하고 있습니다. 마법도, 숨겨진 추론도 없습니다 — 오직 구조, 검증, 명시적인 실행만이 있을 뿐입니다.

---

**Key Takeaway:** AoT is structure, not magic. Agents are systems, not minds. Dependency graphs enable complex workflows while maintaining control and predictability.
> **핵심 요약:** AoT는 마법이 아니라 구조입니다. 에이전트는 정신이 아니라 시스템입니다. 의존관계 그래프는 통제력과 예측 가능성을 유지하면서도 복잡한 워크플로우를 가능하게 합니다.
