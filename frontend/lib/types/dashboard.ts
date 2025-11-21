// Dashboard-specific TypeScript types

export interface ChartDataPoint {
    value: number;
}

export interface DashboardStats {
    agents: {
        total: number;
        active: number;
        idle: number;
        error: number;
        chartData?: ChartDataPoint[];
    };
    news: {
        today: number;
        trend: number; // percentage
        chartData?: ChartDataPoint[];
    };
    videos: {
        total: number;
        pending: number;
        trend: number; // percentage
        chartData?: ChartDataPoint[];
    };
    queue: {
        items: number;
        processing: number;
        chartData?: ChartDataPoint[];
    };
}

export interface PerformanceMetric {
    value: number;
    trend: number; // percentage change
    previousValue: number;
}

export interface PerformanceData {
    scriptsGenerated: PerformanceMetric;
    qualityScore: PerformanceMetric;
    successRate: PerformanceMetric;
}

export interface Activity {
    id: string;
    type: 'success' | 'info' | 'warning' | 'error';
    title: string;
    description: string;
    timestamp: Date;
    agent?: string;
    link?: string;
}
