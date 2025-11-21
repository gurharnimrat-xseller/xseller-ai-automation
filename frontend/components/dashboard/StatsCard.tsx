'use client';

import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { Card, CardContent } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

export interface StatsCardProps {
    title: string;
    value: number | string;
    subtitle?: string;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color?: 'blue' | 'green' | 'amber' | 'red' | 'purple';
    chartData?: { value: number }[];
    onClick?: () => void;
}

const colorVariants = {
    blue: 'bg-blue-500 text-white',
    green: 'bg-green-500 text-white',
    amber: 'bg-amber-500 text-white',
    red: 'bg-red-500 text-white',
    purple: 'bg-purple-500 text-white',
};

const chartColorVariants = {
    blue: '#3b82f6',
    green: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
    purple: '#a855f7',
};

// Generate mock 7-day trend data
const generateTrendData = (isPositive: boolean) => {
    const baseValue = 50;
    return Array.from({ length: 7 }, (_, i) => ({
        value: baseValue + (isPositive ? i * 5 + Math.random() * 10 : -i * 3 + Math.random() * 5)
    }));
};

export function StatsCard({
    title,
    value,
    subtitle,
    icon: Icon,
    trend,
    color = 'blue',
    chartData,
    onClick
}: StatsCardProps) {
    // Use provided chartData or generate fallback
    const trendData = chartData || (trend ? generateTrendData(trend.isPositive) : generateTrendData(true));

    return (
        <Card
            className={cn(
                "transition-all duration-300 hover:shadow-xl cursor-pointer group",
                onClick && "hover:-translate-y-2"
            )}
            onClick={onClick}
        >
            <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                    <div className={cn(
                        "p-3 rounded-xl shadow-md transition-transform duration-300 group-hover:scale-110",
                        colorVariants[color]
                    )}>
                        <Icon className="w-6 h-6" />
                    </div>
                </div>

                <div className="space-y-1 mb-4">
                    <p className="text-3xl font-bold text-gray-900">{value}</p>
                    <p className="text-sm text-gray-600 font-medium">{title}</p>
                    {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
                </div>

                {trend && (
                    <div className="mt-4 flex items-center gap-1">
                        {trend.isPositive ? (
                            <TrendingUp className="w-4 h-4 text-green-600" />
                        ) : (
                            <TrendingDown className="w-4 h-4 text-red-600" />
                        )}
                        <span className={cn(
                            "text-sm font-semibold",
                            trend.isPositive ? "text-green-600" : "text-red-600"
                        )}>
                            {trend.isPositive ? '+' : ''}{trend.value}%
                        </span>
                        <span className="text-xs text-gray-400 ml-1">vs last period</span>
                    </div>
                )}

                {/* Mini Sparkline Chart - 7-day trend visualization */}
                <div className="mt-4 h-12">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={trendData}>
                            <defs>
                                <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={chartColorVariants[color]} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={chartColorVariants[color]} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <Area
                                type="monotone"
                                dataKey="value"
                                stroke={chartColorVariants[color]}
                                strokeWidth={2}
                                fill={`url(#gradient-${color})`}
                                isAnimationActive={false}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
