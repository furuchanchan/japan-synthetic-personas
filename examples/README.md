# Examples / 使用例

| ファイル | 内容 |
|---|---|
| [`quickstart.py`](quickstart.py) | 読み込み＋セグメント抽出（30秒で動く） |
| [`synthetic_survey.py`](synthetic_survey.py) | ペルソナにLLMで**合成コンセプトテスト**を回す（このデータセットの本命用途） |

## セットアップ

```bash
pip install datasets
python quickstart.py
```

合成調査でLLMを使う場合:

```bash
pip install datasets anthropic    # openai / google-genai でも可
export ANTHROPIC_API_KEY=...      # 鍵は環境変数で渡す（コードに書かない）
python synthetic_survey.py
```

## できること

- **コンセプトテスト** — 新商品案への購入意向を3,000体から収集し、年代・所得tier別に集計
- **合成調査** — アンケート/インタビューの事前シミュレーション
- **セグメント設計** — 価格感度・EC利用・ブランド志向でターゲットを切り出す
- **LLM評価** — 多様な属性の被験者ペルソナとして
