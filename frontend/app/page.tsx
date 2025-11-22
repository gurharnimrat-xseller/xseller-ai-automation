'use client';

import React, { useEffect, useState } from 'react';
import { Users, FileText, Video, ListChecks } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { AgentActivityPanel } from '@/components/dashboard/AgentActivityPanel';
import { PerformanceMetrics } from '@/components/dashboard/PerformanceMetrics';
import { RecentActivityFeed } from '@/components/dashboard/RecentActivityFeed';
import { BusinessImpact } from '@/components/dashboard/BusinessImpact';
import { SkeletonStatsCard, SkeletonAgent, SkeletonActivity } from '@/components/ui/Skeleton';
import { apiClient } from '@/lib/api/client';
import { DashboardStats, PerformanceData, Activity } from '@/lib/types/dashboard';
import { Agent } from '@/lib/types/agent';

// Fallback mock data for initial load or errors
import {
  mockDashboardStats,
  mockAgents,
  mockPerformance,
  mockActivities,
  mockBusinessImpact
} from '@/lib/api/mock';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>(mockDashboardStats);
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [performance, setPerformance] = useState<PerformanceData>(mockPerformance);
  const [activities, setActivities] = useState<Activity[]>(mockActivities);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, agentsData, perfData, activitiesData] = await Promise.all([
          apiClient.getStats(),
          apiClient.getAgents(),
          apiClient.getPerformance(),
          apiClient.getActivities(10)
        ]);

        setStats(statsData);
        setAgents(agentsData);
        setPerformance(perfData);
        setActivities(activitiesData);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        // Keep using previous data on error
      } finally {
        setLoading(false);
      }
    }

    // Initial fetch
    fetchData();

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Loading state for initial load only
  if (loading && !lastUpdated) {
    return (
      <div className="space-y-8">
        {/* Page Header Skeleton */}
        <div className="mb-2">
          <div className="h-9 w-48 bg-gray-200 rounded animate-pulse mb-2" />
          <div className="h-5 w-64 bg-gray-200 rounded animate-pulse" />
        </div>

        {/* Stats Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SkeletonStatsCard />
          <SkeletonStatsCard />
          <SkeletonStatsCard />
          <SkeletonStatsCard />
        </div>

        {/* Agent Panel Skeleton */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="h-6 w-32 bg-gray-200 rounded animate-pulse mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SkeletonAgent />
            <SkeletonAgent />
            <SkeletonAgent />
            <SkeletonAgent />
          </div>
        </div>

        {/* Activity Feed Skeleton */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="h-6 w-40 bg-gray-200 rounded animate-pulse mb-4" />
          <div className="space-y-4">
            <SkeletonActivity />
            <SkeletonActivity />
            <SkeletonActivity />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="mb-2 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor your AI automation system</p>
        </div>
        {lastUpdated && (
          <div className="text-xs text-gray-400">
            Last updated: {lastUpdated.toLocaleTimeString()}
            {error && <span className="ml-2 text-amber-500">(using cached data)</span>}
          </div>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-amber-800 text-sm">
          <span className="font-medium">Connection issue:</span> {error}. Showing cached data.
        </div>
      )}

      {/* Stats Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Active Agents"
          value={stats.agents.active}
          subtitle="Est. $18k/mo saved"
          icon={Users}
          color="blue"
          trend={{
            value: stats.agents.error > 0 ? -stats.agents.error : 8.3,
            isPositive: stats.agents.error === 0
          }}
          chartData={stats.agents.chartData}
        />
        <StatsCard
          title="Potential Reach"
          value="2.4M views"
          subtitle={`${stats.news.today} articles today`}
          icon={FileText}
          color="green"
          trend={{
            value: stats.news.trend,
            isPositive: stats.news.trend > 0
          }}
          chartData={stats.news.chartData}
        />
        <StatsCard
          title="Content Value"
          value={`$${(stats.videos.total * 200).toLocaleString()}`}
          subtitle={`${stats.videos.total} videos created`}
          icon={Video}
          color="purple"
          trend={{
            value: Math.abs(stats.videos.trend),
            isPositive: stats.videos.trend > 0
          }}
          chartData={stats.videos.chartData}
        />
        <StatsCard
          title="In Pipeline"
          value={`$${(stats.queue.items * 200).toLocaleString()}`}
          subtitle={`${stats.queue.items} items queued`}
          icon={ListChecks}
          color="amber"
          chartData={stats.queue.chartData}
        />
      </div>

      {/* Agent Activity Panel */}
      <AgentActivityPanel agents={agents} />

      {/* Business Impact */}
      <BusinessImpact data={mockBusinessImpact} />

      {/* Performance Metrics */}
      <PerformanceMetrics data={performance} />

      {/* Recent Activity Feed */}
      <RecentActivityFeed activities={activities} />
    </div>
  );
}
