import time  #실행시간
from datetime import datetime #연월일 등 정보
from zoneinfo import ZoneInfo #타임존(태평양시... 미국 기준시... etc)

import config
import requests

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

def _call_tool():
    pass

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

#
def _flatten(items):
    """LLM이 {"foods": [...]} 처럼 감싸서 줄 때도, 배열로 줄 때도 처리."""
    if isinstance(items, dict):
        return [i for sub in items.values() 
                    for i in (sub if isinstance(sub, list) else [sub])]
    if isinstance(items, list):
        return [str(items)]

    return items


#'''(독스트링)''' -> 함수의 역할에 대해 공식적인 설명 
def classify_intent(state : dict):
    """사용자 입력을 food / activity / unknown 중 하나로 분류."""

    print(f'의도파악중....')
    user_input = state.get("user_input", "")

    prompt = f"""
    당신은 사용자의 자연어 입력을 food / activity / unknown 중 하나로 분류하는 AI입니다.

    입력: "{user_input}"

    분류 기준:
    - 음식 관련 표현 → "food" (예: 배고파, 뭐 먹지, 야식 추천해줘 등)
    - 활동 관련 표현 → "activity" (예: 심심해, 뭐 하지, 놀고 싶어 등)
    - 증상, 감정, 질문, 애매한 표현 → "unknown"

    조금 애매한 표현이라도 의미가 보이면 food 또는 activity로 분류하세요.

    출력은 반드시 다음 중 하나의 JSON 배열 또는 객체로 작성하세요:
    - 배열: ["food"]
    - 객체: {{ "intent": ["food"] }}
    """

    #'role'이 'user'면 gpt에게 위의 프롬프트 내용을 전달
    messages = [{'role':'user', 'content':prompt.strip()}]
    #json파싱을 하도록 세팅해놓은 llm에게 프롬프트를 전달
    response = _call_llm(llm_json, messages=messages)
    if response is None:
        return {**state, 'intent':'unknown'}

    intent = response.content.strip()

    #intent를 파싱
    import json
    import traceback
    try:
        parsed = json.loads(intent)

        #파싱된 데이터의 형식이 list이고, parsed객체 None이 아니며, parsed내용물이 존재하면
        if isinstance(parsed, list) and parsed and parsed[0]:
            return {**state, 'intent':parsed[0]}

        #파싱된 데이터의 형식이 dict이고, 'intent'라는 키가 존재하면
        if isinstance(parsed, dict) and 'intent' in parsed:
            value = parsed['intent']
            if isinstance(value, list) and value and value[0]:
                return {**state, 'intent':value[0]}

            for key in ['food', 'activity']:
                if key in parsed:
                    return {**state, 'intent':key}

    except Exception as e:
        print(traceback.format_exc())

    return {**state, 'intent':'unknown'}



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
    '''카카오맵 API를 활용하여 search_keyword로 생성된 단어를 검색'''
    print('search_place...')
    location = state.get('location', '서울')
    keyword = state.get('search_keyword', '추천')
    query = f'{location} {keyword}'
    print(f'카카오맵 검색어 : {query}')

    #API 사용방법
    def _fetch():
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {'query':query, 'size':1}
        headers = {'Authorization':f'KakaoAK {config.KAKAO_API_KEY}'} #API KEY를 코드로 전달
        resq = requests.get(url, 
                            headers=headers,
                            params=params,
                            timeout=5)

        resq.raise_for_statue()
        return resq.json()['documents']
    #docs = resq.json()['documents']
    docs = _call_tool('kakao_search', _fetch, query=query)
    if docs:
        top=docs[0]
        place = {'name':top['place_name'], 
                 "address": top["road_address_name"], 
                 "url": top["place_url"]}
    else:
        place = {'name':'', "address": '', "url": ''}
    return {**state, 'recommend_place':place}
        
def summarize_output(state:dict):
    print('summarize_output...')

def handle_exception(state:dict):
    print('exception! ')

