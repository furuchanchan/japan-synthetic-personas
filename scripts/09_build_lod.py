#!/usr/bin/env python3
"""3,000体のペルソナを LOD（Turtle・JSON-LD）にして、docs/lod/ に出す。

- 各ペルソナに固定の URI（https://w3id.org/japan-synthetic-personas/id/persona/<uuid>）を付ける
- 都道府県は e-Stat 統計LOD の標準地域コード、業種は日本標準産業分類（統計LOD）、性別は schema.org の値につなぐ
- URI ごとに HTML・Turtle・JSON-LD を用意する

使い方:  python3 scripts/09_build_lod.py [dataset/japan_personas_3000.jsonl]
依存: 標準ライブラリだけ。入力が無ければ Hugging Face から取り寄せる。
"""
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://w3id.org/japan-synthetic-personas/"
NS = BASE + "ns#"
SITE = "https://furuchanchan.github.io/japan-synthetic-personas/lod/"
HF_JSONL = "https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas/resolve/main/japan_personas_3000.jsonl"
ESTAT_CODE = "http://data.e-stat.go.jp/lod/ontology/crossDomain/code/"
VERSION = "1.1.0"
RELEASED = "2026-09-30"

MAPPING = json.load(open(ROOT / "dataset" / "lod_mapping.json", encoding="utf-8"))
PREFECTURE = MAPPING["prefecture"]          # 都道府県名 → {sac: URI, code: "13", en: "Tokyo"}
INDUSTRY = MAPPING["industry"]              # 業種の名前 → {jsic: "85", label: "..."}（大分類は "I" のように英字）
JSIC_LABEL = MAPPING["jsic_label"]          # JSIC のコード → 名前（統計LODの表記）
SEX = {"男": "https://schema.org/Male", "女": "https://schema.org/Female"}
SEX_CODE = {"男": ESTAT_CODE + "sex-male", "女": ESTAT_CODE + "sex-female"}
MARITAL_CODE = {"未婚": "1", "未婚 (子供あり)": "1", "既婚": "2", "既婚 (子供あり)": "2", "死別": "31", "死別 (子供あり)": "31", "離別": "32", "離別 (子供あり)": "32"}
MARITAL_BASE = "http://data.e-stat.go.jp/lod/ontology/g00200521/code/2015/maritalStatus-"


def age_class_uri(age):
    """5歳の年齢階級（統計LOD の crossDomain のコード）。100歳以上は age-over100。"""
    if age >= 100:
        return ESTAT_CODE + "age-over100"
    lo = (age // 5) * 5
    return f"{ESTAT_CODE}age-{lo}-{lo + 4}"
SIZE = {"大手": "Large", "中堅": "Medium", "中小": "Small"}
STATUS = {"現在は引退": "Retired", "現在は離職": "NotEmployed"}
AGE_BAND = {"20代以下": "Under30", "30代": "Age30s", "40代": "Age40s", "50代": "Age50s", "60代": "Age60s", "70代": "Age70s", "80歳以上": "Age80Plus"}
LEVEL3 = {"低": "Low", "中": "Middle", "高": "High"}

def as_list(v):
    """list か、"['a', 'b']" のような文字列か、区切りの無い文字列を、文字列の list にする。"""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    text = str(v).strip()
    if text.startswith("["):
        import ast
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except (ValueError, SyntaxError):
            pass
    return [x.strip() for x in re.split(r"[、,;；]", text) if x.strip()]


OCCUPATION_RE = re.compile(r"^(.*?)(?:\s+(大手|中堅|中小))?(?:\s+(経営))?(?:\s*\((現在は引退|現在は離職)\))?$")


def esc(s):
    """Turtle の文字列の中に入れられる形にする。"""
    return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "")


def lit(s, lang=None, dt=None):
    if dt:
        return f'"{esc(s)}"^^{dt}'
    return f'"{esc(s)}"@{lang}' if lang else f'"{esc(s)}"'


def h(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def parse_occupation(o):
    m = OCCUPATION_RE.match(o.strip())
    industry, size, mgmt, status = m.group(1).strip(), m.group(2), m.group(3), m.group(4)
    return industry, size, bool(mgmt), status


def jsic_uri(code):
    return f"{ESTAT_CODE}industryClassification2013-{code}"


def load_rows(path):
    if not path.exists():
        print(f"{path} が無いので Hugging Face から取り寄せる")
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(HF_JSONL, path)
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def persona_triples(r):
    """1体ぶんのトリプル（Turtle の本文）と JSON-LD の辞書を返す。"""
    uri = f"<{BASE}id/persona/{r['uuid']}>"
    industry, size, mgmt, status = parse_occupation(r["occupation"])
    pref = PREFECTURE[r["prefecture"]]
    ind = INDUSTRY.get(industry)
    t = [f"{uri} a schema:Person, jsp:SyntheticPersona ;"]
    t.append(f"  schema:identifier {lit(r['uuid'])} ;")
    t.append(f"  schema:gender <{SEX[r['sex']]}> ;")
    t.append(f"  jsp:sexClass <{SEX_CODE[r['sex']]}> ;")
    t.append(f"  jsp:age {lit(r['age'], dt='xsd:integer')} ;")
    t.append(f"  jsp:ageClass <{age_class_uri(r['age'])}> ;")
    t.append(f"  jsp:ageBand jsp:{AGE_BAND[r['age_band']]} ;")
    t.append(f"  schema:homeLocation <{pref['sac']}> ;")
    t.append(f"  jsp:prefecture {lit(r['prefecture'], 'ja')} ;")
    t.append(f"  jsp:region {lit(r['region'], 'ja')} ;")
    t.append(f"  schema:nationality <{ESTAT_CODE}country-JP> ;" if MAPPING.get("country_uri") else f"  jsp:country {lit(r['country'], 'ja')} ;")
    t.append(f"  jsp:maritalStatus {lit(r['marital_status'], 'ja')} ;")
    t.append(f"  jsp:maritalStatusClass <{MARITAL_BASE}{MARITAL_CODE[r['marital_status']]}> ;")
    t.append(f"  jsp:educationLevel {lit(r['education_level'], 'ja')} ;")
    t.append(f"  jsp:occupationText {lit(r['occupation'], 'ja')} ;")
    if ind:
        t.append(f"  jsp:industryClass <{jsic_uri(ind['jsic'])}> ;")
        t.append(f"  jsp:industryText {lit(industry, 'ja')} ;")
    if size:
        t.append(f"  jsp:employerSize jsp:{SIZE[size]} ;")
    if mgmt:
        t.append("  jsp:isManagement true ;")
    if status:
        t.append(f"  jsp:employmentStatus jsp:{STATUS[status]} ;")
    if industry == "学生":
        t.append("  jsp:employmentStatus jsp:Student ;")
    t.append(f"  jsp:householdIncomeBracket {lit(r['household_income_bracket'], 'ja')} ;")
    t.append(f"  jsp:householdIncomeMidpointManyen {lit(int(r['household_income_midpoint_manyen']), dt='xsd:integer')} ;")
    t.append(f"  jsp:incomeTier jsp:{r['income_tier'].capitalize()}Income ;")
    t.append(f"  jsp:disposableIncomeFeel {lit(r['disposable_income_feel'], 'ja')} ;")
    t.append(f"  jsp:priceSensitivity jsp:{LEVEL3[r['price_sensitivity']]} ;")
    t.append(f"  jsp:brandOrientation {lit(r['brand_orientation'], 'ja')} ;")
    t.append(f"  jsp:promotionResponsiveness jsp:{LEVEL3[r['promotion_responsiveness']]} ;")
    t.append(f"  jsp:bulkBuyTendency {lit(r['bulk_buy_tendency'], 'ja')} ;")
    t.append(f"  jsp:ecAdoption jsp:{LEVEL3[r['ec_adoption']]} ;")
    t.append(f"  jsp:primaryPurchaseChannels {lit(r['primary_purchase_channels'], 'ja')} ;")
    t.append(f"  jsp:mediaContact {lit(r['media_contact'], 'ja')} ;")
    for key, prop in [("professional_persona", "professionalPersona"), ("sports_persona", "sportsPersona"), ("arts_persona", "artsPersona"), ("travel_persona", "travelPersona"), ("culinary_persona", "culinaryPersona"), ("persona", "personaSummary"), ("cultural_background", "culturalBackground"), ("career_goals_and_ambitions", "careerGoals")]:
        if r.get(key):
            t.append(f"  jsp:{prop} {lit(r[key], 'ja')} ;")
    for item in as_list(r.get("skills_and_expertise_list")):
        t.append(f"  jsp:skill {lit(item, 'ja')} ;")
    for item in as_list(r.get("hobbies_and_interests_list")):
        t.append(f"  jsp:hobby {lit(item, 'ja')} ;")
    t.append(f"  schema:description {lit(r['backstory_250w'], 'ja')} ;")
    t.append(f"  schema:isPartOf <{BASE}dataset> .")
    return "\n".join(t)


def persona_jsonld(r):
    industry, size, mgmt, status = parse_occupation(r["occupation"])
    pref = PREFECTURE[r["prefecture"]]
    ind = INDUSTRY.get(industry)
    d = {
        "id": f"{BASE}id/persona/{r['uuid']}",
        "type": ["schema:Person", "SyntheticPersona"],
        "identifier": r["uuid"],
        "gender": SEX[r["sex"]],
        "sexClass": SEX_CODE[r["sex"]],
        "age": r["age"],
        "ageClass": age_class_uri(r["age"]),
        "ageBand": f"{NS}{AGE_BAND[r['age_band']]}",
        "homeLocation": pref["sac"],
        "prefecture": {"ja": r["prefecture"]},
        "region": {"ja": r["region"]},
        "country": {"ja": r["country"]},
        "maritalStatus": {"ja": r["marital_status"]},
        "maritalStatusClass": MARITAL_BASE + MARITAL_CODE[r["marital_status"]],
        "educationLevel": {"ja": r["education_level"]},
        "occupationText": {"ja": r["occupation"]},
        "householdIncomeBracket": {"ja": r["household_income_bracket"]},
        "householdIncomeMidpointManyen": int(r["household_income_midpoint_manyen"]),
        "incomeTier": f"{NS}{r['income_tier'].capitalize()}Income",
        "disposableIncomeFeel": {"ja": r["disposable_income_feel"]},
        "priceSensitivity": f"{NS}{LEVEL3[r['price_sensitivity']]}",
        "brandOrientation": {"ja": r["brand_orientation"]},
        "promotionResponsiveness": f"{NS}{LEVEL3[r['promotion_responsiveness']]}",
        "bulkBuyTendency": {"ja": r["bulk_buy_tendency"]},
        "ecAdoption": f"{NS}{LEVEL3[r['ec_adoption']]}",
        "primaryPurchaseChannels": {"ja": r["primary_purchase_channels"]},
        "mediaContact": {"ja": r["media_contact"]},
        "description": {"ja": r["backstory_250w"]},
        "isPartOf": f"{BASE}dataset",
    }
    if ind:
        d["industryClass"] = jsic_uri(ind["jsic"])
        d["industryText"] = {"ja": industry}
    if size:
        d["employerSize"] = f"{NS}{SIZE[size]}"
    if mgmt:
        d["isManagement"] = True
    statuses = []
    if status:
        statuses.append(f"{NS}{STATUS[status]}")
    if industry == "学生":
        statuses.append(f"{NS}Student")
    if statuses:
        d["employmentStatus"] = statuses
    for key, prop in [("professional_persona", "professionalPersona"), ("sports_persona", "sportsPersona"), ("arts_persona", "artsPersona"), ("travel_persona", "travelPersona"), ("culinary_persona", "culinaryPersona"), ("persona", "personaSummary"), ("cultural_background", "culturalBackground"), ("career_goals_and_ambitions", "careerGoals")]:
        if r.get(key):
            d[prop] = {"ja": r[key]}
    skills = as_list(r.get("skills_and_expertise_list"))
    if skills:
        d["skill"] = [{"@value": s, "@language": "ja"} for s in skills]
    hobbies = as_list(r.get("hobbies_and_interests_list"))
    if hobbies:
        d["hobby"] = [{"@value": s, "@language": "ja"} for s in hobbies]
    return d


CONTEXT = {
    "@version": 1.1,
    "jsp": NS,
    "schema": "https://schema.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dcterms": "http://purl.org/dc/terms/",
    "void": "http://rdfs.org/ns/void#",
    "id": "@id", "type": "@type",
    "SyntheticPersona": "jsp:SyntheticPersona",
    "identifier": "schema:identifier",
    "gender": {"@id": "schema:gender", "@type": "@id"},
    "sexClass": {"@id": "jsp:sexClass", "@type": "@id"},
    "ageClass": {"@id": "jsp:ageClass", "@type": "@id"},
    "maritalStatusClass": {"@id": "jsp:maritalStatusClass", "@type": "@id"},
    "age": {"@id": "jsp:age", "@type": "xsd:integer"},
    "ageBand": {"@id": "jsp:ageBand", "@type": "@id"},
    "homeLocation": {"@id": "schema:homeLocation", "@type": "@id"},
    "prefecture": {"@id": "jsp:prefecture", "@container": "@language"},
    "region": {"@id": "jsp:region", "@container": "@language"},
    "country": {"@id": "jsp:country", "@container": "@language"},
    "maritalStatus": {"@id": "jsp:maritalStatus", "@container": "@language"},
    "educationLevel": {"@id": "jsp:educationLevel", "@container": "@language"},
    "occupationText": {"@id": "jsp:occupationText", "@container": "@language"},
    "industryClass": {"@id": "jsp:industryClass", "@type": "@id"},
    "industryText": {"@id": "jsp:industryText", "@container": "@language"},
    "employerSize": {"@id": "jsp:employerSize", "@type": "@id"},
    "isManagement": {"@id": "jsp:isManagement", "@type": "xsd:boolean"},
    "employmentStatus": {"@id": "jsp:employmentStatus", "@type": "@id", "@container": "@set"},
    "householdIncomeBracket": {"@id": "jsp:householdIncomeBracket", "@container": "@language"},
    "householdIncomeMidpointManyen": {"@id": "jsp:householdIncomeMidpointManyen", "@type": "xsd:integer"},
    "incomeTier": {"@id": "jsp:incomeTier", "@type": "@id"},
    "disposableIncomeFeel": {"@id": "jsp:disposableIncomeFeel", "@container": "@language"},
    "priceSensitivity": {"@id": "jsp:priceSensitivity", "@type": "@id"},
    "brandOrientation": {"@id": "jsp:brandOrientation", "@container": "@language"},
    "promotionResponsiveness": {"@id": "jsp:promotionResponsiveness", "@type": "@id"},
    "bulkBuyTendency": {"@id": "jsp:bulkBuyTendency", "@container": "@language"},
    "ecAdoption": {"@id": "jsp:ecAdoption", "@type": "@id"},
    "primaryPurchaseChannels": {"@id": "jsp:primaryPurchaseChannels", "@container": "@language"},
    "mediaContact": {"@id": "jsp:mediaContact", "@container": "@language"},
    "professionalPersona": {"@id": "jsp:professionalPersona", "@container": "@language"},
    "sportsPersona": {"@id": "jsp:sportsPersona", "@container": "@language"},
    "artsPersona": {"@id": "jsp:artsPersona", "@container": "@language"},
    "travelPersona": {"@id": "jsp:travelPersona", "@container": "@language"},
    "culinaryPersona": {"@id": "jsp:culinaryPersona", "@container": "@language"},
    "personaSummary": {"@id": "jsp:personaSummary", "@container": "@language"},
    "culturalBackground": {"@id": "jsp:culturalBackground", "@container": "@language"},
    "careerGoals": {"@id": "jsp:careerGoals", "@container": "@language"},
    "skill": {"@id": "jsp:skill", "@container": "@set"},
    "hobby": {"@id": "jsp:hobby", "@container": "@set"},
    "description": {"@id": "schema:description", "@container": "@language"},
    "isPartOf": {"@id": "schema:isPartOf", "@type": "@id"},
}

PREFIXES = f"""@prefix jsp: <{NS}> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix void: <http://rdfs.org/ns/void#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
"""


def vocab_turtle():
    """語彙の定義（クラス・性質・決まった値）。"""
    props_obj = [
        ("ageBand", "年齢の区分", "age band", "jsp:AgeBand"),
        ("industryClass", "産業分類", "industry class", None),
        ("sexClass", "性別のコード", "sex code", None),
        ("ageClass", "年齢階級のコード", "age class code", None),
        ("maritalStatusClass", "配偶関係のコード", "marital status code", None),
        ("employerSize", "勤め先の規模", "employer size", "jsp:EmployerSize"),
        ("employmentStatus", "就業の状態", "employment status", "jsp:EmploymentStatus"),
        ("incomeTier", "所得の層", "income tier", "jsp:IncomeTier"),
        ("priceSensitivity", "価格への敏感さ", "price sensitivity", "jsp:Level"),
        ("promotionResponsiveness", "販促への反応", "promotion responsiveness", "jsp:Level"),
        ("ecAdoption", "ネット通販の利用", "e-commerce adoption", "jsp:Level"),
    ]
    props_data = [
        ("age", "年齢", "age", "xsd:integer"),
        ("prefecture", "都道府県", "prefecture", "rdf:langString"),
        ("region", "地方", "region", "rdf:langString"),
        ("country", "国", "country", "rdf:langString"),
        ("maritalStatus", "配偶関係", "marital status", "rdf:langString"),
        ("educationLevel", "学歴", "education level", "rdf:langString"),
        ("occupationText", "職業の欄（元の表記）", "occupation as written", "rdf:langString"),
        ("industryText", "業種", "industry", "rdf:langString"),
        ("isManagement", "経営の立場", "is in management", "xsd:boolean"),
        ("householdIncomeBracket", "世帯所得の階級", "household income bracket", "rdf:langString"),
        ("householdIncomeMidpointManyen", "世帯所得の階級の中央値（万円）", "household income midpoint (10,000 JPY)", "xsd:integer"),
        ("disposableIncomeFeel", "家計のゆとり", "disposable income feel", "rdf:langString"),
        ("brandOrientation", "ブランド志向", "brand orientation", "rdf:langString"),
        ("bulkBuyTendency", "まとめ買いの傾向", "bulk buy tendency", "rdf:langString"),
        ("primaryPurchaseChannels", "主な購買の経路", "primary purchase channels", "rdf:langString"),
        ("mediaContact", "メディアとの接点", "media contact", "rdf:langString"),
        ("professionalPersona", "仕事の面", "professional persona", "rdf:langString"),
        ("sportsPersona", "運動の面", "sports persona", "rdf:langString"),
        ("artsPersona", "芸術の面", "arts persona", "rdf:langString"),
        ("travelPersona", "旅の面", "travel persona", "rdf:langString"),
        ("culinaryPersona", "食の面", "culinary persona", "rdf:langString"),
        ("personaSummary", "人物の要約", "persona summary", "rdf:langString"),
        ("culturalBackground", "文化的な背景", "cultural background", "rdf:langString"),
        ("careerGoals", "仕事の目標", "career goals", "rdf:langString"),
        ("skill", "技能", "skill", "rdf:langString"),
        ("hobby", "趣味", "hobby", "rdf:langString"),
    ]
    out = [PREFIXES, "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .", "@prefix vann: <http://purl.org/vocab/vann/> .", ""]
    out.append(f"""<{BASE}ns> a owl:Ontology ;
  dcterms:title {lit('日本 合成消費者ペルソナの語彙', 'ja')} , {lit('Japan Synthetic Consumer Personas vocabulary', 'en')} ;
  dcterms:description {lit('統計に接地した合成消費者ペルソナを表す語彙。人物は schema:Person とし、都道府県は e-Stat 統計LOD の標準地域コード、業種は日本標準産業分類（統計LOD）につなぐ。', 'ja')} ;
  dcterms:creator {lit('古野光太朗', 'ja')} , {lit('Kotaro Furuno', 'en')} ;
  dcterms:publisher {lit('株式会社TechWorker', 'ja')} ;
  dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
  owl:versionInfo {lit(VERSION)} ;
  vann:preferredNamespacePrefix {lit('jsp')} ;
  vann:preferredNamespaceUri {lit(NS)} .

jsp:SyntheticPersona a owl:Class ; rdfs:subClassOf schema:Person ;
  rdfs:label {lit('合成ペルソナ', 'ja')} , {lit('Synthetic persona', 'en')} ;
  rdfs:comment {lit('実在しない、統計に接地して生成した人物。schema:Person の下位。', 'ja')} , {lit('A fictional person generated to match population statistics.', 'en')} .
""")
    for name, ja, en, rng in props_obj:
        out.append(f"jsp:{name} a owl:ObjectProperty ; rdfs:label {lit(ja, 'ja')} , {lit(en, 'en')} ; rdfs:domain jsp:SyntheticPersona {('; rdfs:range ' + rng) if rng else ''} .")
    out.append(f"jsp:sexClass rdfs:comment {lit('e-Stat 統計LOD の性別のコード（crossDomain）。', 'ja')} ; rdfs:subPropertyOf rdfs:seeAlso .")
    out.append(f"jsp:ageClass rdfs:comment {lit('e-Stat 統計LOD の5歳の年齢階級のコード（crossDomain）。100歳以上は age-over100。', 'ja')} ; rdfs:subPropertyOf rdfs:seeAlso .")
    out.append(f"jsp:maritalStatusClass rdfs:comment {lit('e-Stat 統計LOD の国勢調査（2015年）の配偶関係のコード。「子供あり」の区別はコードには無いので、jsp:maritalStatus の文字列に残す。', 'ja')} ; rdfs:subPropertyOf rdfs:seeAlso .")
    out.append(f"jsp:industryClass rdfs:comment {lit('勤め先の業種に当たる、日本標準産業分類（平成25年10月改定）の項目。e-Stat 統計LOD のURI。中分類が決められないときは大分類。', 'ja')} ; rdfs:subPropertyOf rdfs:seeAlso .")
    for name, ja, en, rng in props_data:
        out.append(f"jsp:{name} a owl:DatatypeProperty ; rdfs:label {lit(ja, 'ja')} , {lit(en, 'en')} ; rdfs:domain jsp:SyntheticPersona ; rdfs:range {rng} .")
    concepts = [
        ("AgeBand", [("Under30", "20代以下", "under 30"), ("Age30s", "30代", "30s"), ("Age40s", "40代", "40s"), ("Age50s", "50代", "50s"), ("Age60s", "60代", "60s"), ("Age70s", "70代", "70s"), ("Age80Plus", "80歳以上", "80 and over")]),
        ("EmployerSize", [("Large", "大手", "large"), ("Medium", "中堅", "medium"), ("Small", "中小", "small")]),
        ("EmploymentStatus", [("Retired", "引退", "retired"), ("NotEmployed", "離職", "not employed"), ("Student", "学生", "student")]),
        ("IncomeTier", [("LowIncome", "低", "low"), ("MidIncome", "中", "middle"), ("HighIncome", "高", "high")]),
        ("Level", [("Low", "低", "low"), ("Middle", "中", "middle"), ("High", "高", "high")]),
    ]
    for cls, items in concepts:
        out.append(f"jsp:{cls} a owl:Class ; rdfs:subClassOf skos:Concept ; rdfs:label {lit(cls, 'en')} .")
        for name, ja, en in items:
            out.append(f"jsp:{name} a jsp:{cls} ; skos:prefLabel {lit(ja, 'ja')} , {lit(en, 'en')} .")
    return "\n".join(out) + "\n"


def dataset_turtle(rows):
    return f"""<{BASE}dataset> a void:Dataset, dcat:Dataset ;
  dcterms:title {lit('日本 合成消費者ペルソナ 3,000体（LOD版）', 'ja')} , {lit('Japan Synthetic Consumer Personas (N=3,000), Linked Data edition', 'en')} ;
  dcterms:description {lit('日本の人口構成と世帯所得の分布に統計的に接地した、合成消費者ペルソナ3,000体。各人物に属性と一人称の生活叙述が付く。都道府県は e-Stat 統計LOD の標準地域コード、業種は日本標準産業分類のURIにつないでいる。', 'ja')} ;
  dcterms:creator {lit('古野光太朗', 'ja')} , {lit('Kotaro Furuno', 'en')} ;
  dcterms:publisher {lit('株式会社TechWorker', 'ja')} , {lit('TechWorker Inc.', 'en')} ;
  dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
  dcterms:hasVersion {lit(VERSION)} ;
  dcterms:issued {lit(RELEASED, dt='xsd:date')} ;
  dcterms:source <https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan> , <https://data.e-stat.go.jp/lodw/> , <https://www.e-stat.go.jp/> ;
  dcterms:rights {lit('土台は NVIDIA Nemotron-Personas-Japan（CC BY 4.0）を改変したもの。統計の接地は、国民生活基礎調査（厚生労働省）と全国家計構造調査（総務省）を e-Stat で加工して作成。都道府県と産業分類は、政府統計の総合窓口(e-Stat)の統計LODのURIを参照。', 'ja')} ;
  void:vocabulary <{NS}> , <https://schema.org/> ;
  void:entities {lit(len(rows), dt='xsd:integer')} ;
  dcat:landingPage <{SITE}> ;
  dcat:distribution <{SITE}personas.ttl> , <{SITE}personas.jsonld> ;
  rdfs:seeAlso <https://github.com/furuchanchan/japan-synthetic-personas> , <https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas> .
"""


CSS = """:root{--fg:#111;--sub:#555;--bg:#fff;--line:#ddd;--soft:#f5f5f5}@media(prefers-color-scheme:dark){:root{--fg:#eee;--sub:#aaa;--bg:#111;--line:#333;--soft:#1c1c1c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif;line-height:1.8;font-size:16px}
a{color:inherit;text-underline-offset:3px}header,main,footer{max-width:820px;margin:0 auto;padding:0 20px}header{padding-top:20px;font-size:14px;color:var(--sub)}header a{text-decoration:none;margin-right:12px}header .name{color:var(--fg);font-weight:700}
h1{font-size:28px;line-height:1.4;margin:28px 0 0}.en{color:var(--sub);font-size:15px;margin:2px 0 0}h2{font-size:19px;margin:40px 0 8px}p{margin:8px 0}ul{margin:8px 0;padding-left:1.4em}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:8px}th,td{text-align:left;vertical-align:top;padding:8px 10px 8px 0;border-bottom:1px solid var(--line)}th{color:var(--sub);font-weight:400;white-space:nowrap;width:11em}
.tag{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:0 10px;font-size:13px;color:var(--sub)}.data{margin-top:48px;padding:16px 18px;background:var(--soft);border-radius:10px;font-size:14px;overflow-wrap:anywhere}code{font-family:ui-monospace,Menlo,monospace;font-size:.92em}
footer{margin-top:64px;padding-top:20px;padding-bottom:48px;border-top:1px solid var(--line);font-size:13px;color:var(--sub)}@media(max-width:600px){h1{font-size:23px}body{font-size:15px}}"""


def page(title, en, body, uri, root, alt=None, jsonld=None):
    alt_links = "".join(f'<link rel="alternate" type="{t}" href="{h(u)}">' for t, u in (alt or []))
    embedded = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(title)}｜日本 合成消費者ペルソナ</title>{alt_links}<style>{CSS}</style>{embedded}</head>
<body><header><a class="name" href="{root}">日本 合成消費者ペルソナ（LOD版）</a><a href="{root}ns/">語彙</a><a href="https://github.com/furuchanchan/japan-synthetic-personas">GitHub</a><a href="https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas">Hugging Face</a></header>
<main><h1>{h(title)}</h1>{f'<p class="en" lang="en">{h(en)}</p>' if en else ''}{body}
<section class="data"><p>URI　<code>{h(uri)}</code></p>{''.join(f'<p>データ　' + '　'.join(f'<a href="{h(u)}">{h(l)}</a>' for l, u in links) + '</p>' for links in [[(t.split('/')[-1].replace('turtle','Turtle').replace('ld+json','JSON-LD'), u) for t, u in (alt or [])]] if links)}</section></main>
<footer><p>データは <a href="https://creativecommons.org/licenses/by/4.0/deed.ja">CC BY 4.0</a>。土台は NVIDIA Nemotron-Personas-Japan（CC BY 4.0）を改変。統計の接地は国民生活基礎調査（厚生労働省）と全国家計構造調査（総務省）を e-Stat で加工。都道府県と産業分類は、政府統計の総合窓口(e-Stat)の統計LODのURIを参照。作った人：古野光太朗（株式会社TechWorker）。</p></footer></body></html>
"""


def persona_page(r, jl):
    industry, size, mgmt, status = parse_occupation(r["occupation"])
    pref = PREFECTURE[r["prefecture"]]
    ind = INDUSTRY.get(industry)
    rows_html = [
        ("性別", f'<a href="{SEX_CODE[r["sex"]]}">{h(r["sex"])}</a>　<span class="tag">統計LOD</span>'),
        ("年齢", f'{r["age"]}歳（{h(r["age_band"])}）　<a href="{age_class_uri(r["age"])}">5歳の階級</a>　<span class="tag">統計LOD</span>'),
        ("住まい", f'<a href="{h(pref["sac"])}">{h(r["prefecture"])}</a>（{h(r["region"])}）　<span class="tag">統計LOD 標準地域コード {h(pref["code"])}</span>'),
        ("配偶関係", f'{h(r["marital_status"])}　<a href="{MARITAL_BASE}{MARITAL_CODE[r["marital_status"]]}">国勢調査の区分</a>　<span class="tag">統計LOD</span>'),
        ("学歴", h(r["education_level"])),
        ("職業の欄", h(r["occupation"])),
    ]
    if ind:
        rows_html.append(("業種の分類", f'<a href="{jsic_uri(ind["jsic"])}">{h(ind["jsic"])} {h(JSIC_LABEL.get(ind["jsic"], ""))}</a>　<span class="tag">日本標準産業分類 2013</span>'))
    rows_html += [
        ("世帯所得", f'{h(r["household_income_bracket"])}（中央値 {int(r["household_income_midpoint_manyen"])}万円、{h(r["income_tier"])}）'),
        ("家計のゆとり", h(r["disposable_income_feel"])),
        ("価格への敏感さ", h(r["price_sensitivity"])),
        ("ブランド志向", h(r["brand_orientation"])),
        ("販促への反応", h(r["promotion_responsiveness"])),
        ("まとめ買い", h(r["bulk_buy_tendency"])),
        ("ネット通販", h(r["ec_adoption"])),
        ("主な購買の経路", h(r["primary_purchase_channels"])),
        ("メディア", h(r["media_contact"])),
    ]
    table = "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows_html) + "</table>"
    facets = "".join(f"<h2>{h(ja)}</h2><p>{h(r[key])}</p>" for key, ja in [("professional_persona", "仕事"), ("sports_persona", "運動"), ("arts_persona", "芸術"), ("travel_persona", "旅"), ("culinary_persona", "食"), ("cultural_background", "文化的な背景"), ("career_goals_and_ambitions", "仕事の目標")] if r.get(key))
    lists = ""
    if as_list(r.get("skills_and_expertise_list")):
        lists += "<h2>技能</h2><ul>" + "".join(f"<li>{h(s)}</li>" for s in as_list(r["skills_and_expertise_list"])) + "</ul>"
    if as_list(r.get("hobbies_and_interests_list")):
        lists += "<h2>趣味</h2><ul>" + "".join(f"<li>{h(s)}</li>" for s in as_list(r["hobbies_and_interests_list"])) + "</ul>"
    body = f'<p><span class="tag">合成ペルソナ</span>　実在しない、統計に接地して生成した人物です。</p><h2>属性</h2>{table}<h2>生活の叙述（一人称）</h2><p>{h(r["backstory_250w"])}</p>{facets}{lists}'
    uri = f"{BASE}id/persona/{r['uuid']}"
    alt = [("text/turtle", f"../{r['uuid']}.ttl"), ("application/ld+json", f"../{r['uuid']}.jsonld")]
    return page(r["uuid"][:8] + "…", None, body, uri, "../../../", alt, {"@context": CONTEXT, **jl})


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dataset" / "japan_personas_3000.jsonl"
    rows = load_rows(src)
    out = ROOT / "docs" / "lod"
    (out / "id" / "persona").mkdir(parents=True, exist_ok=True)
    (out / "ns").mkdir(parents=True, exist_ok=True)

    missing = Counter()
    for r in rows:
        industry = parse_occupation(r["occupation"])[0]
        if industry not in INDUSTRY and industry != "学生":
            missing[industry] += 1
        if r["prefecture"] not in PREFECTURE:
            raise SystemExit(f"都道府県の対応が無い: {r['prefecture']}")
    if missing:
        raise SystemExit("業種の対応が無い: " + ", ".join(f"{k}({v})" for k, v in missing.most_common()))

    vocab = vocab_turtle()
    (out / "vocab.ttl").write_text(vocab, encoding="utf-8")
    (out / "context.jsonld").write_text(json.dumps({"@context": CONTEXT}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    all_ttl = [PREFIXES, dataset_turtle(rows)]
    all_jl = []
    for r in rows:
        ttl = persona_triples(r)
        jl = persona_jsonld(r)
        all_ttl.append(ttl)
        all_jl.append(jl)
        d = out / "id" / "persona"
        (d / f"{r['uuid']}.ttl").write_text(PREFIXES + "\n" + ttl + "\n", encoding="utf-8")
        (d / f"{r['uuid']}.jsonld").write_text(json.dumps({"@context": CONTEXT, **jl}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        (d / r["uuid"]).mkdir(exist_ok=True)
        (d / r["uuid"] / "index.html").write_text(persona_page(r, jl), encoding="utf-8")
    (out / "personas.ttl").write_text("\n\n".join(all_ttl) + "\n", encoding="utf-8")
    (out / "personas.jsonld").write_text(json.dumps({"@context": CONTEXT, "@graph": all_jl}, ensure_ascii=False) + "\n", encoding="utf-8")

    # 語彙のページと入口
    (out / "ns" / "index.html").write_text(page("語彙", "Vocabulary", f"<p>名前空間は <code>{h(NS)}</code>。人物は schema:Person の下位の jsp:SyntheticPersona。性別は schema:gender（schema:Female / schema:Male）、住まいは schema:homeLocation で e-Stat 統計LOD の標準地域コード、業種は jsp:industryClass で日本標準産業分類（統計LOD）につなぐ。</p><p><a href=\"../vocab.ttl\">Turtle</a>　<a href=\"../context.jsonld\">JSON-LD の文脈</a></p>", BASE + "ns", "../"), encoding="utf-8")
    by_pref = Counter(r["prefecture"] for r in rows)
    by_ind = Counter(INDUSTRY[parse_occupation(r["occupation"])[0]]["jsic"] for r in rows if parse_occupation(r["occupation"])[0] in INDUSTRY)
    index_body = f"""<p>日本の人口構成と世帯所得の分布に統計的に接地した、合成消費者ペルソナ3,000体を、LOD（Linked Open Data）の形で公開しています。1体ごとに固定のURIがあり、都道府県は e-Stat 統計LOD の標準地域コード、業種は日本標準産業分類（統計LOD）のURIにつながっています。元のデータ（CSV・JSONL）は <a href="https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas">Hugging Face</a>、作り方は <a href="https://github.com/furuchanchan/japan-synthetic-personas">GitHub</a> にあります。</p>
<h2>まとめてダウンロード</h2><ul><li><a href="personas.ttl">Turtle</a>（3,000体）　<a href="personas.jsonld">JSON-LD</a></li><li>語彙　<a href="vocab.ttl">Turtle</a>　<a href="context.jsonld">JSON-LD の文脈</a>　<a href="ns/">説明</a></li></ul>
<h2>つなげている外のデータ</h2><ul><li>住まい → e-Stat 統計LOD 標準地域コード（47都道府県）</li><li>業種 → 日本標準産業分類（平成25年10月改定）の中分類・大分類（{len(by_ind)}種）</li><li>性別 → e-Stat 統計LOD の性別のコードと、schema.org（schema:Female / schema:Male）</li><li>年齢 → e-Stat 統計LOD の5歳の年齢階級</li><li>配偶関係 → e-Stat 統計LOD の国勢調査（2015年）の配偶関係</li></ul>
<h2>数</h2><table><tr><th>ペルソナ</th><td>{len(rows)}</td></tr><tr><th>都道府県</th><td>{len(by_pref)}</td></tr><tr><th>業種の分類</th><td>{len(by_ind)}</td></tr><tr><th>URI ごとのページ</th><td>{len(rows)}</td></tr></table>
<h2>例</h2><ul>{''.join(f'<li><a href="id/persona/{r["uuid"]}/">{h(r["prefecture"])}・{h(r["sex"])}・{r["age"]}歳・{h(r["occupation"])}</a></li>' for r in rows[:12])}</ul>
<h2>使うときの表示</h2><p>日本 合成消費者ペルソナ 3,000体、古野光太朗（株式会社TechWorker）、CC BY 4.0。土台は NVIDIA Nemotron-Personas-Japan（CC BY 4.0）を改変。</p>"""
    (out / "index.html").write_text(page("日本 合成消費者ペルソナ 3,000体（LOD版）", "Japan Synthetic Consumer Personas, Linked Data edition", index_body, BASE + "dataset", "./", [("text/turtle", "personas.ttl"), ("application/ld+json", "personas.jsonld")]), encoding="utf-8")
    print(f"ペルソナ {len(rows)}、都道府県 {len(by_pref)}、業種の分類 {len(by_ind)} → {out}")


if __name__ == "__main__":
    main()
