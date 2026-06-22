#!/usr/bin/env python3
# 代表性プール n=3,000 を生成:
#  (1) Nemotron-Personas-Japan を age_band×sex で人口構成比サンプリング
#  (2) e-Stat 国民生活基礎調査(0003131978)で P(所得|世帯主年齢) を作り世帯年収バンドを接地
#  (3) 分布を検証して出力。appIdはKeychainから実行時に読む。
import subprocess, json, urllib.request, urllib.parse, re, os, random
from collections import defaultdict
import pandas as pd
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq

OUTDIR = os.path.expanduser("~/Downloads/japan-personas"); os.makedirs(OUTDIR, exist_ok=True)
N = 3000; SEED = 42
appid = subprocess.run(["security","find-generic-password","-s","estat-app-id","-w"],
                       capture_output=True, text=True, check=True).stdout.strip()
def call(ep, p):
    p={**p,"appId":appid}; url="https://api.e-stat.go.jp/rest/3.0/app/json/"+ep+"?"+urllib.parse.urlencode(p)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"py"}),timeout=60) as r: return json.load(r)

# --- (1) シャード→層化サンプリング ---
path = hf_hub_download("nvidia/Nemotron-Personas-Japan","data/train-00000-of-00008.parquet",repo_type="dataset")
df = pq.read_table(path).to_pandas()
df["age"]=pd.to_numeric(df["age"],errors="coerce"); df=df.dropna(subset=["age","sex"]).copy(); df["age"]=df["age"].astype(int)
def band(a): return "20代以下" if a<30 else "30代" if a<40 else "40代" if a<50 else "50代" if a<60 else "60代" if a<70 else "70代" if a<80 else "80歳以上"
df["age_band"]=df["age"].apply(band); df["stratum"]=df["age_band"]+"_"+df["sex"].astype(str)
shares=df["stratum"].value_counts(normalize=True)
target={k:int(round(v*N)) for k,v in shares.items()}; diff=N-sum(target.values()); order=shares.index.tolist(); i=0
while diff!=0:
    k=order[i%len(order)]
    if diff>0: target[k]+=1; diff-=1
    elif target[k]>0: target[k]-=1; diff+=1
    i+=1
parts=[df[df["stratum"]==k].sample(n=min(n,len(df[df["stratum"]==k])),random_state=SEED) for k,n in target.items() if n>0]
pool=pd.concat(parts).sample(frac=1,random_state=SEED).reset_index(drop=True)

# --- (2) e-Stat P(所得|世帯主年齢) を接地 ---
d=call("getStatsData",{"statsDataId":"0003131978","cdTab":"145","cdCat01":"1","limit":"3000"})
vals=d["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
meta=call("getMetaInfo",{"statsDataId":"0003131978"})["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
inc_name={x["@code"]:x["@name"] for c in meta if c["@id"]=="cat02" for x in (c["CLASS"] if isinstance(c["CLASS"],list) else [c["CLASS"]])}
def mid(name):
    name=name.replace("，","")
    if "未満" in name and "～" not in name: m=re.search(r"(\d+)万",name); return int(m.group(1))/2 if m else None
    if "以上" in name and "～" not in name: m=re.search(r"(\d+)万",name); return int(m.group(1))*1.15 if m else None
    m=re.findall(r"(\d+)",name); return (int(m[0])+int(m[1]))/2 if len(m)>=2 else None
tbl=defaultdict(dict)
for v in vals:
    try: tbl[v.get("@cat03")][v.get("@cat02")]=float(v.get("$"))
    except: pass
def cond(age):
    row=tbl.get(age,{}); items=[(i,c) for i,c in row.items() if i!="1" and "不詳" not in inc_name.get(i,"") and mid(inc_name.get(i,"")) is not None]
    tot=sum(c for _,c in items); return [(i,c/tot) for i,c in items] if tot>0 else []
agemap=lambda a:"120" if a<30 else "320" if a<40 else "330" if a<50 else "340" if a<60 else "350" if a<70 else "370" if a<80 else "520"
dists={ac:cond(ac) for ac in ["120","320","330","340","350","370","520"]}
rng=random.Random(SEED)
def samp(ac):
    dd=dists[ac]; r=rng.random(); acc=0
    for i,p in dd:
        acc+=p
        if r<=acc: return i
    return dd[-1][0]
codes=[samp(agemap(int(a))) for a in pool["age"]]
pool["household_income_bracket"]=[inc_name[c] for c in codes]
pool["household_income_midpoint_manyen"]=[mid(inc_name[c]) for c in codes]
pool["household_income_source"]="国民生活基礎調査(0003131978) P(所得階級|世帯主年齢)条件付き"

# --- (3) 検証＋出力 ---
pool=pool.drop(columns=["stratum"])
pool.to_csv(os.path.join(OUTDIR,"japan_personas_3000.csv"),index=False)
pool.to_json(os.path.join(OUTDIR,"japan_personas_3000.jsonl"),orient="records",lines=True,force_ascii=False)
rep={
 "n":int(len(pool)),
 "性別%":{k:round(v*100,1) for k,v in pool["sex"].value_counts(normalize=True).items()},
 "年代%":{k:round(v*100,1) for k,v in pool["age_band"].value_counts(normalize=True).reindex(["20代以下","30代","40代","50代","60代","70代","80歳以上"]).dropna().items()},
 "平均年齢":round(float(pool["age"].mean()),1),
 "都道府県数":int(pool["prefecture"].nunique()),
 "都道府県上位5%":{k:round(v*100,1) for k,v in pool["prefecture"].value_counts(normalize=True).head(5).items()},
 "都道府県最少件数":int(pool["prefecture"].value_counts().min()),
 "全体平均世帯年収_万":round(float(pool["household_income_midpoint_manyen"].mean()),0),
 "年代別平均世帯年収_万":{k:round(v,0) for k,v in pool.groupby("age_band")["household_income_midpoint_manyen"].mean().reindex(["20代以下","30代","40代","50代","60代","70代","80歳以上"]).dropna().items()},
}
json.dump(rep,open(os.path.join(OUTDIR,"distribution_3000.json"),"w"),ensure_ascii=False,indent=2)
print(json.dumps(rep,ensure_ascii=False,indent=2))
print("\n出力:",os.path.join(OUTDIR,"japan_personas_3000.csv"),"(+.jsonl, distribution_3000.json)")
