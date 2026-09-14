# Lesson 11 - Evals (Regression Testing for Agents)
# 레슨 11 - Evals (에이전트를 위한 회귀 테스트)

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"How do I know if my agent still works after I change something?"**
**"무언가를 바꾼 뒤에도 에이전트가 여전히 잘 작동하는지 어떻게 알 수 있을까?"**

Once you have tools, memory, and structured outputs, changing a prompt becomes risky. A small wording change can break JSON parsing. An "improvement" can make tool calls less reliable. Without evals, quality degrades silently.
> 도구, 메모리, 구조화된 출력이 갖춰지고 나면, 프롬프트를 바꾸는 일이 위험해집니다. 사소한 문구 변경이 JSON 파싱을 깨뜨릴 수 있습니다. "개선"이라고 생각한 변경이 도구 호출의 신뢰성을 떨어뜨릴 수도 있습니다. 평가(evals)가 없으면 품질이 조용히 저하됩니다.

An eval suite is just a Python file that runs your agent and asserts things didn't break.
> 평가 스위트(eval suite)는 그저 에이전트를 실행하고 아무것도 깨지지 않았는지 검증(assert)하는 파이썬 파일일 뿐입니다.

## What You Will Build
## 무엇을 만들게 되나요?

An evaluation system that:
- Tests prompt and JSON parsing reliability
- Validates tool call accuracy
- Checks memory storage and retrieval cycles
- Catches regressions before deployment

> 다음을 수행하는 평가 시스템을 만듭니다:
> - 프롬프트와 JSON 파싱의 신뢰성을 테스트한다
> - 도구 호출의 정확성을 검증한다
> - 메모리 저장·검색 사이클을 확인한다
> - 배포 전에 회귀(regression)를 잡아낸다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Eval Suites
### 1. 평가 스위트(Eval Suites)

An **eval suite** is a collection of test cases that validate agent behavior. Each case has an input and an expected outcome. You run the suite after every prompt change.
> **평가 스위트**는 에이전트의 행동을 검증하는 테스트 케이스들의 모음입니다. 각 케이스는 입력과 기대되는 결과를 가집니다. 프롬프트를 바꿀 때마다 이 스위트를 실행합니다.

This isn't magic - it's just running your agent with known inputs and checking the outputs.
> 마법이 아닙니다 — 그저 이미 알고 있는 입력으로 에이전트를 실행하고 출력을 확인하는 것뿐입니다.

### 2. Golden Datasets
### 2. 골든 데이터셋(Golden Datasets)

A **golden dataset** is your source of truth - known-good examples that must always pass. If a golden case fails, the agent is broken (not the test).
> **골든 데이터셋**은 여러분의 진실의 원천(source of truth)입니다 — 항상 통과해야 하는, 이미 옳다고 검증된 예시들입니다. 골든 케이스가 실패한다면, 그것은 테스트가 아니라 에이전트가 고장 난 것입니다.

Golden datasets are version controlled alongside your prompts. When you change a prompt, you run the golden dataset to verify nothing broke.
> 골든 데이터셋은 프롬프트와 함께 버전 관리됩니다. 프롬프트를 바꿀 때는 골든 데이터셋을 실행해서 아무것도 깨지지 않았는지 확인합니다.

### 3. Hard vs Soft Assertions
### 3. 하드 검증 vs 소프트 검증

**Hard assertions** must always pass:
- JSON must be valid
- Required fields must be present
- Tool names must match available tools

**Soft assertions** should usually pass:
- The answer is semantically correct
- The phrasing is appropriate
- The tool arguments are optimal

Start with hard assertions. Add soft ones later.

> **하드 검증(hard assertions)**은 항상 통과해야 합니다:
> - JSON이 유효해야 함
> - 필수 필드가 존재해야 함
> - 도구 이름이 사용 가능한 도구와 일치해야 함
>
> **소프트 검증(soft assertions)**은 대체로 통과하면 됩니다:
> - 답변이 의미상 올바른가
> - 표현이 적절한가
> - 도구 인자가 최적인가
>
> 하드 검증부터 시작하세요. 소프트 검증은 나중에 추가하세요.

## Why This Fails in the Real World
## 실제 현장에서 이것이 실패하는 이유

A prompt change that improves phrasing can:
- Increase verbosity
- Push JSON out of context window
- Break parsing
- ...without changing correctness

> 표현을 개선하려는 프롬프트 변경이 다음을 일으킬 수 있습니다:
> - 장황함 증가
> - JSON이 컨텍스트 윈도우 밖으로 밀려남
> - 파싱이 깨짐
> - ...정확성 자체는 바뀌지 않았는데도 말입니다

This is why evals exist. They catch these silent failures.
> 이것이 바로 평가(evals)가 존재하는 이유입니다. 이런 조용한 실패들을 잡아냅니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No runtime monitoring ([Lesson 12](12_telemetry.md))
- No A/B testing
- No production observability
- No LLM-as-judge evals (too complex for now)

> - 런타임 모니터링은 다루지 않음 ([레슨 12](12_telemetry.md))
> - A/B 테스트는 다루지 않음
> - 프로덕션 관측가능성(observability)은 다루지 않음
> - LLM을 심사관으로 쓰는 평가(LLM-as-judge)는 다루지 않음 (지금은 너무 복잡함)

## The Code
## 코드

Look at `agent/evals.py`:
> `agent/evals.py`를 살펴보세요:

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalResult:
    """Result of a single eval case."""
    passed: bool
    input: str
    expected: Any = None
    actual: Any = None
    error: str | None = None


@dataclass 
class EvalSuiteResult:
    """Result of running an eval suite."""
    name: str
    passed: int = 0
    failed: int = 0
    results: list[EvalResult] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        return self.passed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0.0
    
    def summary(self) -> str:
        status = "✓ PASSED" if self.failed == 0 else "✗ FAILED"
        return f"{self.name}: {status} ({self.passed}/{self.passed + self.failed})"


class AgentEval:
    """Regression testing for agent capabilities."""
    
    def __init__(self, agent):
        self.agent = agent
    
    def test_structured_output(self, cases: list[dict]) -> EvalSuiteResult:
        """Test that structured output parses correctly and matches schema."""
        suite = EvalSuiteResult(name="Structured Output")
        
        for case in cases:
            result = self.agent.generate_structured(case["input"], case["schema"])
            
            # Check 1: Did we get valid JSON?
            if result is None:
                suite.add_result(EvalResult(
                    passed=False,
                    input=case["input"],
                    error="Failed to parse JSON"
                ))
                continue
            
            # Check 2: Are required fields present?
            missing = [f for f in case.get("must_have_fields", []) if f not in result]
            if missing:
                suite.add_result(EvalResult(
                    passed=False,
                    input=case["input"],
                    error=f"Missing fields: {missing}"
                ))
                continue
            
            suite.add_result(EvalResult(passed=True, input=case["input"], actual=result))
        
        return suite
```

Notice:
- **Plain Python** - No testing framework needed
- **Structured results** - Each result captures input, expected, actual, error
- **Composable** - Run one suite or many
- **Actionable** - Failures tell you exactly what went wrong

> 다음을 확인하세요:
> - **평범한 파이썬** - 별도의 테스트 프레임워크가 필요 없음
> - **구조화된 결과** - 각 결과가 입력, 기대값, 실제값, 오류를 담고 있음
> - **조합 가능성** - 스위트 하나만 실행할 수도, 여러 개를 실행할 수도 있음
> - **실행 가능성** - 실패 시 정확히 무엇이 잘못됐는지 알려줌

## The Golden Dataset
## 골든 데이터셋

Look at `evals/golden_datasets.py`:
> `evals/golden_datasets.py`를 살펴보세요:

```python
STRUCTURED_OUTPUT_GOLDEN = [
    {
        "input": "Explain quantum computing in one sentence",
        "schema": """{
  "topic": "the topic name as a string",
  "difficulty": "beginner" or "intermediate" or "advanced"
}

Example: {"topic": "machine learning", "difficulty": "intermediate"}""",
        "must_have_fields": ["topic", "difficulty"]
    },
]

TOOL_CALL_GOLDEN = [
    {
        "input": "What is 42 * 7?",
        "expected_tool": "calculator",
        "expected_args": {"operation": "multiply"}
    },
]

MEMORY_GOLDEN = [
    {
        "store_input": "My name is Alice",
        "query_input": "What's my name?",
        "expected_in_response": "Alice"
    },
]
```

Notice:
- **Multi-line schemas with examples** - Single-line schemas often confuse models
- **Version controlled** - These live in your repo
- **Cover edge cases** - Special characters, numbers, etc.
- **Specific assertions** - Not "it works" but "this field exists"

> 다음을 확인하세요:
> - **예시가 포함된 여러 줄 스키마** - 한 줄짜리 스키마는 종종 모델을 혼란스럽게 만듦
> - **버전 관리됨** - 이 데이터셋들은 저장소 안에 존재함
> - **엣지 케이스를 다룸** - 특수 문자, 숫자 등
> - **구체적인 검증** - "작동한다"가 아니라 "이 필드가 존재한다"는 식

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_11_evals()` method:
> `complete_example.py`의 `lesson_11_evals()` 메서드를 살펴보세요:

```python
from agent.agent import Agent
from agent.evals import AgentEval, print_eval_report
from evals.golden_datasets import (
    STRUCTURED_OUTPUT_GOLDEN,
    TOOL_CALL_GOLDEN,
    MEMORY_GOLDEN
)

agent = Agent("models/llama-3-8b-instruct.gguf")
evaluator = AgentEval(agent)

# Run all evals
results = evaluator.run_all(
    structured_cases=STRUCTURED_OUTPUT_GOLDEN,
    tool_cases=TOOL_CALL_GOLDEN,
    memory_cases=MEMORY_GOLDEN
)

# Print report
print_eval_report(results)
```

Example output:
> 출력 예시:

```
==================================================
EVAL REPORT
==================================================

Structured Output: ✓ PASSED (4/4)
Tool Calls: ✓ PASSED (5/5)
Memory Cycle: ✓ PASSED (3/3)

--------------------------------------------------
Overall: ✓ ALL PASSED (12/12)
==================================================
```
> ==================================================
> 평가 리포트
> ==================================================
>
> 구조화된 출력: ✓ 통과 (4/4)
> 도구 호출: ✓ 통과 (5/5)
> 메모리 사이클: ✓ 통과 (3/3)
>
> --------------------------------------------------
> 전체: ✓ 모두 통과 (12/12)
> ==================================================

Or when something breaks:
> 혹은 무언가 깨졌을 때:

```
==================================================
EVAL REPORT
==================================================

Structured Output: ✗ FAILED (3/4)
  ✗ Input: What does 'hello world' mean in progra...
    Expected: Fields: ['explanation']
    Actual: Missing: ['explanation']
    Error: Schema contract violated

--------------------------------------------------
Overall: ✗ 1 FAILED (11/12)
==================================================
```
> ==================================================
> 평가 리포트
> ==================================================
>
> 구조화된 출력: ✗ 실패 (3/4)
>   ✗ 입력: What does 'hello world' mean in progra...
>     기대값: 필드: ['explanation']
>     실제값: 누락됨: ['explanation']
>     오류: 스키마 계약 위반
>
> --------------------------------------------------
> 전체: ✗ 1건 실패 (11/12)
> ==================================================

## What to Test
## 무엇을 테스트할까

| Component | What to Eval | Example Assertion |
| --------- | ------------ | ----------------- |
| Structured output | JSON validity + schema contract | `parse_json(output) is not None and matches schema` |
| Decisions | Correct routing | `decision in valid_choices` |
| Tool calls | Correct tool + args | `tool_call["tool"] == "calculator"` |
| Memory | Store/retrieve cycle | `agent.memory.get_all()` contains saved fact |

> | 컴포넌트 | 평가할 것 | 검증 예시 |
> | --------- | ------------ | ----------------- |
> | 구조화된 출력 | JSON 유효성 + 스키마 계약 | `parse_json(output) is not None and matches schema` |
> | 의사결정 | 올바른 라우팅 | `decision in valid_choices` |
> | 도구 호출 | 올바른 도구 + 인자 | `tool_call["tool"] == "calculator"` |
> | 메모리 | 저장/검색 사이클 | `agent.memory.get_all()`에 저장된 사실이 있는가 |

## Compare to Lesson 03
## 레슨 03과 비교하기

**Lesson 03 (Structured Output):**
- One-off validation during generation
- Retry if JSON fails
- No history

> **레슨 03 (구조화된 출력):**
> - 생성 시점의 일회성 검증
> - JSON이 실패하면 재시도
> - 이력(history) 없음

**Lesson 11 (Evals):**
- Systematic testing across many cases
- Track success rates over time
- Catch regressions before deployment

> **레슨 11 (Evals):**
> - 많은 케이스에 걸친 체계적인 테스트
> - 시간에 따른 성공률 추적
> - 배포 전에 회귀를 잡아냄

## Key Insights
## 핵심 통찰

### Evals Are Just Assertions
### 평가는 그저 검증일 뿐이다

There's no magic here. You run the agent, check the output, report pass/fail. The power is in doing this systematically.
> 여기에 마법은 없습니다. 에이전트를 실행하고, 출력을 확인하고, 통과/실패를 보고할 뿐입니다. 힘은 이것을 체계적으로 수행하는 데 있습니다.

### Golden Datasets Are Your Contract
### 골든 데이터셋은 여러분의 계약이다

When someone asks "does the agent work?", you point to the golden dataset. 100% pass rate = it works. Anything less = specific failures to fix.
> 누군가 "이 에이전트가 잘 작동하나요?"라고 물으면, 골든 데이터셋을 가리키면 됩니다. 100% 통과율 = 작동한다는 뜻. 그보다 낮으면 = 고쳐야 할 구체적인 실패들이 있다는 뜻.

### Run Evals Before Every Change
### 변경할 때마다 평가를 실행하라

The workflow:
1. Make prompt change
2. Run evals
3. If any fail, fix or revert
4. Commit

> 워크플로우는 다음과 같습니다:
> 1. 프롬프트를 변경한다
> 2. 평가를 실행한다
> 3. 실패한 게 있으면 고치거나 되돌린다
> 4. 커밋한다

This is how you prevent quality degradation.
> 이것이 바로 품질 저하를 막는 방법입니다.

### Start Simple
### 단순하게 시작하라

You don't need 1000 test cases. Start with 5-10 golden cases per capability. Add more as you find edge cases in production.
> 1000개의 테스트 케이스가 필요한 것은 아닙니다. 능력별로 5~10개의 골든 케이스로 시작하세요. 프로덕션에서 엣지 케이스를 발견할 때마다 추가하면 됩니다.

## Common Issues
## 자주 발생하는 문제

**"Evals are too slow"**
- Run a smaller subset for quick checks
- Run full suite before commits
- Consider caching model loads

> **"평가가 너무 느려요"**
> - 빠른 확인을 위해 더 작은 부분집합을 실행하세요
> - 커밋 전에는 전체 스위트를 실행하세요
> - 모델 로드를 캐싱하는 것을 고려하세요

**"Soft assertions are flaky"**
- Start with hard assertions only
- Add soft ones when you have enough data
- Consider using exact match before semantic match

> **"소프트 검증이 불안정해요"**
> - 하드 검증만으로 시작하세요
> - 데이터가 충분히 쌓이면 소프트 검증을 추가하세요
> - 의미 비교 전에 정확 일치(exact match)를 먼저 사용하는 것을 고려하세요

**"I don't know what to test"**
- Start with the happy path
- Add cases that broke in production
- Cover edge cases (empty input, special chars, etc.)

> **"무엇을 테스트해야 할지 모르겠어요"**
> - 정상 경로(happy path)부터 시작하세요
> - 프로덕션에서 깨졌던 케이스를 추가하세요
> - 엣지 케이스(빈 입력, 특수 문자 등)를 다루세요

## Exercises
## 연습 문제

1. Add a new golden case that currently fails, then fix the prompt
2. Break a prompt intentionally and verify evals catch the regression
3. Add an edge case (empty input, very long input, unicode)
4. Create golden dataset for planning (Lesson 08)

> 1. 현재 실패하는 새로운 골든 케이스를 추가한 뒤 프롬프트를 고쳐보세요
> 2. 프롬프트를 일부러 망가뜨려보고 평가가 회귀를 잡아내는지 확인해보세요
> 3. 엣지 케이스(빈 입력, 아주 긴 입력, 유니코드)를 추가해보세요
> 4. 계획 수립(레슨 08)을 위한 골든 데이터셋을 만들어보세요

## What's Next?
## 다음 단계는?

In [Lesson 12](12_telemetry.md), we'll add **telemetry** - understanding what your agent is doing at runtime, not just in tests.
> [레슨 12](12_telemetry.md)에서는 **텔레메트리(telemetry)**를 추가합니다 — 테스트 안에서뿐만 아니라 실제 런타임에서 에이전트가 무엇을 하고 있는지 파악하는 것입니다.

---

**Key Takeaway:** Evals = systematic testing. Golden datasets = your contract. Run them before every prompt change.
> **핵심 요약:** 평가 = 체계적인 테스트. 골든 데이터셋 = 여러분의 계약. 프롬프트를 바꿀 때마다 실행하세요.
