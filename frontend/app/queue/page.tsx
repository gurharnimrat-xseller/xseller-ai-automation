'use client';

import { useState, useEffect } from 'react';
import { Filter, FileText, CheckCircle, XCircle, Loader2, Clock } from 'lucide-react';
import { getQueue, approvePost, rejectPost, type Post as PostType } from '@/lib/api';

export default function QueuePage() {
    const [posts, setPosts] = useState<PostType[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'all' | 'draft' | 'approved' | 'published'>('draft');
    const [processingId, setProcessingId] = useState<number | null>(null);

    useEffect(() => {
        fetchPosts();
    }, [filter]);

    const fetchPosts = async () => {
        try {
            setLoading(true);
            setError(null);
            const status = filter === 'all' ? undefined : filter;
            const response = await getQueue(status, undefined, 50, 0);
            setPosts(response.posts);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch posts');
            console.error('Error fetching posts:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (postId: number) => {
        try {
            setProcessingId(postId);
            await approvePost(postId, false);
            // Refresh posts after approval
            await fetchPosts();
        } catch (err) {
            console.error('Error approving post:', err);
            alert('Failed to approve post');
        } finally {
            setProcessingId(null);
        }
    };

    const handleReject = async (postId: number) => {
        if (!confirm('Are you sure you want to reject this post?')) {
            return;
        }

        try {
            setProcessingId(postId);
            await rejectPost(postId);
            // Refresh posts after rejection
            await fetchPosts();
        } catch (err) {
            console.error('Error rejecting post:', err);
            alert('Failed to reject post');
        } finally {
            setProcessingId(null);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else {
            return `${diffDays}d ago`;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'draft':
                return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
            case 'approved':
                return 'text-green-500 bg-green-500/10 border-green-500/20';
            case 'published':
                return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
            case 'failed':
                return 'text-red-500 bg-red-500/10 border-red-500/20';
            default:
                return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-[#10F4A0]" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-red-400">
                <p className="font-semibold mb-2">Error Loading Queue</p>
                <p className="text-sm">{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header with Filters */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Content Queue</h1>
                    <p className="text-gray-400">Review and approve AI-generated posts</p>
                </div>

                {/* Filter Buttons */}
                <div className="flex items-center gap-2 flex-wrap">
                    <Filter className="w-5 h-5 text-gray-400" />
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'all'
                            ? 'bg-[#10F4A0] text-black'
                            : 'bg-[#1A1D24] text-gray-400 hover:bg-[#2A2D34]'
                            }`}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setFilter('draft')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'draft'
                            ? 'bg-[#10F4A0] text-black'
                            : 'bg-[#1A1D24] text-gray-400 hover:bg-[#2A2D34]'
                            }`}
                    >
                        Draft
                    </button>
                    <button
                        onClick={() => setFilter('approved')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'approved'
                            ? 'bg-[#10F4A0] text-black'
                            : 'bg-[#1A1D24] text-gray-400 hover:bg-[#2A2D34]'
                            }`}
                    >
                        Approved
                    </button>
                    <button
                        onClick={() => setFilter('published')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'published'
                            ? 'bg-[#10F4A0] text-black'
                            : 'bg-[#1A1D24] text-gray-400 hover:bg-[#2A2D34]'
                            }`}
                    >
                        Published
                    </button>
                </div>
            </div>

            {/* Posts Grid */}
            {posts.length === 0 ? (
                <div className="bg-[#1A1D24] rounded-lg p-12 border border-gray-700">
                    <div className="flex flex-col items-center justify-center text-center">
                        <FileText className="w-16 h-16 text-gray-600 mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">No posts in queue</h3>
                        <p className="text-gray-400">
                            {filter === 'all'
                                ? 'No posts found'
                                : `No ${filter} posts found`}
                        </p>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {posts.map((post) => (
                        <div
                            key={post.id}
                            className="bg-[#1A1D24] rounded-lg p-6 border border-gray-700 hover:border-[#10F4A0] transition-colors"
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <div className={`px-2 py-1 rounded text-xs font-medium border ${getStatusColor(post.status)}`}>
                                        {post.status.toUpperCase()}
                                    </div>
                                </div>
                                <div className="flex items-center gap-1 text-gray-500 text-sm">
                                    <Clock className="w-4 h-4" />
                                    {formatDate(post.created_at)}
                                </div>
                            </div>

                            {/* Title */}
                            <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
                                {post.title}
                            </h3>

                            {/* Body Preview */}
                            <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                                {post.body}
                            </p>

                            {/* Platforms */}
                            {post.platforms && post.platforms.length > 0 && (
                                <div className="flex flex-wrap gap-2 mb-4">
                                    {post.platforms.map((platform, idx) => (
                                        <span
                                            key={idx}
                                            className="px-2 py-1 bg-[#6D28D9]/20 text-[#6D28D9] rounded text-xs"
                                        >
                                            {platform}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Action Buttons */}
                            {post.status === 'draft' && (
                                <div className="flex gap-2 pt-4 border-t border-gray-700">
                                    <button
                                        onClick={() => handleApprove(post.id)}
                                        disabled={processingId === post.id}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {processingId === post.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <CheckCircle className="w-4 h-4" />
                                        )}
                                        Approve
                                    </button>
                                    <button
                                        onClick={() => handleReject(post.id)}
                                        disabled={processingId === post.id}
                                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {processingId === post.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <XCircle className="w-4 h-4" />
                                        )}
                                        Reject
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Total count */}
            {posts.length > 0 && (
                <div className="text-center text-gray-400 text-sm">
                    Showing {posts.length} post{posts.length !== 1 ? 's' : ''}
                </div>
            )}
        </div>
    );
}

