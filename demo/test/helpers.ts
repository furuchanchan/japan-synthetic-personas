import { env } from "cloudflare:workers";
import { createExecutionContext, waitOnExecutionContext } from "cloudflare:test";
import worker from "../src/index";
import { PERSONAS } from "../src/lib";

export const VALID_IDEA =
  "A subscription app that delivers weekly bento boxes tailored to elderly people living alone.";

export function validOutput(ids: string[]) {
  return {
    reactions: ids.map((id, i) => ({
      persona_id: id,
      concern: `Concern ${i + 1} about the idea`,
      question: `Question ${i + 1} about the idea?`,
    })),
    themes: ["theme one", "theme two", "theme three"],
    survey_questions: ["q1?", "q2?", "q3?", "q4?", "q5?"],
  };
}

export function validIds(): string[] {
  return PERSONAS.slice(0, 4).map((p) => p.uuid);
}

interface MockAi {
  calls: { model: string; inputs: unknown }[];
}

/**
 * Build an Env whose AI binding is replaced by a stub. The stub is a test double
 * for the binding contract only — it is not live inference.
 */
export function envWithAi(run: (model: string, inputs: unknown) => Promise<unknown>) {
  const mock: MockAi = { calls: [] };
  const ai = {
    run: async (model: string, inputs: unknown) => {
      mock.calls.push({ model, inputs });
      return run(model, inputs);
    },
  };
  const testEnv = Object.create(env) as Env;
  testEnv.AI = ai as unknown as Env["AI"];
  return { env: testEnv, calls: mock.calls };
}

export async function callWorker(
  env: Env,
  init: { path?: string; method?: string; body?: unknown; headers?: Record<string, string> } = {},
) {
  const headers: Record<string, string> = {
    "CF-Connecting-IP": `test-${Math.random().toString(36).slice(2)}`,
    ...init.headers,
  };
  let body: string | undefined;
  if (typeof init.body === "string") body = init.body;
  else if (init.body !== undefined) body = JSON.stringify(init.body);
  const request = new Request(`http://example.com${init.path ?? "/api/test"}`, {
    method: init.method ?? "POST",
    headers,
    ...(body !== undefined ? { body } : {}),
  });
  const ctx = createExecutionContext();
  const res = await worker.fetch(request, env, ctx);
  await waitOnExecutionContext(ctx);
  return res;
}

export function jsonHeaders() {
  return { "Content-Type": "application/json" };
}
