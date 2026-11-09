# -*- coding: utf-8 -*-
"""对普速 462 条算 cf / df，验证「cf 相同但 df 天差地别」。一次性统计脚本。"""
import json, sys, math, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import jieba

if len(sys.argv) < 2:
    print("usage: python _cfdf_stats.py <corpus.json>")
    sys.exit(1)
p = sys.argv[1]
data = json.load(open(p, encoding="utf-8"))
arts = data["articles"]
N = len(arts)
print("articles =", N)

PUNCT = re.compile(r"^[\W_]+$", re.UNICODE)
df, cf = {}, {}
for a in arts:
    toks = [t for t in jieba.lcut(a.get("text", ""))
            if t.strip() and not PUNCT.match(t)]
    seen = set()
    for t in toks:
        cf[t] = cf.get(t, 0) + 1
        if t not in seen:
            seen.add(t)
            df[t] = df.get(t, 0) + 1

print("vocab =", len(df), "| avg df =", round(sum(df.values()) / len(df), 2))

print("\n--- 三个词的实测 ---")
for w in ["的", "列车", "调车"]:
    if w in df:
        print(f"{w}: df={df[w]:>4}  cf={cf[w]:>5}  idf=log2({N}/df)={math.log2(N / df[w]):>5.2f}")
    else:
        print(f"{w}: 未出现")

print("\n--- cf 最高的 10 个（最常见 = 最该进停用词表）---")
for w, c in sorted(cf.items(), key=lambda x: -x[1])[:10]:
    print(f"{w}: df={df[w]:>4} cf={c:>5} idf={math.log2(N / df[w]):>5.2f}")

print("\n--- cf/df 最高：只在极少数条里出现、但每条里反复出现 ---")
cand = [(w, df[w], cf[w], cf[w] / df[w]) for w in df if df[w] >= 3 and cf[w] >= 5]
for w, dd, cc, r in sorted(cand, key=lambda x: -x[3])[:12]:
    print(f"{w}: df={dd:>3} cf={cc:>4} cf/df={r:>4.1f}  即平均每条出现 {r:.1f} 次")

print("\n--- 反例：cf 相同、df 差 10 倍以上的词对 ---")
vals = sorted({cf[w] for w in cf if cf[w] >= 20})
found = 0
for v in vals:
    grp = sorted([(w, df[w]) for w in cf if cf[w] == v], key=lambda x: x[1])
    if len(grp) >= 2 and grp[-1][1] >= grp[0][1] * 5:
        print(f"cf={v}: " + "  vs  ".join(f"{w}(df={dd})" for w, dd in (grp[0], grp[-1])))
        found += 1
        if found >= 5:
            break
if not found:
    print("（没有恰好 cf 相同的，看上面的 cf/df 表即可）")
