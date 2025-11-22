'use client';

import React from 'react';
import Link from 'next/link';
import { Agent } from '@/lib/types/agent';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AgentActivityPanelProps {
    agents: Agent[];
}

const statusConfig = {
    active: {
        badge: 'success',
        dot: 'bg-green-500',
        label: 'Active'
    },
    processing: {
        badge: 'info',
        dot: 'bg-blue-500',
        label: 'Processing'
    },
    idle: {
        badge: 'secondary',
        dot: 'bg-gray-400',
        label: 'Idle'
    },
    error: {
        badge: 'destructive',
        dot: 'bg-red-500',
        label: 'Error'
    },
    paused: {
        badge: 'warning',
        dot: 'bg-amber-500',
        label: 'Paused'
    }
} as const;

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

// Calculate health color based on uptime
function getHealthColor(uptime?: string): string {
    if (!uptime) return 'gray';
    const uptimeValue = parseFloat(uptime);
    if (uptimeValue >= 95) return 'green';
    if (uptimeValue >= 90) return 'amber';
    return 'red';
}

export function AgentActivityPanel({ agents }: AgentActivityPanelProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg">Active Agents</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {agents.map((agent) => {
                        const config = statusConfig[agent.status];
                        const healthColor = getHealthColor(agent.uptime);

                        return (
                            <div
                                key={agent.id}
                                className={cn(
                                    "p-4 border-2 rounded-lg hover:shadow-md transition-all",
                                    healthColor === 'green' && "border-green-200 hover:border-green-300",
                                    healthColor === 'amber' && "border-amber-200 hover:border-amber-300",
                                    healthColor === 'red' && "border-red-200 hover:border-red-300",
                                    healthColor === 'gray' && "border-gray-200 hover:border-gray-300"
                                )}
                            >
                                {/* Agent Header */}
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <div className={cn("w-2 h-2 rounded-full", config.dot)} />
                                        <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                                    </div>
                                    <Badge variant={config.badge as any}>
                                        {config.label}
                                    </Badge>
                                </div>

                                {/* Agent Type */}
                                <p className="text-xs text-gray-500 mb-2">{agent.type}</p>

                                {/* Current Task */}
                                {agent.currentTask && (
                                    <p className="text-sm text-gray-600 mb-2">
                                        <span className="font-medium">Task:</span> {agent.currentTask}
                                    </p>
                                )}

                                {/* Progress Bar (if processing) */}
                                {agent.status === 'processing' && agent.progress !== undefined && (
                                    <div className="mb-3">
                                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                                            <span>Progress</span>
                                            <span>{agent.progress}%</span>
                                        </div>
                                        <Progress value={agent.progress} />
                                    </div>
                                )}

                                {/* Footer Info */}
                                <div className="flex items-center justify-between text-xs text-gray-500 mt-3 pt-3 border-t border-gray-100">
                                    <span suppressHydrationWarning>
                                        {agent.lastRun ? formatTimeAgo(agent.lastRun) : 'Never'}
                                    </span>
                                    {agent.uptime && (
                                        <span className={cn(
                                            "font-medium",
                                            healthColor === 'green' && "text-green-600",
                                            healthColor === 'amber' && "text-amber-600",
                                            healthColor === 'red' && "text-red-600"
                                        )}>
                                            ↑ {agent.uptime}
                                        </span>
                                    )}
                                </div>

                                {/* View Logs Button */}
                                <Link
                                    href={`/agents/${agent.id}`}
                                    className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                                >
                                    <Eye className="w-4 h-4" />
                                    View Logs
                                </Link>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
