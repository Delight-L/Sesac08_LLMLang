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
        model = 'gpt-5-mini',
        #temperature = 0.7,
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
        ##



if __name__ == '__main__':
    query = input('오늘은 무엇을 도와드릴까요?\n')
    response = generate(query)
    print(response)