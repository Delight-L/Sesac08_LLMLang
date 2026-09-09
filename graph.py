#랭그래프 3요소
#  상태(State) : 노드들이 주고받는 데이터. TypedDict로 자료형을 고정
#  노드(Node)  : 상태를 받아서 "바뀐 부분만" 딕셔너리로 돌려주는 함수
#  엣지(Edge)  : 노드를 잇는 화살표. 조건부 엣지면 갈림길이 생김
from typing import TypedDict, Literal 
#START, END 
from langgraph.graph import StateGraph, START, END 

#1. 상태 그래프를 만듦 
#상태(그래프가 흐를 때 같이 가야 함) -> 중간에 타입변형이 오면 캐치할 수 있도록 
class ShinppingState(TypedDict):
    order_id : str #주문 번호
    city : str     #배송지
    address : str  #상세주소
    weather : str  #날씨
    decision : str #배송 출고 여부
    reason : str   #판단 근거

WEATHER_DB = {
    '서울': '맑음',
    '부산': '비',
    '대구': '눈',
    '광주': '흐림',
    '제주': '비',
}

#2.노드 생성 
#**** 노드는 반드시 '상태'를 매개변수로 가진다.
def check_weather(state:ShinppingState):
    #딕셔너리.get(키, 디폴트값) -> 키에 맞는 값이 나옴. 
    weather = WEATHER_DB.get(state['city'], '맑음')
    print(f'날씨 체크 : {state['city']} -> {weather}')
    return {'weather': weather}


def route_by_weather(state :ShinppingState):
    if state['weather'] == '비' :
        return 'hold'
    return 'delivery'
  
def start_delivery(state:ShinppingState):
    print(f'{state['address']}로 배달을 시작합니다.')
    return {'decision':'배송 진행', 
            'reason' : f'{state['city']} 지역 날씨가 {state['weather']} 이므로 배송 진행' }

def hold_delivery(state:ShinppingState):
    print(f'배송을 중단합니다.')
    return {'decision':'배송 중단', 
            'reason' : f'{state['city']} 지역 날씨가 {state['weather']} 이므로 배송 중단' }


#3. 노드 연결(그래프 빌드)
def build_graph():
    workflow = StateGraph(ShinppingState)

    workflow.add_node('check_weather', check_weather)
    workflow.add_node('start_delivery', start_delivery)
    workflow.add_node('hold_delivery', hold_delivery)



