'use client';

import { TrendingUp, BarChart3, Users, Target, Loader2, Eye, Heart, Share2 } from 'lucide-react';

export default function InsightsPage() {
    const loading = false;

    // Mock data for the vibrant design
    const stats = [
        {
            title: 'Total Views',
            value: '12,450',
            change: '+23%',
            icon: Eye,
            gradient: 'from-blue-400 to-indigo-600',
            bgGradient: 'from-blue-50 to-indigo-50',
            iconBg: 'bg-gradient-to-br from-blue-400 to-indigo-600'
        },
        {
            title: 'Engagement Rate',
            value: '8.5%',
            change: '+5.2%',
            icon: Heart,
            gradient: 'from-pink-400 to-red-600',
            bgGradient: 'from-pink-50 to-red-50',
            iconBg: 'bg-gradient-to-br from-pink-400 to-red-600'
        },
        {
            title: 'Total Shares',
            value: '1,840',
            change: '+18%',
            icon: Share2,
            gradient: 'from-green-400 to-emerald-600',
            bgGradient: 'from-green-50 to-emerald-50',
            iconBg: 'bg-gradient-to-br from-green-400 to-emerald-600'
        },
        {
            title: 'Growth Rate',
            value: '+12.3%',
            change: '+3.4%',
            icon: TrendingUp,
            gradient: 'from-purple-400 to-purple-600',
            bgGradient: 'from-purple-50 to-purple-50',
            iconBg: 'bg-gradient-to-br from-purple-400 to-purple-600'
        }
    ];

    const topPosts = [
        { id: 1, title: 'AI Trends in 2024', platform: 'LinkedIn', views: 3450, engagement: 9.2 },
        { id: 2, title: 'Social Media Automation Guide', platform: 'Twitter', views: 2890, engagement: 7.8 },
        { id: 3, title: 'Content Strategy Tips', platform: 'LinkedIn', views: 2100, engagement: 6.5 },
        { id: 4, title: 'Digital Marketing Insights', platform: 'Facebook', views: 1950, engagement: 5.8 },
        { id: 5, title: 'Tech Industry Updates', platform: 'Twitter', views: 1760, engagement: 5.2 }
    ];

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
                    <p className="text-gray-600 font-medium">Loading analytics...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
                    Analytics Dashboard
                </h1>
                <p className="text-gray-600 font-medium">Track your performance and engagement metrics</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat) => {
                    const Icon = stat.icon;
                    return (
                        <div
                            key={stat.title}
                            className="bg-white border-2 border-gray-200 rounded-2xl p-6 hover:shadow-xl hover:border-gray-300 transition-all hover:-translate-y-1"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-xl ${stat.iconBg} shadow-lg`}>
                                    <Icon className="w-6 h-6 text-white" />
                                </div>
                                <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">
                                    {stat.change}
                                </span>
                            </div>
                            <p className="text-sm text-gray-600 font-semibold mb-1">{stat.title}</p>
                            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                        </div>
                    );
                })}
            </div>

            {/* Chart Section */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-md">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance Trends</h2>
                <div className="h-80 flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 rounded-xl border-2 border-gray-200">
                    <div className="text-center">
                        <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center">
                            <BarChart3 className="w-12 h-12 text-blue-600" />
                        </div>
                        <p className="text-gray-700 font-bold text-lg mb-2">Chart Visualization Coming Soon</p>
                        <p className="text-gray-500 text-sm">API integration in progress</p>
                    </div>
                </div>
            </div>

            {/* Top Posts Table */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl shadow-md overflow-hidden">
                <div className="p-6 border-b-2 border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50">
                    <h2 className="text-2xl font-bold text-gray-900">Top Performing Posts</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b-2 border-gray-200 bg-gray-50">
                                <th className="text-left p-4 text-gray-700 font-bold text-sm">#</th>
                                <th className="text-left p-4 text-gray-700 font-bold text-sm">Title</th>
                                <th className="text-left p-4 text-gray-700 font-bold text-sm">Platform</th>
                                <th className="text-left p-4 text-gray-700 font-bold text-sm">Views</th>
                                <th className="text-left p-4 text-gray-700 font-bold text-sm">Engagement</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topPosts.map((post, index) => (
                                <tr
                                    key={post.id}
                                    className="border-b border-gray-200 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 transition-all"
                                >
                                    <td className="p-4">
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-md ${
                                            index === 0 ? 'bg-gradient-to-br from-amber-400 to-orange-500' :
                                            index === 1 ? 'bg-gradient-to-br from-gray-400 to-gray-500' :
                                            index === 2 ? 'bg-gradient-to-br from-orange-400 to-red-500' :
                                            'bg-gradient-to-br from-blue-400 to-indigo-500'
                                        }`}>
                                            {index + 1}
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <span className="text-gray-900 font-bold">{post.title}</span>
                                    </td>
                                    <td className="p-4">
                                        <span className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 text-sm font-semibold border border-purple-200">
                                            {post.platform}
                                        </span>
                                    </td>
                                    <td className="p-4">
                                        <span className="text-gray-900 font-bold">{post.views.toLocaleString()}</span>
                                    </td>
                                    <td className="p-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-green-600 font-bold">{post.engagement}%</span>
                                            {post.engagement > 7 && (
                                                <TrendingUp className="w-4 h-4 text-green-600" />
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Platform Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-[3px] rounded-2xl shadow-xl">
                    <div className="bg-white rounded-2xl p-6 h-full">
                        <div className="flex items-center gap-3 mb-4">
                            <Users className="w-8 h-8 text-blue-600" />
                            <h3 className="text-xl font-bold text-gray-900">LinkedIn</h3>
                        </div>
                        <p className="text-3xl font-bold text-blue-600 mb-2">5,550</p>
                        <p className="text-sm text-gray-600 font-semibold">Total Engagements</p>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-[3px] rounded-2xl shadow-xl">
                    <div className="bg-white rounded-2xl p-6 h-full">
                        <div className="flex items-center gap-3 mb-4">
                            <Target className="w-8 h-8 text-cyan-600" />
                            <h3 className="text-xl font-bold text-gray-900">Twitter</h3>
                        </div>
                        <p className="text-3xl font-bold text-cyan-600 mb-2">4,650</p>
                        <p className="text-sm text-gray-600 font-semibold">Total Engagements</p>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-[3px] rounded-2xl shadow-xl">
                    <div className="bg-white rounded-2xl p-6 h-full">
                        <div className="flex items-center gap-3 mb-4">
                            <BarChart3 className="w-8 h-8 text-purple-600" />
                            <h3 className="text-xl font-bold text-gray-900">Facebook</h3>
                        </div>
                        <p className="text-3xl font-bold text-purple-600 mb-2">2,250</p>
                        <p className="text-sm text-gray-600 font-semibold">Total Engagements</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
