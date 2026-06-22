#!/usr/bin/env python3
# ① OT結合接地: 年収を「年代×地域」で条件付け（独立サンプリングの歪みを是正）
#    - 国民生活基礎調査0003131978: P(所得|世帯主年齢)
#    - 全国家計構造調査0003426512: 県別平均世帯年収 → 地域所得指数
#    年収 = P(所得|年代)からサンプル → 地域指数で補正 → 最近接バンドへ。
#    その後 L1(価格感度/PB-NB/チャネル等)を新年収で再導出。
import subprocess, json, urllib.request, urllib.parse, re, os, random
from collections import defaultdict
import pandas as pd
OUTDIR=os.path.expanduser("~/Downloads/japan-personas")
appid=subprocess.run(["security","find-generic-password","-s","estat-app-id","-w"],capture_output=True,text=True).stdout.strip()
def call(ep,p):
    p={**p,"appId":appid}; url="https://api.e-stat.go.jp/rest/3.0/app/json/"+ep+"?"+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"py"}),timeout=60))
def midpoint(name):
    name=name.replace("，","").replace(",","")
    if "未満" in name and "～" not in name: m=re.search(r"(\d+)万",name); return int(m.group(1))/2 if m else None
    if ("以上" in name) and "～" not in name: m=re.search(r"(\d+)万",name); return int(m.group(1))*1.15 if m else None
    m=re.findall(r"(\d+)",name); return (int(m[0])+int(m[1]))/2 if len(m)>=2 else None

# --- P(所得|世帯主年齢) ---
d=call("getStatsData",{"statsDataId":"0003131978","cdTab":"145","cdCat01":"1","limit":"3000"})
vals=d["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
m=call("getMetaInfo",{"statsDataId":"0003131978"})["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
inc_name={x["@code"]:x["@name"] for c in m if c["@id"]=="cat02" for x in (c["CLASS"] if isinstance(c["CLASS"],list) else [c["CLASS"]])}
tbl=defaultdict(dict)
for v in vals:
    try: tbl[v.get("@cat03")][v.get("@cat02")]=float(v.get("$"))
    except: pass
def cond(age):
    row=tbl.get(age,{}); items=[(i,c) for i,c in row.items() if i!="1" and "不詳" not in inc_name.get(i,"") and midpoint(inc_name.get(i,"")) is not None]
    tot=sum(c for _,c in items); return [(i,c/tot) for i,c in items] if tot>0 else []
AGE=["120","320","330","340","350","370","520"]; dists={a:cond(a) for a in AGE}
brackets=[(i,midpoint(inc_name[i])) for i,_ in dists["330"]]  # (code, midpoint)
agecode=lambda a:"120" if a<30 else "320" if a<40 else "330" if a<50 else "340" if a<60 else "350" if a<70 else "370" if a<80 else "520"

# --- 県別平均世帯年収 → 地域指数 ---
meta2=call("getMetaInfo",{"statsDataId":"0003426512"})["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
area_name={x["@code"]:x["@name"] for c in meta2 if c["@id"]=="area" for x in c["CLASS"]}
# 金額tabを特定（unitが円/千円/万円）。cat01=0総世帯,cat02=0全世帯,cat03=2年間収入,cat04=00平均
dd=call("getStatsData",{"statsDataId":"0003426512","cdCat01":"0","cdCat02":"0","cdCat03":"2","cdCat04":"00","limit":"500"})
v2=dd["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
def to_manyen(val,unit):
    val=float(val)
    if "万" in unit: return val
    if "千" in unit: return val/10.0
    if unit=="円": return val/10000.0
    return val
pref_income={}
for v in v2:
    u=v.get("@unit","")
    if not any(s in u for s in ["円"]): continue
    try: pref_income[area_name.get(v.get("@area"),v.get("@area"))]=to_manyen(v.get("$"),u)
    except: pass
nat=sum(pref_income.values())/len(pref_income)
region_index={k:(val/nat) for k,val in pref_income.items()}  # 1.0=全国平均
print("地域所得指数 サンプル: 東京",round(region_index.get("東京都",0),2),"/ 大阪",round(region_index.get("大阪府",0),2),
      "/ 沖縄",round(region_index.get("沖縄県",0),2),"/ 全国基準",round(nat,0),"万")

# --- 年収を 年代×地域 で条件付け ---
df=pd.read_csv(os.path.join(OUTDIR,"japan_personas_3000.csv"))
rng=random.Random(42)
def samp_age(ac):
    dd=dists[ac]; r=rng.random(); acc=0
    for i,p in dd:
        acc+=p
        if r<=acc: return midpoint(inc_name[i])
    return midpoint(inc_name[dd[-1][0]])
def snap(mid_adj):
    return min(brackets,key=lambda b:abs(b[1]-mid_adj))
codes=[]; mids=[]
for _,r in df.iterrows():
    base=samp_age(agecode(int(r["age"])))
    idx=region_index.get(r["prefecture"],1.0)
    adj=base*(0.5+0.5*idx)  # 地域指数を半分の強さで反映（過補正回避）
    c,mid=snap(adj); codes.append(c); mids.append(mid)
df["household_income_bracket"]=[inc_name[c] for c in codes]
df["household_income_midpoint_manyen"]=mids
df["household_income_source"]="国民生活基礎調査(0003131978)P(所得|年代)×全国家計構造調査(0003426512)県別所得指数 で年代×地域条件付け"

# --- L1 を新年収で再導出（自由連続値なし・両極維持） ---
SEED=7; r1=random.Random(SEED)
def pick(dist):
    x=r1.random(); acc=0
    for lab,p in dist:
        acc+=p
        if x<=acc: return lab
    return dist[-1][0]
def tier(mm): return "low" if mm<350 else "high" if mm>=700 else "mid"
METRO={"東京都","神奈川県","大阪府","愛知県","埼玉県","千葉県","兵庫県","福岡県","京都府"}
PRICE={"low":[("高",.55),("中",.35),("低",.10)],"mid":[("高",.30),("中",.45),("低",.25)],"high":[("高",.15),("中",.40),("低",.45)]}
DISP={"low":[("切り詰め",.50),("普通",.40),("ゆとり",.10)],"mid":[("切り詰め",.25),("普通",.50),("ゆとり",.25)],"high":[("切り詰め",.10),("普通",.40),("ゆとり",.50)]}
BRAND={"low":[("PB志向",.45),("PB-NB併用",.40),("NB・品質志向",.15)],"mid":[("PB志向",.25),("PB-NB併用",.50),("NB・品質志向",.25)],"high":[("PB志向",.15),("PB-NB併用",.45),("NB・品質志向",.40)]}
PROMO={"高":[("高",.6),("中",.3),("低",.1)],"中":[("高",.3),("中",.5),("低",.2)],"低":[("高",.1),("中",.4),("低",.5)]}
BULK={"高":[("よくする",.5),("たまに",.4),("しない",.1)],"中":[("よくする",.3),("たまに",.5),("しない",.2)],"低":[("よくする",.15),("たまに",.45),("しない",.4)]}
EC={"young":[("高",.6),("中",.3),("低",.1)],"mid":[("高",.35),("中",.45),("低",.2)],"senior":[("高",.15),("中",.4),("低",.45)]}
g=lambda a:"young" if a<35 else "senior" if a>=65 else "mid"
def chan(a,metro):
    grp=g(a)
    if grp=="young": return "EC・コンビニ・ドラッグストア中心" if metro else "EC・ドラッグストア・郊外量販(車)"
    if grp=="mid": return "スーパー・ドラッグストア・EC併用(駅前)" if metro else "スーパー・ドラッグストア・EC・郊外量販(車)"
    return "スーパー・ドラッグストア・地域商店(駅前/徒歩)" if metro else "スーパー・ドラッグストア・地域商店(車/家族送迎)"
med=lambda a:"SNS・動画中心(ネット>テレビ)" if a<35 else "ネット・テレビ併用" if a<60 else "テレビ・新聞中心(ネット利用は限定的)"
t=df["household_income_midpoint_manyen"].apply(tier)
df["income_tier"]=t
df["disposable_income_feel"]=[pick(DISP[x]) for x in t]
df["price_sensitivity"]=[pick(PRICE[x]) for x in t]
df["brand_orientation"]=[pick(BRAND[x]) for x in t]
df["promotion_responsiveness"]=[pick(PROMO[p]) for p in df["price_sensitivity"]]
df["bulk_buy_tendency"]=[pick(BULK[p]) for p in df["price_sensitivity"]]
df["ec_adoption"]=[pick(EC[g(int(a))]) for a in df["age"]]
df["primary_purchase_channels"]=[chan(int(a),pref in METRO) for a,pref in zip(df["age"],df["prefecture"])]
df["media_contact"]=[med(int(a)) for a in df["age"]]

df.to_csv(os.path.join(OUTDIR,"japan_personas_3000_v2.csv"),index=False)
df.to_json(os.path.join(OUTDIR,"japan_personas_3000_v2.jsonl"),orient="records",lines=True,force_ascii=False)

# --- 検証 ---
print("\n=== ①効果: 年収×地域（独立サンプリングなら全県同じになるはず→差が出れば接地成功） ===")
for pf in ["東京都","神奈川県","大阪府","愛知県","沖縄県","青森県","鹿児島県"]:
    sub=df[df["prefecture"]==pf]["household_income_midpoint_manyen"]
    print(f"  {pf}: 平均世帯年収 {round(sub.mean(),0)}万 (n={len(sub)})")
print("  全国平均:",round(df["household_income_midpoint_manyen"].mean(),0),"万")
print("\n=== 年齢カーブが保たれているか(年代別平均年収) ===")
for ab in ["20代以下","30代","40代","50代","60代","70代","80歳以上"]:
    print(f"  {ab}: {round(df[df['age_band']==ab]['household_income_midpoint_manyen'].mean(),0)}万")
print("\n出力:",os.path.join(OUTDIR,"japan_personas_3000_v2.csv"))
