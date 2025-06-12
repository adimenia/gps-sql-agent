import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
  data?: any[]
  error?: string
  loading?: boolean
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your sports analytics AI agent. Ask me questions about your athlete performance data, training activities, or any sports metrics. For example:\n\n• "How many athletes are in the database?"\n• "Who are the top 5 fastest athletes?"\n• "Show me recent training activities"',
      timestamp: new Date().toISOString()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          session_id: 'default',
          include_explanation: true
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from AI agent')
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.success ? data.summary : (data.summary || 'I encountered an error processing your question.'),
        timestamp: new Date().toISOString(),
        data: data.execution?.data || [],
        error: data.success ? undefined : (data.execution?.error || data.error || 'Unknown error occurred')
      }

      // Add detailed explanation if available
      if (data.success && data.explanation) {
        let detailedContent = data.summary

        if (data.execution?.data?.length > 0) {
          detailedContent += '\n\n📊 **Results:**\n'
          const results = data.execution.data.slice(0, 5) // Show first 5 results
          results.forEach((row: any, index: number) => {
            detailedContent += `${index + 1}. ${JSON.stringify(row)}\n`
          })
          
          if (data.execution.data.length > 5) {
            detailedContent += `... and ${data.execution.data.length - 5} more results`
          }
        }

        if (data.explanation.sports_context?.context?.length > 0) {
          detailedContent += '\n\n💡 **Insights:**\n'
          data.explanation.sports_context.context.slice(0, 3).forEach((insight: string) => {
            detailedContent += `• ${insight}\n`
          })
        }

        assistantMessage.content = detailedContent
      }

      // Add error explanation for debugging if not successful
      if (!data.success && data.explanation?.error_explanation) {
        assistantMessage.content += '\n\n🔍 **Debug Info:**\n' + data.explanation.error_explanation
        
        if (data.explanation.suggestions?.length > 0) {
          assistantMessage.content += '\n\n💡 **Suggestions:**\n'
          data.explanation.suggestions.forEach((suggestion: string) => {
            assistantMessage.content += `• ${suggestion}\n`
          })
        }

        if (data.sql_generation?.sql_query) {
          assistantMessage.content += '\n\n📝 **Generated SQL:**\n```sql\n' + data.sql_generation.sql_query + '\n```'
        }
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          🤖 AI Chat Agent
        </h1>
        <p style={{ color: '#6b7280' }}>
          Ask questions about your sports data in natural language
        </p>
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                {message.content.split('\n').map((line, index) => (
                  <div key={index}>
                    {line.startsWith('•') || line.startsWith('**') ? (
                      <div style={{ marginLeft: line.startsWith('•') ? '1rem' : '0' }}>
                        {line.replace(/\*\*(.*?)\*\*/g, '$1')}
                      </div>
                    ) : (
                      line
                    )}
                  </div>
                ))}
              </div>
              {message.error && (
                <div style={{ 
                  marginTop: '0.5rem', 
                  padding: '0.5rem', 
                  backgroundColor: 'rgba(220, 38, 38, 0.1)',
                  borderRadius: '0.25rem',
                  fontSize: '0.875rem'
                }}>
                  Error: {message.error}
                </div>
              )}
              <div className="message-meta">
                {formatTimestamp(message.timestamp)}
                {message.data && message.data.length > 0 && (
                  <span> • {message.data.length} results</span>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">Thinking...</div>
              <div className="message-meta">
                {formatTimestamp(new Date().toISOString())}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <textarea
            className="form-input chat-input form-textarea"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about athletes, training data, performance metrics..."
            disabled={isLoading}
            rows={2}
          />
          <button
            className="btn"
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            style={{ minWidth: '80px' }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          💡 Example Questions
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '0.5rem' }}>
          {[
            "How many athletes are in the database?",
            "Who are the top 5 fastest athletes?",
            "Show me recent training activities",
            "What's the average velocity for all athletes?",
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => setInputValue(example)}
              style={{
                padding: '0.5rem',
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '0.375rem',
                textAlign: 'left',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
              disabled={isLoading}
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}