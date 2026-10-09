#加载向量化模型
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings

def load_embedding_model():
    return HuggingFaceEmbeddings(
        model_name = os.getenv("EMBEDDING_MODEL_PATH"),
        model_kwargs={
            "device":"cpu",
            "local_files_only":True,
        },
    )