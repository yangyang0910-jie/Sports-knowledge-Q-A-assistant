import os
from dotenv import load_dotenv
from FlagEmbedding import FlagReranker
load_dotenv()
def rerankMdel():
    return FlagReranker(
        model_name_or_path=os.getenv("RERANK_MODEL_PATH"),
        # use_fp16=True,
        devices="cpu",
        model_kwargs={
            "low_cpu_mem_usage": False,  # 关键：禁用低内存模式，防止触发 meta tensor
            "local_files_only": True  # 可选：如果你确定本地有文件
        }
    )