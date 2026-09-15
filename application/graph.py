#그래프의 생김새 정의
#노드, 엣지 연결
from typing import TypedDict 
from langgraph.graph import StateGraph, END

#그래프를 따라다닐 state 정의
class State(TypedDict):
    user_input :str
    location :str 
    timeslot :str 
    season : str 
    weather : str 
    intent : str 
    recommend_items : list 
    search_keywords : str 
    recommend_place : dict 
    final_message : str 

#갈림길에서 어디로 연결할 것인가?
def route_intent(state:State):
    #그래프 내부의 상태(state)에서 intent를 가져와서, 상태별로 위치 분기
    intent = state.get('intent', '')

    if intent == 'food':
        return 'recommend_food'
    elif intent == 'activity':
        return 'recommend_activity'
    else:
        return 'unexpected'

import nodes #nodes.py에 우리가 사용할 함수들을 몰아서 작성
def build_graph():

    #그래프를 따라다닐 상태 세팅
    build = StateGraph(State)

    build.add_node('classify_intent', nodes.classify_intent)
    build.add_node('get_time_slot', nodes.get_time_slot)
    build.add_node('get_season', nodes.get_season)
    build.add_node('get_weather', nodes.get_weather)
    build.add_node('recommend_food', nodes.recommend_food)
    build.add_node('recommend_activity', nodes.recommend_activity)
    build.add_node('generate_keyword', nodes.generate_search_keyword)
    build.add_node('search_place', nodes.search_place)
    build.add_node('summarize_output', nodes.summarize_output)
    build.add_node('handle_exception', nodes.handle_exception)

    build.set_entry_point('classify_intent') #시작점 정의
    build.add_edge('classify_intent', 'get_time_slot')
    build.add_edge('get_time_slot', 'get_season')
    build.add_edge('get_season', 'get_weather' ) 
    build.add_conditional_edges('get_weather', route_intent, 
                                #route_intend 함수가 리턴하는 값 : 이동할 노드 이름
                                {'recommend_food': 'recommend_food',
                                 'recommend_activity' : 'recommend_activity',
                                 'unexpected': 'handle_exception'})

    build.add_edge('handle_exception', END)
    build.add_edge('recommend_food', 'generate_keyword')
    build.add_edge('recommend_activity', 'generate_keyword')
    build.add_edge('generate_keyword', 'search_place')
    build.add_edge('search_place', 'summarize_output')
    build.add_edge('summarize_output', END)
    return build.compile()