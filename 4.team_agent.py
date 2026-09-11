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


class AgentState(TypedDict):
    task : str
    plan : str 
    draft : str 
    critique : str
    content : List[str]
    revision_number : int 
    max_revisions : int 
