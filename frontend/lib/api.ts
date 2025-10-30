const BASE_URL = 'http://localhost:8000';

// ==================== Types ====================

interface QueueStats {
    draft: number;
    approved: number;
    published_today: number;
    overdue: number;
    failed: number;
}

interface DashboardStatsResponse {
    queue_stats: QueueStats;
    recent_activity: any[];
}

interface Post {
    id: number;
    kind: string;
    title: string;
    body: string;
    source_url?: string;
    tags?: string[];
    platforms?: string[];
    status: string;
    scheduled_at?: string;
    created_at: string;
    updated_at: string;
}

interface QueueResponse {
    posts: Post[];
    total: number;
}

interface ApprovePostResponse {
    message: string;
    scheduled_at?: string;
}

interface RejectPostResponse {
    message: string;
}

interface UpdatePostResponse {
    message: string;
    post: Post;
}

// ==================== Helper ====================

async function apiCall<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;

    const config: RequestInit = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('Network error occurred');
    }
}

// ==================== API Functions ====================

export async function getDashboardStats(): Promise<DashboardStatsResponse> {
    return apiCall<DashboardStatsResponse>('/api/stats/dashboard');
}

export async function getQueue(
    status?: string,
    platform?: string,
    limit?: number,
    offset?: number
): Promise<QueueResponse> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (platform) params.append('platform', platform);
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());

    const query = params.toString();
    const endpoint = `/api/content/queue${query ? `?${query}` : ''}`;

    return apiCall<QueueResponse>(endpoint);
}

export async function approvePost(
    postId: number,
    scheduleImmediately: boolean = false
): Promise<ApprovePostResponse> {
    return apiCall<ApprovePostResponse>(`/api/content/${postId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ schedule_immediately: scheduleImmediately }),
    });
}

export async function rejectPost(postId: number): Promise<RejectPostResponse> {
    return apiCall<RejectPostResponse>(`/api/content/${postId}/reject`, {
        method: 'POST',
    });
}

export async function updatePost(
    postId: number,
    data: any
): Promise<UpdatePostResponse> {
    return apiCall<UpdatePostResponse>(`/api/content/${postId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
}

// Export types for use in components
export type {
    DashboardStatsResponse,
    Post,
    QueueResponse,
    ApprovePostResponse,
    RejectPostResponse,
    UpdatePostResponse,
};

