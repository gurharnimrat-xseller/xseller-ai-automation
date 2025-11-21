// Post and content-related types for Xseller.ai dashboard

export interface Post {
    id: number;
    kind: PostKind;
    title: string;
    body: string;
    source_url?: string;
    tags: string[];
    platforms: string[];
    status: PostStatus;
    scheduled_at?: Date;
    published_at?: Date;
    created_at: Date;
    updated_at: Date;
    video_duration?: number;
    regeneration_count?: number;
    total_cost?: number;
    extra_data?: Record<string, any>;
    assets?: Asset[];
}

export type PostKind = 'text' | 'video';

export type PostStatus =
    | 'draft'
    | 'approved'
    | 'published'
    | 'failed'
    | 'video_production'
    | 'scheduled';

export interface Asset {
    id: number;
    post_id: number;
    type: AssetType;
    path: string;
    created_at: Date;
}

export type AssetType = 'video' | 'audio' | 'image';

export interface PostStats {
    totalPosts: number;
    draftPosts: number;
    approvedPosts: number;
    publishedToday: number;
    overduePosts: number;
    failedPosts: number;
}

export interface ContentGenerationRequest {
    kind?: PostKind;
    title?: string;
    body?: string;
    platforms?: string[];
    tags?: string[];
}

export interface ContentGenerationResponse {
    message: string;
    post: Post;
}