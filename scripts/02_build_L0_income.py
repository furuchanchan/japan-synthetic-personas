#!/usr/bin/env python3
# L0(核): 国民生活基礎調査0003131978から P(所得金額階級 | 世帯主年齢) を作り、
# 1,000体ペルソナに「年代に整合した世帯年収バンド」を実データ接地で付与する。
# appIdはKeychainから実行時に読み、出力しない。
import subprocess, json, urllib.request, urllib.parse, re, os, random
import pandas as pd

appid = subprocess.run(["security","find-generic-password","-s","estat-app-id","-w"],
                       capture_output=True, text=True, check=True).stdout.strip()
def call(endpoint, params):
    params={**params,"appId":appid}
    url="https://api.e-stat.go.jp/rest/3.0/app/json/"+endpoint+"?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"py"}),timeout=60) as r:
        return json.load(r)

# --- 1) データ取得: tab=145(世帯数), cat01=1(支出総数), 全cat02(所得)×cat03(年齢) ---
d = call("getStatsData", {"statsDataId":"0003131978","cdTab":"145","cdCat01":"1","limit":"3000"})
sd = d["GET_STATS_DATA"]["STATISTICAL_DATA"]
values = sd["DATA_INF"]["VALUE"]
# 最新時点を選ぶ
times = sorted({v.get("@time") for v in values})
latest = times[-1]
print("取得時点(最新):", latest, "/ 全時点:", times)

# 所得階級コード→名称, 年齢コード→名称 をメタから
meta = call("getMetaInfo", {"statsDataId":"0003131978"})["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
def catmap(cid):
    for c in meta:
        if c["@id"]==cid:
            cats=c["CLASS"];  cats=[cats] if isinstance(cats,dict) else cats
            return {x["@code"]:x["@name"] for x in cats}
    return {}
inc_name=catmap("cat02"); age_name=catmap("cat03")

# 所得階級名→数値midpoint(万円)
def midpoint(name):
    name=name.replace("，","").replace(",","")
    if "未満" in name and "～" not in name:  # 「50万円未満」
        m=re.search(r"(\d+)万", name); return int(m.group(1))/2 if m else None
    if "以上" in name and "～" not in name:  # 「2000万円以上」
        m=re.search(r"(\d+)万", name); return int(m.group(1))*1.15 if m else None
    m=re.findall(r"(\d+)", name)            # 「100～150万円未満」
    if len(m)>=2: return (int(m[0])+int(m[1]))/2
    return None

# (年齢コード)->{所得コード:世帯数}
from collections import defaultdict
tbl=defaultdict(dict)
for v in values:
    if v.get("@time")!=latest: continue
    a=v.get("@cat03"); i=v.get("@cat02")
    try: cnt=float(v.get("$"))
    except: continue
    tbl[a][i]=cnt

# --- 2) P(所得 | 年齢) を構築（総数=1 と 不詳/再掲は除外） ---
REAL_AGE=["120","320","330","340","350","370","520"]  # 29以下,30,40,50,60,70,80+
def cond_dist(age_code):
    row=tbl.get(age_code,{})
    items=[(i,c) for i,c in row.items()
           if i!="1" and "不詳" not in inc_name.get(i,"") and midpoint(inc_name.get(i,"")) is not None]
    tot=sum(c for _,c in items)
    return [(i, c/tot) for i,c in items] if tot>0 else []

dists={a:cond_dist(a) for a in REAL_AGE}
# 確認出力: 各年代の中央付近
print("\n=== P(所得│世帯主年齢) サンプル（代表的バンドの割合%）===")
for a in REAL_AGE:
    dd=dict(dists[a]);
    # 上位3バンド
    top=sorted(dists[a], key=lambda x:-x[1])[:3]
    s=" / ".join(f"{inc_name[i]} {p*100:.0f}%" for i,p in top)
    print(f"  {age_name[a]:>8}: {s}")

# --- 3) ペルソナへ付与 ---
PERS="/Users/koutaroufuruno/Downloads/japan-personas/japan_personas_1000.csv"
df=pd.read_csv(PERS)
def to_agecode(age):
    a=int(age)
    if a<30: return "120"
    if a<40: return "320"
    if a<50: return "330"
    if a<60: return "340"
    if a<70: return "350"
    if a<80: return "370"
    return "520"
rng=random.Random(42)
def sample_income(agecode):
    dd=dists[agecode]
    r=rng.random(); acc=0
    for i,p in dd:
        acc+=p
        if r<=acc: return i
    return dd[-1][0]
inc_codes=[]
for _,row in df.iterrows():
    ic=sample_income(to_agecode(row["age"]))
    inc_codes.append(ic)
df["household_income_bracket"]=[inc_name[c] for c in inc_codes]
df["household_income_midpoint_manyen"]=[midpoint(inc_name[c]) for c in inc_codes]
df["household_income_source"]="国民生活基礎調査(0003131978) P(所得階級|世帯主年齢) 条件付きサンプリング・"+str(latest)

# --- 4) 検証: 年代×年収の相関が出ているか ---
df["age_band"]=df["age"].apply(lambda a: "20代以下" if a<30 else "30代" if a<40 else "40代" if a<50 else "50代" if a<60 else "60代" if a<70 else "70代" if a<80 else "80歳~")
piv=df.groupby("age_band")["household_income_midpoint_manyen"].mean().round(0)
print("\n=== 検証: 付与後の 年代別 平均世帯年収(万円・midpoint近似) ===")
print(piv.to_string())
print("\n全体 平均世帯年収(midpoint近似):", round(df["household_income_midpoint_manyen"].mean(),0),"万円")

OUT="/Users/koutaroufuruno/Downloads/japan-personas/japan_personas_1000_L0income.csv"
df.to_csv(OUT,index=False)
print("\n出力:",OUT)
