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