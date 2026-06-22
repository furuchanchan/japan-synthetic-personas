#!/usr/bin/env python3
# KeychainのappIdでe-Stat APIが通るかテスト。appIdは一切出力しない。
import subprocess, json, urllib.request, urllib.parse, sys

def get_appid():
    try:
        v = subprocess.run(["security","find-generic-password","-s","estat-app-id","-w"],
                           capture_output=True, text=True, check=True).stdout.strip()
        return v
    except subprocess.CalledProcessError:
        return ""

appid = get_appid()
print("Keychain(estat-app-id):", "あり" if appid else "なし(未保存)")
if not appid:
    print("→ 保存スクリプトを再実行してください。"); sys.exit(1)
print("appId長:", len(appid), "桁")  # 値は出さず長さだけ

def call(endpoint, params):
    params = {**params, "appId": appid}
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/"+endpoint+"?"+urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":"python"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# 認証テスト＋必要統計表の探索を兼ねる
for word in ["全国家計構造調査 年間収入", "国民生活基礎調査 所得", "国勢調査 男女 年齢 配偶"]:
    try:
        d = call("getStatsList", {"searchWord": word, "limit": 4})
        res = d.get("GET_STATS_LIST", {}).get("RESULT", {})
        status = res.get("STATUS")
        dl = d.get("GET_STATS_LIST", {}).get("DATALIST_INF", {})
        n = dl.get("NUMBER")
        print(f"\n[{word}] STATUS={status} ({res.get('ERROR_MSG','')}) 件数={n}")
        tables = dl.get("TABLE_INF", [])
        if isinstance(tables, dict): tables=[tables]
        for t in (tables or [])[:4]:
            sid = t.get("@id")
            title = t.get("TITLE")
            if isinstance(title, dict): title = title.get("$","")
            stat = t.get("STAT_NAME",{})
            statname = stat.get("$","") if isinstance(stat,dict) else stat
            print(f"   id={sid} | {statname} | {str(title)[:60]}")
    except Exception as e:
        print(f"\n[{word}] ERR {e}")
