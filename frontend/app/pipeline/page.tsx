'use client';

import React, { useState, useEffect } from 'react';
import {
    FileText,
    Video,
    CheckCircle,
    XCircle,
    Clock,
    TrendingUp,
    Sparkles,
    Film,
    Send
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { cn } from '@/lib/utils';

// Pipeline stages
const PIPELINE_STAGES = [
    { id: 1, name: 'Ingestion', icon: FileText, color: 'blue' },
    { id: 2, name: 'Ranking', icon: TrendingUp, color: 'purple' },
    { id: 3, name: 'Script', icon: Sparkles, color: 'amber' },
    { id: 4, name: 'Video', icon: Film, color: 'green' },
    { id: 5, name: 'Publishing', icon: Send, color: 'red' }
];

interface PipelineItem {
    id: number;
    title: string;
    stage: number;
    status: 'processing' | 'completed' | 'failed' | 'pending';
    progress: number;
    value: number; // Dollar value
    createdAt: Date;
    estimatedCompletion?: Date;
}

// Mock data - will be replaced with real API calls
const mockItems: PipelineItem[] = [
    {
        id: 1,
        title: 'AI Breakthrough in NLP',
        stage: 4,
        status: 'processing',
        progress: 75,
        value: 200,
        createdAt: new Date(Date.now() - 10 * 60 * 1000),
        estimatedCompletion: new Date(Date.now() + 5 * 60 * 1000)
    },
    {
        id: 2,
        title: 'Tech Trends 2024',
        stage: 5,
        status: 'completed',
        progress: 100,
        value: 200,
        createdAt: new Date(Date.now() - 60 * 60 * 1000)
    },
    {
        id: 3,
        title: 'Crypto Market Analysis',
        stage: 2,
        status: 'failed',
        progress: 0,
        value: 200,
        createdAt: new Date(Date.now() - 30 * 60 * 1000)
    },
    {
        id: 4,
        title: 'Future of AI',
        stage: 3,
        status: 'processing',
        progress: 45,
        value: 200,
        createdAt: new Date(Date.now() - 15 * 60 * 1000),
        estimatedCompletion: new Date(Date.now() + 10 * 60 * 1000)
    },
    {
        id: 5,
        title: 'Startup Funding News',
        stage: 1,
        status: 'processing',
        progress: 20,
        value: 200,
        createdAt: new Date(Date.now() - 5 * 60 * 1000),
        estimatedCompletion: new Date(Date.now() + 20 * 60 * 1000)
    },
];

const statusConfig = {
    processing: { label: 'Processing', color: 'bg-blue-500', badge: 'info' },
    completed: { label: 'Completed', color: 'bg-green-500', badge: 'success' },
    failed: { label: 'Failed', color: 'bg-red-500', badge: 'destructive' },
    pending: { label: 'Pending', color: 'bg-gray-400', badge: 'secondary' }
};

function formatTimeAgo(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

export default function PipelinePage() {
    const [items, setItems] = useState<PipelineItem[]>(mockItems);
    const [activeTab, setActiveTab] = useState<'all' | 'processing' | 'completed' | 'failed'>('all');
    const [loading, setLoading] = useState(false);

    // Filter items based on active tab
    const filteredItems = items.filter(item => {
        if (activeTab === 'all') return true;
        return item.status === activeTab;
    });

    // Group items by stage
    const itemsByStage = PIPELINE_STAGES.map(stage => ({
        ...stage,
        items: filteredItems.filter(item => item.stage === stage.id)
    }));

    // Calculate overall progress
    const totalItems = items.length;
    const completedItems = items.filter(i => i.status === 'completed').length;
    const processingItems = items.filter(i => i.status === 'processing').length;
    const failedItems = items.filter(i => i.status === 'failed').length;
    const totalValue = items.reduce((sum, item) => sum + item.value, 0);

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Pipeline</h1>
                    <p className="text-gray-600 mt-1">Track content through the production pipeline</p>
                </div>
                <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">${totalValue.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">Total pipeline value</div>
                </div>
            </div>

            {/* Stage Progress Bar */}
            <Card>
                <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        {PIPELINE_STAGES.map((stage, index) => {
                            const stageItems = items.filter(i => i.stage === stage.id);
                            const Icon = stage.icon;
                            const isActive = stageItems.length > 0;

                            return (
                                <React.Fragment key={stage.id}>
                                    <div className="flex flex-col items-center flex-1">
                                        <div className={cn(
                                            "w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all",
                                            isActive
                                                ? `bg-${stage.color}-500 text-white shadow-lg`
                                                : "bg-gray-200 text-gray-400"
                                        )}>
                                            <Icon className="w-6 h-6" />
                                        </div>
                                        <div className="text-sm font-medium text-gray-900">{stage.name}</div>
                                        <div className="text-xs text-gray-500">{stageItems.length} items</div>
                                    </div>
                                    {index < PIPELINE_STAGES.length - 1 && (
                                        <div className={cn(
                                            "h-1 flex-1 mx-2 rounded",
                                            isActive ? `bg-${stage.color}-300` : "bg-gray-200"
                                        )} />
                                    )}
                                </React.Fragment>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>

            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-2xl font-bold text-gray-900">{totalItems}</div>
                                <div className="text-sm text-gray-600">Total Items</div>
                            </div>
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <FileText className="w-5 h-5 text-blue-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-2xl font-bold text-blue-600">{processingItems}</div>
                                <div className="text-sm text-gray-600">Processing</div>
                            </div>
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Clock className="w-5 h-5 text-blue-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-2xl font-bold text-green-600">{completedItems}</div>
                                <div className="text-sm text-gray-600">Completed</div>
                            </div>
                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-2xl font-bold text-red-600">{failedItems}</div>
                                <div className="text-sm text-gray-600">Failed</div>
                            </div>
                            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                                <XCircle className="w-5 h-5 text-red-600" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-200">
                {(['all', 'processing', 'completed', 'failed'] as const).map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={cn(
                            "px-4 py-2 font-medium text-sm border-b-2 transition-colors capitalize",
                            activeTab === tab
                                ? "border-blue-600 text-blue-600"
                                : "border-transparent text-gray-600 hover:text-gray-900"
                        )}
                    >
                        {tab}
                        <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-gray-100">
                            {tab === 'all' ? totalItems : items.filter(i => i.status === tab).length}
                        </span>
                    </button>
                ))}
            </div>

            {/* Pipeline Items by Stage */}
            <div className="space-y-6">
                {itemsByStage.map(stage => {
                    if (stage.items.length === 0) return null;

                    return (
                        <div key={stage.id}>
                            <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                {React.createElement(stage.icon, { className: "w-5 h-5" })}
                                {stage.name} Stage
                                <span className="text-sm font-normal text-gray-500">
                                    ({stage.items.length} {stage.items.length === 1 ? 'item' : 'items'})
                                </span>
                            </h2>

                            <div className="grid grid-cols-1 gap-4">
                                {stage.items.map(item => {
                                    const config = statusConfig[item.status];

                                    return (
                                        <Card key={item.id} className="hover:shadow-md transition-shadow">
                                            <CardContent className="p-4">
                                                <div className="flex items-start justify-between mb-3">
                                                    <div className="flex-1">
                                                        <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                                                        <div className="flex items-center gap-2 text-sm text-gray-600">
                                                            <span suppressHydrationWarning>{formatTimeAgo(item.createdAt)}</span>
                                                            <span>•</span>
                                                            <span>${item.value} value</span>
                                                        </div>
                                                    </div>
                                                    <Badge variant={config.badge as any}>
                                                        {config.label}
                                                    </Badge>
                                                </div>

                                                {item.status === 'processing' && (
                                                    <div className="mb-3">
                                                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                                                            <span>Progress</span>
                                                            <span>{item.progress}%</span>
                                                        </div>
                                                        <Progress value={item.progress} />
                                                        {item.estimatedCompletion && (
                                                            <div className="text-xs text-gray-500 mt-1">
                                                                Est. completion: {formatTimeAgo(item.estimatedCompletion)}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                                <div className="flex gap-2">
                                                    <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                                        View Details
                                                    </button>
                                                    {item.status === 'failed' && (
                                                        <button className="px-3 py-1.5 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                                                            Retry
                                                        </button>
                                                    )}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    );
                                })}
                            </div>
                        </div>
                    );
                })}

                {filteredItems.length === 0 && (
                    <Card>
                        <CardContent className="p-12 text-center">
                            <div className="text-gray-400 mb-2">
                                <FileText className="w-16 h-16 mx-auto mb-4" />
                            </div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                No items found
                            </h3>
                            <p className="text-gray-600">
                                {activeTab === 'all'
                                    ? 'No items in the pipeline yet'
                                    : `No ${activeTab} items`}
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
