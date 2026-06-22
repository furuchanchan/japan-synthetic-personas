#!/usr/bin/env python3
# ワークフロー出力(/tmp/narr/part_*.txt の「uuid ||| backstory」)を
# japan_personas_3000_v2.csv にbackstory_250w列としてマージ＋品質検証。
import os, glob, json, re
import pandas as pd

OUTDIR = os.path.expanduser("~/Downloads/japan-personas")
SRC = os.path.join(OUTDIR, "japan_personas_3000_v2.csv")
PARTS = sorted(glob.glob("/tmp/narr/part_*.txt"))
SEP = " ||| "

# --- パース ---
m = {}
dup = 0
badlines = 0
for p in PARTS:
    with open(p, encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if not ln.strip():
                continue
            if SEP not in ln:
                badlines += 1
                continue
            uid, bs = ln.split(SEP, 1)
            uid = uid.strip()
            bs = bs.strip()
            if not uid or not bs:
                badlines += 1
                continue
            if uid in m:
                dup += 1
            m[uid] = bs

df = pd.read_csv(SRC)
df["backstory_250w"] = df["uuid"].astype(str).map(m)
have = df["backstory_250w"].notna()
missing = df.loc[~have, "uuid"].astype(str).tolist()

# --- 品質検証 ---
lens = df.loc[have, "backstory_250w"].str.len()
brands = ["スターバックス","スタバ","セブンイレブン","セブン-イレブン","ファミマ","ファミリーマート",
          "ローソン","イオン","Amazon","アマゾン","楽天","ユニクロ","無印","ニトリ","マクドナルド",
          "ドンキ","コストコ","Netflix","ネットフリックス","YouTube","ユーチューブ","Instagram","インスタ"]
joined = " ".join(df.loc[have, "backstory_250w"].tolist())
leak = {b: joined.count(b) for b in brands if b in joined}

summary = {
    "part_files": len(PARTS),
    "parsed_unique_uuid": len(m),
    "duplicate_overwrite": dup,
    "bad_lines": badlines,
    "rows_total": int(len(df)),
    "rows_with_backstory": int(have.sum()),
    "rows_missing": int((~have).sum()),
    "len_avg": round(float(lens.mean()), 1) if have.any() else None,
    "len_min": int(lens.min()) if have.any() else None,
    "len_max": int(lens.max()) if have.any() else None,
    "len_under_150": int((lens < 150).sum()) if have.any() else None,
    "len_over_320": int((lens > 320).sum()) if have.any() else None,
    "brand_leak": leak if leak else "なし(OK)",
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

# 欠損uuidとバッチ番号(30人=1バッチ)を保存
if missing:
    with open("/tmp/narr/missing_uuids.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(missing))
    miss_idx = df.index[~have].tolist()
    miss_batches = sorted(set(i // 30 for i in miss_idx))
    print("\n欠損バッチ(再実行対象):", miss_batches)

# サンプル3件(before→after)
print("\n=== サンプル ===")
for _, r in df.loc[have].head(3).iterrows():
    print("----")
    print(f"[属性] {r['age']}歳/{r['sex']}/{r['prefecture']}/{r['occupation']}/年収{r['household_income_bracket']}/価格感度{r['price_sensitivity']}/EC{r['ec_adoption']}")
    print(f"[叙述] {r['backstory_250w']}")

# 出力(常に書く。欠損は空欄)
df.to_csv(os.path.join(OUTDIR, "japan_personas_3000_final.csv"), index=False)
df.to_json(os.path.join(OUTDIR, "japan_personas_3000_final.jsonl"), orient="records", lines=True, force_ascii=False)
print("\n出力:", os.path.join(OUTDIR, "japan_personas_3000_final.csv"), "(+.jsonl)")
print("カバレッジ:", f"{int(have.sum())}/{len(df)}", f"({round(100*have.sum()/len(df),1)}%)")
