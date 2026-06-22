#!/usr/bin/env python3
# L1 消費レイヤー: 接地済み世帯年収＋年代＋地域から、価格感度・PB/NB・チャネル等を
# 「年収条件付きの3類型」で付与。自由連続スコア禁止/両極を残して画一化回避。
import os, json, random
import pandas as pd

OUTDIR = os.path.expanduser("~/Downloads/japan-personas")
SEED = 7
df = pd.read_csv(os.path.join(OUTDIR, "japan_personas_3000.csv"))
rng = random.Random(SEED)

def pick(dist):  # dist: list[(label, prob)] -> sampled label (両極を必ず残す)
    r = rng.random(); acc = 0
    for lab, p in dist:
        acc += p
        if r <= acc: return lab
    return dist[-1][0]

# 年収tier（midpoint・万円）。両極の個体は各tierに残す
def tier(m):
    if pd.isna(m): return "mid"
    return "low" if m < 350 else "high" if m >= 700 else "mid"

METRO = {"東京都","神奈川県","大阪府","愛知県","埼玉県","千葉県","兵庫県","福岡県","京都府"}

# 条件付き分布（低所得ほど価格感度↑だが、低感度の低所得・高感度の高所得も必ず残す）
PRICE = {"low":[("高",.55),("中",.35),("低",.10)], "mid":[("高",.30),("中",.45),("低",.25)], "high":[("高",.15),("中",.40),("低",.45)]}
DISP  = {"low":[("切り詰め",.50),("普通",.40),("ゆとり",.10)], "mid":[("切り詰め",.25),("普通",.50),("ゆとり",.25)], "high":[("切り詰め",.10),("普通",.40),("ゆとり",.50)]}
BRAND = {"low":[("PB志向",.45),("PB-NB併用",.40),("NB・品質志向",.15)], "mid":[("PB志向",.25),("PB-NB併用",.50),("NB・品質志向",.25)], "high":[("PB志向",.15),("PB-NB併用",.45),("NB・品質志向",.40)]}
PROMO = {"高":[("高",.6),("中",.3),("低",.1)], "中":[("高",.3),("中",.5),("低",.2)], "低":[("高",.1),("中",.4),("低",.5)]}
BULK  = {"高":[("よくする",.5),("たまに",.4),("しない",.1)], "中":[("よくする",.3),("たまに",.5),("しない",.2)], "低":[("よくする",.15),("たまに",.45),("しない",.4)]}
EC    = {"young":[("高",.6),("中",.3),("低",.1)], "mid":[("高",.35),("中",.45),("低",.2)], "senior":[("高",.15),("中",.4),("低",.45)]}

def agegrp(a): return "young" if a<35 else "senior" if a>=65 else "mid"
def channels(a, metro):
    g = agegrp(a)
    if g=="young":  return ("EC・コンビニ・ドラッグストア中心" if metro else "EC・ドラッグストア・郊外量販(車)")
    if g=="mid":    return ("スーパー・ドラッグストア・EC併用(駅前)" if metro else "スーパー・ドラッグストア・EC・郊外量販(車)")
    return ("スーパー・ドラッグストア・地域商店(駅前/徒歩)" if metro else "スーパー・ドラッグストア・地域商店(車/家族送迎)")
def media(a):
    if a<35: return "SNS・動画中心(ネット>テレビ)"
    if a<60: return "ネット・テレビ併用"
    return "テレビ・新聞中心(ネット利用は限定的)"

t   = df["household_income_midpoint_manyen"].apply(tier)
df["income_tier"]               = t
df["disposable_income_feel"]    = [pick(DISP[x])  for x in t]
df["price_sensitivity"]         = [pick(PRICE[x]) for x in t]
df["brand_orientation"]         = [pick(BRAND[x]) for x in t]
df["promotion_responsiveness"]  = [pick(PROMO[p]) for p in df["price_sensitivity"]]
df["bulk_buy_tendency"]         = [pick(BULK[p])  for p in df["price_sensitivity"]]
df["ec_adoption"]               = [pick(EC[agegrp(int(a))]) for a in df["age"]]
df["primary_purchase_channels"] = [channels(int(a), pref in METRO) for a,pref in zip(df["age"], df["prefecture"])]
df["media_contact"]             = [media(int(a)) for a in df["age"]]
df["L1_method"] = "年収tier条件付き3類型(自由連続値なし)。方向性は家計調査の平均消費性向/エンゲル係数(低所得ほど価格感度高)に整合。家計調査クロスでの較正は次段。"

df.to_csv(os.path.join(OUTDIR,"japan_personas_3000_enriched.csv"), index=False)
df.to_json(os.path.join(OUTDIR,"japan_personas_3000_enriched.jsonl"), orient="records", lines=True, force_ascii=False)

# --- 検証: 画一化していないか(各income tierで両極が残るか) ---
def dist(s):
    vc = s.value_counts(normalize=True)*100
    return {k:round(v,0) for k,v in vc.items()}
print("=== price_sensitivity × income_tier (両極が残るかの確認) ===")
for tr in ["low","mid","high"]:
    sub = df[df["income_tier"]==tr]["price_sensitivity"]
    print(f"  年収{tr:>4} (n={len(df[df['income_tier']==tr])}): {dist(sub)}")
print("\n=== brand_orientation × income_tier ===")
for tr in ["low","mid","high"]:
    print(f"  年収{tr:>4}: {dist(df[df['income_tier']==tr]['brand_orientation'])}")
print("\n=== ec_adoption × 年代 ===")
for ab in ["20代以下","40代","70代"]:
    print(f"  {ab}: {dist(df[df['age_band']==ab]['ec_adoption'])}")
print("\n全体 price_sensitivity:", dist(df["price_sensitivity"]))
print("追加列:", [c for c in df.columns if c in ["disposable_income_feel","price_sensitivity","brand_orientation","promotion_responsiveness","bulk_buy_tendency","ec_adoption","primary_purchase_channels","media_contact"]])
print("出力:", os.path.join(OUTDIR,"japan_personas_3000_enriched.csv"))
