'use client'

import { useState, useEffect } from 'react'
import { Loader2, CheckCircle, Circle } from 'lucide-react'

interface ContentProgressProps {
  isGenerating: boolean
  onComplete?: () => void
}

interface Step {
  id: number
  label: string
  duration: number
  status: 'pending' | 'in_progress' | 'complete'
}

export default function ContentProgress({ isGenerating, onComplete }: ContentProgressProps) {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [steps, setSteps] = useState<Step[]>([
    { id: 1, label: 'Fetching RSS feeds (6 sources)', duration: 5, status: 'pending' },
    { id: 2, label: 'Ranking articles by relevance', duration: 3, status: 'pending' },
    { id: 3, label: 'Selecting top 12 articles', duration: 1, status: 'pending' },
    { id: 4, label: 'Generating text posts (12 articles)', duration: 20, status: 'pending' },
    { id: 5, label: 'Generating video scripts', duration: 20, status: 'pending' },
    { id: 6, label: 'Creating videos (36 total)', duration: 40, status: 'pending' },
    { id: 7, label: 'Adding voiceovers', duration: 20, status: 'pending' },
    { id: 8, label: 'Saving to database', duration: 3, status: 'pending' },
    { id: 9, label: 'Complete! Ready for review', duration: 0, status: 'pending' }
  ])

  const totalDuration = steps.reduce((sum, step) => sum + step.duration, 0)
  const remainingTime = Math.max(0, totalDuration - elapsedTime)

  useEffect(() => {
    if (!isGenerating) return

    const startTime = Date.now()
    const interval = setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000
      setElapsedTime(elapsed)

      // Calculate progress
      let cumulativeTime = 0
      let newCurrentStep = 0

      for (let i = 0; i < steps.length; i++) {
        if (elapsed < cumulativeTime + steps[i].duration) {
          newCurrentStep = i
          break
        }
        cumulativeTime += steps[i].duration
      }

      setCurrentStep(newCurrentStep)
      setProgress(Math.min((elapsed / totalDuration) * 100, 99))

      // Update step statuses
      setSteps(prevSteps =>
        prevSteps.map((step, index) => ({
          ...step,
          status:
            index < newCurrentStep
              ? 'complete'
              : index === newCurrentStep
              ? 'in_progress'
              : 'pending'
        }))
      )

      // Complete
      if (elapsed >= totalDuration) {
        setProgress(100)
        setSteps(prevSteps =>
          prevSteps.map(step => ({ ...step, status: 'complete' as const }))
        )
        clearInterval(interval)
        setTimeout(() => {
          onComplete?.()
        }, 1000)
      }
    }, 500)

    return () => clearInterval(interval)
  }, [isGenerating, onComplete, totalDuration])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!isGenerating) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#1A1D24] rounded-2xl p-8 max-w-2xl w-full border border-gray-800">
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            🎬 Generating AI Content
          </h2>
          <p className="text-gray-400">Creating viral posts and videos...</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-white font-bold text-lg">{Math.round(progress)}%</span>
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                Elapsed: <span className="text-white font-medium">{formatTime(elapsedTime)}</span>
              </span>
              <span className="text-gray-600">|</span>
              <span className="text-gray-400">
                Remaining: <span className="text-green-400 font-medium">{formatTime(remainingTime)}</span>
              </span>
            </div>
          </div>

          <div className="h-4 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-blue-500 transition-all duration-500 ease-out relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-start gap-3 p-4 rounded-lg transition-all ${
                step.status === 'complete'
                  ? 'bg-green-500/10 border border-green-500/20'
                  : step.status === 'in_progress'
                  ? 'bg-blue-500/10 border border-blue-500/20 scale-105'
                  : 'bg-gray-800/50'
              }`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {step.status === 'complete' && (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
                {step.status === 'in_progress' && (
                  <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                )}
                {step.status === 'pending' && (
                  <Circle className="w-5 h-5 text-gray-600" />
                )}
              </div>

              <div className="flex-1">
                <span
                  className={`font-medium ${
                    step.status === 'complete'
                      ? 'text-green-500'
                      : step.status === 'in_progress'
                      ? 'text-blue-400'
                      : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>

                {step.status === 'in_progress' && step.duration > 0 && (
                  <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 animate-pulse w-3/4"></div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        {progress < 100 && (
          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <p className="text-sm text-blue-400 text-center">
              💡 <strong>Tip:</strong> This takes 2-3 minutes. You can close this and come back!
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

