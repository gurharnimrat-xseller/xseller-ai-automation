'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, Users, Target, Loader2 } from 'lucide-react';

interface TopPost {
    id: number;
    title: string;
    platform: string;
    views: number;
    engagement: number;
}

interface InsightsData {
    totalViews: number;
    engagementRate: number;
    topPlatform: string;
    growthRate: number;
    topPosts: TopPost[];
}

function StatCard({ title, value, icon: Icon, color }: { title: string; value: string | number; icon: any; color: string }) {
    return (
        <div className="bg-[#1A1D24] rounded-lg p-6 border border-gray-700 hover:border-[#10F4A0] transition-all duration-300">
            <div className="flex items-center gap-4">
                <div className={`${color} p-3 rounded-lg flex-shrink-0`}>
                    <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-gray-400 text-sm font-medium mb-1 truncate">{title}</p>
                    <p className="text-3xl font-bold text-white truncate">{value}</p>
                </div>
            </div>
        </div>
    );
}

export default function InsightsPage() {
    const [loading, setLoading] = useState(true);
    const [insightsData, setInsightsData] = useState<InsightsData>({
        totalViews: 0,
        engagementRate: 0,
        topPlatform: '',
        growthRate: 0,
        topPosts: [],
    });

    useEffect(() => {
        // Simulate API call with mock data
        const fetchInsights = async () => {
            setLoading(true);

            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mock data
            const mockData: InsightsData = {
                totalViews: 12450,
                engagementRate: 8.5,
                topPlatform: 'LinkedIn',
                growthRate: 12.3,
                topPosts: [
                    { id: 1, title: 'AI Trends in 2024', platform: 'LinkedIn', views: 3450, engagement: 9.2 },
                    { id: 2, title: 'Social Media Automation Guide', platform: 'Twitter', views: 2890, engagement: 7.8 },
                    { id: 3, title: 'Content Strategy Tips', platform: 'LinkedIn', views: 2100, engagement: 6.5 },
                    { id: 4, title: 'Digital Marketing Insights', platform: 'Facebook', views: 1950, engagement: 5.8 },
                    { id: 5, title: 'Tech Industry Updates', platform: 'Twitter', views: 1760, engagement: 5.2 },
                ],
            };

            setInsightsData(mockData);
            setLoading(false);
        };

        fetchInsights();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-[#10F4A0]" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
                <p className="text-gray-400">Track your performance and engagement metrics</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Views"
                    value={insightsData.totalViews.toLocaleString()}
                    icon={BarChart3}
                    color="bg-blue-500/20 border border-blue-500/30"
                />
                <StatCard
                    title="Engagement Rate"
                    value={`${insightsData.engagementRate}%`}
                    icon={Target}
                    color="bg-green-500/20 border border-green-500/30"
                />
                <StatCard
                    title="Top Platform"
                    value={insightsData.topPlatform}
                    icon={Users}
                    color="bg-purple-500/20 border border-purple-500/30"
                />
                <StatCard
                    title="Growth Rate"
                    value={`+${insightsData.growthRate}%`}
                    icon={TrendingUp}
                    color="bg-orange-500/20 border border-orange-500/30"
                />
            </div>

            {/* Chart Section */}
            <div className="bg-[#1A1D24] rounded-lg p-6 border border-gray-700">
                <h2 className="text-xl font-bold text-white mb-6">Performance Trends</h2>
                <div className="h-64 flex items-center justify-center bg-[#0E1117] rounded-lg border border-gray-800">
                    <div className="text-center">
                        <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500">Chart visualization coming soon</p>
                        <p className="text-gray-600 text-sm mt-1">API integration pending</p>
                    </div>
                </div>
            </div>

            {/* Top Posts Table */}
            <div className="bg-[#1A1D24] rounded-lg border border-gray-700 overflow-hidden">
                <div className="p-6 border-b border-gray-700">
                    <h2 className="text-xl font-bold text-white">Top Performing Posts</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-700">
                                <th className="text-left p-4 text-gray-400 font-medium text-sm">Title</th>
                                <th className="text-left p-4 text-gray-400 font-medium text-sm">Platform</th>
                                <th className="text-left p-4 text-gray-400 font-medium text-sm">Views</th>
                                <th className="text-left p-4 text-gray-400 font-medium text-sm">Engagement %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insightsData.topPosts.map((post, index) => (
                                <tr
                                    key={post.id}
                                    className="border-b border-gray-800 hover:bg-[#2A2D34] transition-colors"
                                >
                                    <td className="p-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 bg-blue-500/20 rounded flex items-center justify-center flex-shrink-0">
                                                <span className="text-blue-400 text-xs font-bold">{index + 1}</span>
                                            </div>
                                            <span className="text-white font-medium truncate">{post.title}</span>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className="inline-flex items-center px-3 py-1 rounded-full bg-gray-700 text-white text-sm">
                                            {post.platform}
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <span className="text-white font-medium">{post.views.toLocaleString()}</span>
                                    </td>
                                    <td className="p-4">
                                        <span className="inline-flex items-center gap-2">
                                            <span className="text-green-400 font-medium">{post.engagement}%</span>
                                            {post.engagement > 7 && (
                                                <TrendingUp className="w-4 h-4 text-green-400" />
                                            )}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

