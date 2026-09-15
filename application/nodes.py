import time  #실행시간
from datetime import datetime #연월일 등 정보
from zoneinfo import ZoneInfo #타임존(태평양시... 미국 기준시... etc)

#랭그래프 내부에서 답변을 주는 chatgpt를 분리해서 사용 -> json포맷을 지키는 gpt
from langchain_openai import ChatOpenAI
llm_json = ChatOpenAI(
    model = 'gpt-4o',
    temperature = 0.3,
    model_kwargs={'response_format':{'type':'json_object'}}
)

llm_normal = ChatOpenAI(
    model = 'gpt-4o',
    temperature = 0.7,
)

#각 함수들이 gpt에 말을 걸 때 사용가능한 기본 함수(랭그래프X, 기능적필요O) 작성
def _call_llm(llm, messages, max_attempts=3):
    #정해진 횟수만큼 gpt와 통신을 시도
    for attempt in range(max_attempts):
        #통신 진행
        try : 
            response = llm.invoke(messages)
            return response

        #에러 발생시 이쪽으로 빠짐
        except Exception as e:
            print(f'_call_llm 에러 발생 : {e}')

    print(f'{max_attempts}만큼의 통신 시도 실패')
    return None
    




def classify_intent(state : dict):
    print(f'의도파악중....')

def get_time_slot(state: dict) -> dict:
    KST = ZoneInfo("Asia/Seoul")
    hour = datetime.now(KST).hour
    if 5 <= hour < 11:
        timeslot = "아침"
    elif 11 <= hour < 14:
        timeslot = "점심"
    elif 14 <= hour < 18:
        timeslot = "오후"
    else:
        timeslot = "저녁"
    return {**state, "timeslot": timeslot}

def get_season(state: dict) -> dict:
    KST = ZoneInfo("Asia/Seoul")
    m = datetime.now(KST).month
    if 3 <= m < 6:
        season = "봄"
    elif 6 <= m < 10:
        season = "여름"
    elif 10 <= m < 11:
        season = "가을"
    else:
        season = "겨울"
    return {**state, "season": season}

def get_weather(state:dict):
    print('get_weather....')

def recommend_food(state:dict):
    print('recommend_food')

def recommend_activity(state:dict):
    print('recommend_activity')

def generate_search_keyword(state:dict):
    print('search keyword...')

def search_place(state:dict):
    print('search_place...')

def summarize_output(state:dict):
    print('summarize_output...')

def handle_exception(state:dict):
    print('exception! ')

