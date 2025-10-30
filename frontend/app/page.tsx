'use client';

import { useState, useEffect } from 'react';
import { FileText, CheckCircle, Send, AlertCircle, XCircle, Loader2 } from 'lucide-react';

interface DashboardStats {
    drafts: number;
    approved: number;
    published_today: number;
    overdue: number;
    failed: number;
}

interface StatCardProps {
    label: string;
    value: number;
    icon: React.ReactNode;
    color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
    return (
        <div className="bg-[#1A1D24] rounded-lg p-6 border border-gray-700 hover:border-[#10F4A0] transition-colors">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-400 text-sm font-medium mb-1">{label}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                </div>
                <div className={`p-3 rounded-lg ${color}`}>
                    {icon}
                </div>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const [stats, setStats] = useState<DashboardStats>({
        drafts: 0,
        approved: 0,
        published_today: 0,
        overdue: 0,
        failed: 0,
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await fetch('http://localhost:8000/api/stats/dashboard');

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                // Backend returns queue_stats wrapper, extract it
                setStats({
                    drafts: data.queue_stats?.draft || 0,
                    approved: data.queue_stats?.approved || 0,
                    published_today: data.queue_stats?.published_today || 0,
                    overdue: data.queue_stats?.overdue || 0,
                    failed: data.queue_stats?.failed || 0,
                });
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats');
                console.error('Error fetching stats:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-[#10F4A0]" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-red-400">
                <p className="font-semibold mb-2">Error Loading Dashboard</p>
                <p className="text-sm">{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Stats Grid */}
            <div>
                <h2 className="text-2xl font-bold text-white mb-6">Overview</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    <StatCard
                        label="Drafts"
                        value={stats.drafts}
                        icon={<FileText className="w-6 h-6 text-yellow-500" />}
                        color="bg-yellow-500/10"
                    />
                    <StatCard
                        label="Approved"
                        value={stats.approved}
                        icon={<CheckCircle className="w-6 h-6 text-green-500" />}
                        color="bg-green-500/10"
                    />
                    <StatCard
                        label="Published Today"
                        value={stats.published_today}
                        icon={<Send className="w-6 h-6 text-blue-500" />}
                        color="bg-blue-500/10"
                    />
                    <StatCard
                        label="Overdue"
                        value={stats.overdue}
                        icon={<AlertCircle className="w-6 h-6 text-red-500" />}
                        color="bg-red-500/10"
                    />
                    <StatCard
                        label="Failed"
                        value={stats.failed}
                        icon={<XCircle className="w-6 h-6 text-orange-500" />}
                        color="bg-orange-500/10"
                    />
                </div>
            </div>

            {/* Recent Activity */}
            <div>
                <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
                <div className="bg-[#1A1D24] rounded-lg p-8 border border-gray-700">
                    <p className="text-gray-400 text-center">No recent activity</p>
                </div>
            </div>
        </div>
    );
}

