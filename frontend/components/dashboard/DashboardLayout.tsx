import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
    Play,
    MoreHorizontal,
    TrendingUp,
    Users,
    Video,
    Clock,
    ArrowUpRight,
    ArrowDownRight
} from 'lucide-react';

export default function DashboardLayout() {
    return (
        <div className="p-8 space-y-8 bg-gray-50/50 min-h-screen">
            {/* Header Section */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Overview</h1>
                    <p className="text-gray-500 mt-1">Welcome back, here&apos;s what&apos;s happening with your agents.</p>
                </div>
                <div className="flex space-x-3">
                    <Button variant="outline" className="bg-white">Last 7 Days</Button>
                    <Button className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20">
                        + New Agent
                    </Button>
                </div>
            </div>

            {/* Stats Grid (Acme Style) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    { label: 'Total Videos', value: '1,284', change: '+12.5%', trend: 'up', icon: Video, color: 'blue' },
                    { label: 'Active Agents', value: '12', change: '+2', trend: 'up', icon: Users, color: 'green' },
                    { label: 'Avg. Watch Time', value: '45s', change: '-1.2%', trend: 'down', icon: Clock, color: 'orange' },
                    { label: 'Engagement Rate', value: '8.4%', change: '+3.1%', trend: 'up', icon: TrendingUp, color: 'purple' },
                ].map((stat, index) => (
                    <Card key={index} className="border-none shadow-sm hover:shadow-md transition-shadow duration-200">
                        <CardContent className="p-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                                    <h3 className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</h3>
                                </div>
                                <div className={`p-2 rounded-lg bg-${stat.color}-50`}>
                                    <stat.icon className={`w-5 h-5 text-${stat.color}-600`} />
                                </div>
                            </div>
                            <div className="mt-4 flex items-center">
                                <span className={`flex items-center text-xs font-medium ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                                    {stat.trend === 'up' ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                                    {stat.change}
                                </span>
                                <span className="text-xs text-gray-400 ml-2">vs last week</span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Main Content - Agent List (Soax Style) */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-gray-900">Active Agents</h2>
                        <Button variant="ghost" className="text-blue-600 hover:text-blue-700 hover:bg-blue-50">View All</Button>
                    </div>

                    <div className="space-y-4">
                        {[
                            { name: 'TechNews Bot', status: 'active', platform: 'TikTok', videos: 45, views: '1.2M' },
                            { name: 'Finance Guru', status: 'processing', platform: 'YouTube', videos: 12, views: '85K' },
                            { name: 'Daily Motivator', status: 'paused', platform: 'Instagram', videos: 89, views: '2.4M' },
                        ].map((agent, index) => (
                            <Card key={index} className="border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 group">
                                <CardContent className="p-5 flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-lg font-bold text-gray-600 group-hover:from-blue-500 group-hover:to-indigo-600 group-hover:text-white transition-all duration-300">
                                            {agent.name.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="flex items-center space-x-2">
                                                <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                                                <Badge variant={agent.status === 'active' ? 'success' : agent.status === 'processing' ? 'info' : 'warning'} className="capitalize">
                                                    {agent.status}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-gray-500 mt-0.5">{agent.platform} • {agent.videos} videos generated</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-6">
                                        <div className="text-right hidden sm:block">
                                            <p className="text-sm font-medium text-gray-900">{agent.views}</p>
                                            <p className="text-xs text-gray-400">Total Views</p>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <Button size="icon" variant="ghost" className="h-8 w-8 text-gray-400 hover:text-blue-600 hover:bg-blue-50">
                                                <Play className="w-4 h-4" />
                                            </Button>
                                            <Button size="icon" variant="ghost" className="h-8 w-8 text-gray-400 hover:text-gray-600">
                                                <MoreHorizontal className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Right Sidebar - Activity & Usage (Soax/Acme Blend) */}
                <div className="space-y-6">
                    <Card className="border-none shadow-sm bg-gradient-to-br from-blue-600 to-indigo-700 text-white overflow-hidden relative">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl transform translate-x-10 -translate-y-10"></div>
                        <CardContent className="p-6 relative z-10">
                            <h3 className="font-semibold text-lg">Pro Plan</h3>
                            <p className="text-blue-100 text-sm mt-1">Your plan renews in 12 days</p>

                            <div className="mt-6 space-y-4">
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-blue-100">Video Credits</span>
                                        <span className="font-medium">850/1000</span>
                                    </div>
                                    <div className="w-full bg-blue-900/30 rounded-full h-2">
                                        <div className="bg-white h-2 rounded-full w-[85%]"></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-blue-100">Storage</span>
                                        <span className="font-medium">45GB/100GB</span>
                                    </div>
                                    <div className="w-full bg-blue-900/30 rounded-full h-2">
                                        <div className="bg-blue-300 h-2 rounded-full w-[45%]"></div>
                                    </div>
                                </div>
                            </div>

                            <Button className="w-full mt-6 bg-white text-blue-600 hover:bg-blue-50 border-none">
                                Upgrade Plan
                            </Button>
                        </CardContent>
                    </Card>

                    <Card className="border-none shadow-sm">
                        <CardHeader>
                            <CardTitle className="text-lg">Recent Activity</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {[
                                { text: 'New video generated by TechNews Bot', time: '2 min ago', type: 'success' },
                                { text: 'Finance Guru started processing', time: '15 min ago', type: 'info' },
                                { text: 'Daily Motivator failed to upload', time: '1 hour ago', type: 'error' },
                            ].map((activity, i) => (
                                <div key={i} className="flex items-start space-x-3">
                                    <div className={`w-2 h-2 mt-1.5 rounded-full flex-shrink-0 ${activity.type === 'success' ? 'bg-green-500' :
                                        activity.type === 'info' ? 'bg-blue-500' : 'bg-red-500'
                                        }`}></div>
                                    <div>
                                        <p className="text-sm text-gray-600">{activity.text}</p>
                                        <p className="text-xs text-gray-400 mt-0.5">{activity.time}</p>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}