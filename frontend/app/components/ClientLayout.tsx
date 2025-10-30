'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Home, List, BarChart3, Settings, Menu } from 'lucide-react';

interface SidebarProps {
    isOpen: boolean;
    setIsOpen: (open: boolean) => void;
}

function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
    const navItems = [
        { href: '/', label: 'Dashboard', icon: Home },
        { href: '/queue', label: 'Queue', icon: List },
        { href: '/insights', label: 'Insights', icon: BarChart3 },
        { href: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <>
            {/* Mobile backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`fixed left-0 top-0 h-full w-64 bg-[#1A1D24] text-white z-50 transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full'
                    } md:translate-x-0`}
            >
                {/* Logo */}
                <div className="p-6 border-b border-gray-700">
                    <h1 className="text-2xl font-bold text-[#10F4A0]">Xseller.ai</h1>
                </div>

                {/* Navigation */}
                <nav className="p-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors hover:bg-[#2A2D34] text-gray-300 hover:text-white group"
                                onClick={() => setIsOpen(false)}
                            >
                                <Icon className="w-5 h-5 group-hover:text-[#10F4A0]" />
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </aside>
        </>
    );
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="flex min-h-screen bg-[#0E1117]">
            {/* Mobile menu button */}
            <div className="md:hidden fixed top-4 left-4 z-50">
                <button
                    onClick={() => setSidebarOpen(true)}
                    className="p-2 bg-[#1A1D24] rounded-lg text-white hover:bg-[#2A2D34] transition-colors"
                >
                    <Menu className="w-6 h-6" />
                </button>
            </div>

            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

            {/* Main content */}
            <main className="flex-1 md:ml-64 p-6 pt-20 md:pt-6">
                {children}
            </main>
        </div>
    );
}

