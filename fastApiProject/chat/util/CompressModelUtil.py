from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def Compress_Model():
    return  ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.7-max-2026-06-08",
)