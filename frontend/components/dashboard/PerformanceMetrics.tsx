'use client';

import React from 'react';
import { PerformanceData } from '@/lib/types/dashboard';
import { Card, CardContent } from '@/components/ui/Card';
import { FileText, Star, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PerformanceMetricsProps {
    data: PerformanceData;
}

const metrics = [
    {
        key: 'scriptsGenerated' as const,
        title: 'Scripts Generated',
        icon: FileText,
        color: 'blue',
        suffix: ''
    },
    {
        key: 'qualityScore' as const,
        title: 'Avg Quality Score',
        icon: Star,
        color: 'amber',
        suffix: '/10'
    },
    {
        key: 'successRate' as const,
        title: 'Success Rate',
        icon: CheckCircle,
        color: 'green',
        suffix: '%'
    }
];

const colorVariants = {
    blue: 'bg-blue-500',
    amber: 'bg-amber-500',
    green: 'bg-green-500'
};

export function PerformanceMetrics({ data }: PerformanceMetricsProps) {
    return (
        <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Performance (Last 24h)</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {metrics.map((metric) => {
                    const metricData = data[metric.key];
                    const Icon = metric.icon;
                    const isPositive = metricData.trend >= 0;

                    return (
                        <Card key={metric.key} className="hover:shadow-md transition-shadow">
                            <CardContent className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className={cn(
                                        "p-3 rounded-xl text-white shadow-md",
                                        colorVariants[metric.color as keyof typeof colorVariants]
                                    )}>
                                        <Icon className="w-5 h-5" />
                                    </div>
                                </div>

                                <div className="space-y-1">
                                    <p className="text-3xl font-bold text-gray-900">
                                        {metricData.value}{metric.suffix}
                                    </p>
                                    <p className="text-sm text-gray-600 font-medium">{metric.title}</p>
                                </div>

                                <div className="mt-4 flex items-center gap-1">
                                    {isPositive ? (
                                        <TrendingUp className="w-4 h-4 text-green-600" />
                                    ) : (
                                        <TrendingDown className="w-4 h-4 text-red-600" />
                                    )}
                                    <span className={cn(
                                        "text-sm font-semibold",
                                        isPositive ? "text-green-600" : "text-red-600"
                                    )}>
                                        {isPositive ? '+' : ''}{metricData.trend}%
                                    </span>
                                    <span className="text-xs text-gray-400 ml-1">
                                        vs yesterday ({metricData.previousValue}{metric.suffix})
                                    </span>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
