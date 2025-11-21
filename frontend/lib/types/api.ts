export interface ApiResponse<T> {
    data: T
    meta?: {
        page: number
        limit: number
        total: number
        totalPages: number
    }
    error?: {
        code: string
        message: string
        details?: unknown
    }
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> { }