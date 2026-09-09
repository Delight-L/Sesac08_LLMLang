#주어진 txt파일을 파싱하여, 
#https://drive.google.com/drive/folders/145_yo6nbFdvqvCqvczGDGJ5CZCOZsY5g
#main.py를 실행했을 때 각 리뷰에 대한 리플이 자동으로 생성되도록 하시오.
import pandas as pd 
#1. pandas 라이브러리를 사용해서 txt파일을 읽어오기
def load_reviews(path):
    df = pd.read_csv(path, sep='\t')
    #print(df.columns)
    #print(df['comment'])
    return df

import templates as T
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser
def build_reply_chain(chat):

    #from_template, from_message
    prompt = ChatPromptTemplate.from_template(T.REPLY_TEMPLATE)

    #return 프롬프트 | 챗 | 파서 -> Str, Json, Structured
    return prompt | chat | StrOutputParser()


if __name__ == '__main__':
    #1. pandas 라이브러리를 사용해서 txt파일을 읽어오기
    load_reviews('./tarr_train.txt')


    #2. 오늘 한 chain 함수를 이용해서 댓글 분류(선택) / 긍정-부정
    #3. 오늘 한 chain 함수를 이용해서 댓글에 대한 답글 생성(필수) > '페르소나' 부여 가능

