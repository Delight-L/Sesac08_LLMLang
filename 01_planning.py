#흐름: 목표(goal) -> create_plan() -> {"steps": [...]}
#                 -> create_atomic_action(step) -> {action, inputs}  (단계마다 반복)
#                 -> execute_plan() -> 실행 결과 리스트
#atomic_action(원자적 액션) -> 실행가능한 작은 크기의 일 단위
#Agent : 목표, 실행, 수정 
from dotenv import load_dotenv 
load_dotenv()

from openai import OpenAI 
client = OpenAI()

#client와 소통(채팅 입력 -> 답변 반환)
def generate(prompt, temperature=0.5):
    completion = client.chat.completions.create(
        #playground의 사용가능한 모델을 선택
        #'추론'이 선행(깊은생각 후 답변)
        #https://developers.openai.com/api/docs/models
        model = 'gpt-4o', #'gpt-5-mini',
        temperature = 0.7,
        messages = [{'role':'user', 'content':prompt}]
    )
    return completion.choices[0].message.content

#[계획 생성]
def create_plan(goal, max_result=3):
    #goal은 사용자 입력을 그대로 쓸 수도 있고, ai가 가공해서 핵심을 넣을수도 있다.
    prompt = f'''
        아래의 목표를 달성하기 위한 단계별 계획을 세워라.
        반드시 json형태의 출력을 만들어라.

        형식 : {{'step':['1단계'], ['2단계'], ['3단계']}}

        목표 : {goal}
        '''

    for attempt in range(max_result):
        response = generate(prompt)
        #json형식을 파싱하는 함수 -> Langchain OutputParser
        plan = extract_json_from_text(response)
        #plan이라는 추출된 텍스트가 dictionary형태로, step이라는 키를 가졌냐?
        if plan and isinstance(plan.get('step'), list):
            return plan 
        print(f' 형식이 맞지 않아 재시도중 ... {attempt+1}/{max_result}')
    return None

#[JSON 파싱 유틸] -> LLM이 JSON 앞뒤에 설명이나 ```json 코드블록을 붙이는 경우가 많음
#                  그대로 json.loads() 하면 실패하므로, 잡다한 텍스트를 벗겨내고 순수 JSON만 추출
import json 
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

#플랜을 실행 가능한 '원자적 액션 단위'로 나눔
#step=> 계획(추출된 계획)
#max_result => 형식에 맞추어 여러 번 시도
def create_atomic_action(step, max_result=3):
    prompt = f'''
            아래의 계획 단계를 실행 가능한 원자적 액션으로 만들어줘.
            반드시 json만 결과물로 생성해.
            단계가 단순하면 객체 하나를, 여러개의 동작이 필요하면 객체의 배열을 출력해.

            
            형식(단일): {{"action": "행동_이름", "inputs": {{"key": "value"}}}}
            형식(복수): [{{"action": "행동_이름", "inputs": {{}}}}, {{"action": "행동_이름2", "inputs": {{}}}}]


            단계 {step}
            json만 출력
    '''

    for attempt in range(max_result):
        response = generate(prompt)
        parsed= extract_json_from_text(response)
        print(parsed)
        #형식(복수) : {{'action':'행동 이름', 'inputs' : {{}}, {{'action':'value'}}}}
        #parsed된 객체가 딕셔너리이고, 결과물에 action이 있다면 -> 양호한 응답을 받아 파싱 잘 한 사례
        if isinstance(parsed, dict) and 'action' in parsed:
            return [parsed]

        if isinstance(parsed, list) and parsed and all('action' in a for a in parsed):
            return parsed

        print(f'action 형식이 맞지 않아 재시도... [{attempt+1}/{max_result}]')
    return None

#[실행] -> 계획(데이터)과 실행(행동)을 분리
#중간에 실행이 끊기거나 문제가 생기더라도 복구 가능
def execute_plan(plan):
    if not plan or 'step' not in plan:
        return []

    results = []
    for i, step in enumerate(plan['step'], 1):
        #step별 action을 받아서 수행
        action = create_atomic_action(step)

        if action is None:
            results.append({'step':step, 'success':False, 'error':'액션 변환 실패'})
            continue

        print(f'action -> {action['action']}, inputs={action.get('inputs', {})}')
        results.append({'step':step, 'action':action, 'success':True})
    return results

if __name__ == '__main__':
    query = input('오늘은 무엇을 도와드릴까요?\n')
    #query == goal
    plan = create_plan(query)
    #print(plan)
    action = create_atomic_action(plan)
    result = execute_plan(plan)

    #print(f'{query}달성을 위해 세운 액션 : \n {action}')  
    print(f'액션을 실행한 결과 리스트 : {result}')