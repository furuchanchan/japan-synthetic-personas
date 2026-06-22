---
license: cc-by-4.0
language:
- ja
tags:
- synthetic
- personas
- japan
- consumer-behavior
- marketing
- survey-simulation
- agent-based
size_categories:
- 1K<n<10K
pretty_name: Japan Synthetic Consumer Personas 3000 (statistically grounded)
---

# 日本 合成消費者ペルソナ 3,000体 / Japan Synthetic Consumer Personas (N=3,000)

![Japan Synthetic Consumer Personas — N=3,000](images/overview.png)

日本の人口構成・世帯所得分布に**統計的に接地**した合成消費者ペルソナ 3,000体。
各人物に消費行動属性（価格感度・ブランド志向・購買チャネル・EC利用・メディア接触）と、
**一人称インタビュー形式の生活叙述（`backstory_250w`）** が付きます。

新商品のコンセプトテスト、合成調査（survey simulation）、エージェントベース・シミュレーション、
LLM回答評価のための被験者ペルソナなどに利用できます。

A set of 3,000 synthetic Japanese consumer personas, statistically grounded in national
demographics and household-income distributions, each enriched with consumer-behavior
attributes and a first-person life narrative. Built for concept testing, survey simulation,
agent-based simulation, and as evaluation personas for LLM outputs.

---

## 🚀 Quickstart

```python
from datasets import load_dataset

ds = load_dataset("furuchanchan/japan-synthetic-personas", split="train")
print(len(ds), "personas")          # 3000
print(ds[0]["backstory_250w"])      # 一人称の生活叙述
```

新商品コンセプトテストを **ペルソナにLLMで回す** 完全な例 → [`examples/synthetic_survey.py`](https://github.com/furuchanchan/japan-synthetic-personas/blob/main/examples/synthetic_survey.py)

## 💬 Community / コミュニティ

質問・フィードバック・活用事例は Discord でどうぞ → **https://discord.gg/JMVG53hGKS**

---

## 概要 / At a glance

| 項目 | 値 |
|---|---|
| 件数 | **3,000体** |
| 列数 | 36列 |
| 性別 | 女 52.2% / 男 47.8% |
| 平均年齢 | 53.6歳（70代以上 25.6% ＝ 日本の高齢化を反映） |
| 地域 | **47都道府県すべて**（人口比で配分・最少県でも10件） |
| 全国平均世帯年収 | **537万円**（年代カーブを再現） |
| 叙述の長さ | 平均278.8字（最短198・最長425） |
| 再現性 | seed固定（`scripts/` 参照） |

### 年代別の平均世帯年収（万円）
| 20代以下 | 30代 | 40代 | 50代 | 60代 | 70代 | 80歳以上 |
|---|---|---|---|---|---|---|
| 320 | 575 | 707 | 743 | 510 | 460 | 342 |

現役期にピーク（50代743万）→ 退職後に低下、という実分布の形を保持しています。

---

## ファイル / Files

| ファイル | 内容 |
|---|---|
| `japan_personas_3000.csv` | 本体（3,000体 × 36列） |
| `japan_personas_3000.jsonl` | 同内容（1行=1人物のJSON） |
| `distribution_3000.json` | 人口統計・年収分布のサマリ |

---

## 列定義（36列・出所別）/ Columns by source

データの透明性のため、各列が**どの素材に由来するか**を明示します（ライセンス節も参照）。

### A. 識別子
- `uuid`

### B. 人物像・属性（NVIDIA Nemotron-Personas-Japan 由来／国勢調査に接地）
- 叙述: `persona`, `professional_persona`, `sports_persona`, `arts_persona`, `travel_persona`, `culinary_persona`, `cultural_background`
- スキル・志向: `skills_and_expertise`(+`_list`), `hobbies_and_interests`(+`_list`), `career_goals_and_ambitions`
- デモグラフィック: `sex`, `age`, `age_band`, `marital_status`, `education_level`, `occupation`, `region`, `area`, `prefecture`, `country`

### C. 世帯所得の接地（e-Stat 公的統計 由来）
- `household_income_bracket`（世帯年収バンド）
- `household_income_midpoint_manyen`（バンド中央値・万円）
- `household_income_source`（接地方法の記録）
- `income_tier`（low <350万 / mid 350–699万 / high ≥700万）

### D. 消費行動レイヤー（本データセット独自・統計の方向性に整合）
- `disposable_income_feel`（可処分感: 切り詰め/普通/ゆとり）
- `price_sensitivity`（価格感度: 高/中/低）
- `brand_orientation`（PB志向 / PB-NB併用 / NB・品質志向）
- `promotion_responsiveness`（販促反応: 高/中/低）
- `bulk_buy_tendency`（まとめ買い: よくする/たまに/しない）
- `ec_adoption`（EC利用: 高/中/低）
- `primary_purchase_channels`（主要購買チャネル）
- `media_contact`（メディア接触）

### E. 一人称叙述（Anthropic Claude 生成）
- `backstory_250w`（その人物が自分の暮らしを語る約220–260字の一人称テキスト）

> `backstory_250w` のみ AI 生成テキストです（A〜D は統計・既存データ由来）。
> データセット全体を CC BY 4.0 で配布します。

---

## 作り方（再現可能・3層カスケード）/ Method

1. **L0 母集団** — NVIDIA Nemotron-Personas-Japan を `age_band × sex` で**人口構成比に比例した層化サンプリング**し3,000体を抽出（乱数固定）。
2. **所得の接地** — e-Stat「国民生活基礎調査」から `P(所得階級 | 世帯主年齢)` を作って世帯年収をサンプリング → 「全国家計構造調査」の県別所得指数で**年代×地域の同時条件付け**を行い、最近接バンドへスナップ。
3. **L1 消費レイヤー** — 接地済みの所得tier・年代・地域から、価格感度・ブランド志向・チャネル等を**所得条件付きの3類型**で付与。自由連続スコアは使わず、各tierに**両極の個体を必ず残す**ことで画一化を回避。
4. **叙述** — 各人物に一人称インタビュー形式の生活叙述を生成（下記「設計思想」）。

接地に使った公的統計:
- 国民生活基礎調査（厚生労働省, e-Stat statsDataId `0003131978`）
- 全国家計構造調査（総務省, e-Stat statsDataId `0003426512`）

再現コードは GitHub リポジトリにあります： https://github.com/furuchanchan/japan-synthetic-personas

---

## 設計思想：なぜステレオタイプを避けたか / Anti-stereotype design

叙述は「属性の箇条書き」ではなく **名前ベースの一人称インタビュー**形式で生成しています。
これは合成ペルソナの忠実度に関する近年の研究（一人称・名前ベースの叙述が
分布再現性を高め、属性羅列が陥りがちな“平均的すぎる”回答＝キャラクチュア化を抑えるという知見）に基づきます。
参考: Argyle et al. 2023 / Park et al. 2025 / "Anthology" (Moon et al., EMNLP 2024, arXiv:2407.06576)。

各叙述に課した制約:
- 属性を箇条書きにせず生活の語りに溶かす
- 所得バンド・価格感度・チャネル等と**矛盾させない**
- 実在ブランド・店舗・施設の固有名詞は出さない（「大手量販店」「動画配信サービス」等に一般化）
- 「低所得＝全方位節約」「高齢＝デジタル弱者」等のステレオタイプを避け、
  **必ず一つ、その人ならではの“例外的なこだわり／選択的支出”** を入れる

---

## 想定用途 / Intended use
- 新商品・コンセプトのリアクション収集（concept testing）
- アンケート/インタビューの事前シミュレーション（survey simulation）
- エージェントベース・マーケティング・シミュレーション
- LLM出力・対話の評価用ペルソナ

## 制約・注意 / Limitations
- **完全な合成データ**であり、実在の個人ではありません。
- 消費レイヤー（D）は公的統計の**方向性**に整合させた条件付き付与であり、特定商品カテゴリの実購買データで較正したものではありません（外的妥当性の検証は今後の課題）。
- 叙述（E）はAI生成であり、事実の正確性は保証しません。

---

## ライセンス・出典・免責 / License, Attribution & Disclaimer

### ライセンス / License
本データセットは **Creative Commons Attribution 4.0 International (CC BY 4.0)** の下で公開されています。
https://creativecommons.org/licenses/by/4.0/

本データセットは以下の3つの素材から構成され、いずれもCC BY互換または出力所有権の移転に基づき再配布しています。

### 出典 / Attribution

**1. ベースペルソナ / Base personas**
NVIDIA「Nemotron-Personas-Japan」(CC BY 4.0) から人口構成比でサンプリングし、3,000体に再構成しました（改変あり）。
https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan

> Fujita, Atsunori; Gong, Vincent; Ogushi, Masaya; Yamamoto, Kotaro; Suhara, Yoshi;
> Corneil, Dane; Meyer, Yev. *Nemotron-Personas-Japan*, September 2025.
> https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan

**2. 統計的接地 / Statistical grounding**
世帯年収等の統計値は、以下の政府統計をe-Stat API経由で取得・加工して付与しました。

> 「国民生活基礎調査」（厚生労働省）および「全国家計構造調査」（総務省）を加工して作成
> 出典：政府統計の総合窓口 (e-Stat) https://www.e-stat.go.jp/

e-Statの利用ルールは政府標準利用規約（第2.0版）に準拠し、CC BY 4.0と互換です。

**3. 一人称叙述 / First-person narratives (`backstory_250w`)**
`backstory_250w` 列は Anthropic Claude (claude-sonnet-4-6) により生成された合成テキストです。

### 免責 / Disclaimer
- 本データは**完全な合成データ**であり、実在の個人を表すものではありません。
- `backstory_250w` 列はAIによる生成テキストで、**事実の正確性は保証されません**。
- 本データの利用に起因するいかなる損害についても、作成者は責任を負いません。

### 作成 / Created by
株式会社TechWorker
