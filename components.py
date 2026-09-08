#LangChain의 기본 대화를 구성하는 3가지 요소
#1.프롬프트와 파서 -> 대화의 양식을 규정
#2.체인 -> |(파이프), LCEL문법
#3.메모리 -> 사용자와의 이전 대화 내용을 기억

#대화 대상 세팅
from langchain_openai import ChatOpenAI
from openai import OpenAI

import os
from dotenv import load_dotenv 
#비밀 키를 가져오는 역할을 함 -> .env 
load_dotenv()

#내가 사용할 gpt모델 
MODEL_NAME = 'gpt-4o'


def get_chat(temperature=0.5, model=MODEL_NAME):
    return ChatOpenAI(temperature=temperature, model=model)

STYLE_TEMPLATE = """Translate the text \
that is delimited by triple backticks \
into a style that is {style}. \
text: ```{text}```
"""

#프롬프팅 양식을 세팅
def build_style_chain(chat):
    from langchain_core.prompts import ChatPromptTemplate 
    from langchain_core.parsers import StrOutputParser
    prompt = ChatPromptTemplate.from_template(STYLE_TEMPLATE)
    #LCEL문법 -> prompt를 chat에 넘겨주고 -> 그 결과를 strOutputParser에 다시 넣어주는 연결
    return prompt | chat | StrOutputParser()

#프롬프팅, 파서
#인풋 텍스트 -> 특정한 양식에 맞추어 정제/답변
def parsing():
    #CS 고객이 문의한 내용을 특정한 양식에 맞춰 뽑아내기/변형하기 
    #해적 손님의 메일.... 
    customer = '''
        Arrr, I be fuming that me blender lid flew off and splattered me kitchen walls \
        with smoothie! And to make matters worse, the warranty don't cover the cost of \
        cleaning up me kitchen. I need yer help right now, matey!
                '''

    #gpt야, 해적손님의 메일을 격식을 갖춘 따뜻한 어투의 영어 메일로 바꿔줘.
    chat = get_chat()

    #gpt에게 위의 손님 메일 + (변형)요청을 보내, 답변을 받아오는 체인 정의
    style_chain = build_style_chain(chat)

    style_chain.invoke()

    # customer_review = 

    # parse_chain, format = 

    # output = 
    # print(f'구조화된 파싱 : {}')


if __name__ == '__main__':
    #Chat = OpenAI()
    Chat = ChatOpenAI(temperature=0.6, model=MODEL_NAME)

    response = Chat.completions.create(
        model = MODEL_NAME,
        #role : system(openai의 세팅), user(사용자)
        messages = [{'role':'system', 'content':'말끝에다가 멍을 붙여라'},
                    {'role':'user', 'content': '한국은 어떤 나라이니?' }],

        #답변의 창의성(0~1) 1에 가까울 수록 창의적(랜덤한) 답변 
        temperature = 0.6
    )

    #답변 중 choices[0].message.content 가 텍스트로 된 답변 추출
    print(response)
    print(response.choices[0].message.content)