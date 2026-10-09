from langchain_community.document_loaders import DirectoryLoader,CSVLoader
from pathlib import Path
from langchain_chroma import Chroma
from chat.util import LoadEmbeddingModel

#加载数据、语义分割、存入数据库

# 加载数据
all_path = Path(r"D:\workspace\fastApiProject\data")
all_data = []  # 用来存放所有加载好的文档
try:
    loader=DirectoryLoader(
        path=all_path,
        loader_cls=CSVLoader,
        glob="*.csv",
        loader_kwargs={"encoding":'utf-8'},
    )
    all_data = loader.load()
    # print(all_data)
    print("成功加载 ")
except Exception as e:
    print(f"加载失败: {e}")

#存入数据库
#向量数据库存储路径
vector_db_path=r"D:\workspace\fastApiProject\sports_chroma"
# 集合名称
collection_name="sports"
#存入数据库
try:
    Chroma.from_documents(
        #数据
        documents=all_data,
        #向量化模型
        embedding=LoadEmbeddingModel.load_embedding_model(),
        #集合名称
        collection_name = collection_name,
        #数据库存储路径
        persist_directory=vector_db_path,
        #相似度
        collection_metadata={"hnsw:space":"cosine"}
    )
    print("数据存入成功")
except Exception as e:
    print(f"数据存放失败:{e}")
