'use client'

import { Key, Clock, Globe, Save } from 'lucide-react'

import { useState } from 'react'

export default function SettingsPage() {
    const [saved, setSaved] = useState(false)

    const handleSave = () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
    }

    return (
        <div className="p-8 max-w-4xl">
            <h1 className="text-3xl font-bold text-white mb-8">Settings</h1>

            {/* API Keys Section */}
            <div className="bg-[#1A1D24] rounded-xl p-6 mb-6">
                <div className="flex items-center gap-3 mb-4">
                    <Key className="w-6 h-6 text-[#10F4A0]" />
                    <h2 className="text-xl font-bold text-white">API Keys</h2>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-gray-400 text-sm mb-2">OpenAI API Key</label>
                        <input
                            type="password"
                            placeholder="sk-..."
                            className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-[#10F4A0] focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-400 text-sm mb-2">Publer API Key</label>
                        <input
                            type="password"
                            placeholder="publ_..."
                            className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-[#10F4A0] focus:outline-none"
                        />
                    </div>

                    <div>
                        <label className="block text-gray-400 text-sm mb-2">InVideo API Key</label>
                        <input
                            type="password"
                            placeholder="inv_..."
                            className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-[#10F4A0] focus:outline-none"
                        />
                    </div>
                </div>
            </div>

            {/* Posting Schedule Section */}
            <div className="bg-[#1A1D24] rounded-xl p-6 mb-6">
                <div className="flex items-center gap-3 mb-4">
                    <Clock className="w-6 h-6 text-[#10F4A0]" />
                    <h2 className="text-xl font-bold text-white">Posting Schedule</h2>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <span className="text-gray-400">Auto-posting Enabled</span>
                        <label className="relative inline-block w-12 h-6">
                            <input type="checkbox" className="sr-only peer" defaultChecked />
                            <div className="w-full h-full bg-gray-700 peer-checked:bg-[#10F4A0] rounded-full peer transition-all"></div>
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full peer-checked:translate-x-6 transition-all"></div>
                        </label>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">Morning</label>
                            <input
                                type="time"
                                defaultValue="07:30"
                                className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-[#10F4A0] focus:outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">Noon</label>
                            <input
                                type="time"
                                defaultValue="12:30"
                                className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-[#10F4A0] focus:outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-400 text-sm mb-2">Evening</label>
                            <input
                                type="time"
                                defaultValue="21:00"
                                className="w-full bg-[#0E1117] border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-[#10F4A0] focus:outline-none"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Platform Preferences Section */}
            <div className="bg-[#1A1D24] rounded-xl p-6 mb-6">
                <div className="flex items-center gap-3 mb-4">
                    <Globe className="w-6 h-6 text-[#10F4A0]" />
                    <h2 className="text-xl font-bold text-white">Platform Preferences</h2>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    {['YouTube', 'TikTok', 'LinkedIn', 'X (Twitter)', 'Instagram'].map((platform) => (
                        <label key={platform} className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                defaultChecked={platform !== 'Instagram'}
                                className="w-5 h-5 rounded border-gray-700 bg-[#0E1117] checked:bg-[#10F4A0] focus:ring-[#10F4A0]"
                            />
                            <span className="text-white">{platform}</span>
                        </label>
                    ))}
                </div>
            </div>

            {/* Save Button */}
            <button
                onClick={handleSave}
                className="flex items-center gap-2 bg-[#10F4A0] text-black font-bold px-6 py-3 rounded-lg hover:bg-[#0FD890] transition"
            >
                <Save className="w-5 h-5" />
                Save Settings
            </button>

            {saved && (
                <div className="mt-4 bg-green-500/20 border border-green-500 rounded-lg px-4 py-3 text-green-500">
                    ✓ Settings saved successfully!
                </div>
            )}
        </div>
    )
}

