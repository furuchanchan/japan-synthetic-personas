export const OPENAPI_SPEC = {
  openapi: "3.1.0",
  info: {
    title: "Japan Launch Check",
    version: "0.1.0",
    description:
      "Free, anonymous, keyless hypothesis generator for product ideas aimed at Japan. " +
      "Given a product idea, it returns reactions from 4 illustrative synthetic personas, " +
      "3 themes, and 5 neutral questions you can take to a real human survey. " +
      "This is a hypothesis generator: synthetic personas are NOT real respondents, " +
      "and output is not a calibrated predictor of purchase rates or market success. " +
      "Persona data: furuchanchan/japan-synthetic-personas (CC BY 4.0), built on NVIDIA " +
      "Nemotron-Personas-Japan with e-Stat income conditioning and TechWorker synthetic " +
      "additions; the demo uses a deterministic 48-record illustrative subset, not a " +
      "representative sample. Submitted text is processed on Cloudflare Workers AI and " +
      "is not stored by this service.",
  },
  servers: [{ url: "/" }],
  paths: {
    "/api/health": {
      get: {
        summary: "Service status, model id, and data provenance",
        operationId: "getHealth",
        responses: {
          "200": { description: "Service status", content: { "application/json": {} } },
        },
      },
    },
    "/api/test": {
      post: {
        summary: "Generate synthetic-persona concerns and human-survey questions for an idea",
        operationId: "testIdea",
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: {
                type: "object",
                additionalProperties: false,
                required: ["idea"],
                properties: {
                  idea: {
                    type: "string",
                    minLength: 20,
                    maxLength: 1200,
                    description: "Product or service idea to test",
                  },
                  price: {
                    type: "string",
                    maxLength: 120,
                    description: "Optional price hint, e.g. \"$20/month\"",
                  },
                  language: {
                    type: "string",
                    enum: ["en", "ja"],
                    default: "en",
                    description: "Output language",
                  },
                  audience: {
                    type: "string",
                    enum: ["all", "young-adults", "working-age", "older-adults"],
                    default: "all",
                    description: "Age-band filter applied to the 48-record illustrative subset",
                  },
                },
              },
            },
          },
        },
        responses: {
          "200": {
            description: "Generated hypotheses",
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  required: ["reactions", "themes", "survey_questions", "meta"],
                  properties: {
                    reactions: {
                      type: "array",
                      minItems: 4,
                      maxItems: 4,
                      items: {
                        type: "object",
                        required: ["persona_id", "profile", "concern", "question"],
                        properties: {
                          persona_id: { type: "string" },
                          profile: {
                            type: "object",
                            description:
                              "Server-authoritative synthetic profile fields (never model-invented)",
                            properties: {
                              age: { type: "integer" },
                              sex: { type: "string" },
                              age_band: { type: "string" },
                              prefecture: { type: "string" },
                              occupation: { type: "string" },
                              household_income_bracket: { type: "string" },
                              income_tier: { type: "string" },
                              price_sensitivity: { type: "string" },
                            },
                          },
                          concern: { type: "string" },
                          question: { type: "string" },
                        },
                      },
                    },
                    themes: { type: "array", minItems: 3, maxItems: 3, items: { type: "string" } },
                    survey_questions: {
                      type: "array",
                      minItems: 5,
                      maxItems: 5,
                      items: { type: "string" },
                    },
                    meta: {
                      type: "object",
                      description:
                        "Model id, selection info, subset size, and data limitations",
                    },
                  },
                },
              },
            },
          },
          "400": { description: "Invalid request body or fields" },
          "413": { description: "Request body exceeds 8192 bytes" },
          "415": { description: "Content-Type must be application/json" },
          "422": { description: "Audience filter too narrow or encoded prompt too large" },
          "429": {
            description:
              "Rate limit exceeded. Either the best-effort per-IP limit (2 requests per 60-second window per colocation via the Cloudflare rate-limit binding) or the strict global trial quota (15 AI attempts per UTC day, Durable Object). Retry-After header set.",
          },
          "502": { description: "AI inference failed or returned invalid output; retryable" },
        },
      },
    },
  },
  "x-trial-limits": {
    perIp:
      "Best-effort: 2 requests per IP per 60-second window per colocation (Cloudflare rate-limit binding). IPs are never stored.",
    globalDaily:
      "Strict: 15 AI attempts per UTC day across all callers, enforced atomically by a Durable Object (launch cap, not a free-tier guarantee)",
    note: "Quota is consumed before inference, including failed attempts. No API keys or payment required. Persona backstories may be byte-truncated inside the prompt to fit the input cap; source data is unchanged.",
  },
} as const;
