export type AgentStatus = 'active' | 'processing' | 'idle' | 'error' | 'paused';

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: AgentStatus;
  currentTask?: string;
  progress?: number; // 0-100
  lastRun?: Date;
  uptime?: string;
}

export interface AgentTask {
  status: "pending" | "processing" | "completed" | "failed"
  progress: number
  startedAt: string
  completedAt?: string
  error?: string
}