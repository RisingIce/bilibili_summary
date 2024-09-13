import os
current_dir = os.path.abspath(os.path.dirname(__file__))

#b站相关参数
SESSDATA = ""
BUVID3 = ""
BILI_JCT = ""

#openai参数
openai_api_key = ""
openai_api_base = ""
openai_model = ""

#embdeding参数
embedings_path = os.path.join(current_dir,"model","bert-base-chinese")
#运行embeding模型的device,可选参数:['cuda','cpu',"mps", "npu"]
embedings_device = "cuda"

#文档切割参数
chunk_size = 1000
chunk_overlap = 20


#RAG文档抽取提示词模板
RAG_TEMPLATE = """
            You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
            <context>
            {context}
            </context>
            Answer the following question:
            {question}
"""

#提问提示词模板
default_prompt ="""请根据视频内容提炼并总结以下关键信息：
1. 视频的核心观点或论述（概述视频所传达的主要思想或立场）,
2. 关键人物或事件（突出视频中涉及的重要角色或事件）,
3. 视频的主线内容（梳理视频的整体逻辑和发展脉络，重点描述重要的情节或讨论的主题）,
4.在总结的最后，提供你个人对视频内容的看法，包括你的评价、支持或质疑的原因，并简要解释为何持有此观点。
输出格式如下：
核心观点：
关键人物/事件：
主线内容：
个人看法：
"""