'use client'

import { useState } from 'react'
import { X, Loader2 } from 'lucide-react'

interface RegenerateModalProps {
  isOpen: boolean
  onClose: () => void
  postId: number
  postType: 'text' | 'video'
  onRegenerate: (options: RegenerateOptions) => Promise<void>
}

interface RegenerateOptions {
  variantCount: number
  customInstructions?: string
  changeHookStyle?: boolean
  changeTone?: boolean
}

export default function RegenerateModal({
  isOpen,
  onClose,
  postId,
  postType,
  onRegenerate
}: RegenerateModalProps) {
  const [variantCount, setVariantCount] = useState(3)
  const [customInstructions, setCustomInstructions] = useState('')
  const [changeHookStyle, setChangeHookStyle] = useState(false)
  const [changeTone, setChangeTone] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)

  const costPerVariant = postType === 'text' ? 0.002 : 0.067
  const totalCost = (costPerVariant * variantCount).toFixed(3)
  const newPostCost = postType === 'text' ? 0.30 : 0.40
  const savings = ((1 - (parseFloat(totalCost) / newPostCost)) * 100).toFixed(0)

  const handleRegenerate = async () => {
    setIsRegenerating(true)
    
    try {
      await onRegenerate({
        variantCount,
        customInstructions: customInstructions.trim() || undefined,
        changeHookStyle,
        changeTone
      })
      onClose()
    } catch (error) {
      console.error('Regeneration failed:', error)
      alert('Failed to regenerate. Please try again.')
    } finally {
      setIsRegenerating(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#1A1D24] rounded-2xl max-w-2xl w-full border border-gray-800 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <h2 className="text-2xl font-bold text-white">
            Regenerate {postType === 'text' ? 'Text' : 'Video'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Cost Savings Banner */}
        <div className="bg-gradient-to-r from-green-500/20 to-blue-500/20 border border-green-500/30 m-6 p-6 rounded-xl text-center">
          <div className="text-4xl font-bold text-green-400 mb-2">
            💰 {savings}% Cheaper
          </div>
          <div className="text-gray-300">
            Than creating new content
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Variant Count */}
          <div>
            <label className="block text-white font-medium mb-3">
              Number of Variants
            </label>
            <div className="flex gap-3">
              {[1, 3, 5].map(count => (
                <button
                  key={count}
                  onClick={() => setVariantCount(count)}
                  className={`flex-1 py-3 rounded-lg font-medium transition ${
                    variantCount === count
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {count} {count === 1 ? 'Variant' : 'Variants'}
                </button>
              ))}
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={changeHookStyle}
                onChange={(e) => setChangeHookStyle(e.target.checked)}
                className="w-5 h-5 rounded border-gray-700 bg-gray-800 checked:bg-green-500"
              />
              <span className="text-white">Try different hook style</span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={changeTone}
                onChange={(e) => setChangeTone(e.target.checked)}
                className="w-5 h-5 rounded border-gray-700 bg-gray-800 checked:bg-green-500"
              />
              <span className="text-white">Change tone (more casual/formal)</span>
            </label>
          </div>

          {/* Custom Instructions */}
          <div>
            <label className="block text-white font-medium mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="E.g., Make it more engaging, Add statistics, Focus on benefits..."
              className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-green-500 focus:outline-none resize-none"
              rows={3}
            />
          </div>

          {/* Cost Breakdown */}
          <div className="bg-gray-900 rounded-lg p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Cost per variant:</span>
              <span className="text-white font-medium">${costPerVariant.toFixed(3)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Number of variants:</span>
              <span className="text-white font-medium">{variantCount}</span>
            </div>
            <div className="h-px bg-gray-700 my-2"></div>
            <div className="flex justify-between">
              <span className="text-white font-medium">Total cost:</span>
              <span className="text-green-400 font-bold text-lg">${totalCost}</span>
            </div>
            <div className="text-sm text-gray-400 text-center mt-2">
              vs ${newPostCost.toFixed(2)} for new content
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t border-gray-800">
          <button
            onClick={onClose}
            disabled={isRegenerating}
            className="flex-1 px-6 py-3 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50 text-white rounded-lg font-medium transition"
          >
            Cancel
          </button>
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="flex-1 px-6 py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white rounded-lg font-bold transition flex items-center justify-center gap-2"
          >
            {isRegenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Regenerating...
              </>
            ) : (
              <>Regenerate for ${totalCost}</>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

