'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
    ArrowLeft,
    Activity,
    Zap,
    DollarSign,
    TrendingUp,
    Clock,
    CheckCircle,
    XCircle,
    Brain,
    MessageSquare
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';
import { mockAgents, mockAgentLogs, mockAgentDecisions, mockPromptResponses, mockAgentMetrics } from '@/lib/api/mock';

const logLevelConfig = {
    info: { color: 'text-blue-600', bg: 'bg-blue-50', badge: 'info' },
    warning: { color: 'text-amber-600', bg: 'bg-amber-50', badge: 'warning' },
    error: { color: 'text-red-600', bg: 'bg-red-50', badge: 'destructive' },
    debug: { color: 'text-gray-600', bg: 'bg-gray-50', badge: 'secondary' }
};

function formatTimeAgo(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

export default function AgentDetailPage() {
    const params = useParams();
    const agentId = params.id as string;

    const agent = mockAgents.find(a => a.id === agentId);
    const logs = mockAgentLogs[agentId] || [];
    const decisions = mockAgentDecisions[agentId] || [];
    const prompts = mockPromptResponses[agentId] || [];
    const metrics = mockAgentMetrics[agentId] || {
        callsPerHour: 0,
        avgLatency: 0,
        errorRate: 0,
        tokenUsage: { input: 0, output: 0, total: 0 },
        totalCost: 0,
        successRate: 100,
        latencyHistory: []
    };

    const [activeTab, setActiveTab] = useState<'logs' | 'decisions' | 'prompts'>('logs');

    if (!agent) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Agent Not Found</h2>
                    <p className="text-gray-600 mb-4">The agent you&apos;re looking for doesn&apos;t exist.</p>
                    <Link href="/agents" className="text-blue-600 hover:text-blue-700 font-medium">
                        ← Back to Agents
                    </Link>
                </div>
            </div>
        );
    }

    // Calculate health color
    const health = metrics.successRate;
    const healthColor = health >= 95 ? 'green' : health >= 90 ? 'amber' : 'red';

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <Link href="/" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Dashboard
                </Link>
                <div className="flex items-start justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{agent.name}</h1>
                        <p className="text-gray-600 mt-1">{agent.type}</p>
                    </div>
                    <Badge variant={agent.status === 'active' ? 'success' : agent.status === 'error' ? 'destructive' : 'secondary'}>
                        {agent.status}
                    </Badge>
                </div>
            </div>

            {/* Live Metrics Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-600">Calls/Hour</div>
                            <Activity className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">{metrics.callsPerHour}</div>
                        <div className="text-xs text-gray-500 mt-1">Last hour</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-600">Avg Latency</div>
                            <Zap className="w-4 h-4 text-amber-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">{metrics.avgLatency}ms</div>
                        <div className="text-xs text-gray-500 mt-1">Response time</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-600">Success Rate</div>
                            <TrendingUp className={`w-4 h-4 text-${healthColor}-600`} />
                        </div>
                        <div className={`text-2xl font-bold text-${healthColor}-600`}>{metrics.successRate}%</div>
                        <div className="text-xs text-gray-500 mt-1">{agent.uptime} uptime</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-gray-600">Total Cost</div>
                            <DollarSign className="w-4 h-4 text-green-600" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900">${metrics.totalCost.toFixed(2)}</div>
                        <div className="text-xs text-gray-500 mt-1">{metrics.tokenUsage.total.toLocaleString()} tokens</div>
                    </CardContent>
                </Card>
            </div>

            {/* Performance Graph */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">API Latency (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-48 flex items-end gap-1">
                        {metrics.latencyHistory.map((point, i) => {
                            const maxLatency = Math.max(...metrics.latencyHistory.map(p => p.value));
                            const height = (point.value / maxLatency) * 100;
                            return (
                                <div
                                    key={i}
                                    className="flex-1 bg-blue-500 rounded-t hover:bg-blue-600 transition-colors cursor-pointer"
                                    style={{ height: `${height}%` }}
                                    title={`${point.value.toFixed(0)}ms at ${point.timestamp.toLocaleTimeString()}`}
                                />
                            );
                        })}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                        <span>24h ago</span>
                        <span>Now</span>
                    </div>
                </CardContent>
            </Card>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-200">
                {(['logs', 'decisions', 'prompts'] as const).map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                            "px-4 py-2 font-medium text-sm border-b-2 transition-colors capitalize",
                            activeTab === tab
                                ? "border-blue-600 text-blue-600"
                                : "border-transparent text-gray-600 hover:text-gray-900"
                        )}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Activity Log */}
            {activeTab === 'logs' && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Clock className="w-5 h-5" />
                            Live Activity Log
                            <span className="text-sm font-normal text-gray-500">(Last 50 events)</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3 max-h-[600px] overflow-y-auto">
                            {logs.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    No logs available for this agent
                                </div>
                            ) : (
                                logs.map(log => {
                                    const config = logLevelConfig[log.level];
                                    return (
                                        <div key={log.id} className={cn("p-3 rounded-lg border", config.bg)}>
                                            <div className="flex items-start justify-between mb-1">
                                                <div className="flex items-center gap-2">
                                                    <Badge variant={config.badge as any} className="text-xs">
                                                        {log.level.toUpperCase()}
                                                    </Badge>
                                                    <span className={cn("font-medium", config.color)}>{log.message}</span>
                                                </div>
                                                <span className="text-xs text-gray-500" suppressHydrationWarning>
                                                    {formatTimeAgo(log.timestamp)}
                                                </span>
                                            </div>
                                            {log.details && (
                                                <div className="text-sm text-gray-600 mt-2 pl-2 border-l-2 border-gray-300">
                                                    {log.details}
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Decision History */}
            {activeTab === 'decisions' && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <Brain className="w-5 h-5" />
                            Decision History
                            <span className="text-sm font-normal text-gray-500">(Last 5 decisions)</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {decisions.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    No decisions recorded for this agent
                                </div>
                            ) : (
                                decisions.map(decision => (
                                    <div key={decision.id} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-start justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                {decision.outcome === 'success' ? (
                                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                                ) : decision.outcome === 'failure' ? (
                                                    <XCircle className="w-5 h-5 text-red-600" />
                                                ) : (
                                                    <Clock className="w-5 h-5 text-gray-400" />
                                                )}
                                                <h4 className="font-semibold text-gray-900">{decision.action}</h4>
                                            </div>
                                            <span className="text-xs text-gray-500" suppressHydrationWarning>
                                                {formatTimeAgo(decision.timestamp)}
                                            </span>
                                        </div>
                                        <div className="bg-gray-50 rounded p-3 mt-2">
                                            <div className="text-xs text-gray-600 mb-1">Reasoning:</div>
                                            <div className="text-sm text-gray-900">{decision.reasoning}</div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Prompt/Response Pairs */}
            {activeTab === 'prompts' && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <MessageSquare className="w-5 h-5" />
                            Prompt/Response History
                            <span className="text-sm font-normal text-gray-500">(Last 5 interactions)</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-6">
                            {prompts.length === 0 ? (
                                <div className="text-center py-8 text-gray-500">
                                    No prompt/response data for this agent
                                </div>
                            ) : (
                                prompts.map(pr => (
                                    <div key={pr.id} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-3">
                                            <span className="text-xs text-gray-500" suppressHydrationWarning>
                                                {formatTimeAgo(pr.timestamp)}
                                            </span>
                                            <div className="flex gap-2 text-xs">
                                                <span className="text-gray-600">
                                                    {pr.tokens.input + pr.tokens.output} tokens
                                                </span>
                                                <span className="text-gray-400">•</span>
                                                <span className="text-gray-600">${pr.tokens.cost.toFixed(4)}</span>
                                                <span className="text-gray-400">•</span>
                                                <span className="text-gray-600">{pr.latency}ms</span>
                                            </div>
                                        </div>

                                        <div className="space-y-3">
                                            <div>
                                                <div className="text-xs font-semibold text-gray-600 mb-1">PROMPT:</div>
                                                <div className="bg-blue-50 rounded p-3 text-sm text-gray-900">
                                                    {pr.prompt}
                                                </div>
                                            </div>
                                            <div>
                                                <div className="text-xs font-semibold text-gray-600 mb-1">RESPONSE:</div>
                                                <div className="bg-green-50 rounded p-3 text-sm text-gray-900 whitespace-pre-wrap">
                                                    {pr.response}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-200">
                                            <div className="text-center">
                                                <div className="text-xs text-gray-600">Input</div>
                                                <div className="text-sm font-semibold text-gray-900">{pr.tokens.input}</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-xs text-gray-600">Output</div>
                                                <div className="text-sm font-semibold text-gray-900">{pr.tokens.output}</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-xs text-gray-600">Cost</div>
                                                <div className="text-sm font-semibold text-gray-900">${pr.tokens.cost.toFixed(4)}</div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
