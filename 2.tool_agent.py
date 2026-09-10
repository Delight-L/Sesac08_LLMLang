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
    message : Annotated[list[AnyMessage], operator.add]


class Agent:
    #이름만 Agent이고 langgraph로 구현함
    #langgraph를 구현
    def __init__(self):
        pass 
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
    def take_action(self):
        pass 

    