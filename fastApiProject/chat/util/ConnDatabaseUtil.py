#连接数据库配置

from langchain_chroma import Chroma
from dotenv import load_dotenv
import  os
from chat.util import LoadEmbeddingModel
load_dotenv()

def chroma_conn():
    return Chroma(
        collection_name= os.getenv('COLLECTION_NAME'),
        embedding_function=LoadEmbeddingModel.load_embedding_model(),
        persist_directory=os.getenv('CHROMA_PATH'),
    )