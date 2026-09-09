
#1. 폴더 안의 pdf를 읽어서 하나의 docs로 세팅
#pdf라는 폴더 아래에 있는 모든 pdf를 읽어서 docs라는 리스트에 내용을 추가
import os
from langchain_community.document_loaders import PyPDFLoader
def load_pdfs(path):
    #1.오류상황 1 -> 경로가 틀린 경우
    if not path:
        print(f'경로가 틀렸습니다.')

    #2.오류상황 2 -> 폴더에 pdf가 없는 경우
    pdf_lists = [os.path.join(path, x) for x in os.listdir(path) if 'pdf' in x]
    if len(pdf_lists) < 1:
        #raise 시스템 오류, 알림 실행
        raise FileNotFoundError(f'{path}에 pdf가 존재하지 않습니다.')

    docs = []
    for pdf in pdf_lists:
        docs.extend(PyPDFLoader(pdf).load())

    print(f'{len(docs)} 개의 문서 취득')
    return docs

#2. docs를 청크화
from langchain_text_splitters import RecursiveCharacterTextSplitter
def split_docs(docs, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)

    split_docs = splitter.split_documents(docs)
    return split_docs

#3. 청크를 벡터화 -> 벡터 DB
#https://docs.pinecone.io/guides/get-started/quickstart/ingest-files
#https://docs.weaviate.io/weaviate/quickstart
#Chroma에서 초기 데이터를 만드는 과정!
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
def vectorstore(dir, collection):
    return Chroma(collection_name = collection,
                  embedding_function = OpenAIEmbeddings(),
                  persist_directory = dir)

#새로운 문서가 들어왔을 때, split한 후 기존의 vectordb에 추가
def add_to_vectorstore(vectordb, splits):
    vectordb.add_documents(splits)
    return vectordb


#python ./rag.py 로 실행시켜서 문제가 없어야 함!
if __name__ == '__main__':

    #내가 pdf를 특정 장소에 가지고 있는가?
    #내가 가진 pdf가 벡터 DB에 있는가?
    vectordb = vectorstore('./vectordb', 'pdf_docs')
    if len(vectordb.get(limit=1)['ids']) > 0:
    #있다 -> 추가 안해도 됨
        print(f'기존 파일 재사용')
    else:
    #없다 -> 추가 해야 함
        docs = load_pdfs('./pdf')
        split_doc = split_docs(docs)
        print(f'{len(docs)} -> {len(split_doc)} 개로 나누어짐')
        add_to_vectorstore(vectordb=vectordb, splits=split_doc)


#4. 리트리버
#5. 리트리버 얹은 chain 정의