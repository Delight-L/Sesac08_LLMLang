#프롬프트를 한 글자만 고쳐도 JSON 파싱이 깨지거나, 분류 결과가 틀어질 수 있음
#eval은 "이 입력엔 이런 결과가 나와야 한다"를 미리 정해두고,
#프롬프트/로직을 바꿀 때마다 다시 돌려서 틀린 output을 잡아내는 장치
#golden dataset : 항상 통과해야 하는 정답 세트. 여기서 실패하면 테스트가 아니라 에이전트가 문제
#hard assertion : 반드시 지켜야 함        (예: JSON 형식이 맞는가)
#soft assertion : 대체로 맞으면 됨        (예: 표현이 자연스러운가)
from dotenv import load_dotenv
load_dotenv()

import json 
from typing import Any 
from dataclasses import dataclass, field 

#클래스 정의~
@dataclass 
class EvalResult:
    passed : bool  #나의 평가 통과 여부(True/False)
    input : str    #내가 입력한 결과(gpt결과물)
    expected : Any = None  #나는 이렇게 받길 원해
    actual : Any = None    #실제로 받은 것
    error : str = None     #에러가 일어난 것

#@(데코레이터) ->함수나 클래스를 감싸서 함수나 클래스에 부가기능 +(자동완성)
#@dataclass -> 원래 class에 필요한 __init__, __repr__, __eq__ 필요함수를 자동 세팅
@dataclass 
class EvalSuiteResult:
    name : str 
    passed : int = 0 
    failed : int = 0
    #eval = EvalSuiteResult(), eval.result (list형식의 변수 생성)
    #eval1, eval2...... 각각 eval1.result, eval2.result = list 강제
    results : list = field(default_factory=list)

    #어디가 틀렸을까요?
    #eval = EvalSuiteResult()
    #eval.total -> 함수이지만 함수가 아닌것처럼 느껴짐
    @property
    def total(self):
        return self.passed + self.failed

    @property
    def pass_rate(self):
        return self.passed / self.total if self.total > 0 else 0.0

    def add(self, result):
        self.results.append(result)
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self):
        status = '전부 통과' if self.failed == 0 else '일부 통과'
        return f'{self.name} -> status {status} 통과 비율 : {self.pass_rate}'


#특정한 덩어리 -> 출력양식을 몇 개나 지켰니? 검사
def run_eval_suite(name, cases, run_fn, check_fn):
    suite = EvalSuiteResult(name=name)

    for case in cases:
        try : 
            acutual = run_fn(case['input'])
            passed = check_fn(acutual, case.get('expected'))
            result = EvalResult(passed=passed,
                                input=case['input'],
                                expected=case.get('expected'),
                                acutual=acutual)

        except Exception as e:
            result = EvalResult(passed=False, input=case['input'],
                                error=str(e))

        suite.add(result)
    return suite

JSON_PARSING_CASES = [
    {'input': '{"steps": ["a", "b"]}', 'expected': True},
    {'input': '```json\n{"steps": ["a"]}\n```', 'expected': True},
    {'input': '물론이죠! 계획은 다음과 같습니다: {"steps": ["a"]}', 'expected': True},
    {'input': '죄송하지만 계획을 세울 수 없습니다.', 'expected': False},  # JSON이 아예 없음 -> 실패해야 정상
    {'input': '', 'expected': False},
]

def check_has_steps(actual, expected):
    #expected=True면 steps 리스트가 있어야 통과, False면 파싱 실패(None)해야 통과
    got_valid = actual is not None and isinstance(actual.get('steps'), list)
    return got_valid == expected

def extract_json_from_text(response):
    if not response:
        return None 
    #' ``(백틱)
    text = response
    if response.startswith('```'):
        text = response.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    text = text.strip()

    #리스트에 대비
    if text.startswith('['):
        open_t, close_t = '[', ']'
    else:
        open_t, close_t = '{', '}'

    start, end = text.find(open_t), text.rfind(close_t)
    if start == -1 or end == -1:
        return None 

    try:
        return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return None

if __name__ == '__main__':
    step1 = run_eval_suite('json_parsing', JSON_PARSING_CASES, 
                   run_fn=extract_json_from_text, 
                   check_fn=check_has_steps)

    print(step1.summary())