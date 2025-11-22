'use client';

import React from 'react';
import { PerformanceData } from '@/lib/types/dashboard';
import { Card, CardContent } from '@/components/ui/Card';
import { DollarSign, TrendingUp, Zap, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface PerformanceMetricsProps {
    data: PerformanceData;
}

const metrics = [
    {
        key: 'scriptsGenerated' as const,
        title: 'Pipeline Value',
        icon: DollarSign,
        color: 'emerald',
        suffix: '',
        valueTransform: (value: number) => `$${(value * 200).toLocaleString()}`
    },
    {
        key: 'qualityScore' as const,
        title: 'Viral Potential',
        icon: Zap,
        color: 'purple',
        suffix: '/10',
        valueTransform: (value: number) => value.toString()
    },
    {
        key: 'successRate' as const,
        title: 'Automation Rate',
        icon: TrendingUp,
        color: 'blue',
        suffix: '%',
        valueTransform: (value: number) => value.toString()
    }
];

const colorVariants = {
    emerald: 'bg-emerald-500',
    purple: 'bg-purple-500',
    blue: 'bg-blue-500'
};

export function PerformanceMetrics({ data }: PerformanceMetricsProps) {
    return (
        <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Business Value (Last 24h)</h2>

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
                                        {metric.valueTransform(metricData.value)}{metric.suffix}
                                    </p>
                                    <p className="text-sm text-gray-600 font-medium">{metric.title}</p>
                                    {metric.key === 'scriptsGenerated' && (
                                        <p className="text-xs text-gray-500 mt-1">
                                            {metricData.value} videos @ $200 each
                                        </p>
                                    )}
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
                                        vs yesterday
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
