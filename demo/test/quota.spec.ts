import { runInDurableObject } from "cloudflare:test";
import { env } from "cloudflare:workers";
import { beforeEach, describe, expect, it } from "vitest";
import { callWorker, envWithAi, jsonHeaders, validOutput, VALID_IDEA } from "./helpers";
import { selectPersonas } from "../src/lib";
import type { TrialQuota } from "../src/trial-quota";

function stub() {
  return env.TRIAL_QUOTA.getByName("global");
}

async function resetQuota() {
  await runInDurableObject(stub(), async (_i, state) => {
    state.storage.sql.exec("DELETE FROM daily_quota");
  });
}

async function setDate(date: string, count: number) {
  await runInDurableObject(stub(), async (_i, state) => {
    state.storage.sql.exec(
      "INSERT INTO daily_quota (id, date, count, total) VALUES (1, ?, ?, 0) ON CONFLICT(id) DO UPDATE SET date = excluded.date, count = excluded.count",
      date,
      count,
    );
  });
}

// Mirror the Worker's deterministic selection for the default request
// (idea only => price "", language "en", audience "all").
const selectedIds = () =>
  selectPersonas("all", [VALID_IDEA, "", "en", "all"].join(String.fromCharCode(0))).map(
    (p) => p.uuid,
  );

const okRun = async () => ({ response: validOutput(selectedIds()) });

describe("TrialQuota durable object", () => {
  beforeEach(resetQuota);

  it("consumes atomically and denies the 16th daily attempt", async () => {
    const s = stub() as DurableObjectStub<TrialQuota>;
    const used: number[] = [];
    for (let i = 0; i < 15; i++) {
      const r = await s.consume();
      expect(r.allowed).toBe(true);
      used.push(r.used);
    }
    expect(used).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);
    const denied = await s.consume();
    expect(denied.allowed).toBe(false);
    expect(denied.used).toBe(15);
    expect(denied.resetAt).toBeGreaterThan(Date.now());
  });

  it("stays atomic under concurrent consume calls", async () => {
    const s = stub() as DurableObjectStub<TrialQuota>;
    const results = await Promise.all(Array.from({ length: 20 }, () => s.consume()));
    const allowed = results.filter((r) => r.allowed);
    const denied = results.filter((r) => !r.allowed);
    expect(allowed).toHaveLength(15);
    expect(denied).toHaveLength(5);
    expect(new Set(allowed.map((r) => r.used)).size).toBe(15);
  });

  it("resets the count on UTC daily rollover keeping a single row", async () => {
    await setDate("2000-01-01", 15);
    const s = stub() as DurableObjectStub<TrialQuota>;
    const r = await s.consume();
    expect(r.allowed).toBe(true);
    expect(r.used).toBe(1);
    const rows = await runInDurableObject(stub(), async (_i, state) =>
      state.storage.sql.exec("SELECT COUNT(*) AS n FROM daily_quota").toArray(),
    );
    expect((rows[0] as { n: number }).n).toBe(1);
  });
});

describe("quota enforcement end to end (AI stubbed, not live inference)", () => {
  beforeEach(resetQuota);

  it("blocks AI calls after the daily cap is consumed", async () => {
    const { env: e, calls } = envWithAi(okRun);
    // Spend the budget directly at the coordination atom.
    const s = stub() as DurableObjectStub<TrialQuota>;
    for (let i = 0; i < 15; i++) await s.consume();
    const res = await callWorker(e, { headers: jsonHeaders(), body: { idea: VALID_IDEA } });
    expect(res.status).toBe(429);
    expect(res.headers.get("Retry-After")).toBeTruthy();
    expect(res.headers.get("Access-Control-Allow-Origin")).toBe("*");
    expect(calls.length).toBe(0);
  });

  it("counts failed AI attempts against the daily budget", async () => {
    const { env: e } = envWithAi(async () => {
      throw new Error("boom");
    });
    await callWorker(e, { headers: jsonHeaders(), body: { idea: VALID_IDEA } });
    const q = await (stub() as DurableObjectStub<TrialQuota>).peek();
    expect(q.used).toBe(1);
  });

  it("enforces the per-IP rate limit", async () => {
    const { env: e } = envWithAi(okRun);
    const headers = { ...jsonHeaders(), "CF-Connecting-IP": "1.2.3.4" };
    const r1 = await callWorker(e, { headers, body: { idea: VALID_IDEA } });
    const r2 = await callWorker(e, { headers, body: { idea: VALID_IDEA } });
    const r3 = await callWorker(e, { headers, body: { idea: VALID_IDEA } });
    expect(r1.status).toBe(200);
    expect(r2.status).toBe(200);
    expect(r3.status).toBe(429);
    expect(r3.headers.get("Retry-After")).toBe("60");
  });
});
