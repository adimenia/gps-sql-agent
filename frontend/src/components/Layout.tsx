import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="app">
      <nav className="nav">
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1e293b' }}>
              🏃‍♂️ Sports Analytics Platform
            </h1>
            <ul className="nav-links">
              <li>
                <Link 
                  to="/dashboard" 
                  className={`nav-link ${location.pathname === '/dashboard' || location.pathname === '/' ? 'active' : ''}`}
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link 
                  to="/chat" 
                  className={`nav-link ${location.pathname === '/chat' ? 'active' : ''}`}
                >
                  Chat Agent
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
      
      <footer style={{ 
        borderTop: '1px solid #e2e8f0', 
        padding: '1rem 0', 
        marginTop: 'auto',
        background: 'white',
        color: '#6b7280',
        textAlign: 'center'
      }}>
        <div className="container">
          <p>&copy; 2024 Sports Analytics Platform. Powered by AI.</p>
        </div>
      </footer>
    </div>
  )
}