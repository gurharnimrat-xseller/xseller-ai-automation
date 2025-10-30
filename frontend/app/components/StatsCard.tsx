import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: number;
    icon: LucideIcon;
    color: 'yellow' | 'green' | 'blue' | 'red' | 'orange';
}

const colorClasses = {
    yellow: {
        bg: 'bg-yellow-500/20',
        text: 'text-yellow-500',
        glow: 'hover:shadow-yellow-500/20',
    },
    green: {
        bg: 'bg-green-500/20',
        text: 'text-green-500',
        glow: 'hover:shadow-green-500/20',
    },
    blue: {
        bg: 'bg-blue-500/20',
        text: 'text-blue-500',
        glow: 'hover:shadow-blue-500/20',
    },
    red: {
        bg: 'bg-red-500/20',
        text: 'text-red-500',
        glow: 'hover:shadow-red-500/20',
    },
    orange: {
        bg: 'bg-orange-500/20',
        text: 'text-orange-500',
        glow: 'hover:shadow-orange-500/20',
    },
};

export default function StatsCard({ title, value, icon: Icon, color }: StatsCardProps) {
    const colors = colorClasses[color];

    return (
        <div
            className={`
        bg-[#1A1D24] rounded-lg p-6 border border-gray-700
        hover:border-opacity-70 hover:-translate-y-1 hover:shadow-2xl ${colors.glow}
        transition-all duration-300 cursor-pointer
      `}
        >
            <div className="flex items-center gap-4">
                {/* Icon on left */}
                <div className={`${colors.bg} ${colors.text} p-3 rounded-lg flex-shrink-0`}>
                    <Icon className="w-6 h-6" />
                </div>

                {/* Value and title on right */}
                <div className="flex flex-col items-end flex-1">
                    <p className="text-3xl font-bold text-white mb-1">{value}</p>
                    <p className="text-sm font-medium text-gray-400">{title}</p>
                </div>
            </div>
        </div>
    );
}

