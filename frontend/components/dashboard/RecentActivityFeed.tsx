'use client';

import React from 'react';
import Link from 'next/link';
import { Activity } from '@/lib/types/dashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { CheckCircle, Info, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RecentActivityFeedProps {
    activities: Activity[];
}

const activityConfig = {
    success: {
        icon: CheckCircle,
        color: 'text-green-600',
        bg: 'bg-green-50',
        border: 'border-green-200'
    },
    info: {
        icon: Info,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
        border: 'border-blue-200'
    },
    warning: {
        icon: AlertTriangle,
        color: 'text-amber-600',
        bg: 'bg-amber-50',
        border: 'border-amber-200'
    },
    error: {
        icon: XCircle,
        color: 'text-red-600',
        bg: 'bg-red-50',
        border: 'border-red-200'
    }
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

export function RecentActivityFeed({ activities }: RecentActivityFeedProps) {
    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg">Recent Activity</CardTitle>
                <Link
                    href="/activity"
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                >
                    View All
                    <ArrowRight className="w-4 h-4" />
                </Link>
            </CardHeader>
            <CardContent>
                <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    {activities.map((activity, index) => {
                        const config = activityConfig[activity.type];
                        const Icon = config.icon;
                        const isLast = index === activities.length - 1;

                        return (
                            <div key={activity.id} className="relative">
                                {/* Timeline Line */}
                                {!isLast && (
                                    <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-gray-200" />
                                )}

                                {/* Activity Item */}
                                <div className="flex gap-4">
                                    {/* Icon */}
                                    <div className={cn(
                                        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border-2",
                                        config.bg,
                                        config.border
                                    )}>
                                        <Icon className={cn("w-4 h-4", config.color)} />
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between gap-2">
                                            <div className="flex-1">
                                                <h4 className="text-sm font-semibold text-gray-900">
                                                    {activity.title}
                                                </h4>
                                                <p className="text-sm text-gray-600 mt-0.5">
                                                    {activity.description}
                                                </p>
                                                {activity.agent && (
                                                    <p className="text-xs text-gray-500 mt-1">
                                                        {activity.agent}
                                                    </p>
                                                )}
                                            </div>
                                            <span
                                                className="text-xs text-gray-400 whitespace-nowrap"
                                                suppressHydrationWarning
                                            >
                                                {formatTimeAgo(activity.timestamp)}
                                            </span>
                                        </div>

                                        {activity.link && (
                                            <Link
                                                href={activity.link}
                                                className="text-xs text-blue-600 hover:text-blue-700 font-medium mt-2 inline-block"
                                            >
                                                View details →
                                            </Link>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
