#!/usr/bin/env python3
# ② Anthology法: 属性羅列でなく「名前＋一人称インタビュー叙述」を生成。
#    ステレオタイプ回避(名前ベース/インタビュー形式/必ず例外的こだわり)・固有ブランド禁止・数値と無矛盾。
#    まず多様な18体で品質検証(before→after)。APIキーはKeychainから実行時に読み出力しない。
import subprocess, json, urllib.request, re, os, random
import pandas as pd
OUTDIR=os.path.expanduser("~/Downloads/japan-personas")
KEY=subprocess.run(["security","find-generic-password","-s","gbrain-anthropic","-w"],capture_output=True,text=True).stdout.strip()
MODEL="claude-haiku-4-5"
df=pd.read_csv(os.path.join(OUTDIR,"japan_personas_3000_v2.csv"))

# 多様な18体を層化抽出（年代×income_tier×metro）
METRO={"東京都","神奈川県","大阪府","愛知県","埼玉県","千葉県","兵庫県","福岡県","京都府"}
df["metro"]=df["prefecture"].isin(METRO)
picks=[]; seen=set()
rng=random.Random(1)
idx=list(df.index); rng.shuffle(idx)
for i in idx:
    r=df.loc[i]; key=(r["age_band"], r["income_tier"], r["metro"])
    if key in seen: continue
    seen.add(key); picks.append(i)
    if len(picks)>=18: break
sample=df.loc[picks].reset_index(drop=True)

def first_name(persona):
    m=re.match(r"\s*([^\sは、。]+(?:\s[^\sは、。]+)?)は", str(persona))
    return m.group(1).strip() if m else "この人物"

SYS=("あなたは日本の生活実態に精通したインタビュアー兼ライターです。与える人物像は公的統計(国勢調査・国民生活基礎調査・全国家計構造調査)に接地済みです。"
 "これを、その人が自分の暮らしを語る『一人称インタビュー』の文章に変換してください。約220〜260字。"
 "厳守: (1)属性を箇条書きにせず生活の語りに溶かす (2)世帯年収バンド・価格感度・購買チャネルと矛盾させない "
 "(3)実在ブランド・店舗・施設の固有名詞は出さない(『大手カフェチェーン』『近所のドラッグストア』等に一般化) "
 "(4)ステレオタイプ(『低所得=全方位節約』『高齢=保守的でデジタル弱者』『主婦=購買主導』『地方=○○』等)を避ける。"
 "そのために必ず一つ、その人ならではの『例外的なこだわり/選択的支出』を入れる "
 "(5)出力は本文の語りのみ。前置き・見出し・鉤括弧の説明は不要。")

def gen(row):
    nm=first_name(row.get("persona",""))
    facts=(f"名前:{nm} / 年齢:{row['age']} / 性別:{row['sex']} / 居住:{row['prefecture']} / 学歴:{row['education_level']} / "
           f"職業:{row['occupation']} / 婚姻:{row['marital_status']} / 世帯年収バンド:{row['household_income_bracket']} / "
           f"可処分感:{row['disposable_income_feel']} / 価格感度:{row['price_sensitivity']} / ブランド観:{row['brand_orientation']} / "
           f"主な買い物チャネル:{row['primary_purchase_channels']} / EC利用:{row['ec_adoption']} / メディア:{row['media_contact']}")
    seed=(f"参考(NVIDIA生成の人物像・矛盾しない範囲で活用): {str(row.get('persona',''))[:160]} / "
          f"趣味:{str(row.get('hobbies_and_interests',''))[:120]}")
    body=json.dumps({"model":MODEL,"max_tokens":600,"system":SYS,
        "messages":[{"role":"user","content":f"次の人物の一人称インタビュー叙述を書いてください。\n{facts}\n{seed}"}]}).encode()
    req=urllib.request.Request("https://api.anthropic.com/v1/messages",data=body,headers={
        "x-api-key":KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
    r=json.load(urllib.request.urlopen(req,timeout=60))
    return "".join(b.get("text","") for b in r.get("content",[]) if b.get("type")=="text").strip()

out=[]
for _,row in sample.iterrows():
    try: nar=gen(row)
    except Exception as e: nar=f"[ERR {e}]"
    out.append({"uuid":row["uuid"],"before":f"{row['age']}歳/{row['sex']}/{row['prefecture']}/{row['education_level']}/{row['occupation']}/年収{row['household_income_bracket']}/価格感度{row['price_sensitivity']}","backstory":nar})

# 保存＋before→afterを3体表示
sample2=sample.copy(); sample2["backstory_250w"]=[o["backstory"] for o in out]
sample2.to_csv(os.path.join(OUTDIR,"japan_personas_sample18_narrative.csv"),index=False)
print(f"生成: {len(out)}体 / モデル {MODEL}")
for o in out[:3]:
    print("\n----------------------------------------")
    print("【before(薄い)】", o["before"])
    print("【after(叙述)】", o["backstory"])
print("\n... 残り15体は japan_personas_sample18_narrative.csv に保存")
# 簡易チェック: 固有ブランドや禁止語の混入確認
import re as _re
joined=" ".join(o["backstory"] for o in out)
ng=[w for w in ["スターバックス","セブン","イオン","Amazon","アマゾン","ユニクロ","無印","ニトリ"] if w in joined]
print("固有ブランド混入:", ng if ng else "なし(OK)")
print("平均文字数:", round(sum(len(o['backstory']) for o in out)/len(out),0))
