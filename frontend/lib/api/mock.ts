// Mock data for Phase 2 Dashboard

import { Agent } from '@/lib/types/agent';
import { DashboardStats, PerformanceData, Activity } from '@/lib/types/dashboard';

// Dashboard Statistics
export const mockDashboardStats: DashboardStats = {
    agents: {
        total: 6,
        active: 4,
        idle: 1,
        error: 1
    },
    news: {
        today: 24,
        trend: 12 // +12%
    },
    videos: {
        total: 18,
        pending: 6,
        trend: -3 // -3%
    },
    queue: {
        items: 12,
        processing: 3
    }
};

// Agent Data (6 agents with different statuses)
export const mockAgents: Agent[] = [
    {
        id: '1',
        name: 'News Ingestion Agent',
        type: 'Ingestion',
        status: 'active',
        currentTask: 'Fetching from TechCrunch',
        lastRun: new Date(Date.now() - 2 * 60 * 1000), // 2 mins ago
        uptime: '99.8%'
    },
    {
        id: '2',
        name: 'Viral Ranking Agent',
        type: 'Analysis',
        status: 'processing',
        currentTask: 'Scoring 24 articles',
        progress: 83,
        lastRun: new Date(Date.now() - 5 * 60 * 1000), // 5 mins ago
        uptime: '99.5%'
    },
    {
        id: '3',
        name: 'Script Generator Agent',
        type: 'Content Creation',
        status: 'active',
        currentTask: 'Writing script for "AI Breakthrough"',
        lastRun: new Date(Date.now() - 1 * 60 * 1000), // 1 min ago
        uptime: '99.9%'
    },
    {
        id: '4',
        name: 'Video Production Agent',
        type: 'Media Production',
        status: 'processing',
        currentTask: 'Rendering video #18',
        progress: 45,
        lastRun: new Date(Date.now() - 10 * 60 * 1000), // 10 mins ago
        uptime: '98.7%'
    },
    {
        id: '5',
        name: 'Publishing Agent',
        type: 'Distribution',
        status: 'idle',
        currentTask: undefined,
        lastRun: new Date(Date.now() - 30 * 60 * 1000), // 30 mins ago
        uptime: '99.2%'
    },
    {
        id: '6',
        name: 'Analytics Agent',
        type: 'Monitoring',
        status: 'error',
        currentTask: 'Connection timeout',
        lastRun: new Date(Date.now() - 45 * 60 * 1000), // 45 mins ago
        uptime: '97.3%'
    }
];

// Performance Metrics (24h)
export const mockPerformance: PerformanceData = {
    scriptsGenerated: {
        value: 42,
        trend: 15, // +15% vs yesterday
        previousValue: 36
    },
    qualityScore: {
        value: 8.7,
        trend: 2.4, // +2.4%
        previousValue: 8.5
    },
    successRate: {
        value: 94.2,
        trend: -1.2, // -1.2%
        previousValue: 95.4
    }
};

// Recent Activities (10 items)
export const mockActivities: Activity[] = [
    {
        id: '1',
        type: 'success',
        title: 'News Ingestion Complete',
        description: 'Fetched 24 articles from 4 sources',
        timestamp: new Date(Date.now() - 2 * 60 * 1000), // 2 mins ago
        agent: 'News Ingestion Agent'
    },
    {
        id: '2',
        type: 'info',
        title: 'Script Generated',
        description: 'Created script for "AI Breakthrough in NLP"',
        timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 mins ago
        agent: 'Script Generator Agent',
        link: '/queue'
    },
    {
        id: '3',
        type: 'success',
        title: 'Video Published',
        description: 'Published "Tech Trends 2024" to YouTube',
        timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 mins ago
        agent: 'Publishing Agent',
        link: '/queue'
    },
    {
        id: '4',
        type: 'warning',
        title: 'Low Quality Score',
        description: 'Article "Crypto News" scored below threshold (6.2/10)',
        timestamp: new Date(Date.now() - 20 * 60 * 1000), // 20 mins ago
        agent: 'Viral Ranking Agent'
    },
    {
        id: '5',
        type: 'info',
        title: 'Video Rendering Started',
        description: 'Processing video #18 with AI voiceover',
        timestamp: new Date(Date.now() - 25 * 60 * 1000), // 25 mins ago
        agent: 'Video Production Agent'
    },
    {
        id: '6',
        type: 'success',
        title: 'Batch Processing Complete',
        description: 'Processed 12 articles in 8 minutes',
        timestamp: new Date(Date.now() - 35 * 60 * 1000), // 35 mins ago
        agent: 'Script Generator Agent'
    },
    {
        id: '7',
        type: 'error',
        title: 'Analytics Connection Failed',
        description: 'Unable to connect to analytics API - timeout after 30s',
        timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 mins ago
        agent: 'Analytics Agent'
    },
    {
        id: '8',
        type: 'info',
        title: 'Queue Updated',
        description: 'Added 6 new items to production queue',
        timestamp: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
        agent: 'News Ingestion Agent'
    },
    {
        id: '9',
        type: 'success',
        title: 'High Quality Content Detected',
        description: 'Article "Future of AI" scored 9.4/10',
        timestamp: new Date(Date.now() - 75 * 60 * 1000), // 1h 15m ago
        agent: 'Viral Ranking Agent'
    },
    {
        id: '10',
        type: 'info',
        title: 'System Health Check',
        description: 'All systems operational - 5/6 agents running',
        timestamp: new Date(Date.now() - 90 * 60 * 1000), // 1h 30m ago
        agent: 'System'
    }
];
