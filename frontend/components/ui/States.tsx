import React from 'react';
import { AlertCircle, RefreshCw, Database, Search, Zap } from 'lucide-react';
import { Button } from './Button';
import { Card, CardContent } from './Card';

export interface LoadingStateProps {
    message?: string;
    className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
    message = 'Loading...',
    className
}) => (
    <div className={`flex flex-col items-center justify-center p-8 ${className || ''}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mb-4"></div>
        <p className="text-gray-600">{message}</p>
    </div>
);

export interface ErrorStateProps {
    title?: string;
    message?: string;
    onRetry?: () => void;
    className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
    title = 'Something went wrong',
    message = 'We encountered an error while loading this content.',
    onRetry,
    className
}) => (
    <Card className={`border-red-200 bg-red-50 ${className || ''}`}>
        <CardContent className="p-6">
            <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                    <AlertCircle className="h-6 w-6 text-red-500" />
                </div>
                <div className="flex-1">
                    <h3 className="text-sm font-medium text-red-800">{title}</h3>
                    <p className="mt-1 text-sm text-red-700">{message}</p>
                    {onRetry && (
                        <div className="mt-4">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={onRetry}
                                className="border-red-300 text-red-700 hover:bg-red-50"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Try Again
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </CardContent>
    </Card>
);

export interface EmptyStateProps {
    icon?: React.ComponentType<{ className?: string }>;
    title: string;
    message: string;
    action?: {
        label: string;
        onClick: () => void;
    };
    className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
    icon: Icon = Database,
    title,
    message,
    action,
    className
}) => (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className || ''}`}>
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Icon className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-500 mb-6 max-w-sm">{message}</p>
        {action && (
            <Button onClick={action.onClick}>
                {action.label}
            </Button>
        )}
    </div>
);

// Specific empty states for common scenarios
export const EmptyAgentsState: React.FC<{ onCreateAgent?: () => void }> = ({ onCreateAgent }) => (
    <EmptyState
        icon={Zap}
        title="No agents configured"
        message="Get started by creating your first AI agent to automate content generation and processing."
        action={onCreateAgent ? {
            label: 'Create Agent',
            onClick: onCreateAgent
        } : undefined}
    />
);

export const EmptyContentState: React.FC<{ onGenerateContent?: () => void }> = ({ onGenerateContent }) => (
    <EmptyState
        icon={Database}
        title="No content found"
        message="Start generating viral content by creating your first post or importing existing content."
        action={onGenerateContent ? {
            label: 'Generate Content',
            onClick: onGenerateContent
        } : undefined}
    />
);

export const EmptySearchState: React.FC<{ searchTerm?: string; onClearSearch?: () => void }> = ({
    searchTerm,
    onClearSearch
}) => (
    <EmptyState
        icon={Search}
        title="No results found"
        message={`We couldn't find any results for "${searchTerm}". Try adjusting your search terms or filters.`}
        action={onClearSearch ? {
            label: 'Clear Search',
            onClick: onClearSearch
        } : undefined}
    />
);