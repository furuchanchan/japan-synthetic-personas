"use strict";

// API base: empty string in config.js means "same origin" (the Worker itself).
// Static mirrors (GitHub Pages / HF / Vercel) set window.API_BASE_URL there.
const API_BASE_URL = window.API_BASE_URL || location.origin;

const SURVEY_EMAIL = "info@techworker.co.jp";
const PRICE_PAGE = "https://techworker.co.jp/personas/";
const DATASET_URL = "https://huggingface.co/datasets/furuchanchan/japan-synthetic-personas";

const I18N = {
  en: {
    lede: "Use synthetic perspectives to find what to ask real people in Japan. Describe an idea, get concerns from 4 illustrative synthetic personas and 5 neutral questions for a real survey. Free, anonymous, no signup, no API key.",
    ideaLabel: "Your product or service idea ",
    ideaHelp: "20–1200 characters.",
    priceLabel: "Price hint ",
    audienceLabel: "Audience",
    opt: "(optional)",
    audienceAll: "All ages",
    audienceYoung: "Young adults (under 30)",
    audienceWorking: "Working age (30s–50s)",
    audienceOlder: "Older adults (60+)",
    fillExample: "Fill an example",
    submit: "Test this idea",
    testing: "Generating…",
    resultsHeading: "Synthetic reactions",
    resultsNote: "Reactions from 4 illustrative synthetic profiles — hypotheses, not predictions and not real respondents.",
    themesHeading: "Themes",
    surveyHeading: "Questions to ask real people",
    concern: "Concern",
    question: "Would ask",
    copyJson: "Copy JSON",
    downloadBrief: "Download survey brief",
    copied: "Copied.",
    copyFailed: "Clipboard unavailable — use the download button instead.",
    downloaded: "Brief downloaded.",
    errorHeading: "Something went wrong",
    quotaNote: "The free daily trial quota is exhausted. You can still request a real survey below — it uses only your own inputs and does not need this API.",
    realHeading: "Ready to ask real people?",
    realCopy1: "The profiles above are synthetic. When a decision rides on the answer, we can run your questions with real Japanese respondents. Published rate: $0.30 per person-question, minimum 3,000 person-questions (e.g. 10 questions × 300 people = $900). Scope and price are confirmed with you first — nothing is ordered or billed by clicking. See ",
    apiLead: "No API key. Rate limited: 2 requests per IP per 60-second window (best-effort, per colocation), 15 AI generations per UTC day globally (strict).",
    mailto: "Request a real survey quote",
    copyBrief: "Copy survey brief",
    mailtoNote: "Opens your mail app with a pre-filled brief. The enquiry is free; sending is always up to you.",
    privacyHeading: "Data & privacy",
    privacyCopy1: "Personas are synthetic: 48 illustrative records sampled from ",
    privacyCopy2: " (CC BY 4.0; built on NVIDIA Nemotron-Personas-Japan with e-Stat income conditioning and TechWorker additions; modified by sampling). Not a representative sample. Your idea text is processed on Cloudflare Workers AI to generate output and is not stored by this app. We log only request counts and status, never prompt or IP content.",
    errIdea: "Please enter an idea of 20–1200 characters.",
    errRateLimited: "Too many requests. Please retry after 60 seconds.",
    errNetwork: "Could not reach the API. Check your connection and retry.",
    example: "A subscription app that delivers weekly bento boxes tailored to elderly people living alone, with dietary restrictions handled automatically.",
    briefTitle: "Real survey enquiry — Japan Launch Check",
  },
  ja: {
    lede: "合成ペルソナの視点で、日本の実際の人々に聞くべきことを見つけます。アイデアを入力すると、4人の例示的な合成ペルソナの懸念と、実際の調査で使える5つの中立な質問が得られます。無料・匿名・登録不要・APIキー不要。",
    ideaLabel: "テストしたい製品・サービスのアイデア ",
    ideaHelp: "20〜1200文字。",
    priceLabel: "価格の目安 ",
    audienceLabel: "対象層",
    opt: "（任意）",
    audienceAll: "全年齢",
    audienceYoung: "若年層（20代以下）",
    audienceWorking: "就労層（30〜50代）",
    audienceOlder: "シニア層（60代以上）",
    fillExample: "例を入力",
    submit: "このアイデアをテスト",
    testing: "生成中…",
    resultsHeading: "合成ペルソナの反応",
    resultsNote: "4つの例示的な合成プロファイルによる仮説です。予測ではなく、実際の回答者でもありません。",
    themesHeading: "テーマ",
    surveyHeading: "実際の人々に聞く質問",
    concern: "懸念",
    question: "質問",
    copyJson: "JSONをコピー",
    downloadBrief: "調査ブリーフをダウンロード",
    copied: "コピーしました。",
    copyFailed: "クリップボードが使えません。ダウンロードボタンをご利用ください。",
    downloaded: "ブリーフをダウンロードしました。",
    errorHeading: "エラーが発生しました",
    quotaNote: "無料トライアルの1日の上限に達しました。下の「実際の調査を依頼」は入力内容だけで作成でき、このAPIを必要としません。",
    realHeading: "実際の人々に聞きますか？",
    realCopy1: "上記のプロファイルは合成データです。実際の判断に使う場合は、日本の実回答者に質問を実施できます。公開料金: 1人×1問あたり$0.30、最低3,000人・問（例: 10問×300人 = $900）。範囲と価格は事前に確認します。クリックしても注文・課金は発生しません。詳細: ",
    apiLead: "APIキー不要。レート制限: IPあたり60秒に2リクエスト（ベストエフォート）、全利用者で1日（UTC）15回まで（厳密）。",
    mailto: "実際の調査の見積もりを依頼",
    copyBrief: "調査ブリーフをコピー",
    mailtoNote: "メールアプリが開き、依頼文が入力されます。相談は無料で、送信するかどうかは常にあなた次第です。",
    privacyHeading: "データとプライバシー",
    privacyCopy1: "ペルソナは合成データです。48件の例示的なレコードを ",
    privacyCopy2: " からサンプリング（CC BY 4.0。NVIDIA Nemotron-Personas-Japanを基盤にe-Stat収入統計で条件付け、TechWorkerが追加。サンプリングによる改変あり）。代表サンプルではありません。入力したアイデアはCloudflare Workers AIで出力生成のために処理され、このアプリでは保存されません。ログはリクエスト回数とステータスのみで、プロンプトやIPは記録しません。",
    errIdea: "20〜1200文字でアイデアを入力してください。",
    errRateLimited: "リクエストが多すぎます。60秒後に再試行してください。",
    errNetwork: "APIに接続できませんでした。接続を確認して再試行してください。",
    example: "一人暮らしの高齢者向けに、食事制限を自動で考慮した週替わり弁当を届けるサブスクアプリ。",
    briefTitle: "実査依頼 — Japan Launch Check",
  },
};

let lang = "en";
let lastResult = null; // { data, inputs: {idea, price, audience} }
let requestSeq = 0;

const $ = (id) => document.getElementById(id);
const t = (k) => I18N[lang][k];

function setText(el, text) {
  el.textContent = text;
}

function link(url, label) {
  const a = document.createElement("a");
  a.href = url;
  a.rel = "noopener";
  a.textContent = label;
  return a;
}

function renderRichParagraph(el, pre, url, post) {
  el.textContent = "";
  el.append(document.createTextNode(pre), link(url, url));
  if (post) el.append(document.createTextNode(post));
}

function applyLang() {
  document.documentElement.lang = lang;
  setText($("lede"), t("lede"));
  $("idea-label").firstChild.textContent = t("ideaLabel");
  setText($("idea-help"), t("ideaHelp"));
  $("price-label").firstChild.textContent = t("priceLabel");
  setText($("audience-label"), t("audienceLabel"));
  const sel = $("audience");
  sel.options[0].textContent = t("audienceAll");
  sel.options[1].textContent = t("audienceYoung");
  sel.options[2].textContent = t("audienceWorking");
  sel.options[3].textContent = t("audienceOlder");
  setText($("fill-example"), t("fillExample"));
  setText($("submit-btn"), t("submit"));
  setText($("results-heading"), t("resultsHeading"));
  setText($("results-note"), t("resultsNote"));
  setText($("themes-heading"), t("themesHeading"));
  setText($("survey-heading"), t("surveyHeading"));
  setText($("copy-json"), t("copyJson"));
  setText($("download-brief"), t("downloadBrief"));
  setText($("error-heading"), t("errorHeading"));
  setText($("error-quota-note"), t("quotaNote"));
  setText($("real-heading"), t("realHeading"));
  renderRichParagraph($("real-copy"), t("realCopy1"), PRICE_PAGE, null);
  setText($("api-lead"), t("apiLead"));
  setText($("mailto-btn"), t("mailto"));
  setText($("copy-brief"), t("copyBrief"));
  setText($("download-brief-alt"), t("downloadBrief"));
  setText($("mailto-note"), t("mailtoNote"));
  setText($("privacy-heading"), t("privacyHeading"));
  renderRichParagraph($("privacy-copy"), t("privacyCopy1"), DATASET_URL, t("privacyCopy2"));
  $("lang-en").classList.toggle("active", lang === "en");
  $("lang-ja").classList.toggle("active", lang === "ja");
  $("lang-en").setAttribute("aria-pressed", String(lang === "en"));
  $("lang-ja").setAttribute("aria-pressed", String(lang === "ja"));
}

function setStatus(msg, isError) {
  const el = $("status");
  el.textContent = msg;
  el.classList.toggle("error", Boolean(isError));
}

function currentInputs() {
  return {
    idea: $("idea").value.trim(),
    price: $("price").value.trim(),
    audience: $("audience").value,
  };
}

function inputsChanged() {
  if (!lastResult) return false;
  const c = currentInputs();
  const s = lastResult.inputs;
  return c.idea !== s.idea || c.price !== s.price || c.audience !== s.audience;
}

/** Drop stale results when inputs change so they cannot feed a new enquiry. */
function invalidateIfChanged() {
  if (lastResult && inputsChanged()) {
    lastResult = null;
    $("results").hidden = true;
  }
  updateMailto();
}

function renderResults(data, inputs) {
  lastResult = { data, inputs };
  const list = $("reactions");
  list.textContent = "";
  for (const r of data.reactions) {
    const li = document.createElement("li");
    const who = document.createElement("p");
    who.className = "who";
    const p = r.profile;
    who.textContent = `${p.age_band} · ${p.sex} · ${p.prefecture} · ${p.occupation} · ${p.household_income_bracket}`;
    const concern = document.createElement("p");
    concern.className = "concern";
    const cl = document.createElement("span");
    cl.className = "lbl";
    cl.textContent = t("concern") + ": ";
    concern.append(cl, document.createTextNode(r.concern));
    const question = document.createElement("p");
    question.className = "question";
    const ql = document.createElement("span");
    ql.className = "lbl";
    ql.textContent = t("question") + ": ";
    question.append(ql, document.createTextNode(r.question));
    li.append(who, concern, question);
    list.appendChild(li);
  }
  const themes = $("themes");
  themes.textContent = "";
  for (const theme of data.themes) {
    const li = document.createElement("li");
    li.textContent = theme;
    themes.appendChild(li);
  }
  const qs = $("survey-questions");
  qs.textContent = "";
  for (const q of data.survey_questions) {
    const li = document.createElement("li");
    li.textContent = q;
    qs.appendChild(li);
  }
  $("results").hidden = false;
  updateMailto();
}

function buildBrief() {
  const c = currentInputs();
  const lines = [
    t("briefTitle"),
    "",
    `Idea: ${c.idea}`,
    c.price ? `Price hint: ${c.price}` : null,
    `Audience: ${c.audience}`,
    "",
    "Questions we'd like to ask real respondents:",
  ];
  const qs = lastResult ? lastResult.data.survey_questions : [];
  if (qs.length) {
    qs.forEach((q, i) => lines.push(`${i + 1}. ${q}`));
  } else {
    lines.push("(add your questions here)");
  }
  lines.push("", `Reference pricing: ${PRICE_PAGE}`);
  return lines.filter((l) => l !== null).join("\n");
}

function updateMailto() {
  const subject = encodeURIComponent("Real survey enquiry — Japan Launch Check");
  const body = encodeURIComponent(buildBrief());
  $("mailto-btn").href = `mailto:${SURVEY_EMAIL}?subject=${subject}&body=${body}`;
}

function download(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

async function copyOrDownload(text, filename) {
  try {
    await navigator.clipboard.writeText(text);
    setStatus(t("copied"), false);
  } catch {
    setStatus(t("copyFailed"), true);
    download(filename, text);
  }
}

function setControlsDisabled(disabled) {
  for (const id of ["idea", "price", "audience", "fill-example", "submit-btn", "lang-en", "lang-ja"]) {
    $(id).disabled = disabled;
  }
}

async function onSubmit(ev) {
  ev.preventDefault();
  const ideaEl = $("idea");
  const c = currentInputs();
  const errEl = $("idea-error");
  if (c.idea.length < 20 || c.idea.length > 1200) {
    ideaEl.classList.add("invalid");
    errEl.textContent = t("errIdea");
    errEl.hidden = false;
    ideaEl.focus();
    return;
  }
  ideaEl.classList.remove("invalid");
  errEl.hidden = true;

  const seq = ++requestSeq;
  setControlsDisabled(true);
  $("error-box").hidden = true;
  setStatus(t("testing"), false);

  const payload = { idea: c.idea, language: lang, audience: c.audience };
  if (c.price) payload.price = c.price;

  try {
    const res = await fetch(`${API_BASE_URL}/api/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (seq !== requestSeq) return; // a newer request superseded this one
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const code = data && data.error ? data.error.code : null;
      const msg = code === "rate_limited_ip"
        ? t("errRateLimited")
        : data && data.error && data.error.message
          ? data.error.message
          : `HTTP ${res.status}`;
      setText($("error-message"), msg);
      $("error-quota-note").hidden = code !== "daily_quota_exceeded";
      $("error-box").hidden = false;
      setStatus(msg, true);
      return;
    }
    renderResults(data, c);
    setStatus("", false);
  } catch {
    if (seq !== requestSeq) return;
    setStatus(t("errNetwork"), true);
    setText($("error-message"), t("errNetwork"));
    $("error-quota-note").hidden = true;
    $("error-box").hidden = false;
  } finally {
    if (seq === requestSeq) setControlsDisabled(false);
  }
}

function init() {
  $("idea-form").addEventListener("submit", onSubmit);
  $("lang-en").addEventListener("click", () => { lang = "en"; applyLang(); });
  $("lang-ja").addEventListener("click", () => { lang = "ja"; applyLang(); });
  $("fill-example").addEventListener("click", () => {
    $("idea").value = t("example");
    invalidateIfChanged();
    $("idea").focus();
  });
  $("copy-json").addEventListener("click", () => {
    if (lastResult) copyOrDownload(JSON.stringify(lastResult.data, null, 2), "result.json");
  });
  $("download-brief").addEventListener("click", () => {
    download("survey-brief.txt", buildBrief());
    setStatus(t("downloaded"), false);
  });
  $("download-brief-alt").addEventListener("click", () => {
    download("survey-brief.txt", buildBrief());
    setStatus(t("downloaded"), false);
  });
  $("copy-brief").addEventListener("click", () => {
    copyOrDownload(buildBrief(), "survey-brief.txt");
  });
  // The enquiry brief is composed from inputs alone — works even when AI fails.
  for (const id of ["idea", "price", "audience"]) {
    $(id).addEventListener("input", invalidateIfChanged);
  }
  $("openapi-link").href = `${API_BASE_URL}/openapi.json`;
  setText(
    $("curl-example"),
    `curl -X POST ${API_BASE_URL}/api/test \\\n  -H 'Content-Type: application/json' \\\n  -d '{"idea":"A subscription app that ...","language":"en","audience":"all"}'`,
  );
  applyLang();
  updateMailto();
}

init();
