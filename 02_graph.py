#의존성 검사, 병렬실행
#의존성이 없는 노드끼리는 실제로 스레드로 동시에 실행
from dotenv import load_dotenv
load_dotenv()

import json, time 
from concurrent.futures import ThreadPoolExecutor #병렬실행
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