'use client';

import React from 'react';
import { Users, FileText, Video, ListChecks } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { AgentActivityPanel } from '@/components/dashboard/AgentActivityPanel';
import { PerformanceMetrics } from '@/components/dashboard/PerformanceMetrics';
import { RecentActivityFeed } from '@/components/dashboard/RecentActivityFeed';
import {
  mockDashboardStats,
  mockAgents,
  mockPerformance,
  mockActivities
} from '@/lib/api/mock';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Monitor your AI automation system</p>
      </div>

      {/* Stats Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Agents"
          value={mockDashboardStats.agents.total}
          icon={Users}
          color="blue"
          trend={{
            value: 20,
            isPositive: true
          }}
        />
        <StatsCard
          title="News Today"
          value={mockDashboardStats.news.today}
          icon={FileText}
          color="green"
          trend={{
            value: mockDashboardStats.news.trend,
            isPositive: mockDashboardStats.news.trend > 0
          }}
        />
        <StatsCard
          title="Videos Created"
          value={mockDashboardStats.videos.total}
          icon={Video}
          color="purple"
          trend={{
            value: mockDashboardStats.videos.trend,
            isPositive: mockDashboardStats.videos.trend > 0
          }}
        />
        <StatsCard
          title="Queue Items"
          value={mockDashboardStats.queue.items}
          icon={ListChecks}
          color="amber"
        />
      </div>

      {/* Agent Activity Panel */}
      <AgentActivityPanel agents={mockAgents} />

      {/* Performance Metrics */}
      <PerformanceMetrics data={mockPerformance} />

      {/* Recent Activity Feed */}
      <RecentActivityFeed activities={mockActivities} />
    </div>
  );
}
