import React from 'react';
import { cn } from '@/lib/utils';

export interface SkeletonProps {
    className?: string;
    variant?: 'default' | 'card' | 'text' | 'circle' | 'rectangle';
    lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
    className,
    variant = 'default',
    lines = 1,
}) => {
    if (variant === 'text' && lines > 1) {
        return (
            <div className="space-y-2">
                {Array.from({ length: lines }).map((_, i) => (
                    <div
                        key={i}
                        className={cn(
                            'h-4 bg-gray-200 rounded animate-pulse',
                            i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full',
                            className
                        )}
                    />
                ))}
            </div>
        );
    }

    const baseClasses = 'bg-gray-200 animate-pulse rounded';

    const variantClasses = {
        default: 'h-4 w-full',
        card: 'h-32 w-full',
        text: 'h-4 w-full',
        circle: 'h-10 w-10 rounded-full',
        rectangle: 'h-20 w-full',
    };

    return (
        <div
            className={cn(baseClasses, variantClasses[variant], className)}
        />
    );
};

// Specific skeleton components for common use cases
export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
    <div className={cn('p-6 border border-gray-200 rounded-lg', className)}>
        <Skeleton variant="text" className="h-6 w-1/3 mb-4" />
        <Skeleton variant="text" lines={3} />
        <div className="flex space-x-2 mt-4">
            <Skeleton variant="circle" className="w-8 h-8" />
            <Skeleton variant="circle" className="w-8 h-8" />
            <Skeleton variant="circle" className="w-8 h-8" />
        </div>
    </div>
);

export const SkeletonTable: React.FC<{ rows?: number; columns?: number; className?: string }> = ({
    rows = 5,
    columns = 4,
    className
}) => (
    <div className={cn('space-y-3', className)}>
        {/* Header */}
        <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, i) => (
                <Skeleton key={i} className="h-4 flex-1" />
            ))}
        </div>
        {/* Rows */}
        {Array.from({ length: rows }).map((_, rowIndex) => (
            <div key={rowIndex} className="flex space-x-4">
                {Array.from({ length: columns }).map((_, colIndex) => (
                    <Skeleton key={colIndex} className="h-4 flex-1" />
                ))}
            </div>
        ))}
    </div>
);

// Skeleton for Agent Card
export const SkeletonAgent: React.FC<{ className?: string }> = ({ className }) => (
    <div className={cn("p-4 border border-gray-200 rounded-lg space-y-3", className)}>
        <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
                <Skeleton className="w-2 h-2 rounded-full" />
                <Skeleton className="h-5 w-40" />
            </div>
            <Skeleton className="h-6 w-16 rounded-full" />
        </div>
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-2 w-full rounded-full" />
        <div className="flex justify-between pt-3 border-t border-gray-100">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-3 w-12" />
        </div>
    </div>
);

// Skeleton for Activity Item
export const SkeletonActivity: React.FC<{ className?: string }> = ({ className }) => (
    <div className={cn("flex gap-4", className)}>
        <Skeleton className="flex-shrink-0 w-8 h-8 rounded-full" />
        <div className="flex-1 space-y-2">
            <div className="flex justify-between gap-2">
                <div className="space-y-1 flex-1">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-full" />
                    <Skeleton className="h-3 w-32" />
                </div>
                <Skeleton className="h-3 w-16" />
            </div>
        </div>
    </div>
);

// Skeleton for Stats Card
export const SkeletonStatsCard: React.FC<{ className?: string }> = ({ className }) => (
    <div className={cn("bg-white rounded-xl shadow-sm p-6 space-y-4", className)}>
        <div className="flex items-start justify-between">
            <Skeleton className="w-12 h-12 rounded-xl" />
        </div>
        <div className="space-y-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-24" />
        </div>
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-12 w-full" />
    </div>
);