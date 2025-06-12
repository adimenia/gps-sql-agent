// Common types used across the application

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Activity {
  activity_id: number
  name?: string
  start_time?: string
  end_time?: string
  game_id?: number
  owner_id?: number
  owner_name?: string
  athlete_count?: number
  period_count?: number
  created_at?: string
  updated_at?: string
}

export interface Athlete {
  athlete_id: number
  first_name?: string
  last_name?: string
  gender?: string
  jersey_number?: number
  height?: number
  weight?: number
  position_id?: number
  date_of_birth?: string
  created_at?: string
}

export interface Period {
  period_id: number
  activity_id: number
  name?: string
  start_time?: string
  end_time?: string
  created_at?: string
  modified_at?: string
  is_deleted: boolean
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
  data?: any[]
  error?: string
  loading?: boolean
  sql_query?: string
  execution_time?: number
  row_count?: number
}

export interface DashboardMetrics {
  activities: number
  athletes: number
  events: number
  efforts: number
  owners: number
}

export interface LoadingState {
  isLoading: boolean
  error: string | null
}

export interface ChatSession {
  session_id: string
  created_at: string
  total_queries: number
  successful_queries: number
  recent_queries: any[]
  context: any
}