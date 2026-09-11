# 여러 에이전트(노드)가 협력해서 에세이를 작성하는 멀티 에이전트 시스템
# 그래프 흐름:
#   planner → research_plan → generate ─┐
#                                ↑       │(max_revisions 초과 시 END)
#                        research_critique ← reflect
#
# 단순 ReAct 에이전트와 달리,
# 각 노드가 하나의 역할(기획/조사/작성/비평)만 전담한다
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List 

from pydantic import BaseModel 

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI 
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langgraph.graph import StateGraph, END 
from langgraph.checkpoint.memory import MemorySaver

# ── 프롬프트 ───────────────────────
PLAN_PROMPT = (
    "You are an expert writer. "
    "Write a high-level outline for an essay on the given topic. "
    "Include relevant notes or instructions for each section."
)

WRITER_PROMPT = """You are an essay assistant writing excellent 5-paragraph essays.
Generate the best essay possible for the user's request and the initial outline.
If the user provides critique, respond with a revised version of your previous attempt.
Use the following reference content as needed:

------

{content}"""

REFLECTION_PROMPT = (
    "You are a teacher grading an essay submission. "
    "Provide detailed critique and recommendations including length, depth, and style."
)

RESEARCH_PROMPT = (
    "You are a researcher. Generate up to 3 Wikipedia search queries "
    "to gather information relevant to the given topic or critique. "
    "Return only the queries as a JSON list."
)



class AgentState(TypedDict):
    task : str
    plan : str 
    draft : str 
    critique : str
    content : List[str]
    revision_number : int 
    max_revisions : int 

#pydantic의 상속을 받음(BaseModel)
class Queries(BaseModel):
    queries : List[str]

model = ChatOpenAI(model="gpt-4o", temperature=0)
def plan_node(state:AgentState):
    print(f'[plan node] .... 계획 수립 중 ....')
    response = model.invoke([
        SystemMessage(content=PLAN_PROMPT), #1.시스템 프롬프트 정의
        HumanMessage(content=state['task']) #2.인간의 요청 넣기 
    ])
    return {'plan':response.content}

def generate_node(state:AgentState):
    pass 

def research_node(state:AgentState):
    pass 

def reflection_node(state:AgentState):
    pass 

def critique_node(state:AgentState):
    pass

def should_continue(state:AgentState):
    pass


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node('planner', plan_node)
    graph.add_node('researcher', research_node)
    graph.add_node('generator', generate_node)
    graph.add_node('reflect', reflection_node)
    graph.add_node('critique', critique_node)

    #연결
    graph.set_entry_node('planner')
    graph.add_edge('planner', 'researcher')
    graph.add_edge('researcher', 'generator')
    graph.add_conditional_edges(
        'generator',
        should_continue, 
        {END:END,
         'reflect':'reflect'}
    )
    graph.add_edge('reflect', 'critique')
    graph.add_edge('critique', 'generator')

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)