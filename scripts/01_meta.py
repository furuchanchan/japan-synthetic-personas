#!/usr/bin/env python3
# 0003131978 のメタ情報（軸=CLASS_OBJ と各カテゴリ）を確認。appIdは出さない。
import subprocess, json, urllib.request, urllib.parse

appid = subprocess.run(["security","find-generic-password","-s","estat-app-id","-w"],
                       capture_output=True, text=True, check=True).stdout.strip()

def call(endpoint, params):
    params = {**params, "appId": appid}
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/"+endpoint+"?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"py"}), timeout=30) as r:
        return json.load(r)

d = call("getMetaInfo", {"statsDataId":"0003131978"})
meta = d.get("GET_META_INFO",{})
print("STATUS:", meta.get("RESULT",{}).get("STATUS"))
classes = meta.get("METADATA_INF",{}).get("CLASS_INF",{}).get("CLASS_OBJ",[])
if isinstance(classes, dict): classes=[classes]
for c in classes:
    cid=c.get("@id"); cname=c.get("@name")
    cats=c.get("CLASS",[])
    if isinstance(cats,dict): cats=[cats]
    print(f"\n=== {cid} : {cname}  (カテゴリ数 {len(cats)}) ===")
    for x in cats[:14]:
        print(f"   code={x.get('@code')} | {x.get('@name')}")
    if len(cats)>14: print("   ...")
