#Agent가 포함된 랭 그래프~
from dotenv import load_dotenv 
load_dotenv()

#Annotated[자료형, 덮어쓰기] -> '자료형'데이터가 여기 들어올거야. 데이터가 새로 들어올 때 '덮어쓰기' 할거야. 
from typing import TypedDict, Annotated 
from langgraph.graph import StateGraph, END 

#에이전트 구성을 위해 필요한 langchain 컴포넌트
from langchain_core.messages import (AnyMessage, SystemMessage, 
                                     HumanMessage, ToolMessage)

#검색을 하기 위한 툴! (tools)
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_openai import ChatOpenAI

#리스트를 합쳐줌 [] [] -> [] operator.add
import operator

class AgentState(TypedDict):
    messages : Annotated[list[AnyMessage], operator.add]


import wikipedia
wikipedia.set_user_agent('CoredataLectureBot/1.0 (chorokje@gmail.com)') 


class Agent:
    #이름만 Agent이고 langgraph로 구현함
    #langgraph를 구현
    def __init__(self, system, tools, model):
        self.system = system #시스템에 대한 전반적인 답변 매너를 정하는 프롬프트

        #그래프 정의
        graph = StateGraph(AgentState)
        graph.add_node('llm', self.call_openai) #1.채팅을 한다
        graph.add_node('tool', self.take_action) #2.혹시 채팅중 도구 필요하면 쓴다

        graph.add_conditional_edges('llm', self.exist_action, 
                                    {True : 'tool',
                                     False : END})

        graph.add_edge('tool', 'llm') #<<<< 여기 체크
        graph.set_entry_point('llm') #START 노드에서 시작하지 않았으므로 시작점이 llm 함수임을 알림
        # END -> LLM (while루프에서 돌려줌)
        self.graph = graph.compile()

        #print('ffffffffffffftttttttt : ', tools.name)
        self.tools = {t.name : t for t in tools}
        self.model = model.bind_tools(tools)

  
    #조건 판단함 -> 툴이 있나?
    def exist_action(self, state:AgentState):
        return len(state['messages'][-1].tool_calls) > 0
        
    #실행함(execute)
    def call_openai(self, state:AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages':[message]}
        
    #도구 실행
    def take_action(self, state:AgentState):
        #도구 실행 -> 최신 메세지(state['messages'][-1])의 tool_calls
        tool_calls = state['messages'][-1].tool_calls

        results = []
        #t -> 1개의 개별 도구(함수, API)
        #위치, 맛집 api / 날씨 
        for t in tool_calls:
            print(f"도구 호출 : {t['name']} -> {t['args']}")

            if t['name'] not in self.tools:
                result = '존재하지 않는 도구입니다.'
            else:
                #self.tools -> 함수, api .invoke(도구실행에필요한매개변수)
                result = self.tools[t['name']].invoke(t['args'])
            results.append(
                #tool의 id, name, conent(툴을 쓴 결과)
                ToolMessage(tool_call_id=t['id'], name=t['name'], 
                            content=str(result))
            )
            print(f'모델로 복귀\n')
        return {'messages':results}


if __name__ == '__main__':
    model = ChatOpenAI(model='gpt-4o', temperature=0.5)
    system = '''
        You are a smart research assistant. 
        Using Wekipedia tools for search.
        You could search when you sure what you want.
    '''
    tools = WikipediaQueryRun(api_wrapper = WikipediaAPIWrapper(top_k_results=2,
                                                                doc_content_chars_max=1000))
    print(f'사용 도구 : {tools.name}')
    bot = Agent(system, [tools], model)

    question = input('질문해주세요 : \n')
    message = [HumanMessage(content=question)]
    #bot.graph => Agent.graph
    result = bot.graph.invoke({'messages':message})
    print(f'{result['messages'][-1].content}')