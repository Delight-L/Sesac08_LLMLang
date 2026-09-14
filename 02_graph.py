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


#의존성 그래프 생성 -> 노드(함수)마다 id를 가짐
#depends_on -> 비어있으면 개별적으로 실행 가능한 독립적인 일
def create_depend_graph(goal, max_result=3):
    prompt = f'''
            다음 목표를 달성하기 위해 실행 그래프를 만드세요.
            Json만 출력하고,
            서로 관계없는 작업은 depends_on이라는 요소를 비워두고,
            앞 작업의 결과가 필요한 작업은 depends_on에 
            그 작업의 id를 적어주세요.

            형식: {{"nodes": [
        {{"id": "1", "action": "경쟁사_조사", "depends_on": []}},
        {{"id": "2", "action": "시장_조사", "depends_on": []}},
        {{"id": "3", "action": "초안_작성", "depends_on": ["1", "2"]}}
        ]}}

        목표: {goal}

        
        JSON만 출력: '''

    for attempts in range(max_result):
        response = generate(prompt)
        graph = extract_json_from_text(response=response)

        #1.graph라는 객체가 존재하고(None이 아니고)
        if (graph) and (isinstance(graph.get('nodes'), list)) and (graph['nodes']) :
                #graph가 list냐? / 
                #graph['nodes']라는 값이 존재하니?    
            return graph 
        print(f'재시도 중... {attempts+1}/{max_result}') 
    return None 

#병렬적인 그래프 실행
def execute_graph(graph):
    #{'nodes': [{'id': '1', 'action': '컴퓨터_전원_끄기', 'depends_on': []}, {'id': '2', 'action': '케이스_열기',
    #1:{'id': '1', 'action': '컴퓨터_전원_끄기', 'depends_on': []}
    #2:{'id': '2', 'action': '케이스_열기', 'depends_on': ['1']}
    nodes = {n['id']:n for n in graph['nodes']}
    done = set() #마친 일
    results = [] #마친 결과

    section = 1 #한 덩어리의 묶음 실행(병렬실행 가능 단위)
    # 마친 일의 길이 < 노드의 일의 길이보다 작다. => 일이 남은동안 while해라.
    while len(done) < len(nodes):
        #nid -> 1, 2, .... n => {'id': '1', 'action': '컴퓨터_전원_끄기', 'depends_on': []}
        #nodes.items() -> 딕셔너리 nid(키), n(값)
        ready = [n for nid, n in nodes.items()
                 #nid not in done : 마치지 않은 nid -> 해야하는 일
                 if nid not in done and all(d in done for d in n.get('depends_on', []))]

        #ready가 없음 -> 할일이 없음/depends_on이 없는 노드만 남았다!
        if not ready:
            print(f'더 이상 실행가능한 노드가 없음(검증되지 않음)')
            break 

        print(f'섹션 {section} 동시 실행 : {[n['action'] for n in ready]}')
        #지금 task를 할 때 시간 기록 
        t0 = time.time()

        #병렬실행 어떻게? len(ready) 만큼
        with ThreadPoolExecutor(max_workers=len(ready)) as executor:
            #map -> 
            outputs = list(executor.map(lambda n : run_action(n['action']), ready))

        elapsed = time.time() - t0
        print(f'elapsed 걸린 시간 : {elapsed} ')

        for n, out in zip(ready, outputs):
            results.append({'id':n['id'], 'action':n['action'], 'result':out})
            done.add(n['id'])
        section += 1 
    return results 

def run_action(action):
    time.sleep(1)
    return f'{action} 완료'


#검증 -> 선행 step에 대한 의존성 검증(그래프가 순환하지 않는가?)
#DFS 
def valid_graph(graph):
    nodes = graph['nodes']
    ids = {n['id'] for n in nodes}

    for n in nodes:
        for d in n.get('depends_on', []):
            if d not in ids:
                return False, f'{n['id']}가 존재하지 않는 {d}를 참조함'

    #DFS 
    # {4 : [2, 3], 5:[4], ...}
    graph_maps = {n['id'] : n.get('depends_on', []) for n in nodes}
    visiting, visited = set(), set() #set을 왜 쓸까? -> 중복없음
    #재귀적(내가 나를 부르는) 호출
    def has_cycle(node_id):

        if node_id in visiting:
            print(f'True -> {node_id}')
            return True

        if node_id in visited:
            print(f'False -> {node_id}')
            return False

        visiting.add(node_id)
        #1, 2, 3, 4, 5, .....
        #4 => [2, 3] (2와 3이 dep임)
        #5 => 4 => [2, 3]
        for dep in graph_maps.get(node_id, []):
            # has_cycle(2) / has_cycle(3) 
            if has_cycle(dep):
                return True

        #1번 -> 의존 노드 없음 -> visited목록에 1번 추가 (F)
        #2번 -> 의존 노드 없음 -> visited목록에 2번 추가 (F)
        #3번 -> 의존 노드 없음 -> visited목록에 2번 추가 (F)
        #4번 -> 2, 3번 노드 있음 -> False를 리턴  (T)
        #5번 -> 4번 노드 -> 2, 3번 노드 -> False리턴 (T)
        visiting.discard(node_id)
        visited.add(node_id)
        return False

    #True(순환이 있음) / False(순환이 없음)
    # 2번, 3번 자체는 더 밑으로 안내려감
    # 4번 -> 2, 3번이 있어서 True
    # 5번 -> 4번이 있어서 True
    for node_id in ids:
        if has_cycle(node_id):
            return False, f"순환 의존성 발견 (노드 '{node_id}' 근처)"
    return True, 'OK'


if __name__ == '__main__':
    query = input('무엇을 하고 싶은지 알려주세요. :\n')
    #쿼리를 기반으로 작업을 생성 -> result 
    #{'nodes': [{'id': '1', 'action': '컴퓨터_전원_끄기', 'depends_on': []}, {'id': '2', 'action': '케이스_열기', 'depends_on': ['1']}, {'id': '3', 'action': '기존_HDD_제거', 'depends_on': ['2']}, {'id': '4', 'action': '새_HDD_장착', 'depends_on': ['3']}, {'id': '5', 'action': '케이스_닫기', 'depends_on': ['4']}, {'id': '6', 'action': '컴퓨터_전원_켜기', 'depends_on': ['5']}, {'id': '7', 'action': 'HDD_마운트', 'depends_on': ['6']}]}
    result = create_depend_graph(query)
    print(result)

    #r -> {'id': '1', 'action': '컴퓨터_전원_끄기', 'depends_on': []}
    ok, msg = valid_graph(result)
    print(f'{msg}')
    
    response = execute_graph(result)
    print(f'response : {response}')