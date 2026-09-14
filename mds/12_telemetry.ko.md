# Lesson 12 - Telemetry (Runtime Observability)
# 레슨 12 - 텔레메트리 (런타임 관측가능성)

## What Question Are We Answering?
## 우리가 답하려는 질문은?

**"What is my agent actually doing at runtime?"**
**"내 에이전트는 런타임에서 실제로 무엇을 하고 있을까?"**

Evals tell you if the agent works before deployment. Telemetry tells you what's happening during deployment. Without telemetry, debugging is guesswork.
> 평가(evals)는 배포 전에 에이전트가 잘 작동하는지 알려줍니다. 텔레메트리는 배포 중에 무슨 일이 일어나고 있는지 알려줍니다. 텔레메트리가 없으면 디버깅은 추측에 불과합니다.

## What You Will Build
## 무엇을 만들게 되나요?

A telemetry system that:
- Logs every LLM call with inputs and outputs
- Tracks tool call success/failure rates
- Measures latency and retry counts
- Enables post-hoc debugging with traces

> 다음을 수행하는 텔레메트리 시스템을 만듭니다:
> - 모든 LLM 호출을 입력·출력과 함께 기록한다
> - 도구 호출의 성공/실패율을 추적한다
> - 지연 시간과 재시도 횟수를 측정한다
> - 트레이스를 통한 사후 디버깅을 가능하게 한다

## New Concepts Introduced
## 새로 등장하는 개념

### 1. Structured Logging
### 1. 구조화된 로깅(Structured Logging)

**Structured logging** means JSON logs, not print statements. Every log entry has a consistent schema: timestamp, event type, data, error.
> **구조화된 로깅**이란 print문이 아니라 JSON 형태의 로그를 뜻합니다. 모든 로그 항목은 타임스탬프, 이벤트 타입, 데이터, 오류라는 일관된 스키마를 가집니다.

```json
{"event_type": "llm_call", "timestamp": "2024-01-15T10:30:00", "duration_ms": 1523, "success": true}
```

This is searchable, parseable, and machine-readable.
> 이는 검색 가능하고, 파싱 가능하며, 기계가 읽을 수 있습니다.

### 2. Spans and Traces
### 2. 스팬(Spans)과 트레이스(Traces)

A **span** is one operation - a single LLM call, one tool execution, one memory access.
> **스팬**은 하나의 연산입니다 — 하나의 LLM 호출, 하나의 도구 실행, 하나의 메모리 접근 등.

A **trace** is a full agent interaction - multiple spans linked together by a trace ID.
> **트레이스**는 하나의 완전한 에이전트 상호작용입니다 — 트레이스 ID로 서로 연결된 여러 개의 스팬입니다.

When something fails, you find the trace and see exactly what happened step by step.
> 무언가 실패했을 때, 해당 트레이스를 찾아 단계별로 정확히 무슨 일이 있었는지 확인할 수 있습니다.

### 3. Metrics
### 3. 지표(Metrics)

**Metrics** are aggregated numbers:
- `llm_success_rate` - How often does JSON parse correctly?
- `avg_latency_ms` - How long do LLM calls take?
- `tool_failure_rate` - How often do tool calls fail?

> **지표**는 집계된 수치입니다:
> - `llm_success_rate` - JSON이 얼마나 자주 올바르게 파싱되는가?
> - `avg_latency_ms` - LLM 호출이 얼마나 오래 걸리는가?
> - `tool_failure_rate` - 도구 호출이 얼마나 자주 실패하는가?

Metrics tell you the health of your agent at a glance.
> 지표는 에이전트의 건강 상태를 한눈에 알려줍니다.

## What We Are NOT Doing (Yet)
## 아직 다루지 않는 것

- No distributed tracing (single machine only)
- No production dashboards (file-based logging)
- No alerting (manual inspection)
- No OpenTelemetry (keeping it simple)

> - 분산 트레이싱은 다루지 않음 (단일 머신만 다룸)
> - 프로덕션 대시보드는 다루지 않음 (파일 기반 로깅만 다룸)
> - 알림(alerting)은 다루지 않음 (수동 점검)
> - OpenTelemetry는 다루지 않음 (단순하게 유지)

## The Code
## 코드

Look at `agent/telemetry.py`:
> `agent/telemetry.py`를 살펴보세요:

```python
import json
import time
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Span:
    """A single operation in a trace."""
    span_id: str
    trace_id: str
    event_type: str
    timestamp: str
    duration_ms: Optional[float] = None
    data: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class Metrics:
    """Aggregated metrics for the agent."""
    llm_calls: int = 0
    llm_failures: int = 0
    llm_retries: int = 0
    tool_calls: int = 0
    tool_failures: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.llm_calls if self.llm_calls > 0 else 0.0
    
    @property
    def llm_success_rate(self) -> float:
        return 1 - (self.llm_failures / self.llm_calls) if self.llm_calls > 0 else 0.0


class Telemetry:
    """Simple telemetry for agent observability."""
    
    def __init__(self, log_file: str = "agent_telemetry.jsonl"):
        self.log_file = log_file
        self.current_trace_id = None
        self.metrics = Metrics()
    
    def start_trace(self) -> str:
        """Start a new trace (one full agent interaction)."""
        self.current_trace_id = str(uuid4())[:8]
        return self.current_trace_id
    
    def log_llm_call(self, prompt_length: int, response_length: int, 
                     duration_ms: float, success: bool = True, error: str = None):
        """Log an LLM call."""
        span = Span(
            span_id=str(uuid4())[:8],
            trace_id=self.current_trace_id or "no-trace",
            event_type="llm_call",
            timestamp=datetime.now().isoformat(),
            duration_ms=round(duration_ms, 2),
            data={"prompt_length": prompt_length, "response_length": response_length},
            error=error
        )
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(span)) + "\n")
        
        # Update metrics
        self.metrics.llm_calls += 1
        self.metrics.total_latency_ms += duration_ms
        if not success:
            self.metrics.llm_failures += 1
```

Notice:
- **Dataclasses** - Clean, typed structures
- **JSONL format** - One JSON object per line, easy to parse
- **Metrics accumulation** - Track aggregates as we go
- **Trace linking** - All spans share a trace ID

> 다음을 확인하세요:
> - **데이터클래스** - 깔끔하고 타입이 있는 구조
> - **JSONL 형식** - 한 줄에 하나의 JSON 객체, 파싱하기 쉬움
> - **지표 누적** - 진행하면서 집계값을 추적함
> - **트레이스 연결** - 모든 스팬이 트레이스 ID를 공유함

## How to Run
## 실행 방법

Look at `complete_example.py`, see `lesson_12_telemetry()` method:
> `complete_example.py`의 `lesson_12_telemetry()` 메서드를 살펴보세요:

```python
from agent.agent import Agent
from agent.telemetry import Telemetry

agent = Agent("models/llama-3-8b-instruct.gguf")
telemetry = Telemetry()

# Start a trace
trace_id = telemetry.start_trace()
print(f"Trace ID: {trace_id}")

# Simulate some operations (in real usage, these come from instrumented agent)
import time

start = time.time()
result = agent.generate_structured("What is Python?", '{"answer": string}')
duration = (time.time() - start) * 1000

telemetry.log_llm_call(
    prompt_length=100,
    response_length=len(str(result)),
    duration_ms=duration,
    success=result is not None
)

# Check metrics
telemetry.print_summary()
```

Example output:
> 출력 예시:

```
========================================
TELEMETRY SUMMARY
========================================
LLM Calls:      3
  Success Rate: 100.00%
  Avg Latency:  1245ms
  Retries:      0
Tool Calls:     2
  Success Rate: 100.00%
Memory Ops:     1
========================================
```
> ========================================
> 텔레메트리 요약
> ========================================
> LLM 호출:      3
>   성공률:      100.00%
>   평균 지연시간: 1245ms
>   재시도:      0
> 도구 호출:      2
>   성공률:      100.00%
> 메모리 연산:    1
> ========================================

## Viewing the Log File
## 로그 파일 살펴보기

The telemetry logs to `agent_telemetry.jsonl`:
> 텔레메트리는 `agent_telemetry.jsonl`에 로그를 남깁니다:

```jsonl
{"span_id": "a1b2c3d4", "trace_id": "x9y8z7w6", "event_type": "llm_call", "timestamp": "2024-01-15T10:30:00.123456", "duration_ms": 1523.45, "data": {"prompt_length": 256, "response_length": 89, "success": true}}
{"span_id": "e5f6g7h8", "trace_id": "x9y8z7w6", "event_type": "tool_call", "timestamp": "2024-01-15T10:30:02.456789", "duration_ms": 5.23, "data": {"tool": "calculator", "arguments": {"a": 42, "b": 7, "operation": "multiply"}}}
```

To debug a specific interaction, filter by trace_id:
> 특정 상호작용을 디버깅하려면 trace_id로 필터링하세요:
```bash
grep "x9y8z7w6" agent_telemetry.jsonl
```

## What to Log
## 무엇을 기록할까

| Event | Data to Capture | Why |
|-------|-----------------|-----|
| LLM call | prompt_length, response_length, duration_ms, success | Track latency, identify slow/failing calls |
| Tool request | tool_name, arguments | Debug wrong tool selection |
| Tool execution | tool_name, result, error | Debug tool failures |
| Memory operation | operation, data | Track what's being stored/retrieved |
| Decision | choices, selected | Debug routing issues |

> | 이벤트 | 기록할 데이터 | 이유 |
> |-------|-----------------|-----|
> | LLM 호출 | prompt_length, response_length, duration_ms, success | 지연 시간 추적, 느리거나 실패하는 호출 식별 |
> | 도구 요청 | tool_name, arguments | 잘못된 도구 선택 디버깅 |
> | 도구 실행 | tool_name, result, error | 도구 실패 디버깅 |
> | 메모리 연산 | operation, data | 무엇이 저장/검색되는지 추적 |
> | 의사결정 | choices, selected | 라우팅 문제 디버깅 |

## Compare to Lesson 11
## 레슨 11과 비교하기

**Lesson 11 (Evals):**
- Run before deployment
- Known inputs, expected outputs
- Binary pass/fail
- Catches regressions

> **레슨 11 (Evals):**
> - 배포 전에 실행됨
> - 알려진 입력, 기대되는 출력
> - 이분법적인 통과/실패
> - 회귀를 잡아냄

**Lesson 12 (Telemetry):**
- Run during deployment
- Unknown inputs, observed outputs
- Continuous monitoring
- Enables debugging

> **레슨 12 (텔레메트리):**
> - 배포 중에 실행됨
> - 알 수 없는 입력, 관찰된 출력
> - 지속적인 모니터링
> - 디버깅을 가능하게 함

They're complementary. Evals prevent bad code from shipping. Telemetry helps you understand what shipped code is doing.
> 이 둘은 상호보완적입니다. 평가는 나쁜 코드가 배포되는 것을 막아줍니다. 텔레메트리는 이미 배포된 코드가 무엇을 하고 있는지 이해하도록 도와줍니다.

## Key Insights
## 핵심 통찰

### Telemetry is Just Structured Logging
### 텔레메트리는 그저 구조화된 로깅일 뿐이다

No magic. You're writing JSON to a file. The power is in:
- Consistent schema
- Trace IDs linking related events
- Aggregated metrics

> 마법은 없습니다. 그저 파일에 JSON을 쓰는 것뿐입니다. 힘은 다음에 있습니다:
> - 일관된 스키마
> - 관련된 이벤트들을 연결하는 트레이스 ID
> - 집계된 지표

### Traces Are Your Debugging Superpower
### 트레이스는 디버깅의 초능력이다

When a user reports "the agent gave a weird answer", you:
1. Get the trace ID
2. Find all spans for that trace
3. See exactly what happened

Without traces, you're guessing.

> 사용자가 "에이전트가 이상한 답을 줬어요"라고 신고하면, 여러분은:
> 1. 트레이스 ID를 확보하고
> 2. 그 트레이스에 속한 모든 스팬을 찾고
> 3. 정확히 무슨 일이 있었는지 확인합니다
>
> 트레이스가 없다면 그저 추측할 뿐입니다.

### Metrics Tell You System Health
### 지표는 시스템의 건강 상태를 알려준다

Glance at metrics to know if something's wrong:
- Success rate dropping? Check for prompt issues
- Latency increasing? Check model/hardware
- Retries increasing? Check JSON parsing

> 지표를 한번 훑어보는 것만으로 무언가 잘못됐는지 알 수 있습니다:
> - 성공률이 떨어지고 있나요? 프롬프트 문제를 확인하세요
> - 지연 시간이 늘고 있나요? 모델/하드웨어를 확인하세요
> - 재시도가 늘고 있나요? JSON 파싱을 확인하세요

### Start Simple, Add More Later
### 단순하게 시작하고, 나중에 더하라

This implementation logs to a file. That's enough to start. Later you might add:
- Database storage
- Real-time dashboards
- Alerting on thresholds

But start with a file.

> 이 구현은 파일에 로그를 남깁니다. 시작하기엔 그것으로 충분합니다. 나중에 다음을 추가할 수도 있습니다:
> - 데이터베이스 저장
> - 실시간 대시보드
> - 임계치 기반 알림
>
> 하지만 파일로 시작하세요.

## Common Issues
## 자주 발생하는 문제

**"The log file is too big"**
- Rotate logs (new file per day/hour)
- Only log failures in production
- Truncate long data fields

> **"로그 파일이 너무 커요"**
> - 로그를 로테이션하세요 (하루/시간마다 새 파일)
> - 프로덕션에서는 실패만 기록하세요
> - 긴 데이터 필드는 잘라내세요

**"I can't find the trace I need"**
- Add trace IDs to user-facing errors
- Log trace IDs in your application logs
- Consider adding user IDs to traces

> **"필요한 트레이스를 찾을 수 없어요"**
> - 사용자에게 보이는 오류에 트레이스 ID를 추가하세요
> - 애플리케이션 로그에 트레이스 ID를 기록하세요
> - 트레이스에 사용자 ID를 추가하는 것을 고려하세요

**"Telemetry is slowing down my agent"**
- Log asynchronously (buffer, then write)
- Reduce data captured per span
- Sample instead of logging everything

> **"텔레메트리가 에이전트를 느리게 만들어요"**
> - 비동기로 로깅하세요 (버퍼링 후 쓰기)
> - 스팬마다 기록하는 데이터를 줄이세요
> - 모든 것을 기록하는 대신 샘플링하세요

## Exercises
## 연습 문제

1. Add telemetry to the agent loop and trace a full multi-step interaction
2. Calculate JSON parse success rate across 20 structured output calls
3. Compare latency between different prompt lengths
4. Find a failing span in the logs and debug what went wrong

> 1. 에이전트 루프에 텔레메트리를 추가하고 다단계 상호작용 전체를 추적해보세요
> 2. 구조화된 출력 호출 20회에 걸친 JSON 파싱 성공률을 계산해보세요
> 3. 서로 다른 프롬프트 길이 사이의 지연 시간을 비교해보세요
> 4. 로그에서 실패한 스팬을 찾아 무엇이 잘못됐는지 디버깅해보세요

## What's Next?
## 다음 단계는?

Congratulations! You've completed the core curriculum.
> 축하합니다! 핵심 커리큘럼을 모두 마쳤습니다.

You now have an agent with:
- Structured outputs (Lesson 03)
- Decision making (Lesson 04)
- Tool calling (Lesson 05)
- Agent loop (Lesson 06)
- Memory (Lesson 07)
- Planning (Lesson 08)
- Atomic actions (Lesson 09)
- Dependency graphs (Lesson 10)
- Regression testing (Lesson 11)
- Runtime observability (Lesson 12)

> 여러분은 이제 다음을 갖춘 에이전트를 가지고 있습니다:
> - 구조화된 출력 (레슨 03)
> - 의사결정 (레슨 04)
> - 도구 호출 (레슨 05)
> - 에이전트 루프 (레슨 06)
> - 메모리 (레슨 07)
> - 계획 수립 (레슨 08)
> - 원자적 행동 (레슨 09)
> - 의존관계 그래프 (레슨 10)
> - 회귀 테스트 (레슨 11)
> - 런타임 관측가능성 (레슨 12)

This is a complete, observable, testable agent built from first principles.
> 이것은 기본 원리로부터 구축된, 완전하고, 관측 가능하고, 테스트 가능한 에이전트입니다.

---

**Key Takeaway:** Telemetry = structured logging + traces + metrics. It turns "something's wrong" into "here's exactly what happened."
> **핵심 요약:** 텔레메트리 = 구조화된 로깅 + 트레이스 + 지표. 이는 "뭔가 잘못됐다"를 "정확히 무슨 일이 있었는지 여기 있다"로 바꿔줍니다.
