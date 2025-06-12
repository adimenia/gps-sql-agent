import { useState, useEffect, useCallback } from 'react'
import { apiService, formatError, isNetworkError } from '../services/api'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface UseApiOptions {
  immediate?: boolean
  deps?: any[]
}

// Generic hook for API calls
export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
): UseApiState<T> & { refetch: () => Promise<void> } {
  const { immediate = true, deps = [] } = options
  
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: immediate,
    error: null
  })

  const executeApiCall = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      const data = await apiCall()
      setState({ data, loading: false, error: null })
    } catch (error) {
      const errorMessage = formatError(error)
      setState({ data: null, loading: false, error: errorMessage })
    }
  }, [apiCall])

  useEffect(() => {
    if (immediate) {
      executeApiCall()
    }
  }, [immediate, executeApiCall, ...deps])

  return {
    ...state,
    refetch: executeApiCall
  }
}

// Specific hooks for common API calls
export function useDashboardOverview(days: number = 30) {
  return useApi(
    () => apiService.getDashboardOverview(days),
    { deps: [days] }
  )
}

export function useHealthCheck() {
  return useApi(() => apiService.getHealth())
}

export function useChatStats() {
  return useApi(() => apiService.getChatStats(), { immediate: false })
}

export function useActivities(params: any = {}) {
  return useApi(
    () => apiService.getActivities(params),
    { deps: [JSON.stringify(params)] }
  )
}

// Hook for managing async operations with loading states
export function useAsyncOperation() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const execute = useCallback(async <T>(
    operation: () => Promise<T>
  ): Promise<T | null> => {
    try {
      setLoading(true)
      setError(null)
      const result = await operation()
      return result
    } catch (err) {
      const errorMessage = formatError(err)
      setError(errorMessage)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
  }, [])

  return { loading, error, execute, reset }
}

// Hook for chat functionality
export function useChat(sessionId: string = 'default') {
  const [messages, setMessages] = useState<any[]>([])
  const { loading, error, execute } = useAsyncOperation()

  const sendMessage = useCallback(async (question: string) => {
    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: question,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    // Send to API
    const response = await execute(() => 
      apiService.askQuestion({
        question,
        session_id: sessionId,
        include_explanation: true
      })
    )

    if (response) {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant' as const,
        content: response.success ? response.summary : 'I encountered an error processing your question.',
        timestamp: new Date().toISOString(),
        data: response.execution?.data || [],
        error: response.success ? undefined : response.error || 'Unknown error occurred',
        sql_query: response.sql_generation?.sql_query,
        execution_time: response.execution?.execution_time,
        row_count: response.execution?.row_count
      }
      setMessages(prev => [...prev, assistantMessage])
    }
  }, [sessionId, execute])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return {
    messages,
    sendMessage,
    clearMessages,
    loading,
    error
  }
}