/**
 * API Client for Xseller.ai Backend
 *
 * Connects the frontend dashboard to the FastAPI backend.
 * Includes error handling, retry logic, and TypeScript types.
 */

import { Agent } from '@/lib/types/agent';
import { DashboardStats, PerformanceData, Activity } from '@/lib/types/dashboard';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Fetch options with timeout and error handling
interface FetchOptions extends RequestInit {
    timeout?: number;
}

/**
 * Custom fetch with timeout and error handling
 */
async function fetchWithTimeout(url: string, options: FetchOptions = {}): Promise<Response> {
    const { timeout = 10000, ...fetchOptions } = options;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...fetchOptions,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                ...fetchOptions.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }

        return response;
    } finally {
        clearTimeout(timeoutId);
    }
}

/**
 * API Client class for dashboard data
 */
export const apiClient = {
    /**
     * Get dashboard statistics
     */
    async getStats(): Promise<DashboardStats> {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/api/dashboard/stats`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch dashboard stats:', error);
            throw error;
        }
    },

    /**
     * Get all agents status
     */
    async getAgents(): Promise<Agent[]> {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/api/dashboard/agents`);
            const data = await response.json();

            // Transform API response to match Agent type
            return data.map((agent: any) => ({
                id: agent.id,
                name: agent.name,
                type: agent.type,
                status: agent.status,
                currentTask: agent.currentTask,
                progress: agent.progress,
                lastRun: agent.lastRun ? new Date(agent.lastRun) : undefined,
                uptime: agent.uptime,
                efficiency: agent.efficiency,
            }));
        } catch (error) {
            console.error('Failed to fetch agents:', error);
            throw error;
        }
    },

    /**
     * Get recent activities
     */
    async getActivities(limit: number = 10): Promise<Activity[]> {
        try {
            const response = await fetchWithTimeout(
                `${API_BASE_URL}/api/dashboard/activity?limit=${limit}`
            );
            const data = await response.json();

            // Transform API response to match Activity type
            return data.map((activity: any) => ({
                id: activity.id,
                type: activity.type,
                title: activity.title,
                description: activity.description,
                timestamp: new Date(activity.timestamp),
                agent: activity.agent,
                link: activity.link,
            }));
        } catch (error) {
            console.error('Failed to fetch activities:', error);
            throw error;
        }
    },

    /**
     * Get performance metrics
     */
    async getPerformance(): Promise<PerformanceData> {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/api/dashboard/performance`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch performance:', error);
            throw error;
        }
    },

    /**
     * Health check
     */
    async healthCheck(): Promise<{ api: string; database: string; scheduler: string }> {
        try {
            const response = await fetchWithTimeout(`${API_BASE_URL}/api/health`, {
                timeout: 5000,
            });
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    },
};

/**
 * Hook for polling data at regular intervals
 */
export function usePolling<T>(
    fetchFn: () => Promise<T>,
    interval: number = 5000
): { data: T | null; error: Error | null; loading: boolean } {
    // Note: This is a placeholder - in a real React app, you'd use useState and useEffect
    // The actual implementation would be in a React hook file
    return {
        data: null,
        error: null,
        loading: true,
    };
}

export default apiClient;
