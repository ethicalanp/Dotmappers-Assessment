import { useState, useEffect } from 'react'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import ChatPanel from './components/ChatPanel'
import AnomalyList from './components/AnomalyList'
import './App.css'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [systemStatus, setSystemStatus] = useState({ ok: false, msg: 'Connecting…', provider: '' })
  const [anomalies, setAnomalies] = useState([])
  const [anomalyCount, setAnomalyCount] = useState(0)

  useEffect(() => {
    // Health check
    fetch('/health')
      .then(r => r.json())
      .then(d => {
        setSystemStatus({
          ok: true,
          msg: `Backend Active · ${d.csv_rows} rows · ${(d.default_provider || '').toUpperCase()}`,
          provider: d.default_provider || 'groq'
        })
      })
      .catch(() => setSystemStatus({ ok: false, msg: 'Cannot connect to backend', provider: '' }))

    // Anomalies
    fetch('/anomalies')
      .then(r => r.json())
      .then(d => {
        setAnomalies(d.anomalies || [])
        setAnomalyCount(d.total_anomalies || 0)
      })
      .catch(err => console.error('Failed to fetch anomalies:', err))
  }, [])

  return (
    <div className="app-shell">
      <Header systemStatus={systemStatus} />
      <main className="main-content">
        {/* Tab Navigation */}
        <nav className="tab-nav">
          <button
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            🤖 AI Chat
          </button>
          <button
            className={`tab-btn ${activeTab === 'anomalies' ? 'active' : ''}`}
            onClick={() => setActiveTab('anomalies')}
          >
            ⚠️ Anomalies
            {anomalyCount > 0 && (
              <span className="tab-badge">{anomalyCount}</span>
            )}
          </button>
        </nav>

        {/* Panels */}
        {activeTab === 'dashboard' && <Dashboard anomalyCount={anomalyCount} />}
        {activeTab === 'chat' && <ChatPanel defaultProvider={systemStatus.provider} />}
        {activeTab === 'anomalies' && <AnomalyList anomalies={anomalies} />}
      </main>
    </div>
  )
}
