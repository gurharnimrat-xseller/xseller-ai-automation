'use client';

import React from 'react';
import Link from 'next/link';
import {
    Bot,
    Activity,
    Clock,
    Zap,
    PlayCircle,
    Database,
    Settings,
    Eye,
    Pause,
    RotateCcw,
    AlertCircle,
    CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';

const agents = [
    {
        id: 'news-ingester',
        name: 'News Ingester',
        type: 'news_ingestion',
        status: 'active',
        currentTask: 'Fetching articles from TechCrunch',
        lastRun: '2 minutes ago',
        uptime: '99.9%',
        tasksCompleted: 1247,
        errorCount: 0,
        icon: Database,
    },
    {
        id: 'viral-ranker',
        name: 'Viral Ranker',
        type: 'viral_ranking',
        status: 'processing',
        currentTask: 'Analyzing article virality scores',
        lastRun: '1 minute ago',
        uptime: '99.7%',
        tasksCompleted: 892,
        errorCount: 2,
        icon: Activity,
    },
    {
        id: 'script-writer',
        name: 'Script Writer',
        type: 'script_generation',
        status: 'idle',
        currentTask: 'Waiting for ranked articles',
        lastRun: '5 minutes ago',
        uptime: '99.8%',
        tasksCompleted: 756,
        errorCount: 1,
        icon: Zap,
    },
    {
        id: 'video-producer',
        name: 'Video Producer',
        type: 'video_production',
        status: 'queued',
        currentTask: 'Preparing video assets',
        lastRun: '8 minutes ago',
        uptime: '99.5%',
        tasksCompleted: 623,
        errorCount: 3,
        icon: PlayCircle,
    },
    {
        id: 'content-publisher',
        name: 'Content Publisher',
        type: 'publishing',
        status: 'idle',
        currentTask: 'Monitoring publishing queue',
        lastRun: '12 minutes ago',
        uptime: '99.9%',
        tasksCompleted: 489,
        errorCount: 0,
        icon: Bot,
    },
    {
        id: 'tts-service',
        name: 'TTS Service',
        type: 'tts_service',
        status: 'active',
        currentTask: 'Generating voiceover for video',
        lastRun: '30 seconds ago',
        uptime: '99.6%',
        tasksCompleted: 345,
        errorCount: 1,
        icon: Activity,
    },
];

const getStatusColor = (status: string) => {
    switch (status) {
        case 'active': return 'success';
        case 'processing': return 'info';
        case 'idle': return 'secondary';
        case 'queued': return 'warning';
        case 'error': return 'error';
        default: return 'secondary';
    }
};

const getStatusIcon = (status: string) => {
    switch (status) {
        case 'active': return CheckCircle;
        case 'processing': return Clock;
        case 'idle': return Pause;
        case 'queued': return Clock;
        case 'error': return AlertCircle;
        default: return Pause;
    }
};

export default function AgentsPage() {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Agent Management</h1>
                    <p className="text-gray-600 mt-1">Monitor and control your AI agents</p>
                </div>
                <div className="flex items-center space-x-3">
                    <Badge variant="success" className="px-3 py-1">
                        <div className="w-2 h-2 bg-current rounded-full mr-2 animate-pulse"></div>
                        6 Agents Online
                    </Badge>
                    <Button>
                        <Settings className="w-4 h-4 mr-2" />
                        Configure All
                    </Button>
                </div>
            </div>

            {/* Agent Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => {
                    const StatusIcon = getStatusIcon(agent.status);
                    const AgentIcon = agent.icon;

                    return (
                        <Card key={agent.id} className="relative">
                            <CardHeader className="pb-3">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${agent.status === 'active' ? 'bg-success-100' :
                                            agent.status === 'processing' ? 'bg-info-100' :
                                                agent.status === 'idle' ? 'bg-gray-100' :
                                                    agent.status === 'queued' ? 'bg-warning-100' : 'bg-error-100'
                                            }`}>
                                            <AgentIcon className={`w-5 h-5 ${agent.status === 'active' ? 'text-success-600' :
                                                agent.status === 'processing' ? 'text-info-600' :
                                                    agent.status === 'idle' ? 'text-gray-600' :
                                                        agent.status === 'queued' ? 'text-warning-600' : 'text-error-600'
                                                }`} />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                                            <p className="text-sm text-gray-500 capitalize">{agent.type.replace('_', ' ')}</p>
                                        </div>
                                    </div>
                                    <Badge variant={getStatusColor(agent.status) as any}>
                                        <StatusIcon className="w-3 h-3 mr-1" />
                                        {agent.status}
                                    </Badge>
                                </div>
                            </CardHeader>

                            <CardContent className="space-y-4">
                                {/* Current Task */}
                                <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">Current Task</p>
                                    <p className="text-sm text-gray-600">{agent.currentTask}</p>
                                </div>

                                {/* Stats */}
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <p className="text-gray-500">Last Run</p>
                                        <p className="font-medium text-gray-900">{agent.lastRun}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-500">Uptime</p>
                                        <p className="font-medium text-gray-900">{agent.uptime}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-500">Completed</p>
                                        <p className="font-medium text-gray-900">{agent.tasksCompleted}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-500">Errors</p>
                                        <p className="font-medium text-gray-900">{agent.errorCount}</p>
                                    </div>
                                </div>

                                {/* Progress Bar */}
                                <div>
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-sm font-medium text-gray-700">Performance</span>
                                        <span className="text-sm text-gray-500">94%</span>
                                    </div>
                                    <Progress value={94} />
                                </div>

                                {/* Actions */}
                                <div className="flex space-x-2 pt-2">
                                    <Link href={`/agents/${agent.id}`}>
                                        <Button variant="outline" size="sm" className="flex-1">
                                            <Eye className="w-4 h-4 mr-1" />
                                            View
                                        </Button>
                                    </Link>
                                    <Button variant="outline" size="sm">
                                        <Pause className="w-4 h-4" />
                                    </Button>
                                    <Button variant="outline" size="sm">
                                        <RotateCcw className="w-4 h-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* System Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium text-gray-700">Overall Uptime</span>
                            <span className="text-sm font-bold text-success-600">99.7%</span>
                        </div>
                        <Progress value={99.7} color="success" />

                        <div className="grid grid-cols-3 gap-4 pt-4">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-success-600">6</div>
                                <div className="text-sm text-gray-500">Active</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-info-600">1</div>
                                <div className="text-sm text-gray-500">Processing</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-gray-600">2</div>
                                <div className="text-sm text-gray-500">Idle</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <div className="flex items-start space-x-3">
                                <div className="w-2 h-2 bg-success-500 rounded-full mt-2"></div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">News Ingester completed batch</p>
                                    <p className="text-xs text-gray-500">Processed 50 articles • 2 minutes ago</p>
                                </div>
                            </div>

                            <div className="flex items-start space-x-3">
                                <div className="w-2 h-2 bg-info-500 rounded-full mt-2"></div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">Viral Ranker started analysis</p>
                                    <p className="text-xs text-gray-500">Analyzing 25 articles • 1 minute ago</p>
                                </div>
                            </div>

                            <div className="flex items-start space-x-3">
                                <div className="w-2 h-2 bg-warning-500 rounded-full mt-2"></div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900">Script Writer paused</p>
                                    <p className="text-xs text-gray-500">Rate limit reached • 5 minutes ago</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}