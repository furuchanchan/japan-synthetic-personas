---
license: cc-by-4.0
language:
- en
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

# Japan Synthetic Consumer Personas (N=3,000) / 日本 合成消費者ペルソナ 3,000体

![Japan Synthetic Consumer Personas — N=3,000](images/overview.png)

**3,000 synthetic Japanese consumer personas, statistically grounded** in national demographics and household-income distributions. Each persona carries consumer-behavior attributes (price sensitivity, brand orientation, purchase channels, EC adoption, media contact) and a **first-person life narrative** (`backstory_250w`). Built for concept testing, survey simulation, agent-based simulation, and as evaluation personas for LLM outputs.

日本の人口構成・世帯所得分布に**統計的に接地**した合成消費者ペルソナ 3,000体。各人物に消費行動属性と一人称の生活叙述（`backstory_250w`）が付きます。新商品のコンセプトテスト・合成調査・エージェントシミュレーション・LLM評価ペルソナ向け。

> **New — real answers, not just synthetic.** Ask **real Japanese respondents** from **$0.30/answer**; see **Ask real Japanese people** below. 合成に加えて**実在の日本人**にも聞けます（1回答$0.30〜／下記参照）。

## 🌐 Language / 言語

- **Column names are in English; column values are in Japanese** — this is a dataset of Japanese consumers, so values are intentionally kept native (e.g. `prefecture = 長崎県`, `sex = 女`).
- `backstory_250w` is a Japanese first-person narrative.
- **Non-Japanese speakers:** the [**Value reference (Japanese → English)**](#value-reference-japanese--english) table below decodes every categorical field, so you can use the dataset without reading Japanese.

## 🚀 Quickstart

```python
from datasets import load_dataset

ds = load_dataset("furuchanchan/japan-synthetic-personas", split="train")
print(len(ds), "personas")          # 3000
print(ds[0]["backstory_250w"])      # first-person narrative (Japanese)
```

Run a full LLM-driven concept test over the personas → [`examples/synthetic_survey.py`](https://github.com/furuchanchan/japan-synthetic-personas/blob/main/examples/synthetic_survey.py)

## 💬 Community

Questions, feedback, and use cases on Discord → **https://discord.gg/JMVG53hGKS**
質問・フィードバック・活用事例は Discord でどうぞ → **https://discord.gg/JMVG53hGKS**

## Ask real Japanese people (paid layer) / 実在の日本人に聞く（有料レイヤー）

These 3,000 personas are **synthetic** — a statistically grounded *model* of Japanese consumers: free and fast for wide exploration, but not the people themselves. So the project adds a second layer: **put the same question to real Japanese respondents.**

- **When synthetic isn't enough** — pre-test on the synthetic panel for free, then ask real respondents when a decision rides on it. No full research project to stand up.
- **Every real answer sharpens the synthetic** — real responses are ground truth we use to calibrate where the personas drift, so this free dataset keeps improving.

**How it works** — (1) target by age, gender, region, occupation & industry, education / student status, household income; (2) write your questions; (3) we run them with real Japanese respondents and return individual answers plus segment aggregates.
**Pricing** — **$0.30 per answer** (questions × respondents), **from 3,000 answers** (e.g. 10 questions × 300 people = **$900**).
**Contact** — tell us your question, target, and rough sample size; we'll confirm feasibility and reply with a secure payment link. Email **info@techworker.co.jp** · X **[@koutarou_en](https://x.com/koutarou_en)** (EN) / **[@koutarou_furuno](https://x.com/koutarou_furuno)** (JP) · or start a discussion in the Community tab.

**日本語** — これら3,000体は**合成データ**＝統計接地した消費者の“モデル”で本人ではありません。無料で速く広く試せますが、合成だけでは足りない場面があります。そこで**同じ質問を実在の日本人に投げられる**層を用意しました。①年齢・性別・居住地・職業/業種・学歴/学生区分・世帯年収でターゲティング → ②質問を書く → ③実在の日本人に実施し個票＋セグメント別集計を返却。**料金＝1回答$0.30（質問数×人数）・3,000回答から（例：10問×300人＝$900）。** 実在の回答は合成データの較正にも使い、無料データセットの精度を上げ続けます。お問い合わせは質問内容・ターゲット・サンプル数を添えて メール **info@techworker.co.jp** ／ X **[@koutarou_en](https://x.com/koutarou_en)**（英語）・**[@koutarou_furuno](https://x.com/koutarou_furuno)**（日本語）／ Community タブから。実現可否を確認のうえお支払いリンクを返信します。

---

# English

## At a glance

| Property | Value |
|---|---|
| Records | **3,000** |
| Columns | 36 |
| Sex | Female 52.2% / Male 47.8% |
| Mean age | 53.6 (25.6% are 70+, mirroring Japan's aging society) |
| Geography | **all 47 prefectures** (population-weighted; min 10 each) |
| Mean household income | **¥5.37M** (reproduces the age curve) |
| Narrative length | avg 278.8 chars (min 198 / max 425) |
| Reproducibility | fixed seeds (see `scripts/`) |

### Mean household income by age band (万円 / ¥10k)
| ≤29 | 30s | 40s | 50s | 60s | 70s | 80+ |
|---|---|---|---|---|---|---|
| 320 | 575 | 707 | 743 | 510 | 460 | 342 |

Peaks in working years (50s, ¥7.43M) and declines after retirement — preserving the shape of the real distribution.

## Files

| File | Content |
|---|---|
| `japan_personas_3000.csv` | main table (3,000 × 36) |
| `japan_personas_3000.jsonl` | same content (1 JSON per line; powers the HF viewer) |
| `distribution_3000.json` | demographic & income summary |

## Columns (36) by source

For transparency, each column is labeled with **where it comes from** (see also License).

### A. Identifier
- `uuid`

### B. Persona & attributes (from NVIDIA Nemotron-Personas-Japan; census-grounded)
- Narratives: `persona`, `professional_persona`, `sports_persona`, `arts_persona`, `travel_persona`, `culinary_persona`, `cultural_background`
- Skills / interests: `skills_and_expertise` (+`_list`), `hobbies_and_interests` (+`_list`), `career_goals_and_ambitions`
- Demographics: `sex`, `age`, `age_band`, `marital_status`, `education_level`, `occupation`, `region`, `area`, `prefecture`, `country`

### C. Household-income grounding (from e-Stat official statistics)
- `household_income_bracket` — annual household income band
- `household_income_midpoint_manyen` — band midpoint (万円 / ¥10k)
- `household_income_source` — record of the grounding method
- `income_tier` — `low` (<¥3.5M) / `mid` (¥3.5–7M) / `high` (≥¥7M)

### D. Consumer-behavior layer (this dataset; consistent with the statistical direction)
- `disposable_income_feel`, `price_sensitivity`, `brand_orientation`, `promotion_responsiveness`, `bulk_buy_tendency`, `ec_adoption`, `primary_purchase_channels`, `media_contact`

### E. First-person narrative (this dataset)
- `backstory_250w` — a ~220–260 character first-person account of the persona's daily life (see "Why a first-person narrative" below)

> `backstory_250w` is synthetically composed for this dataset; A–D derive from statistics / existing data. The whole dataset is distributed under CC BY 4.0.

## Value reference (Japanese → English)

Decodes every categorical value so the dataset is usable without reading Japanese.

| Column | Japanese values | English |
|---|---|---|
| `sex` | 女 / 男 | Female / Male |
| `area` | 東日本 / 西日本 | East Japan / West Japan |
| `region` | 北海道地方 / 東北地方 / 関東地方 / 中部地方 / 近畿地方 / 中国地方 / 四国地方 / 九州地方 | Hokkaido / Tohoku / Kanto / Chubu / Kinki (Kansai) / Chugoku / Shikoku / Kyushu |
| `country` | 日本 | Japan |
| `age_band` | 20代以下 / 30代 / 40代 / 50代 / 60代 / 70代 / 80歳以上 | ≤29 / 30s / 40s / 50s / 60s / 70s / 80+ |
| `marital_status` | 既婚 / 未婚 / 死別 / 離別 (＋「(子供あり)」) | Married / Single / Widowed / Divorced (＋ "with children") |
| `education_level` | 中学卒 / 高校卒 / 高専卒 / 短大卒 / 大学(卒) 文系・理系 / 大学院(卒) 文系・理系 | Junior high / High school / Technical college (kōsen) / Junior college / University (humanities / sciences) / Graduate school (humanities / sciences) |
| `income_tier` | low / mid / high | low (<¥3.5M) / mid (¥3.5–7M) / high (≥¥7M) |
| `household_income_bracket` | e.g. ５００～５５０万円未満 | annual household income band, e.g. "¥5.0–5.5M" (万円 = ¥10k) |
| `disposable_income_feel` | 切り詰め / 普通 / ゆとり | Tight / Normal / Comfortable |
| `price_sensitivity` | 高 / 中 / 低 | High / Mid / Low |
| `brand_orientation` | PB志向 / PB-NB併用 / NB・品質志向 | Private-brand-oriented / PB–NB mix / National-brand & quality-oriented |
| `promotion_responsiveness` | 高 / 中 / 低 | High / Mid / Low |
| `bulk_buy_tendency` | よくする / たまに / しない | Often / Sometimes / Rarely |
| `ec_adoption` | 高 / 中 / 低 | High / Mid / Low |
| `primary_purchase_channels` | (Japanese phrase) | retail-channel mix — free text, in Japanese |
| `media_contact` | (Japanese phrase) | media-consumption pattern — free text, in Japanese |
| `occupation` | (Japanese) | 499 unique values, in Japanese |

## How it was built (reproducible, 3-layer cascade)

1. **L0 population** — stratified sample of NVIDIA [Nemotron-Personas-Japan](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan) by `age_band × sex` to match population proportions → 3,000 personas (fixed seed).
2. **Income grounding** — `P(income | head-of-household age)` from e-Stat "Comprehensive Survey of Living Conditions", combined with the prefecture income index from the "National Survey of Family Income and Expenditure", for joint **age × region** conditioning; snapped to the nearest band.
3. **L1 consumer layer** — income-tier-conditioned 3-type assignment of price sensitivity, brand orientation, channels, etc. No free continuous scores; **both poles are always retained** within each tier to avoid homogenization.
4. **Narrative** — composed as a name-based first-person interview (see "Why a first-person narrative" for the rationale and research basis).

Official statistics used:
- Comprehensive Survey of Living Conditions (MHLW, e-Stat statsDataId `0003131978`)
- National Survey of Family Income and Expenditure (MIC, e-Stat statsDataId `0003426512`)

Reproduction code is in the GitHub repository: https://github.com/furuchanchan/japan-synthetic-personas

## Why a first-person narrative

`backstory_250w` is a deliberate design choice, not decoration. A table of attributes **underdetermines** a person: an LLM conditioned only on a demographic list tends to drift to the population average and reproduce stereotypes ("low income → saves on everything", "elderly → not digital"), collapsing the diversity that simulation depends on. A concrete first-person life narrative conditions the model far more richly, and a growing body of research shows this raises the fidelity and representativeness of LLM-simulated respondents:

- **Argyle et al. (2023)** introduce *algorithmic fidelity*: conditioning a language model on detailed real backstories makes it "accurately emulate response distributions from a wide variety of human subgroups" — the basis of *silicon sampling*.
- **Moon et al. — "Anthology" (EMNLP 2024)** show that conditioning on open-ended, naturalistic **backstories** rather than attribute lists yields more **consistent** and more **representative** virtual personas (reported up to +18% representativeness and +27% consistency on Pew Research benchmarks).
- **Park et al. (2024)** find that grounding an agent in a person's own first-person **interview** lets it predict that individual's real survey answers at ~85% of their own test–retest reliability — far above a demographics-only baseline.

So each persona here is written as a **name-based, first-person account** — attributes dissolved into a life story — to make it a better conditioning prompt for downstream simulation, not just a label.

**References**
- Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). *Out of One, Many: Using Language Models to Simulate Human Samples.* Political Analysis, 31(3), 337–351. https://doi.org/10.1017/pan.2023.2
- Moon, S., Abdulhai, M., Kang, M., Suh, J., Soedarmadji, W., Kohen Behar, E., & Chan, D. M. (2024). *Virtual Personas for Language Models via an Anthology of Backstories.* EMNLP 2024. https://aclanthology.org/2024.emnlp-main.1110/
- Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Willer, R., Liang, P., & Bernstein, M. S. (2024). *Generative Agent Simulations of 1,000 People.* arXiv:2411.10109. https://arxiv.org/abs/2411.10109v1

Constraints imposed on each narrative:
- dissolve attributes into a life story rather than listing them
- never contradict the income band / price sensitivity / channels, etc.
- no real brand, store, or facility names (generalized to "a major retailer", "a video-streaming service", etc.)
- avoid stereotypes ("low income = saves on everything", "elderly = digitally illiterate") by **always including one distinctive splurge / selective spend** unique to that person

## Intended use
- collecting reactions to new products / concepts (concept testing)
- pre-simulating surveys / interviews (survey simulation)
- agent-based marketing simulation
- evaluation personas for LLM outputs / dialogue

## Limitations
- **Fully synthetic data** — these are not real individuals.
- The consumer layer (D) is a conditional assignment aligned with the **direction** of official statistics; it is **not** calibrated against real category-level purchase data (external validity is future work).
- Narratives (E) are synthetically generated and not guaranteed to be factually accurate.

## License, Attribution & Disclaimer

Released under **Creative Commons Attribution 4.0 International (CC BY 4.0)** — https://creativecommons.org/licenses/by/4.0/

Composed of three sources, all redistributed under CC BY-compatible terms or output-ownership transfer:

**1. Base personas** — sampled and re-composed (with modification) from NVIDIA "Nemotron-Personas-Japan" (CC BY 4.0). https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan
> Fujita, Atsunori; Gong, Vincent; Ogushi, Masaya; Yamamoto, Kotaro; Suhara, Yoshi; Corneil, Dane; Meyer, Yev. *Nemotron-Personas-Japan*, September 2025.

**2. Statistical grounding** — household-income values were derived from Japanese government statistics via the e-Stat API.
> Created by processing the "Comprehensive Survey of Living Conditions" (MHLW) and the "National Survey of Family Income and Expenditure" (MIC). Source: e-Stat (https://www.e-stat.go.jp/). e-Stat terms follow the Government Standard Terms of Use (v2.0), which is compatible with CC BY 4.0.

**3. First-person narratives** (`backstory_250w`) — original synthetic text composed for this dataset; no third-party attribution is required. See "Why a first-person narrative" for the method and its research basis.

**Disclaimer:** Fully synthetic; does not represent real individuals. `backstory_250w` is a generated narrative and not guaranteed to be factually accurate. The creator assumes no liability for any use of this data.

**Created by 株式会社TechWorker.**

---

# 日本語

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

## ファイル / Files

| ファイル | 内容 |
|---|---|
| `japan_personas_3000.csv` | 本体（3,000体 × 36列） |
| `japan_personas_3000.jsonl` | 同内容（1行=1人物のJSON） |
| `distribution_3000.json` | 人口統計・年収分布のサマリ |

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

### E. 一人称叙述（本データセット独自）
- `backstory_250w`（その人物が自分の暮らしを語る約220–260字の一人称テキスト。設計根拠は下記「なぜ一人称叙述か」を参照）

> `backstory_250w` は本データセットのために合成的に作成した叙述です（A〜D は統計・既存データ由来）。
> データセット全体を CC BY 4.0 で配布します。

## 作り方（再現可能・3層カスケード）/ Method

1. **L0 母集団** — NVIDIA Nemotron-Personas-Japan を `age_band × sex` で**人口構成比に比例した層化サンプリング**し3,000体を抽出（乱数固定）。
2. **所得の接地** — e-Stat「国民生活基礎調査」から `P(所得階級 | 世帯主年齢)` を作って世帯年収をサンプリング → 「全国家計構造調査」の県別所得指数で**年代×地域の同時条件付け**を行い、最近接バンドへスナップ。
3. **L1 消費レイヤー** — 接地済みの所得tier・年代・地域から、価格感度・ブランド志向・チャネル等を**所得条件付きの3類型**で付与。自由連続スコアは使わず、各tierに**両極の個体を必ず残す**ことで画一化を回避。
4. **叙述** — 各人物に一人称インタビュー形式の生活叙述を構成（設計根拠は下記「なぜ一人称叙述か」を参照）。

接地に使った公的統計:
- 国民生活基礎調査（厚生労働省, e-Stat statsDataId `0003131978`）
- 全国家計構造調査（総務省, e-Stat statsDataId `0003426512`）

## なぜ一人称叙述か（設計根拠）/ Why a first-person narrative

`backstory_250w` は飾りではなく意図的な設計です。属性の表だけでは人物像は**決まりきりません**——LLMに属性リストだけを与えると、母集団の平均に引きずられてステレオタイプ（「低所得＝全方位節約」「高齢＝デジタル弱者」）を再生産し、シミュレーションに必要な多様性が潰れます。具体的な一人称の生活叙述を与えるとモデルははるかに豊かに条件付けされ、これがLLMで模擬する回答の忠実度・代表性を高めることは、近年の研究が一貫して示しています:

- **Argyle et al. (2023)** は *algorithmic fidelity（アルゴリズム的忠実度）* を提唱。詳細な実在の背景でLLMを条件付けると「多様な人間サブグループの回答分布を正確に再現する」ことを示し、*silicon sampling* の基礎となりました。
- **Moon et al.「Anthology」(EMNLP 2024)** は、属性リストではなく**自由記述の自然な backstory** で条件付けると、より**一貫**して**代表性**の高い仮想ペルソナが得られることを示しました（Pew Research のベンチマークで代表性 最大+18%・一貫性 最大+27%）。
- **Park et al. (2024)** は、本人の一人称**インタビュー**でエージェントを接地すると、その個人の実際の調査回答を、本人の再検査信頼性の約85%の精度で予測できる（属性のみの基準を大きく上回る）ことを示しました。

そこで本データセットの各人物は、属性を生活の語りに溶かした**名前ベースの一人称**で記述しています。単なるラベルではなく、下流のシミュレーションにとってより良い条件付けプロンプトにするためです。

**参考文献 / References**
- Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). *Out of One, Many: Using Language Models to Simulate Human Samples.* Political Analysis, 31(3), 337–351. https://doi.org/10.1017/pan.2023.2
- Moon, S., Abdulhai, M., Kang, M., Suh, J., Soedarmadji, W., Kohen Behar, E., & Chan, D. M. (2024). *Virtual Personas for Language Models via an Anthology of Backstories.* EMNLP 2024. https://aclanthology.org/2024.emnlp-main.1110/
- Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Willer, R., Liang, P., & Bernstein, M. S. (2024). *Generative Agent Simulations of 1,000 People.* arXiv:2411.10109. https://arxiv.org/abs/2411.10109v1

各叙述に課した制約:
- 属性を箇条書きにせず生活の語りに溶かす
- 所得バンド・価格感度・チャネル等と**矛盾させない**
- 実在ブランド・店舗・施設の固有名詞は出さない（「大手量販店」「動画配信サービス」等に一般化）
- 「低所得＝全方位節約」「高齢＝デジタル弱者」等のステレオタイプを避け、**必ず一つ、その人ならではの“例外的なこだわり／選択的支出”** を入れる

## 想定用途 / Intended use
- 新商品・コンセプトのリアクション収集（concept testing）
- アンケート/インタビューの事前シミュレーション（survey simulation）
- エージェントベース・マーケティング・シミュレーション
- LLM出力・対話の評価用ペルソナ

## 制約・注意 / Limitations
- **完全な合成データ**であり、実在の個人ではありません。
- 消費レイヤー（D）は公的統計の**方向性**に整合させた条件付き付与であり、特定商品カテゴリの実購買データで較正したものではありません（外的妥当性の検証は今後の課題）。
- 叙述（E）は合成生成であり、事実の正確性は保証しません。

## ライセンス・出典・免責 / License, Attribution & Disclaimer

本データセットは **CC BY 4.0** の下で公開されています。https://creativecommons.org/licenses/by/4.0/

以下の3つの素材から構成され、いずれもCC BY互換または出力所有権の移転に基づき再配布しています。

**1. ベースペルソナ** — NVIDIA「Nemotron-Personas-Japan」(CC BY 4.0) から人口構成比でサンプリングし、3,000体に再構成（改変あり）。https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan

**2. 統計的接地** — 世帯年収等は政府統計をe-Stat API経由で取得・加工して付与。
> 「国民生活基礎調査」（厚生労働省）および「全国家計構造調査」（総務省）を加工して作成。出典：政府統計の総合窓口 (e-Stat)。政府標準利用規約（第2.0版）準拠・CC BY 4.0互換。

**3. 一人称叙述**（`backstory_250w`）— 本データセットのために作成した独自の合成テキスト。第三者への帰属表示は不要です。生成方法と研究的根拠は「なぜ一人称叙述か」を参照。

**免責**: 完全な合成データであり実在の個人を表すものではありません。`backstory_250w` は生成された叙述であり事実の正確性は保証しません。本データの利用に起因する損害について作成者は責任を負いません。

**作成 / Created by: 株式会社TechWorker**
