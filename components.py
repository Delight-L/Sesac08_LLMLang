#LangChain의 기본 대화를 구성하는 3가지 요소
#1.프롬프트와 파서 -> 대화의 양식을 규정
#2.체인 -> |(파이프), LCEL문법
#3.메모리 -> 사용자와의 이전 대화 내용을 기억

#대화 대상 세팅
from langchain_openai import ChatOpenAI
from openai import OpenAI

#ChatPromptTemplate -> gpt나 llm에 질문할 내용을 정리하는 것
from langchain_core.prompts import ChatPromptTemplate 
#StrOutputParser -> output으로 나온 결과물을 정제
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv 
#비밀 키를 가져오는 역할을 함 -> .env 
load_dotenv()

#내가 사용할 gpt모델 
# o 알파벳 o..(소문자)
MODEL_NAME = 'gpt-4o'

#내가 대화할 gpt모델과의 '채팅 방' 만들기 절차
def get_chat(temperature=0.5, model=MODEL_NAME):
    return ChatOpenAI(temperature=temperature, model=model)

STYLE_TEMPLATE = """Translate the text \
that is delimited by triple backticks \
into a style that is {style}. \
text: ```{text}```
"""

#프롬프팅 양식을 세팅
#매개변수 chat은 gpt와의 채팅 방 
# prompt | chat (미리 정해놓은 prompt를 chat채팅방에 넘겨주는 작동)
# chat | StrOutputParser() (chat의 답변을 StrOutputParser로 넘겨주는 작동)
def build_style_chain(chat):
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
    #gpt-4o모델과 temperate 0.5로 만든 채팅방을 연 상태(채팅방 = chat)
    chat = get_chat()

    #gpt에게 위의 손님 메일 + (변형)요청을 보내, 답변을 받아오는 체인 정의
    #style_chain은 prompt -> chat -> stroutput parser로 이어지는 파이프라인
    style_chain = build_style_chain(chat)

    #style_chain.invoke
    result = style_chain.invoke({'style':'''Korean 
                                        in a calm and 
                                        respectful tone''',
                                          'text':customer})

    print(result)

    text = input(f'{result}에 대한 나의 답변')
    reply = style_chain.invoke({'style':'''english
                                        in a calm and 
                                        respectful tone 
                                        if my response contains some
                                        bad words, plz translate it or remove it''',
                                          'text':text})

    print(reply)


REVIEW_TEMPLATE = """\
For the following text, extract the following information:

gift: Was the item purchased as a gift for someone else? \
Answer True if yes, False if not or unknown.

delivery_days: How many days did it take for the product\
to arrive? If this information is not found, output -1.

price_value: Extract any sentences about the value or price,\
and output them as a comma separated Python list.

text: {text}

{format_instructions}
"""

from langchain_classic.output_parsers import ResponseSchema, StructuredOutputParser
def build_review_chain(chat):
    #1. prompt를 만드시오(build_style_chain 참고)
    # AutoTokneizer.from_pretrained(모델이름)
    prompt = ChatPromptTemplate.from_template(REVIEW_TEMPLATE)

    #**StrOutputParser는 '거의 아무것도 하지 않는' str만 추출하는 역할
    #StructuredOutputParser 은 gpt가 생성한 str을 특정한 구조(자료형)로 파싱
    #schemas -> 나 이런 정보 필요해~ name(변수이름)
    schemas = [
        ResponseSchema(name="gift",
                       description="Was the item purchased as a gift for someone else? "
                                   "Answer True if yes, False if not or unknown."),
        ResponseSchema(name="delivery_days",
                       description="How many days did it take for the product to arrive? "
                                   "If this information is not found, output -1."),
        ResponseSchema(name="price_value",
                       description="Extract any sentences about the value or price, "
                                   "and output them as a comma separated Python list."),
    ]

    #리뷰를 합친 prompt가 인풋 -> chat이 이를 확인 -> gpt(chat)이 생성한 결과를 schemas에 따라 구조화
    return prompt | chat | StructuredOutputParser.from_response_schemas(schemas), StructuredOutputParser.from_response_schemas(schemas).get_format_instructions()

#OutputParser의 종류를 바꿔서 Parser의 역할을 확인
#리뷰 -> 리뷰 여기저기에 존재하는 정보를 Parser가 골라내서 정리해 주는 역할
def output_parsing():
    customer_review = """ 
    This leaf blower is pretty amazing. It has four settings: candle blower, gentle breeze, 
    windy city, and tornado. It arrived in two days, just in time for my wife's anniversary 
    present. I think my wife liked it so much she was speechless. It's slightly more expensive \
    than the other leaf blowers out there, but I think it's worth it for the extra features.
    """
    chat = get_chat()
    parse_chain, format = build_review_chain(chat)

    #build_review_chain이 시작할 때 필요한 재료가 들어가야함
    output = parse_chain.invoke({'text':customer_review,
                                 'format_instructions':format }) 
    print(f'구조화된 파싱 : {type(output).__name__, output}')
    print(f'구조화 결과 delivery : {output.get('delivery_days')}')


if __name__ == '__main__':
    output_parsing()
    #Chat = OpenAI()
    # Chat = ChatOpenAI(temperature=0.6, model=MODEL_NAME)

    # response = Chat.completions.create(
    #     model = MODEL_NAME,
    #     #role : system(openai의 세팅), user(사용자)
    #     messages = [{'role':'system', 'content':'말끝에다가 멍을 붙여라'},
    #                 {'role':'user', 'content': '한국은 어떤 나라이니?' }],

    #     #답변의 창의성(0~1) 1에 가까울 수록 창의적(랜덤한) 답변 
    #     temperature = 0.6
    # )

    # #답변 중 choices[0].message.content 가 텍스트로 된 답변 추출
    # print(response)
    # print(response.choices[0].message.content)