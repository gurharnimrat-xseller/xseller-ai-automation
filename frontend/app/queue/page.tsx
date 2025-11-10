'use client'

import { useState, useEffect, useRef } from 'react'
import { Loader2, FileText } from 'lucide-react'
import VideoPlayer from '@/components/VideoPlayer'
import RegenerateModal from '@/components/RegenerateModal'
import VideoGenerationProgress from '@/components/VideoGenerationProgress'

export default function QueuePage() {
    const [activeTab, setActiveTab] = useState('text')
    const [posts, setPosts] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [regenerateModalOpen, setRegenerateModalOpen] = useState(false)
    const [selectedPostId, setSelectedPostId] = useState<number | null>(null)
    const [selectedPostType, setSelectedPostType] = useState<'text' | 'video'>('text')
    const [generatingVideoIds, setGeneratingVideoIds] = useState<Set<number>>(new Set())
    const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        loadQueue()

        // Poll for updates every 5 seconds if there are videos in production
        pollIntervalRef.current = setInterval(() => {
            const videoProducing = posts.filter(p => p.kind === 'video' && p.status === 'video_production')
            if (videoProducing.length > 0) {
                loadQueue()
            }
        }, 5000)

        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current)
            }
        }
    }, [posts])

    const loadQueue = async () => {
        try {
            // Fetch more posts to see all of them
            const res = await fetch('/api/content/queue?limit=100')
            const data = await res.json()
            console.log('Queue loaded:', {
                total: data.total,
                postsCount: data.posts?.length,
                byKind: {
                    text: data.posts?.filter((p: any) => p.kind === 'text').length,
                    video: data.posts?.filter((p: any) => p.kind === 'video').length,
                },
                byStatus: {
                    draft: data.posts?.filter((p: any) => p.status === 'draft').length,
                    approved: data.posts?.filter((p: any) => p.status === 'approved').length,
                    video_production: data.posts?.filter((p: any) => p.status === 'video_production').length,
                },
                posts: data.posts
            })
            setPosts(data.posts || [])
            setLoading(false)
        } catch (error) {
            console.error('Error loading queue:', error)
            setLoading(false)
        }
    }

    const handleRegenerateText = (postId: number) => {
        setSelectedPostId(postId)
        setSelectedPostType('text')
        setRegenerateModalOpen(true)
    }

    const handleRegenerateVideo = (postId: number) => {
        setSelectedPostId(postId)
        setSelectedPostType('video')
        setRegenerateModalOpen(true)
    }

    const handleRegenerateSubmit = async (options: any) => {
        if (!selectedPostId) return

        const endpoint = selectedPostType === 'text'
            ? `/api/content/${selectedPostId}/regenerate-text`
            : `/api/content/${selectedPostId}/regenerate-video`

        try {
            // Ensure body is sent even if empty
            const body = Object.keys(options).length > 0 ? JSON.stringify(options) : JSON.stringify({})

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: body
            })

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}))
                const errorMsg = errorData.detail || errorData.message || `HTTP ${res.status}: Regeneration failed`
                throw new Error(errorMsg)
            }

            const data = await res.json()
            console.log('Regeneration success:', data)

            alert(`✅ ${data.message || 'Regenerated successfully!'}`)
            setRegenerateModalOpen(false)
            loadQueue()
        } catch (error: any) {
            console.error('Regeneration error:', error)
            const errorMessage = error.message || 'Failed to regenerate. Please try again.'
            alert(`❌ Error: ${errorMessage}`)
            // Don't throw - let modal stay open so user can try again
        }
    }

    const handleApproveText = async (postId: number) => {
        if (!confirm('Approve this text post?')) return

        try {
            const res = await fetch(`/api/content/${postId}/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}))
                throw new Error(errorData.detail || 'Approval failed')
            }

            const data = await res.json()
            console.log('Approval response:', data)

            // Always reload queue first
            await loadQueue()

            // If a video post was created, add it to generating set and switch to video tab
            if (data.video_post_id) {
                console.log('Video post created:', data.video_post_id)
                setGeneratingVideoIds(prev => new Set(prev).add(data.video_post_id))
                setActiveTab('video')
                // Reload again after a short delay to ensure video posts are loaded
                setTimeout(() => {
                    loadQueue()
                }, 500)
            } else {
                console.log('No video_post_id in response')
            }
        } catch (error: any) {
            console.error('Approval error:', error)
            alert('Error: ' + error.message)
        }
    }

    const handleApproveVideo = async (postId: number) => {
        if (!confirm('Approve this video?')) return

        try {
            await fetch(`/api/content/${postId}/approve-video`, { method: 'POST' })
            alert('✅ Video approved! Scheduled for publishing...')
            loadQueue()
        } catch (error: any) {
            alert('Error: ' + error.message)
        }
    }

    const handleReject = async (postId: number) => {
        if (!confirm('Reject this post?')) return

        try {
            await fetch(`/api/content/${postId}/reject`, { method: 'POST' })
            alert('Post rejected')
            loadQueue()
        } catch (error: any) {
            alert('Error: ' + error.message)
        }
    }

    const handleTestCompetitorVideo = async (postId: number) => {
        if (!confirm('Generate competitor-style video for this post?')) return

        try {
            const res = await fetch(`/api/video/competitor-test/${postId}`, {
                method: 'POST'
            })

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}))
                throw new Error(errorData.detail || 'Failed to generate test video')
            }

            const data = await res.json()
            alert(`✅ Video created!\n\nPath: ${data.video_path}\n\nCheck backend/output/test_videos/`)
        } catch (err: any) {
            alert('❌ Error: ' + err.message)
        }
    }

    // Show all posts in different tabs
    const textPosts = posts.filter(p => p.kind === 'text' && p.status === 'draft')
    const videoPosts = posts.filter(p => p.kind === 'video' && (p.status === 'video_production' || p.status === 'approved'))
    const scheduledPosts = posts.filter(p => p.status === 'ready_to_publish' || p.status === 'approved')
    const allApprovedPosts = posts.filter(p => p.status === 'approved')

    console.log('Filtered posts:', {
        textPosts: textPosts.length,
        videoPosts: videoPosts.length,
        scheduledPosts: scheduledPosts.length,
        allApproved: allApprovedPosts.length,
        videoPostsDetails: videoPosts.map((p: any) => ({ id: p.id, status: p.status, kind: p.kind }))
    })

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-center min-h-[50vh]">
                    <div className="text-center">
                        <Loader2 className="w-10 h-10 text-blue-500 animate-spin mx-auto mb-4" />
                        <p className="text-gray-400">Loading content queue...</p>
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
                    Content Queue
                </h1>
                <p className="text-gray-600 font-medium">Review and manage your content pipeline</p>
            </div>

            {/* Tabs */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-2 shadow-md">
                <div className="flex gap-2 overflow-x-auto">
                    <button
                        onClick={() => setActiveTab('text')}
                        className={`px-6 py-3 font-semibold transition-all whitespace-nowrap rounded-xl ${
                            activeTab === 'text'
                                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                                : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            📝 Text Posts
                            <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                                activeTab === 'text'
                                    ? 'bg-white/20 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {textPosts.length}
                            </span>
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('video')}
                        className={`px-6 py-3 font-semibold transition-all whitespace-nowrap rounded-xl ${
                            activeTab === 'video'
                                ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg'
                                : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            🎬 Video Production
                            <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                                activeTab === 'video'
                                    ? 'bg-white/20 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {videoPosts.length}
                            </span>
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('approved')}
                        className={`px-6 py-3 font-semibold transition-all whitespace-nowrap rounded-xl ${
                            activeTab === 'approved'
                                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                                : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            ✅ Approved
                            <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                                activeTab === 'approved'
                                    ? 'bg-white/20 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {allApprovedPosts.length}
                            </span>
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('scheduled')}
                        className={`px-6 py-3 font-semibold transition-all whitespace-nowrap rounded-xl ${
                            activeTab === 'scheduled'
                                ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg'
                                : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            📅 Scheduled
                            <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                                activeTab === 'scheduled'
                                    ? 'bg-white/20 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {scheduledPosts.length}
                            </span>
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('all')}
                        className={`px-6 py-3 font-semibold transition-all whitespace-nowrap rounded-xl ${
                            activeTab === 'all'
                                ? 'bg-gradient-to-r from-gray-700 to-gray-900 text-white shadow-lg'
                                : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            📋 All Posts
                            <span className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                                activeTab === 'all'
                                    ? 'bg-white/20 text-white'
                                    : 'bg-gray-200 text-gray-600'
                            }`}>
                                {posts.length}
                            </span>
                        </span>
                    </button>
                </div>
            </div>

            {/* TEXT POSTS TAB */}
            {activeTab === 'text' && (
                <div className="space-y-4">
                    {textPosts.length === 0 ? (
                        <div className="bg-white border-2 border-gray-200 rounded-2xl p-12 text-center shadow-md">
                            <FileText className="w-20 h-20 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-700 font-bold text-lg mb-1">No text posts awaiting approval</p>
                            <p className="text-sm text-gray-500">Generate content to get started</p>
                        </div>
                    ) : (
                        textPosts.map(post => (
                            <div key={post.id} className="bg-white border-2 border-gray-200 rounded-2xl p-6 hover:border-blue-300 hover:shadow-xl transition-all">
                                {/* Header with badges */}
                                <div className="flex flex-wrap items-center gap-2 mb-4">
                                    {post.regeneration_count > 0 && (
                                        <span className="badge badge-green">
                                            🔄 Regenerated {post.regeneration_count}x
                                        </span>
                                    )}
                                    {post.total_cost > 0 && (
                                        <span className="badge badge-blue">
                                            💰 ${(post.total_cost || 0).toFixed(3)}
                                        </span>
                                    )}
                                    {post.hook_type && (
                                        <span className="badge badge-yellow">
                                            🎯 {post.hook_type.replace(/_/g, ' ')}
                                        </span>
                                    )}
                                </div>

                                {/* Title */}
                                <h3 className="text-2xl font-bold text-gray-900 mb-4">{post.title}</h3>

                                {/* Content */}
                                <div className="bg-gradient-to-br from-gray-50 to-blue-50 border-2 border-gray-200 rounded-xl p-5 mb-4">
                                    <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                                        {post.body}
                                    </p>
                                </div>

                                {/* Meta info */}
                                <div className="space-y-3 mb-4">
                                    {/* Source */}
                                    {post.source_url && (
                                        <a
                                            href={post.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold text-sm transition-colors"
                                        >
                                            🔗 View Source
                                        </a>
                                    )}

                                    {/* Platforms */}
                                    {post.platforms && post.platforms.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {post.platforms.map((platform: string) => (
                                                <span
                                                    key={platform}
                                                    className="badge badge-purple"
                                                >
                                                    {platform}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {/* Hashtags */}
                                    {post.tags && post.tags.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {post.tags.map((tag: string, i: number) => (
                                                <span key={i} className="text-blue-600 font-semibold text-sm">#{tag}</span>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex flex-wrap gap-3 pt-5 border-t-2 border-gray-200">
                                    <button
                                        onClick={() => handleApproveText(post.id)}
                                        className="btn btn-success flex-1 min-w-[180px] py-3"
                                    >
                                        ✅ Approve Post
                                    </button>
                                    <button
                                        onClick={() => handleRegenerateText(post.id)}
                                        className="btn btn-secondary flex-1 min-w-[140px] py-3"
                                    >
                                        🔄 Regenerate
                                    </button>
                                    <button className="btn btn-ghost px-5 py-3">
                                        ✏️ Edit
                                    </button>
                                    <button
                                        onClick={() => handleReject(post.id)}
                                        className="btn btn-danger px-5 py-3"
                                    >
                                        ❌ Reject
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* VIDEO PRODUCTION TAB */}
            {activeTab === 'video' && (
                <div className="space-y-4">
                    {videoPosts.length === 0 ? (
                        <div className="bg-white border-2 border-gray-200 rounded-2xl p-12 text-center shadow-md">
                            <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-100 to-pink-100 rounded-2xl flex items-center justify-center text-6xl">
                                🎬
                            </div>
                            <p className="text-gray-700 font-bold text-lg mb-2">No videos in production</p>
                            <p className="text-sm text-gray-500 mb-4">Approve text posts to create videos</p>
                            <button
                                onClick={() => setActiveTab('text')}
                                className="btn btn-primary px-6 py-3"
                            >
                                Go to Text Posts
                            </button>
                        </div>
                    ) : (
                        videoPosts.map(post => {
                            const isGenerating = post.status === 'video_production'
                            const showProgress = isGenerating && generatingVideoIds.has(post.id)

                            // Debug logging for video posts
                            console.log('🎬 Rendering video post:', {
                                id: post.id,
                                title: post.title,
                                status: post.status,
                                has_assets: !!post.assets,
                                asset_count: post.assets?.length || 0,
                                first_asset: post.assets?.[0],
                                isGenerating,
                                showProgress
                            })

                            return (
                                <div key={post.id} className="bg-[#1A1D24] rounded-xl p-6">
                                    {isGenerating ? (
                                        <div className="flex items-center gap-2 mb-6">
                                            <Loader2 className="w-5 h-5 text-purple-500 animate-spin" />
                                            <span className="text-purple-400 font-medium">Generating video...</span>
                                            <span className="ml-auto text-purple-500 font-bold">In Progress</span>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2 mb-6">
                                            <span className="text-green-500">✅</span>
                                            <span className="text-white font-medium">Video ready for review</span>
                                            <span className="ml-auto text-green-500 font-bold">100%</span>
                                        </div>
                                    )}

                                    {/* VIDEO PLAYER - Show if video exists, otherwise show placeholder */}
                                    {post.assets && post.assets.length > 0 && post.assets[0].path ? (
                                        <VideoPlayer
                                            videoUrl={`/output/${post.assets[0].path}`}
                                            duration={post.video_duration || 18}
                                            title={post.title}
                                        />
                                    ) : isGenerating ? (
                                        <div className="aspect-[9/16] max-w-[400px] mx-auto bg-gray-900 rounded-lg flex items-center justify-center">
                                            <div className="text-center">
                                                <Loader2 className="w-16 h-16 text-purple-500 animate-spin mx-auto mb-4" />
                                                <p className="text-white font-medium">Generating video...</p>
                                                <p className="text-gray-400 text-sm mt-2">Using Eleven Labs & StockStack</p>
                                                <button
                                                    onClick={async () => {
                                                        try {
                                                            await fetch(`/api/content/${post.id}/generate-video`, { method: 'POST' })
                                                            alert('Video generation triggered!')
                                                            loadQueue()
                                                        } catch (e: any) {
                                                            alert('Error: ' + e.message)
                                                        }
                                                    }}
                                                    className="mt-4 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm"
                                                >
                                                    Force Generate Video
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="aspect-[9/16] max-w-[400px] mx-auto bg-gray-900 rounded-lg flex items-center justify-center">
                                            <div className="text-center">
                                                <p className="text-white font-medium mb-4">No video generated yet</p>
                                                <button
                                                    onClick={async () => {
                                                        try {
                                                            await fetch(`/api/content/${post.id}/generate-video`, { method: 'POST' })
                                                            alert('Video generation started!')
                                                            loadQueue()
                                                        } catch (e: any) {
                                                            alert('Error: ' + e.message)
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg"
                                                >
                                                    Generate Video Now
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {/* Details */}
                                    <div className="mt-6">
                                        <h3 className="text-2xl font-bold text-white mb-4">{post.title}</h3>

                                        {/* Script */}
                                        <div className="bg-[#0E1117] rounded-lg p-5 mb-4 border border-gray-800">
                                            <div className="text-sm text-gray-400 mb-2">📜 Video Script:</div>
                                            <p className="text-white whitespace-pre-wrap">{post.body}</p>
                                        </div>

                                        {/* Platforms */}
                                        <div className="flex gap-2 mb-4">
                                            {post.platforms?.map((platform: string) => (
                                                <span
                                                    key={platform}
                                                    className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm"
                                                >
                                                    {platform}
                                                </span>
                                            ))}
                                        </div>

                                        {/* Video Stats */}
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 p-4 bg-[#0E1117] rounded-lg">
                                            <div>
                                                <div className="text-gray-400 text-xs">Duration</div>
                                                <div className="text-white font-bold">{post.video_duration || 18}s</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400 text-xs">Format</div>
                                                <div className="text-white font-bold">9:16</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400 text-xs">Voiceover</div>
                                                <div className="text-green-500 font-bold">✅</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-400 text-xs">Captions</div>
                                                <div className="text-green-500 font-bold">✅</div>
                                            </div>
                                        </div>

                                        {/* Actions */}
                                        <div className="flex flex-wrap gap-3">
                                            <button
                                                onClick={() => handleRegenerateVideo(post.id)}
                                                className="flex-1 min-w-[200px] bg-gray-700 hover:bg-gray-600 text-white px-5 py-3 rounded-lg font-medium"
                                            >
                                                🔄 Regenerate Video (~$0.15)
                                            </button>
                                            <button
                                                onClick={() => handleApproveVideo(post.id)}
                                                className="flex-1 min-w-[200px] bg-green-500 hover:bg-green-600 text-white px-5 py-3 rounded-lg font-bold"
                                            >
                                                ✅ Approve Video
                                            </button>
                                            <button
                                                onClick={() => handleTestCompetitorVideo(post.id)}
                                                className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                                            >
                                                🧪 Test Competitor Video
                                            </button>
                                            <button className="bg-gray-700 hover:bg-gray-600 text-white px-5 py-3 rounded-lg">
                                                ✏️
                                            </button>
                                            <button
                                                onClick={() => handleReject(post.id)}
                                                className="bg-red-500 hover:bg-red-600 text-white px-5 py-3 rounded-lg"
                                            >
                                                ❌
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )
                        })
                    )}
                </div>
            )}

            {/* APPROVED TAB */}
            {activeTab === 'approved' && (
                <div className="space-y-6">
                    {allApprovedPosts.length === 0 ? (
                        <div className="text-center py-12 text-gray-400">
                            No approved posts
                        </div>
                    ) : (
                        allApprovedPosts.map(post => (
                            <div key={post.id} className="bg-[#1A1D24] rounded-xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div>
                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="text-2xl">{post.kind === 'video' ? '🎬' : '📝'}</span>
                                            <span className={`px-3 py-1 rounded-full text-sm ${post.kind === 'video'
                                                ? 'bg-purple-500/20 text-purple-400'
                                                : 'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {post.kind}
                                            </span>
                                            <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400">
                                                {post.status}
                                            </span>
                                        </div>
                                        <h3 className="text-xl font-bold text-white">{post.title}</h3>
                                    </div>
                                </div>
                                <div className="bg-[#0E1117] rounded-lg p-4 mb-4 border border-gray-800">
                                    <p className="text-white whitespace-pre-wrap text-sm">{post.body}</p>
                                </div>
                                {post.kind === 'video' && (
                                    <div className="mb-4">
                                        <VideoPlayer
                                            videoUrl={post.assets?.[0]?.path ? `/output/${post.assets[0].path}` : 'https://www.w3schools.com/html/mov_bbb.mp4'}
                                            duration={post.video_duration || 18}
                                            title={post.title}
                                        />
                                    </div>
                                )}
                                <div className="flex gap-2 mb-4">
                                    {post.platforms?.map((platform: string) => (
                                        <span
                                            key={platform}
                                            className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm"
                                        >
                                            {platform}
                                        </span>
                                    ))}
                                </div>
                                {post.kind === 'video' && (
                                    <div className="flex gap-2 pt-4 border-t border-gray-800">
                                        <button
                                            onClick={() => handleTestCompetitorVideo(post.id)}
                                            className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
                                        >
                                            🧪 Test Competitor Video
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* SCHEDULED TAB */}
            {activeTab === 'scheduled' && (
                <div className="space-y-6">
                    {scheduledPosts.length === 0 ? (
                        <div className="text-center py-12 text-gray-400">
                            No posts scheduled
                        </div>
                    ) : (
                        scheduledPosts.map(post => (
                            <div key={post.id} className="bg-[#1A1D24] rounded-xl p-6">
                                <h3 className="text-xl font-bold text-white">{post.title}</h3>
                                <p className="text-gray-400 mt-2">Scheduled for publishing</p>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* ALL POSTS TAB */}
            {activeTab === 'all' && (
                <div className="space-y-6">
                    {posts.length === 0 ? (
                        <div className="text-center py-12 text-gray-400">
                            No posts found
                        </div>
                    ) : (
                        posts.map(post => (
                            <div key={post.id} className="bg-[#1A1D24] rounded-xl p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <span className="text-2xl">{post.kind === 'video' ? '🎬' : '📝'}</span>
                                        <h3 className="text-xl font-bold text-white">{post.title}</h3>
                                    </div>
                                    <div className="flex gap-2">
                                        <span className={`px-3 py-1 rounded-full text-xs ${post.status === 'draft' ? 'bg-yellow-500/20 text-yellow-400' :
                                            post.status === 'approved' ? 'bg-green-500/20 text-green-400' :
                                                post.status === 'video_production' ? 'bg-purple-500/20 text-purple-400' :
                                                    'bg-gray-500/20 text-gray-400'
                                            }`}>
                                            {post.status}
                                        </span>
                                        <span className={`px-3 py-1 rounded-full text-xs ${post.kind === 'video' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
                                            }`}>
                                            {post.kind}
                                        </span>
                                    </div>
                                </div>
                                <div className="bg-[#0E1117] rounded-lg p-4 mb-4 border border-gray-800">
                                    <p className="text-white whitespace-pre-wrap text-sm line-clamp-3">{post.body}</p>
                                </div>
                                <div className="flex gap-2">
                                    {post.platforms?.map((platform: string) => (
                                        <span
                                            key={platform}
                                            className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-full text-xs"
                                        >
                                            {platform}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Regenerate Modal */}
            <RegenerateModal
                isOpen={regenerateModalOpen}
                onClose={() => {
                    setRegenerateModalOpen(false)
                    setSelectedPostId(null)
                }}
                postId={selectedPostId || 0}
                postType={selectedPostType}
                onRegenerate={handleRegenerateSubmit}
            />

            {/* Video Generation Progress Modals */}
            {Array.from(generatingVideoIds).map(videoId => {
                const post = posts.find(p => p.id === videoId && p.kind === 'video')
                const isGenerating = post && post.status === 'video_production'

                // If post not found or status changed, remove from generating set
                if (!post || post.status !== 'video_production') {
                    setTimeout(() => {
                        setGeneratingVideoIds(prev => {
                            const next = new Set(prev)
                            next.delete(videoId)
                            return next
                        })
                    }, 100)
                    return null
                }

                return (
                    <VideoGenerationProgress
                        key={videoId}
                        postId={videoId}
                        isGenerating={isGenerating}
                        onComplete={() => {
                            setGeneratingVideoIds(prev => {
                                const next = new Set(prev)
                                next.delete(videoId)
                                return next
                            })
                            loadQueue()
                        }}
                    />
                )
            })}

            {/* Also show progress for any video posts in production that aren't tracked */}
            {videoPosts
                .filter(post => post.status === 'video_production' && !generatingVideoIds.has(post.id))
                .map(post => (
                    <VideoGenerationProgress
                        key={`auto-${post.id}`}
                        postId={post.id}
                        isGenerating={true}
                        onComplete={() => {
                            loadQueue()
                        }}
                    />
                ))}
        </div>
    )
}
