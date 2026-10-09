import os
from dotenv import load_dotenv
load_dotenv()
from langchain_ollama import ChatOllama


class PurposeLLM:
    """意图识别模型单例：进程内只创建一次客户端配置"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 只初始化一次
            cls._instance._llm = ChatOllama(
                model="qwen2.5:1.5b",     # ✅ 核心：小模型，常驻仅 ~1GB
                base_url=os.getenv('OLLAMA_BASE_URL'),
                temperature=0.1,
                keep_alive="30m",         # ✅ 让模型在 Ollama 里常驻30分钟，避免反复加载
            )
        return cls._instance

    @property
    def llm(self):
        return self._llm


# 模块级实例，全局唯一
purpose_llm = PurposeLLM().llm


def purpose_recognition(question):
    purpose_template = """你是一个运动健康与健身领域的问题分类助手。
    （你的原有提示词不变...）
    """
    try:
        data = purpose_llm.invoke([
            {"role": "system", "content": purpose_template},
            {"role": "user", "content": question}
        ])
        result = data.content.strip().lower()
        return "true" in result and "false" not in result
    except Exception as e:
        print(f"意图识别失败，默认走RAG: {e}")
        return True
