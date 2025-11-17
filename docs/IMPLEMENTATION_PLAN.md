# 📋 XSELLER.AI DASHBOARD MVP - IMPLEMENTATION PLAN

**Project:** Xseller.ai AI Agent Dashboard
**Goal:** Build a professional frontend dashboard for multi-agent content automation
**Timeline:** 10-12 days (6 phases)
**Tech Stack:** Next.js 14 + TypeScript + Tailwind CSS + ShadCN UI
**Approach:** Frontend-only MVP with mock data, clean API layer for future backend integration

---

## 🎯 CURRENT STATE ANALYSIS

### What We Have ✅

**Backend (Fully Operational):**
- ✅ FastAPI backend with REST API
- ✅ Multi-agent system (news ingestion, ranking, script generation, video production, TTS, publishing)
- ✅ SQLite database with models for posts, articles, assets, rankings
- ✅ Scheduler for automated jobs (news fetch at 7:30 AM, 12:30 PM, 9 PM NZDT)
- ✅ External API integrations (OpenAI, Gemini, ElevenLabs, Pexels, NewsAPI, Publer)

**Frontend (Needs Enhancement):**
- ✅ Next.js 14 with App Router + TypeScript
- ✅ Basic dashboard with stats cards ([app/page.tsx](../frontend/app/page.tsx))
- ✅ Queue management page ([app/queue/page.tsx](../frontend/app/queue/page.tsx))
- ✅ Settings page ([app/settings/page.tsx](../frontend/app/settings/page.tsx))
- ✅ Insights page ([app/insights/page.tsx](../frontend/app/insights/page.tsx))
- ✅ Tailwind CSS with custom design system

### What Needs Building 🔨

**New Pages:**
1. **Enhanced Dashboard** - System overview with agent activity monitoring
2. **Agent Management** - List view + detail view for all agents
3. **Video Pipeline** - Visual workflow showing News → Ranking → Script → Video → Publish
4. **Enhanced Settings** - Professional API key management with testing

**New Components:**
- Layout system (Sidebar, Header, MainLayout)
- Agent monitoring components (AgentCard, AgentStatusBadge, AgentProgressBar, AgentLogViewer)
- Workflow components (PipelineStage, PipelineOverview)
- Settings components (ApiKeyInput, ApiKeyCard)
- Base UI components (using ShadCN UI)

**New Infrastructure:**
- API layer ([lib/api/](../frontend/lib/api/)) with mock data support
- TypeScript types ([lib/types/](../frontend/lib/types/))
- Custom React hooks ([lib/hooks/](../frontend/lib/hooks/))

---

## 🎨 DESIGN SYSTEM

### Design Reference
**Helm HR Ops Dashboard** - Clean left sidebar, professional layout, card-based design

### Color Palette

```css
/* Primary Colors (Brand) */
--primary-50: #f0f9ff;   /* Ice Blue - backgrounds */
--primary-100: #e0f2fe;  /* Sky Light - hover states */
--primary-500: #0ea5e9;  /* Sky Blue - primary actions */
--primary-600: #0284c7;  /* Deep Sky - active states */
--primary-700: #0369a1;  /* Ocean Blue - emphasis */

/* Semantic Colors (Status) */
--success-500: #22c55e;  /* Green - success/approved */
--warning-500: #f59e0b;  /* Amber - warning/pending */
--error-500: #ef4444;    /* Red - error/failed */
--info-500: #3b82f6;     /* Blue - info/processing */

/* Neutral Colors (UI) */
--gray-50: #f9fafb;      /* Backgrounds */
--gray-100: #f3f4f6;     /* Cards */
--gray-200: #e5e7eb;     /* Borders */
--gray-500: #6b7280;     /* Secondary text */
--gray-700: #374151;     /* Headings */
--gray-900: #111827;     /* Titles */

/* Agent Status Colors */
--agent-active: #22c55e;    /* 🟢 Green - running */
--agent-processing: #3b82f6; /* 🔵 Blue - working */
--agent-queued: #f59e0b;    /* 🟡 Amber - queued */
--agent-idle: #9ca3af;      /* ⚪ Gray - waiting */
--agent-error: #ef4444;     /* 🔴 Red - failed */
```

### Typography

```css
/* Font Stack */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

/* Type Scale */
--text-xs: 0.75rem;      /* 12px - captions */
--text-sm: 0.875rem;     /* 14px - small text */
--text-base: 1rem;       /* 16px - body */
--text-lg: 1.125rem;     /* 18px - large body */
--text-xl: 1.25rem;      /* 20px - H4 */
--text-2xl: 1.5rem;      /* 24px - H3 */
--text-3xl: 1.875rem;    /* 30px - H2 */
--text-4xl: 2.25rem;     /* 36px - H1 */

/* Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing System

```css
/* Spacing Scale (based on 4px grid) */
--spacing-1: 0.25rem;    /* 4px */
--spacing-2: 0.5rem;     /* 8px */
--spacing-3: 0.75rem;    /* 12px */
--spacing-4: 1rem;       /* 16px */
--spacing-6: 1.5rem;     /* 24px */
--spacing-8: 2rem;       /* 32px */
--spacing-12: 3rem;      /* 48px */

/* Usage */
Card padding: p-6
Section margins: mb-8
Button padding: px-4 py-2
Grid gaps: gap-6
```

### Border & Radius

```css
--radius-sm: 0.375rem;   /* 6px - buttons, badges */
--radius-md: 0.5rem;     /* 8px - cards, inputs */
--radius-lg: 0.75rem;    /* 12px - modals */
--radius-xl: 1rem;       /* 16px - panels */

--border-width: 1px;
--border-color: var(--gray-200);
```

### Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## 📐 FOLDER STRUCTURE

```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout (enhance with new design)
│   ├── page.tsx                      # Main Dashboard (rebuild)
│   ├── agents/                       # NEW: Agent Management
│   │   ├── page.tsx                  # Agent list view
│   │   └── [id]/
│   │       └── page.tsx              # Agent detail page
│   ├── workflow/                     # NEW: Workflow Pages
│   │   └── video-creation/
│   │       └── page.tsx              # Video pipeline visualization
│   ├── queue/                        # EXISTING: Keep & enhance styling
│   │   └── page.tsx
│   ├── insights/                     # EXISTING: Keep & enhance styling
│   │   └── page.tsx
│   └── settings/                     # EXISTING: Rebuild with new design
│       └── page.tsx
│
├── components/
│   ├── layout/                       # NEW: Layout Components
│   │   ├── Sidebar.tsx               # Left navigation sidebar
│   │   ├── Header.tsx                # Top header with search/notifications
│   │   └── MainLayout.tsx            # Wrapper component
│   │
│   ├── dashboard/                    # NEW: Dashboard Components
│   │   ├── StatsCard.tsx             # Metric card with trends
│   │   ├── AgentActivityPanel.tsx    # Live agent activity
│   │   ├── PerformanceMetrics.tsx    # 24h performance metrics
│   │   └── RecentActivityFeed.tsx    # Activity timeline
│   │
│   ├── agents/                       # NEW: Agent Components
│   │   ├── AgentCard.tsx             # Individual agent card
│   │   ├── AgentStatusBadge.tsx      # Status indicator
│   │   ├── AgentProgressBar.tsx      # Progress visualization
│   │   └── AgentLogViewer.tsx        # Log display modal
│   │
│   ├── workflow/                     # NEW: Workflow Components
│   │   ├── PipelineStage.tsx         # Pipeline stage card
│   │   ├── PipelineOverview.tsx      # Visual flow diagram
│   │   └── StageProgressBar.tsx      # Stage progress indicator
│   │
│   ├── settings/                     # NEW: Settings Components
│   │   ├── ApiKeyInput.tsx           # API key field with show/hide
│   │   ├── ApiKeyCard.tsx            # API key section card
│   │   └── SettingsSection.tsx       # Settings section wrapper
│   │
│   └── ui/                           # ShadCN UI Components
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       ├── dialog.tsx
│       ├── tabs.tsx
│       └── ... (other ShadCN components)
│
├── lib/
│   ├── api/                          # NEW: API Layer
│   │   ├── client.ts                 # Base API client
│   │   ├── agents.ts                 # Agent API calls
│   │   ├── workflow.ts               # Workflow API calls
│   │   ├── stats.ts                  # Stats API calls
│   │   └── mock.ts                   # Mock data generator
│   │
│   ├── hooks/                        # NEW: Custom Hooks
│   │   ├── useAgents.ts              # Fetch & manage agents
│   │   ├── useWorkflow.ts            # Workflow state
│   │   ├── useStats.ts               # Dashboard stats
│   │   └── usePolling.ts             # Polling for real-time updates
│   │
│   ├── types/                        # NEW: TypeScript Types
│   │   ├── agent.ts                  # Agent types
│   │   ├── workflow.ts               # Workflow types
│   │   ├── post.ts                   # Post/content types
│   │   └── api.ts                    # API response types
│   │
│   └── utils/                        # Utilities
│       ├── formatters.ts             # Date, number formatters
│       └── constants.ts              # App constants
│
└── styles/
    └── globals.css                   # Tailwind + custom CSS variables
```

---

## 🏗️ IMPLEMENTATION PHASES

## **PHASE 1: Foundation & Layout** (Days 1-2)

### Goal
Set up professional layout structure matching Helm HR Ops design reference

### Tasks

#### 1.1 Create Base Layout Components

**[components/layout/Sidebar.tsx](../frontend/components/layout/Sidebar.tsx)**
```tsx
// Left navigation sidebar
// Features:
// - Logo at top
// - Navigation items (Dashboard, Agents, Workflow, Queue, Insights, Settings)
// - Icon + label for each item
// - Active state highlighting
// - Collapse/expand (future)
```

**[components/layout/Header.tsx](../frontend/components/layout/Header.tsx)**
```tsx
// Top header bar
// Features:
// - Search input (placeholder for now)
// - Notification bell icon
// - User menu dropdown
```

**[components/layout/MainLayout.tsx](../frontend/components/layout/MainLayout.tsx)**
```tsx
// Wrapper component
// Layout: Sidebar (left) + Main Content Area (right)
// Responsive: Collapsible sidebar on mobile
```

#### 1.2 Set Up Design System

**[styles/globals.css](../frontend/styles/globals.css)**
- Add CSS variables for color palette (see Design System section above)
- Configure Tailwind theme extensions
- Add typography scale
- Define spacing, shadows, borders

#### 1.3 Install & Configure ShadCN UI

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add badge button card progress dialog tabs input label
```

#### 1.4 Create TypeScript Types

**[lib/types/agent.ts](../frontend/lib/types/agent.ts)**
```typescript
export type AgentStatus = 'active' | 'idle' | 'processing' | 'error' | 'paused';

export interface Agent {
  id: string;
  name: string;
  type: 'news_ingestion' | 'ranking' | 'script_generator' |
        'video_production' | 'tts' | 'publishing';
  status: AgentStatus;
  uptime: number;           // seconds
  lastRun: Date | null;
  currentTask: string | null;
  progress: number | null;  // 0-100
  config: AgentConfig;
  stats: AgentStats;
  recentActivity: AgentActivity[];
}

export interface AgentConfig {
  model?: string;
  timeout?: number;
  retries?: number;
  autoRestart?: boolean;
}

export interface AgentStats {
  totalRuns: number;
  successRate: number;
  avgDuration: number;
  totalCost: number;
  lastError?: string;
}

export interface AgentActivity {
  id: string;
  timestamp: Date;
  action: string;
  status: 'success' | 'error' | 'warning';
  details?: string;
}
```

**[lib/types/workflow.ts](../frontend/lib/types/workflow.ts)**
```typescript
export type PipelineStageStatus = 'completed' | 'active' | 'waiting' | 'error';

export interface PipelineStage {
  id: string;
  name: string;
  order: number;
  status: PipelineStageStatus;
  agentType: Agent['type'];
  progress: number | null;
  queueCount: number;
  lastRun: Date | null;
  nextRun: Date | null;
  currentItem: string | null;
  stats: Record<string, any>;
}
```

**[lib/types/stats.ts](../frontend/lib/types/stats.ts)**
```typescript
export interface DashboardStats {
  agents: {
    active: number;
    idle: number;
    error: number;
  };
  news: {
    fetched: number;
    ranked: number;
    pending: number;
  };
  videos: {
    ready: number;
    processing: number;
    failed: number;
  };
  queue: {
    pending: number;
    approved: number;
    failed: number;
  };
}

export interface Activity {
  id: string;
  type: 'video_published' | 'ranking_failed' | 'script_approved' |
        'video_started' | 'agent_error';
  title: string;
  timestamp: Date;
  status: 'success' | 'warning' | 'error';
  link?: string;
}
```

#### 1.5 Update Root Layout

**[app/layout.tsx](../frontend/app/layout.tsx)**
- Use new MainLayout component
- Remove old layout structure
- Apply new design system

### Deliverable
✅ Professional layout shell with sidebar navigation ready for content

---

## **PHASE 2: Main Dashboard Rebuild** (Days 3-4)

### Goal
Transform main dashboard to show system overview with agent activity monitoring

### Tasks

#### 2.1 Create Mock API Layer

**[lib/api/client.ts](../frontend/lib/api/client.ts)**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private useMock = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

  async get<T>(endpoint: string): Promise<T> {
    if (this.useMock) {
      return this.getMockData(endpoint);
    }
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return response.json();
  }

  private async getMockData<T>(endpoint: string): Promise<T> {
    const { getMockResponse } = await import('./mock');
    return getMockResponse(endpoint);
  }
}

export const apiClient = new ApiClient();
```

**[lib/api/mock.ts](../frontend/lib/api/mock.ts)**
```typescript
// Mock data generator
// Returns realistic data for:
// - /api/stats/dashboard
// - /api/agents
// - /api/workflow/pipeline
// - /api/activity/recent
```

**[lib/api/stats.ts](../frontend/lib/api/stats.ts)**
```typescript
import { apiClient } from './client';
import type { DashboardStats, Activity } from '@/lib/types/stats';

export const statsApi = {
  async getDashboardStats(): Promise<DashboardStats> {
    return apiClient.get('/api/stats/dashboard');
  },

  async getRecentActivity(limit = 10): Promise<Activity[]> {
    return apiClient.get(`/api/activity/recent?limit=${limit}`);
  },
};
```

#### 2.2 Build Dashboard Components

**[components/dashboard/StatsCard.tsx](../frontend/components/dashboard/StatsCard.tsx)**
```tsx
interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

// Design:
// - Card container with hover effect
// - Icon in top-right corner
// - Large value text
// - Subtitle below value
// - Trend indicator at bottom (arrow + percentage + label)
```

**[components/dashboard/AgentActivityPanel.tsx](../frontend/components/dashboard/AgentActivityPanel.tsx)**
```tsx
// Real-time list of agent statuses
// Shows:
// - Agent name
// - Status badge (🟢 Active, 🔵 Processing, ⚪ Idle, 🔴 Error)
// - Current task
// - Timestamp
// - Progress bar (if applicable)

// Updates every 5 seconds via polling
```

**[components/dashboard/PerformanceMetrics.tsx](../frontend/components/dashboard/PerformanceMetrics.tsx)**
```tsx
// 3 metric cards showing 24h performance:
// 1. News Processed (342 articles, +12% vs prev)
// 2. Videos Created (28 videos, +8% vs prev)
// 3. Publish Rate (92% success, -3% vs prev)
```

**[components/dashboard/RecentActivityFeed.tsx](../frontend/components/dashboard/RecentActivityFeed.tsx)**
```tsx
// Timeline of recent events
// Shows:
// - Activity type icon
// - Activity title
// - Relative timestamp ("2 min ago")
// - Status badge
// - Click to view details (if link provided)
```

#### 2.3 Rebuild Dashboard Page

**[app/page.tsx](../frontend/app/page.tsx)**
```tsx
// Layout:
// 1. Page title "Dashboard"
// 2. 4x StatsCard grid (Agents, News, Videos, Queue)
// 3. AgentActivityPanel (full width)
// 4. PerformanceMetrics (3 columns)
// 5. RecentActivityFeed (full width)

// Use custom hook for data fetching:
// - useStats() - fetches dashboard stats
// - usePolling() - refetches every 5 seconds
```

#### 2.4 Create Custom Hooks

**[lib/hooks/useStats.ts](../frontend/lib/hooks/useStats.ts)**
```typescript
export function useStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await statsApi.getDashboardStats();
        setStats(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  return { stats, loading, error };
}
```

**[lib/hooks/usePolling.ts](../frontend/lib/hooks/usePolling.ts)**
```typescript
export function usePolling(callback: () => void, interval = 5000) {
  useEffect(() => {
    const id = setInterval(callback, interval);
    return () => clearInterval(id);
  }, [callback, interval]);
}
```

### Deliverable
✅ Fully functional main dashboard with live data (mock) and real-time updates

---

## **PHASE 3: Agent Management** (Days 5-7)

### Goal
Build comprehensive agent monitoring and control interface

### Tasks

#### 3.1 Create Agent API Layer

**[lib/api/agents.ts](../frontend/lib/api/agents.ts)**
```typescript
import { apiClient } from './client';
import type { Agent, AgentActivity } from '@/lib/types/agent';

export const agentsApi = {
  async getAll(): Promise<Agent[]> {
    return apiClient.get('/api/agents');
  },

  async getById(id: string): Promise<Agent> {
    return apiClient.get(`/api/agents/${id}`);
  },

  async pause(id: string): Promise<void> {
    return apiClient.post(`/api/agents/${id}/pause`, {});
  },

  async restart(id: string): Promise<void> {
    return apiClient.post(`/api/agents/${id}/restart`, {});
  },

  async getLogs(id: string, limit = 50): Promise<AgentActivity[]> {
    return apiClient.get(`/api/agents/${id}/logs?limit=${limit}`);
  },
};
```

#### 3.2 Build Agent Components

**[components/agents/AgentCard.tsx](../frontend/components/agents/AgentCard.tsx)**
```tsx
interface AgentCardProps {
  agent: Agent;
  onPause: (id: string) => void;
  onRestart: (id: string) => void;
  onViewLogs: (id: string) => void;
}

// Design:
// - Card with agent name and type
// - Status badge in top-left
// - Uptime and last run info
// - Current task (if any)
// - Progress bar (if applicable)
// - Recent activity (last 3 actions)
// - Action buttons: Pause, Restart, View Logs
```

**[components/agents/AgentStatusBadge.tsx](../frontend/components/agents/AgentStatusBadge.tsx)**
```tsx
interface AgentStatusBadgeProps {
  status: AgentStatus;
  size?: 'sm' | 'md' | 'lg';
}

// Status colors:
// - active: green
// - processing: blue
// - queued: amber
// - idle: gray
// - error: red
// - paused: gray with strikethrough
```

**[components/agents/AgentProgressBar.tsx](../frontend/components/agents/AgentProgressBar.tsx)**
```tsx
interface AgentProgressBarProps {
  progress: number;        // 0-100
  label?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

// Uses ShadCN Progress component
// Shows percentage label
// Animated progress fill
```

**[components/agents/AgentLogViewer.tsx](../frontend/components/agents/AgentLogViewer.tsx)**
```tsx
interface AgentLogViewerProps {
  agentId: string;
  isOpen: boolean;
  onClose: () => void;
}

// Modal/dialog showing agent logs
// Features:
// - Timestamp + action + status for each log entry
// - Color-coded by status (success/warning/error)
// - Auto-scroll to bottom
// - Refresh button
// - Filter by log level (future)
```

#### 3.3 Build Agent List Page

**[app/agents/page.tsx](../frontend/app/agents/page.tsx)**
```tsx
// Layout:
// 1. Page title "Agent Management"
// 2. Filter tabs: [All] [Active] [Idle] [Error]
// 3. Grid of AgentCard components (2 columns on desktop, 1 on mobile)
// 4. Empty state if no agents

// Features:
// - Filter agents by status
// - Search by agent name (future)
// - Refresh button
// - Real-time updates via polling
```

#### 3.4 Build Agent Detail Page

**[app/agents/[id]/page.tsx](../frontend/app/agents/[id]/page.tsx)**
```tsx
// Layout:
// 1. Back button + Agent name
// 2. Large status badge
// 3. Stats cards: Total Runs, Success Rate, Avg Duration, Total Cost
// 4. Current task section (if active)
// 5. Configuration panel (model, timeout, retries, auto-restart)
// 6. Full activity log (paginated)
// 7. Action buttons: Pause/Resume, Restart, Test Connection

// Features:
// - Edit configuration inline
// - Save changes
// - View full log history
// - Export logs (future)
```

#### 3.5 Create Agent Hook

**[lib/hooks/useAgents.ts](../frontend/lib/hooks/useAgents.ts)**
```typescript
export function useAgents(filter?: AgentStatus) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAgents() {
      const data = await agentsApi.getAll();
      const filtered = filter
        ? data.filter(a => a.status === filter)
        : data;
      setAgents(filtered);
      setLoading(false);
    }
    fetchAgents();
  }, [filter]);

  const pauseAgent = async (id: string) => {
    await agentsApi.pause(id);
    // Refetch agents
  };

  const restartAgent = async (id: string) => {
    await agentsApi.restart(id);
    // Refetch agents
  };

  return { agents, loading, pauseAgent, restartAgent };
}
```

### Deliverable
✅ Complete agent monitoring and control system (list view + detail view)

---

## **PHASE 4: Video Pipeline Visualization** (Days 8-9)

### Goal
Build interactive pipeline showing News → Ranking → Script → Review → Video

### Tasks

#### 4.1 Create Workflow API Layer

**[lib/api/workflow.ts](../frontend/lib/api/workflow.ts)**
```typescript
import { apiClient } from './client';
import type { PipelineStage } from '@/lib/types/workflow';

export const workflowApi = {
  async getPipeline(): Promise<PipelineStage[]> {
    return apiClient.get('/api/workflow/pipeline');
  },
};
```

#### 4.2 Build Workflow Components

**[components/workflow/PipelineOverview.tsx](../frontend/components/workflow/PipelineOverview.tsx)**
```tsx
// Visual flow diagram showing 5 stages:
// News Ingestion → Ranking → Script Gen → Review → Video Gen
//      ✅             ✅         🔵          ⏸️         ⏳
//   (45 done)     (33 done)  (12 active) (8 waiting) (queue)

// Each stage shows:
// - Status icon
// - Stage name
// - Count of items
```

**[components/workflow/PipelineStage.tsx](../frontend/components/workflow/PipelineStage.tsx)**
```tsx
interface PipelineStageProps {
  stage: PipelineStage;
  isExpanded: boolean;
  onToggle: () => void;
}

// Expandable card for each pipeline stage
// Header (always visible):
// - Status icon
// - Stage name
// - Last run / Next run
// - Queue count badge
// - Expand/collapse chevron

// Expanded content:
// - Current item being processed
// - Progress bar
// - Stats (articles fetched, duplicates removed, etc.)
// - Top items (for ranking stage: top 3 scores)
// - Actions (View Queue, Configure, etc.)
```

**[components/workflow/StageProgressBar.tsx](../frontend/components/workflow/StageProgressBar.tsx)**
```tsx
// Progress bar for stage
// Shows: X/Y complete (Z%)
// Color-coded by stage status
```

#### 4.3 Build Video Creation Page

**[app/workflow/video-creation/page.tsx](../frontend/app/workflow/video-creation/page.tsx)**
```tsx
// Layout:
// 1. Page title "Video Creation Pipeline"
// 2. Tabs: [Overview] [Active Jobs] [History]
// 3. PipelineOverview component (visual flow)
// 4. List of PipelineStage components (5 stages)

// Features:
// - Real-time updates via polling
// - Click stage to expand/collapse
// - View queue for each stage
// - Manual trigger buttons (future)
```

#### 4.4 Create Workflow Hook

**[lib/hooks/useWorkflow.ts](../frontend/lib/hooks/useWorkflow.ts)**
```typescript
export function useWorkflow() {
  const [pipeline, setPipeline] = useState<PipelineStage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPipeline() {
      const data = await workflowApi.getPipeline();
      setPipeline(data);
      setLoading(false);
    }
    fetchPipeline();
  }, []);

  return { pipeline, loading };
}
```

### Deliverable
✅ Interactive pipeline visualization showing real-time status of all stages

---

## **PHASE 5: Settings Enhancement** (Day 10)

### Goal
Professional settings interface for API keys and configuration

### Tasks

#### 5.1 Build Settings Components

**[components/settings/ApiKeyInput.tsx](../frontend/components/settings/ApiKeyInput.tsx)**
```tsx
interface ApiKeyInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  status?: 'connected' | 'error' | 'unknown';
  usage?: string;
  onTest?: () => Promise<void>;
}

// Design:
// - Label (e.g., "OpenAI API Key")
// - Input field with show/hide toggle
// - Test button
// - Status indicator (✅ Connected, ⚠️ Warning, ❌ Error)
// - Usage info (e.g., "45/100 calls today")
```

**[components/settings/ApiKeyCard.tsx](../frontend/components/settings/ApiKeyCard.tsx)**
```tsx
// Card wrapper for API key section
// Groups related keys (e.g., "AI Generation", "Media Assets", "Publishing")
```

**[components/settings/SettingsSection.tsx](../frontend/components/settings/SettingsSection.tsx)**
```tsx
// Section wrapper with title and description
// Used for grouping related settings
```

#### 5.2 Rebuild Settings Page

**[app/settings/page.tsx](../frontend/app/settings/page.tsx)**
```tsx
// Layout:
// 1. Page title "Settings"
// 2. Tab navigation: [API Keys] [Agents] [Publishing] [Advanced]
// 3. Tab content area

// API Keys Tab:
// - OpenAI API Key (with test, status)
// - Google Gemini API Key (with test, status, usage)
// - ElevenLabs API Key (with test, status, balance warning)
// - Pexels API Key (with test, status, rate limit)
// - NewsAPI Key (with test, status)
// - [+ Add API Key] button

// Agents Tab:
// - Default model selection (Gemini Flash, Gemini Pro, GPT-4o-mini)
// - Default timeout (90s)
// - Default retries (3)
// - Auto-restart toggle

// Publishing Tab:
// - Publishing provider (Publer, Buffer, Native)
// - Platform credentials (TikTok, Instagram, YouTube, etc.)
// - Default posting schedule

// Advanced Tab:
// - Database path (read-only)
// - Log level (Debug, Info, Warning, Error)
// - Debug mode toggle
// - Clear cache button

// Features:
// - Save changes button (bottom right)
// - Unsaved changes warning
// - Test all connections button
```

### Deliverable
✅ Complete settings management interface with API key testing

---

## **PHASE 6: Polish & Responsive** (Days 11-12)

### Goal
Ensure production-ready quality, responsive design, and error handling

### Tasks

#### 6.1 Responsive Design
- Mobile-friendly layouts for all pages
- Collapsible sidebar on mobile (hamburger menu)
- Stack cards vertically on small screens
- Touch-friendly buttons and controls
- Test on iPhone, iPad, Android

#### 6.2 Loading States
- Skeleton loaders for cards while data loads
- Spinner animations for actions (pause, restart, test)
- Progressive loading (show partial data while rest loads)
- Disable buttons during async operations

#### 6.3 Error Handling
- Error boundaries for component crashes
- User-friendly error messages
- Retry buttons for failed API calls
- Fallback UI for missing data
- 404 page for invalid routes

#### 6.4 Notifications System
- Toast notifications for actions (success/error)
  - "Agent paused successfully"
  - "API key test failed"
  - "Settings saved"
- Auto-dismiss after 3-5 seconds
- Action undo buttons (for destructive actions)

#### 6.5 Performance Optimization
- Code splitting (lazy load heavy components)
- Memoize expensive renders (React.memo)
- Debounce search inputs
- Virtualize long lists (if needed)
- Optimize images

#### 6.6 Accessibility
- Keyboard navigation (Tab, Enter, Esc)
- ARIA labels for icons and buttons
- Focus indicators
- Color contrast compliance (WCAG 2.1 AA)
- Screen reader support

#### 6.7 Final Polish
- Smooth transitions and animations
- Hover effects on interactive elements
- Empty states with helpful messages
- Favicon and meta tags
- Loading spinner for page transitions

### Deliverable
✅ Production-ready dashboard MVP with responsive design and error handling

---

## 🔌 BACKEND INTEGRATION STRATEGY

### Current Approach: Frontend-Only with Mock Data

**Environment Variable:**
```bash
# frontend/.env.local
NEXT_PUBLIC_USE_MOCK=true
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**How It Works:**
1. API client checks `NEXT_PUBLIC_USE_MOCK` flag
2. If `true`, returns mock data from `lib/api/mock.ts`
3. If `false`, calls real backend at `NEXT_PUBLIC_API_URL`

### Future: Real Backend Integration

**When backend is stable:**
1. Update environment variable: `NEXT_PUBLIC_USE_MOCK=false`
2. Ensure backend endpoints match API layer:
   - `GET /api/stats/dashboard`
   - `GET /api/agents`
   - `GET /api/agents/{id}`
   - `POST /api/agents/{id}/pause`
   - `POST /api/agents/{id}/restart`
   - `GET /api/agents/{id}/logs`
   - `GET /api/workflow/pipeline`
   - `GET /api/activity/recent`
3. Test real API calls
4. Adjust mock data if response format differs
5. Deploy!

**Backend Endpoints to Build:**
- Dashboard stats (aggregate counts from database)
- Agent status (if agents expose status endpoints)
- Activity feed (from logs or database events)
- Pipeline status (aggregate workflow stage counts)

---

## 📊 COMPONENT SPECIFICATIONS

### StatsCard Component

**File:** [components/dashboard/StatsCard.tsx](../frontend/components/dashboard/StatsCard.tsx)

**Props:**
```typescript
interface StatsCardProps {
  title: string;           // "Active Agents"
  value: string | number;  // "8" or "23"
  subtitle?: string;       // "2 idle"
  trend?: {
    value: number;         // +12
    direction: 'up' | 'down' | 'neutral';
    label: string;         // "vs previous week"
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error';
}
```

**Design:**
- Card with padding `p-6`
- Hover effect: `hover:shadow-lg transition-shadow`
- Icon in top-right corner (3xl size, primary color)
- Title: `text-sm text-gray-500`
- Value: `text-3xl font-bold mt-2`
- Subtitle: `text-sm text-gray-400 mt-1`
- Trend (if provided):
  - Arrow icon (↑ green, ↓ red, → gray)
  - Percentage: `text-sm font-medium` (color-coded)
  - Label: `text-xs text-gray-400`

**Example Usage:**
```tsx
<StatsCard
  title="Active Agents"
  value={8}
  subtitle="2 idle"
  trend={{ value: 12, direction: 'up', label: 'vs last week' }}
  icon={<RobotIcon />}
  variant="success"
/>
```

---

### AgentCard Component

**File:** [components/agents/AgentCard.tsx](../frontend/components/agents/AgentCard.tsx)

**Props:**
```typescript
interface AgentCardProps {
  agent: Agent;
  onPause: (id: string) => void;
  onRestart: (id: string) => void;
  onViewLogs: (id: string) => void;
}
```

**Design:**
- Card container `p-6`
- Header section:
  - Status badge (left)
  - Agent name (center, `text-lg font-semibold`)
  - Action icons (right: Logs 📊, Settings ⚙️)
- Info row: `text-sm text-gray-500`
  - Uptime: "14h 23m"
  - Last run: "2 min ago"
- Current task section (if active):
  - Label: "Current Task:"
  - Task description: `text-sm text-gray-600`
  - Progress bar (if progress available)
- Recent activity:
  - Label: "Recent Activity:"
  - List of last 3 actions
  - Bullet points: "• Fetched 45 articles from NewsAPI"
- Action buttons (bottom):
  - Pause button (outline)
  - Restart button (outline)

**Example Usage:**
```tsx
<AgentCard
  agent={newsIngestionAgent}
  onPause={(id) => handlePause(id)}
  onRestart={(id) => handleRestart(id)}
  onViewLogs={(id) => setSelectedAgent(id)}
/>
```

---

### PipelineStage Component

**File:** [components/workflow/PipelineStage.tsx](../frontend/components/workflow/PipelineStage.tsx)

**Props:**
```typescript
interface PipelineStageProps {
  stage: PipelineStage;
  isExpanded: boolean;
  onToggle: () => void;
}
```

**Design:**
- Card container `p-6`
- Header (always visible, clickable):
  - Status icon (left, 2xl size, color-coded)
  - Stage name + info (center)
    - Name: `text-lg font-semibold`
    - Info: `text-sm text-gray-500` ("Last run: 2 min ago • Next: 11:28 AM")
  - Queue badge + chevron (right)
    - Badge: "X in queue"
    - Chevron: rotate based on `isExpanded`
- Expanded content (if `isExpanded`):
  - Current item section
  - Progress bar with percentage
  - Stats grid (3 columns)
  - Top items (for ranking: top 3 scores)

**Example Usage:**
```tsx
<PipelineStage
  stage={newsIngestionStage}
  isExpanded={expandedStages.includes('news_ingestion')}
  onToggle={() => toggleStage('news_ingestion')}
/>
```

---

## ❓ QUESTIONS & ANSWERS

### 1. Workflow Builder - Phase 1 or Phase 2?
**Answer:** **Defer to Phase 2** (after core monitoring works)

**Reasoning:**
- Not critical for MVP
- Main Dashboard, Agent Panel, and Video Pipeline are more important
- Workflow Builder is complex (drag-and-drop, visual editor)
- Better to validate core functionality first

---

### 2. Real-time Updates - WebSocket or Polling?
**Answer:** **Use polling (every 5-10 seconds) for MVP**

**Reasoning:**
- Simpler to implement (no WebSocket server needed)
- Works with mock data strategy
- Backend doesn't have WebSocket setup yet
- Can upgrade to WebSocket later when backend is stable
- 5-10 second updates are acceptable for agent monitoring

**Implementation:**
```typescript
// lib/hooks/usePolling.ts
export function usePolling(callback: () => void, interval = 5000) {
  useEffect(() => {
    const id = setInterval(callback, interval);
    return () => clearInterval(id);
  }, [callback, interval]);
}

// Usage in dashboard:
const { stats, refetch } = useStats();
usePolling(refetch, 5000); // Refetch every 5 seconds
```

---

### 3. Authentication - Add now or later?
**Answer:** **Defer authentication** - focus on dashboard functionality

**Reasoning:**
- Not in priority list
- Adds complexity to MVP
- Building for yourself initially (no multi-user need)
- Can add later when deploying for production
- For now, assume authenticated user

---

### 4. Backend APIs - Build as you go or mock first?
**Answer:** **Build frontend with mock data first, integrate backend later**

**Reasoning:**
- Backend is not stable/ready yet
- Matches "frontend-only MVP" requirement
- Can focus on UI/UX without backend blockers
- Clean API layer makes swapping easy later
- Backend can be developed separately (using Codex)

**Strategy:**
1. Build all frontend components with mock data
2. Test UI/UX thoroughly
3. When backend is stable:
   - Update `NEXT_PUBLIC_USE_MOCK=false`
   - Test real API integration
   - Fix any response format differences

---

### 5. Existing Pages - Keep or Rebuild?
**Answer:** **Keep existing pages, update styling to match new design system**

**Reasoning:**
- Queue page is already functional
- Don't waste time rebuilding working features
- Just apply new design tokens (colors, typography, components)
- Focus on net-new pages (Agents, Workflow)

**Approach:**
- Update [app/queue/page.tsx](../frontend/app/queue/page.tsx):
  - Use new StatsCard component (instead of old one)
  - Apply new color palette
  - Use ShadCN UI components
  - Keep existing functionality
- Same for [app/insights/page.tsx](../frontend/app/insights/page.tsx)

---

### 6. Timeline - Phased reviews or build all together?
**Answer:** **Phased reviews after each phase** (strongly recommended)

**Reasoning:**
- Better to checkpoint frequently
- Allows course-correction early
- Test each phase before moving forward
- Reduces risk of large rewrites
- Matches "incremental progress" requirement

**Review Checkpoints:**
- After Phase 1: Review layout and design system
- After Phase 2: Review main dashboard functionality
- After Phase 3: Review agent management
- After Phase 4: Review pipeline visualization
- After Phase 5: Review settings
- After Phase 6: Final production review

---

## 🚀 FIRST SESSION PROMPT FOR EMERGENT

```
I want to build an AI Agent Dashboard MVP for Xseller.ai based on this implementation plan.

Reference files:
- Architecture: .claude/CLAUDE.md
- Implementation plan: docs/IMPLEMENTATION_PLAN.md (this file)
- Existing frontend: frontend/app/page.tsx (current dashboard)
- Existing backend: backend/app/main.py (FastAPI)

Let's start with PHASE 1: Foundation & Layout (Days 1-2).

Tasks:
1. Create base layout components (Sidebar, Header, MainLayout)
2. Set up design system in styles/globals.css (colors, typography, spacing)
3. Install & configure ShadCN UI components (badge, button, card, progress, dialog, tabs)
4. Create TypeScript types in lib/types/ (agent.ts, workflow.ts, post.ts, stats.ts)
5. Update app/layout.tsx to use new layout structure

Design reference: Helm HR Ops dashboard (clean sidebar, professional layout)

Color palette:
- Primary Blue: #0ea5e9
- Success Green: #22c55e
- Warning Amber: #f59e0b
- Error Red: #ef4444
- Grays: #f9fafb to #111827

Use:
- Next.js 14 + TypeScript
- Tailwind CSS
- ShadCN UI (no heavy UI library)
- Frontend-only with mock data (backend integration later)

Let's start with the Sidebar component. Show me the design and structure first, then we'll build it.
```

---

## 📈 SUCCESS METRICS

After completion, the dashboard will have:

✅ Professional, clean design matching Helm HR Ops reference quality
✅ Real-time agent monitoring and control
✅ Complete pipeline visualization (News → Ranking → Script → Review → Video)
✅ Comprehensive settings management with API key testing
✅ Responsive mobile design
✅ Fast performance (< 3s load time)
✅ Type-safe codebase (TypeScript)
✅ Easy backend integration (clean API layer)
✅ Comprehensive error handling
✅ Accessible UI (WCAG 2.1 AA)

---

## 📝 NEXT STEPS

1. ✅ Review this implementation plan
2. ✅ Confirm approach and answers to questions
3. ✅ Start Phase 1 in Emergent
4. ✅ Review Phase 1 deliverable before proceeding
5. ✅ Continue through phases with checkpoints
6. ✅ Integrate backend when stable
7. ✅ Deploy to production

---

**Last Updated:** 2025-11-17
**Version:** 1.0
**Status:** Ready for implementation
**Owner:** Gurvinder + Emergent AI
