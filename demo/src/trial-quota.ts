import { DurableObject } from "cloudflare:workers";

export interface QuotaResult {
  allowed: boolean;
  used: number;
  limit: number;
  /** Unix ms of the next UTC midnight (daily reset). */
  resetAt: number;
  total: number;
}

const LIMIT = 15;

function utcToday(now = Date.now()): string {
  return new Date(now).toISOString().slice(0, 10);
}

function nextUtcMidnight(now = Date.now()): number {
  const d = new Date(now);
  d.setUTCHours(24, 0, 0, 0);
  return d.getTime();
}

/**
 * Single coordination atom for the trial's global daily AI budget.
 *
 * One shared object is intentional: the trial budget is a single global counter
 * (<=15 AI attempts per UTC day across ALL callers), so there is exactly one
 * coordination atom and no benefit to sharding it. Inference itself never runs
 * through this object — the worker calls consume() (a short synchronous SQL
 * transaction) and releases the object before calling Workers AI, so the DO is
 * not on the inference path and never holds a lock across network I/O.
 *
 * Storage contains only {date, count, total} — never submitted ideas, model
 * output, IPs, or any other customer data.
 */
export class TrialQuota extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      ctx.storage.sql.exec(
        `CREATE TABLE IF NOT EXISTS daily_quota (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          date TEXT NOT NULL,
          count INTEGER NOT NULL,
          total INTEGER NOT NULL DEFAULT 0
        )`,
      );
    });
  }

  /**
   * Atomically check-and-consume one daily AI attempt. Synchronous SQL in a
   * transaction: concurrent RPC calls are serialized by the object, so the
   * read-modify-write cannot double-spend the budget.
   */
  consume(): QuotaResult {
    return this.ctx.storage.transactionSync(() => {
      const today = utcToday();
      const resetAt = nextUtcMidnight();
      const sql = this.ctx.storage.sql;
      sql.exec(
        `INSERT INTO daily_quota (id, date, count, total) VALUES (1, ?, 0, 0)
         ON CONFLICT(id) DO NOTHING`,
        today,
      );
      const row = sql
        .exec<{ date: string; count: number; total: number }>(
          "SELECT date, count, total FROM daily_quota WHERE id = 1",
        )
        .one();
      const count = row.date === today ? row.count : 0;
      if (count >= LIMIT) {
        // Daily rollover: keep a single small row; update the date so stale
        // dates do not accumulate.
        if (row.date !== today) {
          sql.exec("UPDATE daily_quota SET date = ?, count = 0 WHERE id = 1", today);
        }
        return { allowed: false, used: count, limit: LIMIT, resetAt, total: row.total };
      }
      sql.exec(
        "UPDATE daily_quota SET date = ?, count = ?, total = total + 1 WHERE id = 1",
        today,
        count + 1,
      );
      return { allowed: true, used: count + 1, limit: LIMIT, resetAt, total: row.total + 1 };
    });
  }

  /** Read-only view for /api/health and tests. Does not consume budget. */
  peek(): QuotaResult {
    const today = utcToday();
    const resetAt = nextUtcMidnight();
    const row = this.ctx.storage.sql
      .exec<{ date: string; count: number; total: number }>(
        "SELECT date, count, total FROM daily_quota WHERE id = 1",
      )
      .toArray()[0];
    const used = row && row.date === today ? row.count : 0;
    return { allowed: used < LIMIT, used, limit: LIMIT, resetAt, total: row?.total ?? 0 };
  }
}
