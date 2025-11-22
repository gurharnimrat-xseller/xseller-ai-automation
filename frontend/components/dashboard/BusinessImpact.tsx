'use client';

import React from 'react';
import { TrendingUp, DollarSign, Video, Eye, Percent, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

export interface BusinessImpactData {
    videosPublished: number;
    totalViews: number;
    engagementRate: number; // percentage
    estimatedRevenue: number;
    costPerVideo: number;
    roi: number; // percentage
}

export interface BusinessImpactProps {
    data: BusinessImpactData;
}

export function BusinessImpact({ data }: BusinessImpactProps) {
    const metrics = [
        {
            label: 'Videos Published',
            value: data.videosPublished,
            icon: Video,
            color: 'blue',
            suffix: ' videos'
        },
        {
            label: 'Total Potential Views',
            value: data.totalViews >= 1000000
                ? `${(data.totalViews / 1000000).toFixed(1)}M`
                : `${(data.totalViews / 1000).toFixed(0)}K`,
            icon: Eye,
            color: 'purple',
            suffix: ' views'
        },
        {
            label: 'Engagement Rate',
            value: `${data.engagementRate.toFixed(1)}%`,
            icon: Percent,
            color: 'green',
            suffix: ''
        },
        {
            label: 'Est. Ad Revenue',
            value: `$${data.estimatedRevenue.toLocaleString()}`,
            icon: DollarSign,
            color: 'emerald',
            suffix: ''
        },
        {
            label: 'Cost per Video',
            value: `$${data.costPerVideo}`,
            icon: Clock,
            color: 'amber',
            suffix: ' (vs $200 manual)',
            comparison: true
        },
        {
            label: 'ROI',
            value: `${data.roi}%`,
            icon: TrendingUp,
            color: 'green',
            suffix: ' return',
            highlight: true
        }
    ];

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    Business Impact (Last 7 Days)
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {metrics.map((metric, index) => {
                        const Icon = metric.icon;
                        const colorClasses = {
                            blue: 'bg-blue-50 text-blue-600 border-blue-200',
                            purple: 'bg-purple-50 text-purple-600 border-purple-200',
                            green: 'bg-green-50 text-green-600 border-green-200',
                            emerald: 'bg-emerald-50 text-emerald-600 border-emerald-200',
                            amber: 'bg-amber-50 text-amber-600 border-amber-200'
                        };

                        return (
                            <div
                                key={index}
                                className={cn(
                                    "p-4 rounded-lg border-2 transition-all hover:shadow-md",
                                    metric.highlight && "ring-2 ring-green-500 ring-offset-2",
                                    colorClasses[metric.color as keyof typeof colorClasses]
                                )}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="text-sm font-medium opacity-80">{metric.label}</div>
                                    <Icon className="w-4 h-4" />
                                </div>
                                <div className="text-2xl font-bold mb-1">
                                    {metric.value}
                                </div>
                                {metric.suffix && (
                                    <div className={cn(
                                        "text-xs opacity-70",
                                        metric.comparison && "font-medium"
                                    )}>
                                        {metric.suffix}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Summary */}
                <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-sm text-green-700 font-medium mb-1">
                                💰 Total Value Generated
                            </div>
                            <div className="text-2xl font-bold text-green-900">
                                ${(data.estimatedRevenue - (data.videosPublished * data.costPerVideo)).toLocaleString()}
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                                Revenue minus production costs
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-green-700 font-medium mb-1">
                                Time Saved
                            </div>
                            <div className="text-2xl font-bold text-green-900">
                                {Math.round(data.videosPublished * 2.5)}h
                            </div>
                            <div className="text-xs text-green-600 mt-1">
                                vs manual production
                            </div>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
