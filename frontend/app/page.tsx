'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { FileText, CheckCircle, Send, AlertCircle, XCircle, Loader2, Sparkles, TrendingUp, Clock } from 'lucide-react'
import ContentProgress from '@/components/ContentProgress'

export default function Dashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<any>(null)
  const [recentPosts, setRecentPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      // Load stats
      const statsRes = await fetch('/api/stats/dashboard')
      const statsData = await statsRes.json()
      setStats(statsData.queue_stats || {})

      // Load recent posts
      const postsRes = await fetch('/api/content/queue?limit=10')
      const postsData = await postsRes.json()
      setRecentPosts(postsData.posts?.slice(0, 10) || [])

      setLoading(false)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      setLoading(false)
    }
  }

  const handleGenerateDemo = () => {
    setIsGenerating(true)
  }

  const handleProgressComplete = async () => {
    try {
      // First check if backend is reachable
      try {
        const healthCheck = await fetch('/api/health')
        if (!healthCheck.ok) {
          throw new Error('Backend server is not responding. Please make sure the backend is running on port 8000.')
        }
      } catch (healthError: any) {
        if (healthError.message.includes('Failed to fetch') || healthError.message.includes('NetworkError')) {
          throw new Error('Cannot connect to backend server. Please start it:\n\ncd backend\nsource venv/bin/activate\nuvicorn app.main:app --host 0.0.0.0 --port 8000 --reload')
        }
        throw healthError
      }

      // Call the actual generation endpoint
      const res = await fetch('/api/content/generate-demo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!res.ok) {
        // Try to get error details from response
        let errorMessage = `HTTP ${res.status}: Generation failed`
        try {
          const errorData = await res.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
          // If response is not JSON, use status text
          errorMessage = res.statusText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data = await res.json()
      console.log('Generated:', data)

      setIsGenerating(false)

      // Show success and redirect
      alert(`✅ Created ${data.count || 20} sample posts! Redirecting to Queue...`)
      setTimeout(() => {
        router.push('/queue')
      }, 500)
    } catch (error: any) {
      console.error('Error generating content:', error)
      const errorMsg = error.message || 'Unknown error. Please check console and backend logs.'
      alert(`❌ Error generating content:\n\n${errorMsg}`)
      setIsGenerating(false)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'Drafts',
      value: stats?.draft || 0,
      icon: FileText,
      gradient: 'from-amber-400 to-orange-500',
      iconBg: 'bg-gradient-to-br from-amber-400 to-orange-500',
      shadowColor: 'shadow-orange-200'
    },
    {
      title: 'Approved',
      value: stats?.approved || 0,
      icon: CheckCircle,
      gradient: 'from-emerald-400 to-green-600',
      iconBg: 'bg-gradient-to-br from-emerald-400 to-green-600',
      shadowColor: 'shadow-green-200'
    },
    {
      title: 'Published Today',
      value: stats?.published_today || 0,
      icon: Send,
      gradient: 'from-blue-400 to-indigo-600',
      iconBg: 'bg-gradient-to-br from-blue-400 to-indigo-600',
      shadowColor: 'shadow-blue-200'
    },
    {
      title: 'Overdue',
      value: stats?.overdue || 0,
      icon: AlertCircle,
      gradient: 'from-red-400 to-pink-600',
      iconBg: 'bg-gradient-to-br from-red-400 to-pink-600',
      shadowColor: 'shadow-red-200'
    },
    {
      title: 'Failed',
      value: stats?.failed || 0,
      icon: XCircle,
      gradient: 'from-orange-400 to-red-500',
      iconBg: 'bg-gradient-to-br from-orange-400 to-red-500',
      shadowColor: 'shadow-orange-200'
    }
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 font-medium">Manage and monitor your content automation</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-3 bg-white border-2 border-gray-200 rounded-xl shadow-sm">
          <Clock className="w-4 h-4 text-blue-500" />
          <span className="text-sm text-gray-700 font-semibold">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.title}
              className={`bg-white border-2 border-gray-200 rounded-2xl p-5 hover:shadow-xl hover:border-gray-300 transition-all group cursor-pointer hover:-translate-y-1`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl ${card.iconBg} group-hover:scale-110 transition-transform shadow-lg ${card.shadowColor}`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-3xl font-bold text-gray-900">{card.value}</p>
                <p className="text-sm text-gray-600 font-semibold">{card.title}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generate Content Card */}
        <div className="bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-[3px] rounded-2xl shadow-2xl shadow-blue-200 hover:shadow-3xl transition-all">
          <div className="bg-white rounded-2xl p-6 h-full relative overflow-hidden">
            <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-blue-200 to-purple-200 rounded-full blur-3xl opacity-50"></div>
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl shadow-lg">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Content Generation
                </h2>
              </div>
              <p className="text-gray-600 mb-6 font-medium">
                Generate AI-powered content for your social media channels
              </p>

              <button
                onClick={handleGenerateDemo}
                disabled={isGenerating}
                className="w-full btn btn-primary py-4 text-base font-bold flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Generating Content...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-6 h-6" />
                    Generate Demo Content
                  </>
                )}
              </button>

              <div className="mt-4 flex items-center justify-between text-xs font-semibold">
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full">20 posts</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full">~2-3 minutes</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Card */}
        <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-gradient-to-br from-emerald-400 to-green-600 rounded-xl shadow-lg shadow-green-200">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Performance</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
              <span className="text-sm text-gray-700 font-semibold">Total Content</span>
              <span className="text-2xl font-bold text-blue-600">{(stats?.draft || 0) + (stats?.approved || 0) + (stats?.published_today || 0)}</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
              <span className="text-sm text-gray-700 font-semibold">Success Rate</span>
              <span className="text-2xl font-bold text-green-600">
                {stats?.failed > 0
                  ? Math.round(((stats?.approved || 0) / ((stats?.approved || 0) + (stats?.failed || 1))) * 100)
                  : 100}%
              </span>
            </div>
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl">
              <span className="text-sm text-gray-700 font-semibold">Active Queue</span>
              <span className="text-2xl font-bold text-purple-600">{stats?.draft || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Activity</h2>
          <button
            onClick={() => router.push('/queue')}
            className="px-4 py-2 text-sm font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-all"
          >
            View all →
          </button>
        </div>

        {recentPosts.length === 0 ? (
          <div className="text-center py-12 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl border-2 border-dashed border-gray-300">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-700 font-semibold mb-1">No recent posts</p>
            <p className="text-sm text-gray-500">Generate some content to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentPosts.map((post) => (
              <div
                key={post.id}
                onClick={() => router.push('/queue')}
                className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white hover:from-blue-50 hover:to-purple-50 border border-gray-200 hover:border-blue-300 rounded-xl transition-all cursor-pointer group"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-sm ${
                    post.kind === 'video'
                      ? 'bg-gradient-to-br from-purple-400 to-pink-500'
                      : 'bg-gradient-to-br from-blue-400 to-indigo-500'
                  }`}>
                    <span className="text-2xl">
                      {post.kind === 'video' ? '🎬' : '📝'}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-gray-900 font-bold group-hover:text-blue-600 transition-colors">
                      {post.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`badge ${
                        post.status === 'draft' ? 'badge-yellow' :
                        post.status === 'approved' ? 'badge-green' :
                        post.status === 'video_production' ? 'badge-purple' :
                        'badge-blue'
                      }`}>
                        {post.status}
                      </span>
                      <span className="text-gray-400 text-xs">•</span>
                      <span className="text-gray-600 text-xs font-medium">
                        {formatTimeAgo(post.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-gray-400 group-hover:text-blue-600 transition-colors text-xl">
                  →
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Progress Modal */}
      <ContentProgress
        isGenerating={isGenerating}
        onComplete={handleProgressComplete}
      />
    </div>
  )
}
