#!/usr/bin/env python3
# 完成DB(japan_personas_3000_final.csv)から、年代×所得tier×都市/地方が散る代表サンプルを表示。
import os, textwrap, random
import pandas as pd

CSV = os.path.expanduser("~/Downloads/japan-personas/japan_personas_3000_final.csv")
df = pd.read_csv(CSV)

# --- 全体像 ---
print("="*78)
print(f"DB全体像  行数={len(df)}  列数={df.shape[1]}  backstory充足={df['backstory_250w'].notna().sum()}/{len(df)}")
print("="*78)
print("列一覧:")
print("  " + " / ".join(df.columns.tolist()))
print()
print(f"性別: {dict(df['sex'].value_counts())}")
print(f"年代: {dict(df['age_band'].value_counts().reindex(['20代以下','30代','40代','50代','60代','70代','80歳以上']).dropna().astype(int))}")
print(f"所得tier: {dict(df['income_tier'].value_counts())}")
print(f"全国平均世帯年収: {round(df['household_income_midpoint_manyen'].mean())}万  / 都道府県数: {df['prefecture'].nunique()}")
print(f"backstory文字数: 平均{round(df['backstory_250w'].str.len().mean(),1)} (最短{df['backstory_250w'].str.len().min()} / 最長{df['backstory_250w'].str.len().max()})")

# --- 層化して多様な10体を抽出 ---
METRO = {"東京都","神奈川県","大阪府","愛知県","埼玉県","千葉県","兵庫県","福岡県","京都府"}
df["metro"] = df["prefecture"].isin(METRO)
rng = random.Random(3)
idx = list(df.index); rng.shuffle(idx)
seen = set(); picks = []
for i in idx:
    r = df.loc[i]
    key = (r["age_band"], r["income_tier"], r["metro"])
    if key in seen:
        continue
    seen.add(key); picks.append(i)
    if len(picks) >= 10:
        break

print("\n" + "="*78)
print(f"代表サンプル {len(picks)}体（年代×所得×都市/地方で層化抽出）")
print("="*78)
for n, i in enumerate(picks, 1):
    r = df.loc[i]
    print(f"\n──[{n}] uuid={r['uuid'][:8]}… ─────────────────────────────────────────")
    print(f"  属性  {r['age']}歳 {r['sex']} / {r['prefecture']}{'(都市圏)' if r['metro'] else '(非都市圏)'} / {r['occupation']} / {r['marital_status']} / {r['education_level']}")
    print(f"  接地  世帯年収{r['household_income_bracket']}({r['income_tier']}) / 可処分感:{r['disposable_income_feel']} / 価格感度:{r['price_sensitivity']} / ブランド観:{r['brand_orientation']}")
    print(f"  購買  チャネル:{r['primary_purchase_channels']} / EC:{r['ec_adoption']} / メディア:{r['media_contact']}")
    print(f"  叙述(backstory_250w):")
    for line in textwrap.wrap(str(r["backstory_250w"]), width=58):
        print(f"      {line}")
