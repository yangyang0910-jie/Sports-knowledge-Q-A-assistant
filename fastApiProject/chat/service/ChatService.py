import json
import threading
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from chat.service import HistoryService
from chat.util import LoadModelUtil, ConnDatabaseUtil, RerankModelUtil, RRFUtile, PurposeUtil
from chat.util import BM25Util, CompressUtil
from chat.dao import SaveConversationDao, CompressDao


# 构建大模型
def chat(question, dialogueId):
    # 历史记忆
    try:
        dialogueId = int(dialogueId)
    except (TypeError, ValueError):
        dialogueId = 0

    if dialogueId == 0:
        history_all = []
    else:
        history_all = HistoryService.query_one_history(dialogueId)['data']

    # 只保留未压缩的消息拼上下文（压缩过的内容由摘要代表，防止重复压缩/膨胀）
    history = [m for m in history_all if not (m.get('compressed') or m.get('is_compressed'))]

    # 意图识别
    purpose = PurposeUtil.purpose_recognition(question)
    # 加载聊天大模型
    LLM = LoadModelUtil.chat_Load_Model()

    # chat 流程里不执行压缩（压缩在 save_conversation 保存之后做）
    # 这里只读取现有摘要，用于拼提示词（dialogueId 本身就是会话ID）
    current_summary = CompressDao.get_summary_from_db(dialogueId) or "无"

    if not purpose:
        history.append({"role": "user", "content": question})
        history_text = "\n".join(
            [f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content']}" for m in history]
        )
        template = """
                回答时有历史记录可以参考，没有就不参考
                压缩后的历史记录：
                    {compress_result}
                最近的历史记录：
                    {history}
                问题：
                    {question}
                """
        prompt = PromptTemplate(
            template=template,
            input_variables=["history", "question", "compress_result"],
        )
        final_prompt = prompt.invoke({
            "history": history_text,
            "question": question,
            "compress_result": current_summary
        })
        print("意图识别判断：不相关")
        for chunk in LLM.stream(final_prompt):
            # 兼容不同模型返回格式，确保有内容才 yield
            content = ""
            if hasattr(chunk, 'content'):
                content = chunk.content
            elif isinstance(chunk, str):
                content = chunk
            if content:
                yield content
        return

    print("意图识别判断：相关")
    # 提示词
    template = """
    你是一个运动专家AI，请根据RAG检索内容回答用户问题。
        规则：
            - 仅基于提供的知识回答，不使用外部知识补充。
            - 检索内容不足时，说明信息不足，不要猜测。
            - 优先提炼关键答案，避免冗长解释。
            - 保持回答自然、简洁、有帮助。
            - 输出结果的时候，不允许输出根据提供的参考资料这样的内容
            - 输出结果的时候，如果没有参考的上下文信息，请给出一个友好的回复信息
        压缩后的历史记录：
            {compress_result}
        历史记录：
            {history}
        参考资料：
            {context}
        问题：
            {question}
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["history", "context", "question", "compress_result"],
    )
    # 连接向量数据库
    chroma_db = ConnDatabaseUtil.chroma_conn()
    retriever = chroma_db.as_retriever(search_kwargs={"k": 5})

    def call_back(docs):
        for doc in docs:
            r = doc.page_content
        print(r)
        return docs

    # BM25检索和向量检索融合
    def fusion_retrieval():
        retriever_result = retriever.invoke(question)
        print("向量检索：")
        call_back(retriever_result)
        bm25, text = BM25Util.bm_object(chroma_db)
        bm_result = BM25Util.BM_retriever(bm25, text, question, 10)
        print("BM25检索：")
        call_back(bm_result)
        RRF = RRFUtile.RRF_fuse(bm_result, retriever_result)
        print("RRF后的数据：")
        call_back(RRF)
        return RRF

    # 重排序
    def rerank(data):
        print("开始重排序：")
        question = data["question"]
        content = data["context"]
        history = data["history"]
        compress_result = data["compress_result"]

        reranker = RerankModelUtil.rerankMdel()
        source = reranker.compute_score([(question, doc.page_content) for doc in content])
        print("重排序成功", source)

        result = []
        for index, item in enumerate(source):
            result.append({content[index].id: item})
        result.sort(key=lambda x: list(x.values())[0], reverse=True)
        results = []
        for index in result:
            for key in index.keys():
                for doc in content:
                    if key == doc.id:
                        results.append(doc.page_content)
        content = results[:5]
        return {
            "question": question,
            "context": content,
            "history": history,
            "compress_result": compress_result,
        }

    # 构建langchain链
    qa_lain = (
        RunnableParallel({
            "compress_result": RunnableLambda(lambda _: current_summary),
            "history": RunnableLambda(lambda _: history),
            "context": RunnableLambda(lambda _: fusion_retrieval()),
            "question": RunnablePassthrough(),
        })
        | RunnableLambda(rerank)
        | prompt
        | LLM
        | StrOutputParser()
    )
    for chunk in qa_lain.stream(question):
        yield chunk


def save_conversation(saveconversationentity, username):
    # 接收前的传来的数据
    question = saveconversationentity.question
    answer = saveconversationentity.answer
    current_id = saveconversationentity.currentId
    # 将数据存入数据库中
    dialogue_id = SaveConversationDao.saveConversationDao(current_id, username, question, answer)

    if dialogue_id:
        # 保存成功后执行压缩检查（后台线程，不拖慢保存接口）
        # 会话ID确定规则：
        #   - 前端传的 currentId > 0 → 就是会话ID（后续轮次）
        #   - currentId = 0 → 本行是新会话的第一轮，会话ID = 本行 dialogue_id
        try:
            session_id = int(current_id) if current_id else 0
            if session_id <= 0:
                session_id = int(dialogue_id)
            print(f"保存成功，触发压缩检查 | 行ID={dialogue_id} | 会话ID={session_id}")
            threading.Thread(
                target=CompressUtil.compress_history,
                args=(session_id,),
                daemon=True
            ).start()
        except Exception as e:
            print(f"压缩检查启动失败(不影响保存):{e}")

        return {
            "code": 200,
            "msg": "添加成功",
            "data": dialogue_id
        }
    return {
        "code": 500,
        "msg": "添加失败",
        "data": 0
    }
