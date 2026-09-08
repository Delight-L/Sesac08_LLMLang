#질문을 할 때, 질문 답변에 참고할 자료를 미리 셋팅 -> 자료를 찾아 같이 전달
#Retrieval(검색) Augmented(증강) Generation(생성)
#유사도 검색 ->1.VectorDB를 이용  2.TF-IDF를 이용
#벡터DB : 문장들을 임베딩해서, 비슷한 문장을 분류해놓고 유사도 검색
#Augmented : 알고리즘을 이용해서 유사도 검색
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

def build_rag_chain(llm, retriever, document_sep='\n\n'):
    prompt = ChatPromptTemplate.from_message([
        ('human', '''Answer the question using only the context below. \n\n
                        {context}\n\n 
                        question : {input}''')
    ])

    combine = create_stuff_documents_chain(llm, prompt, document_seperator=document_sep)
    return create_retrieval_chain(retriever, combine)