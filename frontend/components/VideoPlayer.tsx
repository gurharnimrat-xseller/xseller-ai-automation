'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX, Maximize2 } from 'lucide-react'

interface VideoPlayerProps {
  videoUrl: string
  thumbnailUrl?: string
  duration?: number
  title?: string
}

export default function VideoPlayer({
  videoUrl,
  thumbnailUrl,
  duration = 18,
  title
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [videoDuration, setVideoDuration] = useState(duration)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    console.log('[VideoPlayer] Initialized with videoUrl:', videoUrl)
  }, [videoUrl])

  const togglePlay = () => {
    if (!videoRef.current) return
    
    if (isPlaying) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const toggleMute = () => {
    if (!videoRef.current) return
    videoRef.current.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const toggleFullscreen = () => {
    if (!videoRef.current) return
    
    if (document.fullscreenElement) {
      document.exitFullscreen()
    } else {
      videoRef.current.requestFullscreen()
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setVideoDuration(videoRef.current.duration)
      setIsLoading(false)
      console.log('[VideoPlayer] Metadata loaded, duration:', videoRef.current.duration)
    }
  }

  const handleError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    const videoElement = e.currentTarget
    const error = videoElement.error
    const errorMessage = error
      ? `Video Error ${error.code}: ${error.message}`
      : 'Unknown video error'
    console.error('[VideoPlayer] Error loading video:', errorMessage, 'URL:', videoUrl)
    setError(errorMessage)
    setIsLoading(false)
  }

  const handleCanPlay = () => {
    console.log('[VideoPlayer] Video can play')
    setIsLoading(false)
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="relative bg-black rounded-lg overflow-hidden group">
      {/* Video Container - Vertical 9:16 for TikTok/YouTube Shorts */}
      <div className="aspect-[9/16] max-w-[360px] mx-auto relative">
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-900/80 z-50 p-4">
            <div className="text-center text-white">
              <p className="font-bold mb-2">Video Error</p>
              <p className="text-sm">{error}</p>
              <p className="text-xs mt-2 opacity-70">URL: {videoUrl}</p>
            </div>
          </div>
        )}
        {isLoading && !error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-40">
            <div className="text-center text-white">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-2"></div>
              <p className="text-sm">Loading video...</p>
            </div>
          </div>
        )}
        <video
          ref={videoRef}
          src={videoUrl}
          poster={thumbnailUrl}
          className="w-full h-full object-cover"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onError={handleError}
          onCanPlay={handleCanPlay}
          playsInline
          preload="metadata"
        />

        {/* Play Overlay */}
        <div 
          className="absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
          onClick={togglePlay}
        >
          {!isPlaying && (
            <div className="bg-green-500/90 rounded-full p-6 hover:bg-green-600 transition">
              <Play className="w-12 h-12 text-white fill-white" />
            </div>
          )}
        </div>

        {/* Duration Badge */}
        <div className="absolute top-3 right-3 bg-black/80 px-3 py-1 rounded-full text-white text-sm font-medium">
          {formatTime(videoDuration)}
        </div>

        {/* Title Overlay */}
        {title && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <p className="text-white text-sm font-medium line-clamp-2">{title}</p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-900 p-4">
        {/* Progress Bar */}
        <input
          type="range"
          min="0"
          max={videoDuration}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer mb-3"
          style={{
            background: `linear-gradient(to right, #10F4A0 0%, #10F4A0 ${(currentTime / videoDuration) * 100}%, #374151 ${(currentTime / videoDuration) * 100}%, #374151 100%)`
          }}
        />

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="text-white hover:text-green-500 transition"
            >
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
            </button>
            
            <button
              onClick={toggleMute}
              className="text-white hover:text-green-500 transition"
            >
              {isMuted ? <VolumeX className="w-6 h-6" /> : <Volume2 className="w-6 h-6" />}
            </button>

            <span className="text-white text-sm">
              {formatTime(currentTime)} / {formatTime(videoDuration)}
            </span>
          </div>

          <button
            onClick={toggleFullscreen}
            className="text-white hover:text-green-500 transition"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}

