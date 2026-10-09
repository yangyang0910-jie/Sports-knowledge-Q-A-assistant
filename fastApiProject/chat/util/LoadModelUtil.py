from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()


#加载问答大模型配置
def chat_Load_Model():
    return  ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="kimi-k2.7-code",
)

#测试
def test_Load_Model(question):
    llm=chat_Load_Model()
    message=[
        {"role":"system","content":"你是一个热情的助手"},
        {"role":"user","content":question}
    ]
    result =llm.invoke(message)
    return result
if __name__ == '__main__':
    question=input("输入问题：")
    data = test_Load_Model(question)
    # chunk 是一个 AIMessageChunk 对象，真正的文字在 .content 里
    print(data.content)