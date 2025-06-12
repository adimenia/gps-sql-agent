import axios from 'axios'

// API client configuration
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Types
export interface ChatRequest {
  question: string
  session_id?: string
  include_explanation?: boolean
  max_execution_time?: number
  max_rows?: number
}

export interface ChatResponse {
  success: boolean
  question: string
  session_id: string
  timestamp: string
  total_processing_time: number
  summary: string
  sql_generation: {
    sql_query?: string
    is_valid: boolean
    confidence: number
    errors: string[]
    warnings: string[]
  }
  execution: {
    success: boolean
    sql?: string
    execution_time?: number
    row_count?: number
    columns?: string[]
    data?: any[]
    error?: string
  }
  explanation?: {
    summary: string
    data_insights: any
    sports_context: any
    recommendations: string[]
  }
  performance: any
  error?: string
}

export interface DashboardOverview {
  totals: {
    activities: number
    athletes: number
    events: number
    efforts: number
    owners: number
  }
  recent: {
    activities: number
    events: number
    efforts: number
  }
  latest_activity: {
    id?: number
    name?: string
    date?: string
  }
}

export interface HealthStatus {
  status: string
  timestamp: string
  components?: any
}

// API service functions
export const apiService = {
  // Health endpoints
  async getHealth(): Promise<HealthStatus> {
    const response = await apiClient.get('/health/')
    return response.data
  },

  async getFullHealth(): Promise<HealthStatus> {
    const response = await apiClient.get('/health/full')
    return response.data
  },

  // Dashboard endpoints
  async getDashboardOverview(days: number = 30): Promise<DashboardOverview> {
    const response = await apiClient.get('/dashboard/metrics/overview', {
      params: { days }
    })
    return response.data
  },

  async getActivityMetrics(days: number = 30, groupBy: string = 'day') {
    const response = await apiClient.get('/dashboard/metrics/activities', {
      params: { days, group_by: groupBy }
    })
    return response.data
  },

  async getAthleteMetrics(days: number = 30, limit: number = 10) {
    const response = await apiClient.get('/dashboard/metrics/athletes', {
      params: { days, limit }
    })
    return response.data
  },

  async getPerformanceMetrics(days: number = 30, athleteId?: number) {
    const response = await apiClient.get('/dashboard/metrics/performance', {
      params: { days, athlete_id: athleteId }
    })
    return response.data
  },

  // Chat endpoints
  async askQuestion(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post('/chat/ask', {
      question: request.question,
      session_id: request.session_id || 'default',
      include_explanation: request.include_explanation ?? true,
      max_execution_time: request.max_execution_time || 30,
      max_rows: request.max_rows || 1000
    })
    return response.data
  },

  async quickQuestion(question: string) {
    const response = await apiClient.post('/chat/quick', { question })
    return response.data
  },

  async getSessionHistory(sessionId: string) {
    const response = await apiClient.get(`/chat/sessions/${sessionId}`)
    return response.data
  },

  async getChatStats() {
    const response = await apiClient.get('/chat/stats')
    return response.data
  },

  async getExampleQuestions() {
    const response = await apiClient.post('/chat/examples')
    return response.data
  },

  async testChatAgent() {
    const response = await apiClient.post('/chat/test')
    return response.data
  },

  // Periods/Activities endpoints
  async getActivities(params: {
    page?: number
    size?: number
    sort_by?: string
    sort_order?: string
    name_filter?: string
    owner_filter?: string
    start_date?: string
    end_date?: string
  } = {}) {
    const response = await apiClient.get('/periods/activities', { params })
    return response.data
  },

  async getActivity(activityId: number, includePeriods: boolean = true) {
    const response = await apiClient.get(`/periods/activities/${activityId}`, {
      params: { include_periods: includePeriods }
    })
    return response.data
  },

  async getPeriods(params: {
    page?: number
    size?: number
    sort_by?: string
    sort_order?: string
    activity_id?: number
    name_filter?: string
    start_date?: string
    end_date?: string
  } = {}) {
    const response = await apiClient.get('/periods/', { params })
    return response.data
  },

  async getPeriodsStats(params: {
    activity_id?: number
    start_date?: string
    end_date?: string
  } = {}) {
    const response = await apiClient.get('/periods/stats/summary', { params })
    return response.data
  }
}

// Utility functions
export const formatError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}

export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request
}

export default apiService