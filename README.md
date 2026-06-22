# Japan Synthetic Consumer Personas (N=3,000)

日本の人口構成・世帯所得分布に統計的に接地した合成消費者ペルソナ **3,000体**。
各人物に消費行動属性と一人称の生活叙述（`backstory_250w`）が付きます。
新商品コンセプトテスト・合成調査・エージェントシミュレーション・LLM評価ペルソナ向け。

> **データ本体は Hugging Face にあります** → https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas
> このリポジトリは**生成パイプライン（再現コード）と方法論**を提供します。

---

## このリポジトリの中身 / What's here

```
.
├── dataset/
│   ├── README.md                  # データカード（HFと共通）
│   ├── sample_50.csv              # 先頭50件のサンプル（全体はHF）
│   └── distribution_3000.json     # 分布サマリ
├── scripts/                       # 生成パイプライン（00〜08）
└── LICENSE                        # CC BY 4.0
```

データ本体（`japan_personas_3000.csv` / `.jsonl`、計28MB）は Hugging Face に置いています。
GitHub にはサンプル50件のみ同梱しています。

---

## 作り方 / How it was built（3層カスケード）

1. **L0 母集団** — NVIDIA [Nemotron-Personas-Japan](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Japan) を `age_band × sex` で人口構成比に層化サンプリング → 3,000体。
2. **所得の接地** — e-Stat「国民生活基礎調査」`P(所得|世帯主年齢)` ＋「全国家計構造調査」県別所得指数で、年代×地域の同時条件付け。
3. **L1 消費レイヤー** — 所得tier条件付き3類型で価格感度・ブランド志向・チャネル等を付与（両極を残し画一化回避）。
4. **叙述** — 名前ベースの一人称インタビュー形式で生活叙述を生成（属性羅列を避けステレオタイプを抑制）。

接地に使った公的統計:
- 国民生活基礎調査（厚生労働省, e-Stat `0003131978`）
- 全国家計構造調査（総務省, e-Stat `0003426512`）

### 再現手順 / Reproduce
`scripts/` を番号順に実行します。e-Stat APIキーは環境から取得する設計で、コードには含まれません。

```bash
pip install pandas pyarrow huggingface_hub
# scripts/03_build_3000.py → 05_L0_region_L1.py → 06_narrative_sample.py → 07_merge.py
```

詳細なデータ仕様は [`dataset/README.md`](dataset/README.md) を参照。

---

## ライセンス・出典 / License & Attribution

本リポジトリおよびデータセットは **CC BY 4.0**（[LICENSE](LICENSE)）。

- **ベース**: NVIDIA Nemotron-Personas-Japan (CC BY 4.0) を改変
- **統計接地**: 「国民生活基礎調査」（厚生労働省）「全国家計構造調査」（総務省）を加工して作成（出典: e-Stat）
- **`backstory_250w` 列**: Anthropic Claude (claude-sonnet-4-6) による生成テキスト。
  事実の正確性は無保証。

完全な出典・免責は [`dataset/README.md`](dataset/README.md) を参照。

Created by 株式会社TechWorker.
