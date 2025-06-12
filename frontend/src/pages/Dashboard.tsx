import { useState, useEffect } from 'react'

interface DashboardStats {
  activities: number
  athletes: number
  events: number
  efforts: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Basic API call to get overview metrics
      const response = await fetch('/api/v1/dashboard/metrics/overview')
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard stats')
      }
      
      const data = await response.json()
      setStats(data.totals)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error">
        <p>Error loading dashboard: {error}</p>
        <button className="btn" onClick={fetchDashboardStats} style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Dashboard
        </h1>
        <p style={{ color: '#6b7280' }}>
          Overview of your sports analytics data
        </p>
      </div>

      {stats && (
        <div className="dashboard-grid">
          <div className="card stat-card">
            <div className="stat-value">{stats.activities}</div>
            <div className="stat-label">Training Activities</div>
          </div>
          
          <div className="card stat-card">
            <div className="stat-value">{stats.athletes}</div>
            <div className="stat-label">Athletes</div>
          </div>
          
          <div className="card stat-card">
            <div className="stat-value">{stats.events}</div>
            <div className="stat-label">Performance Events</div>
          </div>
          
          <div className="card stat-card">
            <div className="stat-value">{stats.efforts}</div>
            <div className="stat-label">Training Efforts</div>
          </div>
        </div>
      )}

      <div className="card">
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          Quick Actions
        </h2>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button 
            className="btn" 
            onClick={() => window.location.href = '/chat'}
          >
            🤖 Ask the AI Agent
          </button>
          <button 
            className="btn" 
            onClick={fetchDashboardStats}
            style={{ backgroundColor: '#10b981' }}
          >
            🔄 Refresh Data
          </button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          Getting Started
        </h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          <div>
            <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
              💬 Ask Questions
            </h3>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Go to the Chat Agent and ask questions like "Who are the fastest athletes?" or "Show me recent training data"
            </p>
          </div>
          <div>
            <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
              📊 View Analytics
            </h3>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              The dashboard shows key metrics from your sports performance data
            </p>
          </div>
          <div>
            <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>
              🔍 Explore Data
            </h3>
            <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Use natural language to explore velocity, acceleration, distance, and training patterns
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}