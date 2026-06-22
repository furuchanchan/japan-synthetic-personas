"""
合成コンセプトテスト — ペルソナになりきらせて新商品の購入意向を集める。
このデータセットの本命ユースケース。

    pip install datasets anthropic   # or openai / google-genai など任意のLLM
    export ANTHROPIC_API_KEY=...     # 鍵は環境変数で（コードに書かない）
    python synthetic_survey.py

LLM部分はコメントアウトしてあるので、まずはプロンプトの組み立てだけ確認できる。
"""
import json
from datasets import load_dataset

# テストしたい新商品コンセプト（自由に書き換える）
CONCEPT = "1本300円・高タンパク質・低糖質の和風プロテインドリンク（だし風味）"
N = 200  # 合成回答者の人数

ds = load_dataset("furuchanchan/japan-synthetic-personas", split="train")
sample = ds.shuffle(seed=42).select(range(N))


def build_prompt(p: dict) -> str:
    return f"""あなたは以下の人物です。この人物になりきって回答してください。

# あなたのプロフィール
{p['backstory_250w']}
（世帯年収帯: {p['household_income_bracket']} / 価格感度: {p['price_sensitivity']} / EC利用: {p['ec_adoption']} / ブランド志向: {p['brand_orientation']}）

# 質問
次の新商品をあなたは買いますか? 1〜5の5段階（1=絶対買わない, 5=絶対買う）で評価し、理由を1〜2文で。
商品: {CONCEPT}

出力は次のJSONのみ: {{"score": <1-5の整数>, "reason": "<理由>"}}"""


# --- まずはプロンプトを確認（先頭3体） ---
for p in sample.select(range(3)):
    print(build_prompt(p))
    print("=" * 60)

# --- 実際にLLMへ投げる例（Anthropic）。鍵を設定してコメント解除 ---
# from anthropic import Anthropic
# client = Anthropic()
# scores = []
# for p in sample:
#     msg = client.messages.create(
#         model="claude-sonnet-4-6",
#         max_tokens=200,
#         messages=[{"role": "user", "content": build_prompt(p)}],
#     )
#     ans = json.loads(msg.content[0].text)
#     scores.append(ans["score"])
# print(f"\n平均購入意向スコア: {sum(scores)/len(scores):.2f} / 5  (n={len(scores)})")
# # → 年代別・所得tier別に集計すれば、どのセグメントに刺さるか可視化できる
