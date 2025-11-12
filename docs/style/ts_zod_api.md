# TypeScript + Zod — API Validation & UI Safety

**Purpose:** Strong runtime validation for API routes and UI components using Zod.
**Stack:** Next.js (App Router), TypeScript, Zod, React Query.

---

## 1) Install (reference)
```bash
pnpm add zod
# or: npm i zod
```

## 2) Schemas

```typescript
// /frontend/lib/schemas.ts
import { z } from "zod";

export const KpiSchema = z.object({
  videosToday: z.number().int().nonnegative(),
  failRate: z.number().min(0).max(1),
  budgetNZD: z.number().nonnegative(),
});

export const StatusSchema = z.object({
  kpis: KpiSchema,
  guardrails: z.enum(["passing", "failing", "unknown"]).default("unknown").optional(),
  lastOffload: z
    .object({ ts: z.string().datetime(), request_id: z.string() })
    .nullable()
    .optional(),
});

export const PipelineItemSchema = z.object({
  stage: z.enum(["Fetch","Rank","Script","Video","Voice","Post"]),
  status: z.enum(["idle","queued","running","success","warn","fail"]),
  progress: z.number().min(0).max(100).default(0),
  lastRun: z.string().datetime().optional(),
  eta: z.string().optional(),
});

export const OffloadRowSchema = z.object({
  request_id: z.string(),
  model: z.string(),
  timestamp_utc: z.string().datetime(),
  prompt_hash: z.string(),
  artifact_url: z.string().url(),
  status: z.enum(["success","failure","unknown"]).default("unknown").optional(),
  costNZD: z.number().nonnegative().optional(),
});

export const PrChecksSchema = z.object({
  id: z.number(),
  title: z.string(),
  checks: z.object({
    lint: z.enum(["pass","fail","skip"]),
    test: z.enum(["pass","fail","skip"]),
    guardrails: z.enum(["pass","fail","skip"]),
  }),
});

export const SettingsSchema = z.object({
  MAX_TOKENS: z.number().int().positive(),
  HEAVY_TIMEOUT_SEC: z.number().int().positive(),
  BUDGET_NZD_MONTHLY: z.number().positive(),
  MONITOR_WINDOW: z.string(), // e.g. "05:00-10:00"
});
```

## 3) Next.js API Routes (mock → real swap ready)

```typescript
// /frontend/app/api/mock/status/route.ts
import { NextResponse } from "next/server";
import { StatusSchema } from "@/lib/schemas";

export async function GET() {
  const data = {
    kpis: { videosToday: 6, failRate: 0.08, budgetNZD: 12.4 },
    guardrails: "passing",
    lastOffload: { ts: new Date().toISOString(), request_id: "smoketest1" },
  };
  const parsed = StatusSchema.parse(data);
  return NextResponse.json(parsed);
}

// /frontend/app/api/mock/pipelines/route.ts
import { NextResponse } from "next/server";
import { PipelineItemSchema } from "@/lib/schemas";

export async function GET() {
  const data = [
    { stage:"Fetch", status:"success", progress:100, lastRun:new Date().toISOString() },
    { stage:"Rank", status:"success", progress:100, lastRun:new Date().toISOString() },
    { stage:"Script", status:"running", progress:42, eta:"5m" },
    { stage:"Video", status:"queued", progress:0 },
    { stage:"Voice", status:"idle", progress:0 },
    { stage:"Post", status:"idle", progress:0 },
  ];
  const parsed = data.map((d) => PipelineItemSchema.parse(d));
  return NextResponse.json(parsed);
}

// /frontend/app/api/mock/offloads/route.ts
import { NextResponse } from "next/server";
import { OffloadRowSchema } from "@/lib/schemas";

export async function GET() {
  const data = [
    {
      request_id:"smoketest1",
      model:"gemini-1.5-pro-latest",
      timestamp_utc:new Date().toISOString(),
      prompt_hash:"abc1234",
      artifact_url:"/docs/LAST_OFFLOAD.json",
      status:"success",
      costNZD:0.19
    },
  ];
  const parsed = data.map(d => OffloadRowSchema.parse(d));
  return NextResponse.json(parsed);
}

// /frontend/app/api/mock/prs/route.ts
import { NextResponse } from "next/server";
import { PrChecksSchema } from "@/lib/schemas";

export async function GET() {
  const data = [
    { id: 14, title: "chore(guardrails)", checks: { lint: "pass", test: "pass", guardrails: "pass" } }
  ];
  const parsed = data.map(d => PrChecksSchema.parse(d));
  return NextResponse.json(parsed);
}

// /frontend/app/api/mock/settings/route.ts
import { NextResponse } from "next/server";
import { SettingsSchema } from "@/lib/schemas";

export async function GET() {
  const data = {
    MAX_TOKENS: 12000,
    HEAVY_TIMEOUT_SEC: 90,
    BUDGET_NZD_MONTHLY: 20,
    MONITOR_WINDOW: "05:00-10:00"
  };
  const parsed = SettingsSchema.parse(data);
  return NextResponse.json(parsed);
}
```

## 4) UI Consumption (React Query + Zod)

```typescript
// /frontend/hooks/useStatus.ts
import { useQuery } from "@tanstack/react-query";
import { StatusSchema } from "@/lib/schemas";

export function useStatus() {
  return useQuery({
    queryKey: ["status"],
    queryFn: async () => {
      const res = await fetch("/api/mock/status");
      const json = await res.json();
      return StatusSchema.parse(json);
    },
    staleTime: 30_000,
  });
}
```

## 5) Error Boundaries & Fallbacks

- Wrap pages with an error boundary component.
- Show skeleton loaders while fetching.
- On Zod parse error: render a compact error card with a retry button.

Example fallback:

```typescript
// /frontend/components/ErrorCard.tsx
export function ErrorCard({ title = "Error", message = "Something went wrong." }) {
  return (
    <div className="rounded-xl border p-4 text-sm text-red-600 bg-red-50 dark:bg-red-950/20">
      <div className="font-semibold">{title}</div>
      <div className="opacity-80">{message}</div>
    </div>
  );
}
```

## 6) Testing (Jest/RTL)

- Unit-test schema parsing for happy + error paths.
- Snapshot test PipelineCard for each status.

```typescript
// /frontend/__tests__/schemas.test.ts
import { StatusSchema } from "@/lib/schemas";

test("status schema parses valid payload", () => {
  const parsed = StatusSchema.parse({ kpis: { videosToday: 1, failRate: 0.1, budgetNZD: 3 } });
  expect(parsed.kpis.videosToday).toBe(1);
});
```

## Notes

- Keep schemas the single source of truth for props & API contracts.
- Convert mock routes to real APIs later without changing UI code.
- Validate on boundary: API route parses → UI consumes typed-safe data.
