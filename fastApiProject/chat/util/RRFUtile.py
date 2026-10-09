
def RRF_fuse(bm_result,retriever_result):
    score_list = {}
    docs_list={}
    #向量排序
    for index,item in enumerate(retriever_result,start=1):
        score_list[item.id]= score_list.get(item.id,0)+1/(60+index) #get根据key取值
        docs_list[item.id]=item
    #BM25检索
    for index,item in enumerate(bm_result,start=1):
        score_list[item.id]=score_list.get(item.id,0)+1/(60+index)
        docs_list[item.id]=item
    #分数排序-----只是排序，格式没变
    result_list =sorted(score_list.items(),key=lambda x:x[1],reverse=True) #返回列表
    #找对应的文档
    results=[docs_list[item[0]]for item in result_list]
    return results