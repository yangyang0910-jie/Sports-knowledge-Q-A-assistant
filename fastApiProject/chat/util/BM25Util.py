import jieba
from langchain_core.documents import Document
from rank_bm25 import  BM25Okapi
from chat.util import ConnDatabaseUtil

# 中文停用词表（常见停用词，避免无意义词干扰BM25排序）
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦",
    "还", "被", "把", "让", "从", "对", "与", "但", "而", "或", "所",
    "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后",
    "之", "其", "中", "等", "等等", "即", "使", "向", "将", "按", "当",
    "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外",
    "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于",
])

#分词+过滤
def participle(text):
    text_cut =jieba.cut(text)
    result = []
    for word in text_cut:
        if word.strip() not in STOP_WORDS and len(word.strip())>0:
            result.append(word)
    return  result
#创建BM检索对象
def bm_object(chroma_db):
    #取出数据库中的数据
    text=chroma_db.get()
    #处理数据格式-----和检索器一样的
    ids = text['ids']
    documents = text['documents']
    metadatas = text['metadatas']
    text =[Document(id=ids[i],page_content=documents[i],metadata={"source":metadatas[i]})for i in range(len(ids))]
    #分词
    docs=[participle(doc) for doc in documents]
    #创建BM25对象
    bm25=BM25Okapi(docs)
    return bm25,text

#BM25检索
def BM_retriever(bm25,text,question,k=10):
    # 计算得分
    score =bm25.get_scores(participle(question)) #返回是个列表
    # 排序
    score_sort = sorted(range(len(score)),key=lambda x: score[x],reverse=True)[:k]
    # 按照索引找对应的文档
    result=[text[x] for x in score_sort]
    print("检索结果为：",result)
    return  result

if __name__ == '__main__':
    chroma_db =ConnDatabaseUtil.chroma_conn()
    bm25,text=bm_object(chroma_db)
    BM_retriever(bm25,text,"如何减肥",10)