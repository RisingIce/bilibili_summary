import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import BiliBiliLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.vectorstores import Chroma
from fastapi import HTTPException
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# bilibili工具类
class BiliBiliTool:
    def __init__(self) -> None:
        # 初始化llm（语言模型）
        self._llm = ChatOpenAI(model=openai_model, openai_api_key=openai_api_key, openai_api_base=openai_api_base, max_tokens=1024, temperature=0, streaming=True)
        # 初始化embeddings（嵌入模型）
        self._embedding_model = HuggingFaceEmbeddings(model_name=embedings_path, model_kwargs={'device': f'{embedings_device}'})
        self._sessdata = sessdata
        self._buvid3 = buvid3
        self._bili_jct = bili_jct
        # 初始化文本分割器
        self._text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 切割bilibili docs（文档）
    def _split_docs(self, docs):
        # 初步分割文档
        document = self._text_splitter.split_documents(docs)
        # 过滤复杂metadata（元数据）
        return filter_complex_metadata(documents=document)

    # 获取bv号详细信息
    def _get_bv_docs(self, bv_id):
        # 根据bv号加载bilibili视频信息
        loader = BiliBiliLoader([f"https://www.bilibili.com/video/{bv_id}"], sessdata=self._sessdata, bili_jct=self._bili_jct, buvid3=self._buvid3)
        docs = loader.load()
        #判断字幕内容是否为空
        if docs[0].__dict__['page_content'] =='':
            st.error("No subtitles found for video")
        # 切割并处理文档
        pure_doc = self._split_docs(docs=docs)
        return pure_doc
    def _format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)
    # 总结视频内容
    def get_video_summary(self, bv_id, prompt: str = None,stream: bool = False):
        # 获取处理后的视频文档
        docs = self._get_bv_docs(bv_id)
        RAG_TEMPLATE = """
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            <context>
            {context}
            </context>
            Answer the following question:
            {question}
        """

        rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

        chain = (RunnablePassthrough.assign(context=lambda input: self._format_docs(input["context"]))
            | rag_prompt
            | self._llm
            | StrOutputParser()
        )
        if stream:
            gen = chain.stream({"context": docs, "question": prompt})
            return gen
        ans = chain.invoke({"context": docs, "question":  prompt})
        try:
            ans_dict = docs["context"][0].__dict__
            # 构建响应数据
            resp = {
                "avid": ans_dict['metadata']['aid'],
                "bvid": ans_dict['metadata']['bvid'],
                "cid": ans_dict['metadata']['cid'],
                "title": ans_dict['metadata']['title'],
                "url": ans_dict['metadata']['url'],
                "answer": ans
            }
        except Exception as e:
            # 异常处理：返回HTTP 500错误
            raise HTTPException(status_code=500, detail=str(e))
        return resp

st.set_page_config(page_title="💬 BiliBili Summary")
#检查参数是否填充
def check_params(params:dict) -> bool:
    for key in params:
        if params[key] == "":
            return False
    return True

st.sidebar.title("Parameter setting")
st.sidebar.text("B站相关参数设置:")
sessdata = st.sidebar.text_input(label="SESSDATA",type="password")
buvid3 = st.sidebar.text_input(label="BVID3",type="password")
bili_jct = st.sidebar.text_input(label="BILI_JCT",type="password")

st.sidebar.text("Openai API 相关参数设置:")
openai_model = st.sidebar.text_input(label="Openai Model")
openai_api_key = st.sidebar.text_input(label="Openai API Key",type="password")
openai_api_base = st.sidebar.text_input(label="Openai API Base")

st.sidebar.text("Embedings Model相关参数设置:")
embedings_path = st.sidebar.text_input(label="Embedings Model Absolute Path")
embedings_device = st.sidebar.selectbox(label="Embedings Device",options=['cuda','cpu',"mps", "npu"])

st.sidebar.text("文本分割器参数设置:")
chunk_size = int(st.sidebar.text_input(label="chunk_size",value=1000))
chunk_overlap =int(st.sidebar.text_input(label="chunk_overlap",value=20))

st.sidebar.text("自定义提问Prompt参数设置(可选):")
prompt = st.sidebar.text_area(label="Prompt",value="""请根据视频内容提炼并总结以下关键信息：
1. 视频的核心观点或论述（概述视频所传达的主要思想或立场）,
2. 关键人物或事件（突出视频中涉及的重要角色或事件）,
3. 视频的主线内容（梳理视频的整体逻辑和发展脉络，重点描述重要的情节或讨论的主题）,
4.在总结的最后，提供你个人对视频内容的看法，包括你的评价、支持或质疑的原因，并简要解释为何持有此观点。
输出格式如下：
核心观点：
关键人物/事件：
主线内容：
个人看法：
 """,height=450)

st.title("BiliBili Summary")

params = {
    "sessdata":sessdata,
    "buvid3":buvid3,
    "bili_jct":bili_jct,
    "openai_model":openai_model,
    "openai_api_key":openai_api_key,
    "openai_api_base":openai_api_base,
    "embedings_path":embedings_path,
}

if check_params(params):
    bt = BiliBiliTool()
else:
    st.error("参数未设置，请先设置参数")
    st.stop()

if bv_id := st.text_input(label="bv号"):
    if st.button(label="开始总结"):
        gen = bt.get_video_summary(bv_id,prompt=prompt,stream=True)
        st.write_stream(gen)
        if st.button(label="清空"):
            bv_id = None
