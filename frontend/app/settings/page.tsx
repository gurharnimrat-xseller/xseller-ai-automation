'use client'

import { Key, Clock, Globe, Save, Bell, Shield, Palette } from 'lucide-react'
import { useState } from 'react'

export default function SettingsPage() {
    const [saved, setSaved] = useState(false)

    const handleSave = () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
    }

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 bg-clip-text text-transparent mb-2">
                    Settings
                </h1>
                <p className="text-gray-600 font-medium">Configure your automation preferences</p>
            </div>

            {/* API Keys Section */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                        <Key className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-gray-700 text-sm font-semibold mb-2">OpenAI API Key</label>
                        <input
                            type="password"
                            placeholder="sk-..."
                            className="input"
                        />
                        <p className="text-xs text-gray-500 mt-1">Used for content generation and AI processing</p>
                    </div>

                    <div>
                        <label className="block text-gray-700 text-sm font-semibold mb-2">ElevenLabs API Key</label>
                        <input
                            type="password"
                            placeholder="el_..."
                            className="input"
                        />
                        <p className="text-xs text-gray-500 mt-1">Required for voice generation in videos</p>
                    </div>

                    <div>
                        <label className="block text-gray-700 text-sm font-semibold mb-2">Pexels API Key</label>
                        <input
                            type="password"
                            placeholder="pex_..."
                            className="input"
                        />
                        <p className="text-xs text-gray-500 mt-1">For sourcing stock videos and images</p>
                    </div>
                </div>
            </div>

            {/* Posting Schedule Section */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl shadow-lg">
                        <Clock className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Posting Schedule</h2>
                </div>

                <div className="space-y-6">
                    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200">
                        <div>
                            <span className="text-gray-900 font-bold">Auto-posting Enabled</span>
                            <p className="text-xs text-gray-600 mt-1">Automatically publish approved content</p>
                        </div>
                        <label className="relative inline-block w-14 h-7 cursor-pointer">
                            <input type="checkbox" className="sr-only peer" defaultChecked />
                            <div className="w-full h-full bg-gray-300 peer-checked:bg-gradient-to-r peer-checked:from-green-500 peer-checked:to-emerald-600 rounded-full peer transition-all shadow-inner"></div>
                            <div className="absolute left-1 top-1 w-5 h-5 bg-white rounded-full peer-checked:translate-x-7 transition-all shadow-md"></div>
                        </label>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-gray-700 text-sm font-semibold mb-2">Morning Post</label>
                            <input
                                type="time"
                                defaultValue="07:30"
                                className="input"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700 text-sm font-semibold mb-2">Afternoon Post</label>
                            <input
                                type="time"
                                defaultValue="12:30"
                                className="input"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700 text-sm font-semibold mb-2">Evening Post</label>
                            <input
                                type="time"
                                defaultValue="21:00"
                                className="input"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Platform Preferences Section */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg">
                        <Globe className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Platform Preferences</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                        { name: 'YouTube Shorts', icon: '📹', color: 'from-red-100 to-pink-100' },
                        { name: 'TikTok', icon: '🎵', color: 'from-cyan-100 to-blue-100' },
                        { name: 'LinkedIn', icon: '💼', color: 'from-blue-100 to-indigo-100' },
                        { name: 'X (Twitter)', icon: '🐦', color: 'from-sky-100 to-cyan-100' },
                        { name: 'Instagram Reels', icon: '📸', color: 'from-purple-100 to-pink-100' },
                        { name: 'Facebook', icon: '👥', color: 'from-blue-100 to-purple-100' }
                    ].map((platform) => (
                        <label key={platform.name} className={`flex items-center gap-3 p-4 bg-gradient-to-r ${platform.color} border-2 border-gray-200 rounded-xl cursor-pointer hover:border-blue-300 hover:shadow-md transition-all`}>
                            <input
                                type="checkbox"
                                defaultChecked={platform.name !== 'Instagram Reels'}
                                className="w-5 h-5 rounded border-2 border-gray-300 checked:bg-blue-500 focus:ring-2 focus:ring-blue-500 cursor-pointer"
                            />
                            <span className="text-2xl">{platform.icon}</span>
                            <span className="text-gray-900 font-bold">{platform.name}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Notifications Section */}
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl shadow-lg">
                        <Bell className="w-6 h-6 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Notifications</h2>
                </div>

                <div className="space-y-3">
                    {[
                        { label: 'Email notifications for new content', checked: true },
                        { label: 'Push notifications for approvals', checked: true },
                        { label: 'Weekly performance reports', checked: false },
                        { label: 'Content generation alerts', checked: true }
                    ].map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <span className="text-gray-900 font-medium">{item.label}</span>
                            <label className="relative inline-block w-12 h-6 cursor-pointer">
                                <input type="checkbox" className="sr-only peer" defaultChecked={item.checked} />
                                <div className="w-full h-full bg-gray-300 peer-checked:bg-gradient-to-r peer-checked:from-blue-500 peer-checked:to-indigo-600 rounded-full peer transition-all"></div>
                                <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full peer-checked:translate-x-6 transition-all"></div>
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center gap-4">
                <button
                    onClick={handleSave}
                    className="btn btn-success flex items-center gap-2 px-8 py-4 text-lg"
                >
                    <Save className="w-5 h-5" />
                    Save All Settings
                </button>

                {saved && (
                    <div className="flex items-center gap-2 px-6 py-3 bg-green-100 border-2 border-green-500 rounded-xl text-green-700 font-bold animate-fadeIn">
                        ✓ Settings saved successfully!
                    </div>
                )}
            </div>
        </div>
    )
}
