import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader } from './Card';
import { Button } from './Button';
import { RefreshCw, Maximize2, MoreVertical, Settings } from 'lucide-react';

export interface PanelProps {
    title: string;
    subtitle?: string;
    icon?: React.ReactNode;
    children: React.ReactNode;
    className?: string;
    headerClassName?: string;
    contentClassName?: string;

    // Panel controls
    showRefresh?: boolean;
    showMaximize?: boolean;
    showSettings?: boolean;
    showMore?: boolean;
    onRefresh?: () => void;
    onMaximize?: () => void;
    onSettings?: () => void;
    onMore?: () => void;

    // Styling variants
    variant?: 'default' | 'gradient' | 'glass';
    gradient?: 'blue' | 'emerald' | 'purple' | 'rose';
}

const gradientClasses = {
    blue: 'bg-gradient-to-br from-blue-50 via-blue-100/50 to-indigo-100/30 border-l-4 border-l-blue-500',
    emerald: 'bg-gradient-to-br from-emerald-50 via-emerald-100/50 to-green-100/30 border-l-4 border-l-emerald-500',
    purple: 'bg-gradient-to-br from-purple-50 via-purple-100/50 to-pink-100/30 border-l-4 border-l-purple-500',
    rose: 'bg-gradient-to-br from-rose-50 via-rose-100/50 to-pink-100/30 border-l-4 border-l-rose-500',
};

export const Panel: React.FC<PanelProps> = ({
    title,
    subtitle,
    icon,
    children,
    className,
    headerClassName,
    contentClassName,
    showRefresh = false,
    showMaximize = false,
    showSettings = false,
    showMore = false,
    onRefresh,
    onMaximize,
    onSettings,
    onMore,
    variant = 'default',
    gradient = 'blue',
}) => {
    const getVariantClasses = () => {
        switch (variant) {
            case 'gradient':
                return gradientClasses[gradient];
            case 'glass':
                return 'bg-white/80 backdrop-blur-sm border-2 border-gray-100/50 shadow-xl';
            default:
                return 'bg-white border border-gray-200 shadow-sm';
        }
    };

    const getHeaderClasses = () => {
        switch (variant) {
            case 'gradient':
                return `bg-gradient-to-r from-${gradient === 'blue' ? 'blue' : gradient === 'emerald' ? 'emerald' : gradient === 'purple' ? 'purple' : 'rose'}-50 to-${gradient === 'blue' ? 'indigo' : gradient === 'emerald' ? 'green' : gradient === 'purple' ? 'pink' : 'pink'}-50 border-b border-${gradient}-100/50`;
            case 'glass':
                return 'bg-white/60 backdrop-blur-sm border-b border-gray-100/50';
            default:
                return 'bg-gray-50 border-b border-gray-200';
        }
    };

    return (
        <Card className={cn('transition-all duration-300', getVariantClasses(), className)}>
            <CardHeader className={cn('flex items-center justify-between', getHeaderClasses(), headerClassName)}>
                <div className="flex items-center space-x-3">
                    {icon && (
                        <div className="w-10 h-10 bg-white/80 rounded-lg flex items-center justify-center shadow-md">
                            {icon}
                        </div>
                    )}
                    <div>
                        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
                        {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
                    </div>
                </div>

                {(showRefresh || showMaximize || showSettings || showMore) && (
                    <div className="flex items-center space-x-2">
                        {showRefresh && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-8 h-8 p-0 hover:bg-white/50"
                                onClick={onRefresh}
                                title="Refresh"
                            >
                                <RefreshCw className="w-4 h-4 text-gray-600" />
                            </Button>
                        )}
                        {showMaximize && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-8 h-8 p-0 hover:bg-white/50"
                                onClick={onMaximize}
                                title="Maximize"
                            >
                                <Maximize2 className="w-4 h-4 text-gray-600" />
                            </Button>
                        )}
                        {showSettings && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-8 h-8 p-0 hover:bg-white/50"
                                onClick={onSettings}
                                title="Settings"
                            >
                                <Settings className="w-4 h-4 text-gray-600" />
                            </Button>
                        )}
                        {showMore && (
                            <Button
                                variant="ghost"
                                size="sm"
                                className="w-8 h-8 p-0 hover:bg-white/50"
                                onClick={onMore}
                                title="More options"
                            >
                                <MoreVertical className="w-4 h-4 text-gray-600" />
                            </Button>
                        )}
                    </div>
                )}
            </CardHeader>

            <CardContent className={cn('p-6', contentClassName)}>
                {children}
            </CardContent>
        </Card>
    );
};

// Specialized panel components for common use cases
export const MetricPanel: React.FC<Omit<PanelProps, 'variant'> & {
    value: string | number;
    label: string;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    icon: React.ReactNode;
}> = ({ value, label, trend, icon, children, ...props }) => (
    <Panel {...props} variant="gradient">
        <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-semibold text-gray-700 mb-1">{label}</p>
                <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
                {trend && (
                    <div className="flex items-center">
                        <span className={cn(
                            'text-xs font-medium',
                            trend.isPositive ? 'text-green-600' : 'text-red-600'
                        )}>
                            {trend.isPositive ? '+' : ''}{trend.value}%
                        </span>
                    </div>
                )}
            </div>
            <div className="w-14 h-14 bg-white/80 rounded-xl flex items-center justify-center shadow-md">
                {icon}
            </div>
        </div>
        {children}
    </Panel>
);

export const StatusPanel: React.FC<Omit<PanelProps, 'variant'> & {
    status: 'success' | 'warning' | 'error' | 'info';
    statusText: string;
}> = ({ status, statusText, children, ...props }) => {
    const statusColors = {
        success: 'text-green-600 bg-green-50 border-green-200',
        warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
        error: 'text-red-600 bg-red-50 border-red-200',
        info: 'text-blue-600 bg-blue-50 border-blue-200',
    };

    return (
        <Panel {...props} variant="glass">
            <div className="space-y-4">
                <div className={cn(
                    'flex items-center space-x-3 px-4 py-3 rounded-lg border',
                    statusColors[status]
                )}>
                    <div className={cn(
                        'w-2 h-2 rounded-full',
                        status === 'success' ? 'bg-green-500' :
                            status === 'warning' ? 'bg-yellow-500' :
                                status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    )} />
                    <span className="text-sm font-medium">{statusText}</span>
                </div>
                {children}
            </div>
        </Panel>
    );
};