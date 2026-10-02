import {
  ApiError,
  BODY_LIMIT_BYTES,
  DATASET_PROVENANCE,
  MODEL_ID,
  PERSONAS,
  PROMPT_INPUT_LIMIT_BYTES,
  SELECT_COUNT,
  VERSION,
  buildAiInput,
  decodeAiResult,
  parseTestBody,
  readBoundedBody,
  selectPersonas,
  validateModelOutput,
} from "./lib";
import { OPENAPI_SPEC } from "./openapi";
import type { Persona } from "./lib";

export { TrialQuota } from "./trial-quota";

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
};

const SECURITY_HEADERS: Record<string, string> = {
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
  "X-Frame-Options": "DENY",
  "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
};

const API_RESPONSE_HEADERS: Record<string, string> = {
  ...CORS_HEADERS,
  // API responses (success and error) are never cached or shared.
  "Cache-Control": "no-store",
};

function json(body: unknown, status = 200, extra: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...API_RESPONSE_HEADERS,
      ...extra,
    },
  });
}

function errorResponse(err: unknown, requestId: string): Response {
  if (err instanceof ApiError) {
    const extra: Record<string, string> = {};
    if (err.status === 429 && err.message.startsWith("retry_after:")) {
      extra["Retry-After"] = err.message.slice("retry_after:".length);
      return json(
        { error: { code: err.code, message: "Rate limit exceeded" } },
        429,
        extra,
      );
    }
    return json({ error: { code: err.code, message: err.message } }, err.status);
  }
  console.log(
    JSON.stringify({ event: "unhandled_error", request_id: requestId, status: 500 }),
  );
  return json(
    { error: { code: "internal_error", message: "Internal error" } },
    500,
  );
}

function profileOf(p: Persona) {
  return {
    age: p.age,
    sex: p.sex,
    age_band: p.age_band,
    prefecture: p.prefecture,
    occupation: p.occupation,
    household_income_bracket: p.household_income_bracket,
    income_tier: p.income_tier,
    price_sensitivity: p.price_sensitivity,
  };
}

function mediaType(request: Request): string {
  return (request.headers.get("Content-Type") ?? "").split(";")[0]!.trim().toLowerCase();
}

async function handleTest(request: Request, env: Env, requestId: string): Promise<Response> {
  if (mediaType(request) !== "application/json") {
    throw new ApiError(415, "unsupported_media_type", "Content-Type must be application/json");
  }
  const raw = await readBoundedBody(request);
  const body = parseTestBody(raw);

  // Select illustrative profiles and build/validate the complete model input
  // before consuming any budget.
  const seed = `${body.idea}\u0000${body.price ?? ""}\u0000${body.language}\u0000${body.audience}`;
  const selected = selectPersonas(body.audience, seed);
  const input = buildAiInput(body, selected);

  // Per-IP limit: best-effort 2 requests per 60-second window per colocation via
  // the Cloudflare rate-limit binding (not a strict global rolling minute; the
  // IP is only used as the ephemeral limit key and is never stored).
  const ip = request.headers.get("CF-Connecting-IP") ?? "anonymous";
  const { success } = await env.IP_RATE_LIMITER.limit({ key: ip });
  if (!success) {
    throw new ApiError(429, "rate_limited_ip", "retry_after:60");
  }

  // Global trial budget: consume BEFORE inference, including failed attempts.
  // One shared coordination atom because the budget is a single global counter;
  // the DO transaction is synchronous and released before the AI call.
  const quota = await env.TRIAL_QUOTA.getByName("global").consume();
  if (!quota.allowed) {
    const retryAfter = Math.max(1, Math.ceil((quota.resetAt - Date.now()) / 1000));
    throw new ApiError(429, "daily_quota_exceeded", `retry_after:${retryAfter}`);
  }

  let aiResult: unknown;
  try {
    aiResult = await env.AI.run(MODEL_ID, input.params);
  } catch {
    // No retry here: a retry would consume extra inference quota.
    throw new ApiError(502, "ai_inference_failed", "AI inference failed; please retry");
  }
  const output = decodeAiResult(aiResult);
  const validated = validateModelOutput(output, selected.map((p) => p.uuid));

  console.log(
    JSON.stringify({
      event: "test_completed",
      request_id: requestId,
      status: 200,
      daily_used: quota.used,
      total_attempts: quota.total,
    }),
  );

  return json(
    {
      reactions: validated.reactions.map((r) => ({
        persona_id: r.persona_id,
        profile: profileOf(selected.find((p) => p.uuid === r.persona_id) as Persona),
        concern: r.concern,
        question: r.question,
      })),
      themes: validated.themes,
      survey_questions: validated.survey_questions,
      meta: {
        model: MODEL_ID,
        audience: body.audience,
        language: body.language,
        profiles_selected: SELECT_COUNT,
        subset_size: PERSONAS.length,
        selection: "deterministic by request text over the audience-filtered illustrative subset",
        prompt_input_bytes: input.bytes,
        backstories_condensed_for_prompt: input.backstoriesCondensed,
        daily_ai_attempts_used: quota.used,
        daily_ai_attempts_limit: quota.limit,
        limitations: [
          "Hypotheses generated from 4 illustrative synthetic profiles; not a representative sample of Japan and not real respondents.",
          "Not a calibrated predictor: no purchase rates, success probabilities, or market-size estimates are produced or implied.",
          "Use the survey questions to validate with real people before making decisions.",
        ],
        provenance: DATASET_PROVENANCE,
      },
    },
    200,
  );
}

export default {
  async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
    const requestId = crypto.randomUUID();
    const url = new URL(request.url);
    try {
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: API_RESPONSE_HEADERS });
      }

      if (url.pathname === "/api/health") {
        if (request.method !== "GET") {
          return json({ error: { code: "method_not_allowed", message: "Use GET" } }, 405, {
            Allow: "GET",
          });
        }
        const quota = await env.TRIAL_QUOTA.getByName("global").peek();
        return json({
          status: "ok",
          version: VERSION,
          model: MODEL_ID,
          limits: {
            body_bytes: BODY_LIMIT_BYTES,
            prompt_input_bytes: PROMPT_INPUT_LIMIT_BYTES,
            per_ip_per_minute: 2,
            daily_ai_attempts: quota.limit,
            daily_ai_attempts_used: quota.used,
          },
          data: DATASET_PROVENANCE,
        });
      }

      if (url.pathname === "/openapi.json") {
        if (request.method !== "GET") {
          return json({ error: { code: "method_not_allowed", message: "Use GET" } }, 405, {
            Allow: "GET",
          });
        }
        return json(OPENAPI_SPEC);
      }

      if (url.pathname === "/api/test") {
        if (request.method !== "POST") {
          return json({ error: { code: "method_not_allowed", message: "Use POST" } }, 405, {
            Allow: "POST",
          });
        }
        return await handleTest(request, env, requestId);
      }

      if (url.pathname.startsWith("/api/")) {
        return json({ error: { code: "not_found", message: "Unknown API route" } }, 404);
      }

      // Static assets (public/) with security headers.
      const asset = await env.ASSETS.fetch(request);
      const res = new Response(asset.body, asset);
      for (const [k, v] of Object.entries(SECURITY_HEADERS)) res.headers.set(k, v);
      return res;
    } catch (err) {
      const res = errorResponse(err, requestId);
      console.log(
        JSON.stringify({
          event: "request_error",
          request_id: requestId,
          status: res.status,
        }),
      );
      return res;
    }
  },
} satisfies ExportedHandler<Env>;
