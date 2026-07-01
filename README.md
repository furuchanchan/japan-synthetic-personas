# Japan Synthetic Consumer Personas (N=3,000)

[![🤗 Dataset on Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-Hugging%20Face-005EFF)](https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-005EFF)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join-7C3AED?logo=discord&logoColor=white)](https://discord.gg/JMVG53hGKS)

**3,000 synthetic Japanese consumer personas, statistically grounded** in national demographics and household-income distributions. Each persona carries consumer-behavior attributes (price sensitivity, brand orientation, channels, EC adoption, media) and a **first-person life narrative** (`backstory_250w`). Built for concept testing, survey simulation, agent-based simulation, and LLM evaluation personas.

> **New — real answers, not just synthetic.** Put your question to **real Japanese respondents** (from **$0.30/answer**), and every real answer helps make this free dataset more accurate → [**Ask real Japanese people**](#ask-real-japanese-people)

![Japan Synthetic Consumer Personas — overview](dataset/images/overview.png)

> **The dataset itself lives on Hugging Face** → https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas
> This repository holds the **generation pipeline (reproduction code) and methodology**.

---

## 🚀 Quickstart

```python
from datasets import load_dataset

ds = load_dataset("furuchanchan/japan-synthetic-personas", split="train")
print(len(ds), "personas")        # 3000
print(ds[0]["backstory_250w"])    # first-person narrative (Japanese)
```

- [`examples/quickstart.py`](examples/quickstart.py) — load + segment in 30 seconds
- [`examples/synthetic_survey.py`](examples/synthetic_survey.py) — **run an LLM-driven concept test over the personas** (the core use case)

## Ask real Japanese people

The 3,000 personas here are **synthetic** — a statistically grounded *model* of Japanese consumers. Free, fast, and ideal for wide early exploration, but not the people themselves. So this project adds a second layer: **put the same question to real Japanese respondents.**

- **When synthetic isn't enough.** Pre-test on the synthetic panel for free, then ask real respondents when a decision actually rides on it — no full research project to stand up.
- **Every real answer sharpens the synthetic.** Real responses are ground truth we use to calibrate where the personas drift, so this free dataset keeps getting more accurate over time.

**How it works** — (1) choose who to ask: target by age, gender, region, occupation & industry, education / student status, and household income; (2) write your questions; (3) we run them with real Japanese respondents and return individual answers plus segment-level aggregates.

**Pricing** — **$0.30 per answer** (one person × one question), billed as *questions × respondents*, **from 3,000 answers** (e.g. 10 questions × 300 people = 3,000 = **$900**).

**Contact** — tell us your question, target, and rough sample size; we'll confirm feasibility and reply with a secure payment link.
- Email: **info@techworker.co.jp**
- X / Twitter: **[@koutarou_en](https://x.com/koutarou_en)** (EN) · **[@koutarou_furuno](https://x.com/koutarou_furuno)** (JP)
- Or open an issue on this repo · Discord: **https://discord.gg/JMVG53hGKS**

## 💬 Community

Questions, feedback, and use cases on Discord → https://discord.gg/JMVG53hGKS
質問・フィードバック・活用事例は Discord でどうぞ → https://discord.gg/JMVG53hGKS

## 🌐 Language

Column **names are in English**; column **values are in Japanese** (this is a dataset of Japanese consumers — values are kept native). A complete **Japanese → English value reference** table is in the [**dataset card**](https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas#value-reference-japanese--english), so the data is usable without reading Japanese.

---

## What's here

```
.
├── dataset/
│   ├── README.md                  # data card (bilingual EN/JA — full spec)
│   ├── sample_50.csv              # first 50 rows (full data on HF)
│   ├── distribution_3000.json     # distribution summary
│   └── images/overview.png        # overview visual
├── examples/                       # usage examples (load, synthetic survey)
├── scripts/                        # generation pipeline (00–08)
└── LICENSE                         # CC BY 4.0
```

The full data (`japan_personas_3000.csv` / `.jsonl`, ~28MB) is on Hugging Face. Only a 50-row sample is bundled here.

## How it was built (3-layer cascade)

1. **L0 population** — stratified sample of NVIDIA [Nemotron-Personas-Japan](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan) by `age_band × sex` to match population proportions → 3,000 personas.
2. **Income grounding** — `P(income | head-of-household age)` from e-Stat "Comprehensive Survey of Living Conditions" + prefecture income index from "National Survey of Family Income and Expenditure", for joint age × region conditioning.
3. **L1 consumer layer** — income-tier-conditioned 3-type assignment of price sensitivity, brand orientation, channels, etc. (keeps both poles, avoids homogenization).
4. **Narrative** — name-based first-person interview format (avoids attribute-listing and stereotyping; see [Why a first-person narrative](#why-a-first-person-narrative)).

Official statistics:
- Comprehensive Survey of Living Conditions (MHLW, e-Stat `0003131978`)
- National Survey of Family Income and Expenditure (MIC, e-Stat `0003426512`)

### Reproduce
Run `scripts/` in numeric order. The e-Stat API key is read from an environment variable and is not in the code. Full data spec (EN + JA) → [`dataset/README.md`](dataset/README.md).

## Why a first-person narrative

`backstory_250w` is a design choice, not decoration. A table of attributes underdetermines a person: an LLM conditioned only on a demographic list drifts to the population average and reproduces stereotypes, collapsing the diversity simulation needs. A concrete first-person life narrative conditions the model far more richly — and recent research shows this raises the fidelity and representativeness of LLM-simulated respondents:

- **Argyle et al. (2023)** — *algorithmic fidelity*: conditioning on detailed real backstories lets a model emulate the response distributions of human subgroups ("silicon sampling"). *Political Analysis* 31(3), 337–351. https://doi.org/10.1017/pan.2023.2
- **Moon et al. (2024), "Anthology"** — open-ended naturalistic **backstories** beat attribute lists, yielding more consistent and representative virtual personas (up to +18% representativeness, +27% consistency on Pew benchmarks). EMNLP 2024. https://aclanthology.org/2024.emnlp-main.1110/
- **Park et al. (2024)** — grounding an agent in a person's own first-person **interview** predicts that individual's real survey answers at ~85% of their own test–retest reliability, far above a demographics-only baseline. arXiv:2411.10109. https://arxiv.org/abs/2411.10109v1

So every persona is written as a name-based, first-person account — attributes dissolved into a life story — to be a better conditioning prompt for downstream simulation. Full design notes (anti-stereotype constraints) → [`dataset/README.md`](dataset/README.md).

## License & Attribution

This repository and dataset are released under **CC BY 4.0** ([LICENSE](LICENSE)).

- **Base**: NVIDIA Nemotron-Personas-Japan (CC BY 4.0), modified
- **Statistical grounding**: "Comprehensive Survey of Living Conditions" (MHLW) and "National Survey of Family Income and Expenditure" (MIC), processed via e-Stat
- **`backstory_250w`**: original synthetic first-person narrative composed for this dataset (no third-party attribution required); see [Why a first-person narrative](#why-a-first-person-narrative)

Full attribution and disclaimer → [`dataset/README.md`](dataset/README.md).

Created by 株式会社TechWorker.

---

## 日本語

日本の人口構成・世帯所得分布に統計的に接地した合成消費者ペルソナ **3,000体**。各人物に消費行動属性と一人称の生活叙述（`backstory_250w`）が付きます。新商品コンセプトテスト・合成調査・エージェントシミュレーション・LLM評価ペルソナ向け。

- **データ本体は Hugging Face** → https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas
- このリポジトリは**生成パイプライン（再現コード）と方法論**
- データの値は日本語のまま。列の意味の**日英対訳表**は[データカード](https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas#value-reference-japanese--english)に収録
- 詳細な日本語ドキュメント（概要・列定義・作り方・ライセンス）→ [`dataset/README.md`](dataset/README.md)
- **なぜ一人称叙述か（設計根拠・論文参照）** → [Why a first-person narrative](#why-a-first-person-narrative)（Argyle 2023 / Anthology・Moon 2024 / Park 2024）

### 実在の日本人に聞く（有料レイヤー）

ここにある3,000体は**合成データ**＝統計接地した消費者の“モデル”で、本人ではありません。無料で速く広く試せますが、合成だけでは足りない場面があります。そこで**同じ質問を実在の日本人に投げられる**層を用意しました。

- **合成だけでは物足りないとき** — まず合成パネルで無料で事前検証し、意思決定がかかる場面で実在の回答者に聞く。フル調査を立ち上げる必要はありません。
- **実回答が合成の精度を上げる** — 実在の回答をグラウンドトゥルースに、ペルソナのズレを較正。この無料データセットは使うほど正確になります。

**使い方** — ①誰に聞くかを選ぶ（年齢・性別・居住地・職業/業種・学歴/学生区分・世帯年収でターゲティング）②質問を書く ③実在の日本人に実施し、個票＋セグメント別集計を返却。

**料金** — **1回答$0.30**（＝1人×1問）、課金は*質問数×人数*、**3,000回答から**（例：10問×300人＝3,000回答＝**$900**）。

**お問い合わせ** — 質問内容・ターゲット・おおよそのサンプル数をお送りください。実現可否を確認のうえ、お支払いリンクを返信します。
- メール: **info@techworker.co.jp**
- X: **[@koutarou_en](https://x.com/koutarou_en)**（英語）・**[@koutarou_furuno](https://x.com/koutarou_furuno)**（日本語）
- 本リポジトリの Issue、または Discord: **https://discord.gg/JMVG53hGKS**
