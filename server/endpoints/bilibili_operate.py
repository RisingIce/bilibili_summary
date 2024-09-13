from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import BiliBiliLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from server.config import (openai_api_base, openai_api_key, SESSDATA, BUVID3, BILI_JCT, embedings_path, default_prompt, chunk_size, chunk_overlap, embedings_device,openai_model,RAG_TEMPLATE)
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
        self._embedding_model = HuggingFaceEmbeddings(model_name=embedings_path, model_kwargs={'device': f'{embedings_device}'}, encode_kwargs = {'normalize_embeddings': False})
        self._sessdata = SESSDATA
        self._buvid3 = BUVID3
        self._bili_jct = BILI_JCT
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
        loader = BiliBiliLoader([f"https://www.bilibili.com/video/{bv_id}", ], sessdata=self._sessdata, bili_jct=self._bili_jct, buvid3=self._buvid3)
        docs = loader.load()
        #判断字幕内容是否为空
        if docs[0].__dict__['page_content'] =='':
            raise HTTPException(status_code=500, detail="No subtitles found for video")
        # 切割并处理文档
        pure_doc = self._split_docs(docs=docs)
        return pure_doc
    #构建流式回复生成器
    def _generate_response(self,gen):
        import json
        for chunk in gen:
            yield json.dumps({"answer":chunk}) 
        yield "[DONE]"
    def _format_docs(self,docs):
        # 格式化文档列表，将每个文档的页面内容连接成一个字符串
        return "\n\n".join(doc.page_content for doc in docs)

    # 总结视频内容
    async def get_video_summary(self, bv_id, prompt: str = None,stream: bool = False):
        # 获取处理后的视频文档
        docs = self._get_bv_docs(bv_id)
        # 加载提示模板
        rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
        # 创建检索链
        rag_chain = (RunnablePassthrough.assign(context=lambda input: self._format_docs(input["context"]))
            | rag_prompt
            | self._llm
            | StrOutputParser()
        )
        # 设置提问提示词
        question_prompt = prompt if prompt else default_prompt
        # 流式处理
        if stream:
            gen = rag_chain.stream({"context": docs, "question": question_prompt})
            return self._generate_response(gen)
        # 非流式处理
        ans = rag_chain.invoke({"context": docs, "question": question_prompt})
        try:
            # 构建响应数据
            ans_dict = docs[0].__dict__
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