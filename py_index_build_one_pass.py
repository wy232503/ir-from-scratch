from collections import defaultdict,Counter
def tokenize(text):
    #词条化
    return text.lower().split()
#返回词条化小写且切分后的词元
def index_build(documents):
    #建立索引
    post = defaultdict(list)
    #post字典
    df = defaultdict(int)
    #df用int计数
    for doc_id,text in documents.items():
        cnt = Counter(tokenize(text))
        #counter后返回的是key为word，value为tf的一个dict
        print(cnt)
        for word,tf in cnt.items():
            post[word].append((doc_id,tf))
            #post里key为word的对应的value为元组(doc_id,tf)
            df[word]+=1
            #对应的df+1
        print(dict(post))
        #以字典形式打印
        print(df)
    for word in post:
        post[word].sort(key=lambda item:item[0])
        #对该单词对应的倒排列表，按照元组里的 doc_id 升序排序
    print(dict(post))
    return post,df
def intersect(a,b):
    assert not a or isinstance(a[0], int), "intersect: a 只接受 docID 整数列表，请先转换"
    assert not b or isinstance(b[0], int), "intersect: b 只接受 docID 整数列表，请先转换"
    i = j = 0
    result = []
    while i < len(a) and j < len(b):
        da = a[i]
        db = b[j]
        if da == db:
            result.append(da)
            i += 1
            j += 1
        elif da < db:
            i += 1
        else:
            j += 1
    return result
def docids(post,w):
    return [d for d,_ in post.get(w,[])]
def multi_and(post, df, words):
    """返回所有词同时出现的 docID 列表（升序）。"""
    if not words:
        return []
    ordered = sorted(words, key=lambda w: df.get(w, 0))
    lists = [docids(post, w) for w in ordered]
    if any(not l for l in lists):
        return []
    res = lists[0]
    for lst in lists[1:]:
        res = intersect(res,lst)
    return res
def search(post, df, query):
    return multi_and(post, df, tokenize(query))




DOCS = {
    1: "railway signal system controls train movement",
    2: "train signal failure causes delay",
    3: "railway bridge inspection and maintenance",
    4: "signal maintenance requires trained staff",
    5: "bridge delay affects train schedule",
}

EXPECT = {
    "signal":      ([(1, 1), (2, 1), (4, 1)], 3),
    "train":       ([(1, 1), (2, 1), (5, 1)], 3),
    "delay":       ([(2, 1), (5, 1)], 2),
    "bridge":      ([(3, 1), (5, 1)], 2),
    "maintenance": ([(3, 1), (4, 1)], 2),
}


if __name__ == "__main__":
    post, df = index_build(DOCS)

    print(f"词条总数: {len(post)}\n")
    for word in EXPECT:
        print(f"{word:12} post={post[word]}  df={df[word]}")

    # 逐条对期望值,有一条不对就报错停下
    for word, (want_post, want_df) in EXPECT.items():
        assert post[word] == want_post, f"{word} 的 posting 不对: {post[word]} != {want_post}"
        assert df[word] == want_df, f"{word} 的 df 不对: {df[word]} != {want_df}"

    a = [d for d, _ in post.get("signal", [])]
    b = [d for d, _ in post.get("train", [])]
    res = intersect(a, b)
    print(res)
    assert res == [1, 2], f"求交结果不对: {res}"
    print("\n全部对上 ")
    assert multi_and(post, df, ["signal","train","delay"]) == [2]
    assert multi_and(post, df, ["signal"]) == [1, 2, 4]
    assert multi_and(post, df, ["signal","nonexistent"]) == []
    assert multi_and(post, df, []) == []
    assert all(docids(post, w) != [] for w in ["signal","train","delay"])

    print("multi_and 全过")

    assert search(post, df, "signal train") == [1, 2]
    assert search(post, df, "signal train delay") == [2]
    assert search(post, df, "bridge") == [3, 5]
    assert search(post, df, "Signal") == [1, 2, 4]
    assert search(post, df, "") == []
    

    ordered = sorted(["signal","train","delay"], key=lambda w: df.get(w, 0))
    print("求交顺序:", ordered)