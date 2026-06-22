"""
Quickstart — 読み込みとスライス（30秒で動く）
    pip install datasets
    python quickstart.py
"""
from datasets import load_dataset

# Hugging Face から直接ロード（自動でキャッシュされる）
ds = load_dataset("furuchanchan/japan-synthetic-personas", split="train")
print(f"{len(ds):,} personas / {len(ds.column_names)} columns")

# 例: 30代・高所得・EC利用が高い女性だけ抽出
sub = ds.filter(
    lambda r: r["age_band"] == "30代"
    and r["income_tier"] == "high"
    and r["ec_adoption"] == "高"
    and r["sex"] == "女"
)
print(f"\nmatched personas: {len(sub)}")

# 1体の生活叙述（backstory）を見てみる
p = sub[0]
print(f"\n--- {p['age']}歳 / {p['sex']} / {p['prefecture']} / {p['occupation']} ---")
print(p["backstory_250w"])

# pandas 派はこちら
# import pandas as pd
# df = ds.to_pandas()
# df.groupby("income_tier")["household_income_midpoint_manyen"].mean()
