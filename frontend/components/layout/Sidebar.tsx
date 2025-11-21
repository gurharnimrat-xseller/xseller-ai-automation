"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/Progress';
import {
    LayoutDashboard,
    Users,
    Video,
    ListVideo,
    BarChart3,
    Settings,
    HelpCircle,
    LogOut
} from 'lucide-react';

const sidebarItems = [
    { icon: LayoutDashboard, label: 'Overview', href: '/' },
    { icon: Users, label: 'Agents', href: '/agents' },
    { icon: Video, label: 'Pipeline', href: '/pipeline' },
    { icon: BarChart3, label: 'Insights', href: '/insights' },
    { icon: Settings, label: 'Settings', href: '/settings' },
];

export function Sidebar({ className }: { className?: string }) {
    const pathname = usePathname();

    return (
        <div className={cn("flex flex-col w-64 h-screen bg-gradient-to-b from-[#0f172a] to-[#1e293b] text-white border-r border-gray-800", className)}>
            <div className="p-6 flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <span className="text-white font-bold text-xl">X</span>
                </div>
                <span className="text-xl font-bold tracking-tight">Xseller.ai</span>
            </div>

            <div className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-2">
                    Manage
                </div>
                {sidebarItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
                                isActive
                                    ? "bg-blue-600 text-white shadow-md shadow-blue-900/20"
                                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                            )}
                        >
                            <Icon className={cn("w-5 h-5", isActive ? "text-white" : "text-gray-400 group-hover:text-white")} />
                            <span className="font-medium">{item.label}</span>
                        </Link>
                    );
                })}
            </div>

            <div className="p-4 border-t border-gray-800">
                <div className="space-y-1">
                    <Link
                        href="/help"
                        className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-white/5 hover:text-white transition-colors"
                    >
                        <HelpCircle className="w-5 h-5" />
                        <span className="font-medium">Help & Support</span>
                    </Link>
                    <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-colors">
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
                {/* Pro Plan Usage - Bottom Section */}
                <div className="mt-6 px-2">
                    <div className="bg-gradient-to-br from-blue-600/10 to-purple-600/10 rounded-xl p-4 border border-blue-500/20">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-sm font-semibold text-white">Pro Plan</span>
                            <span className="text-xs text-gray-400">75% used</span>
                        </div>
                        <Progress value={75} className="h-2 mb-3" />
                        <p className="text-xs text-gray-400">
                            7,500 / 10,000 videos this month
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}