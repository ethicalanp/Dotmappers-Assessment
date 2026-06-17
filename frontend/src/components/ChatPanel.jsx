import { useState, useRef, useEffect, useCallback } from 'react'
import styles from './ChatPanel.module.css'

const SUGGESTIONS = [
  'How many tickets are currently open?',
  'Which agent resolved the most tickets?',
  'Show me all Critical priority tickets.',
  'What is the average customer rating?',
  'Which category has the most issues?',
  'How many SLA breaches are there?',
]

export default function ChatPanel({ defaultProvider }) {
  const [messages, setMessages] = useState([
    { role: 'bot', text: '👋 Hi! I\'m your AI assistant for support ticket analysis. Ask me anything about the dataset!' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState({
    provider: defaultProvider || 'groq',
    groqKey: localStorage.getItem('groq_key') || '',
    groqModel: 'llama-3.1-8b-instant',
    ollamaHost: 'http://localhost:11434',
    ollamaModel: 'llama3',
  })

  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = useCallback(async (text) => {
    const question = (text || input).trim()
    if (!question || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: question }])
    setLoading(true)

    const body = { question }
    if (config.provider === 'groq') {
      body.provider = 'groq'
      body.model = config.groqModel
      if (config.groqKey) {
        body.api_key = config.groqKey
        localStorage.setItem('groq_key', config.groqKey)
      }
    } else {
      body.provider = 'ollama'
      body.host = config.ollamaHost
      body.model = config.ollamaModel
    }

    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'bot', text: data.answer || data.detail || 'No response received.' }])
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: '⚠️ Failed to reach backend. Make sure the server is running on port 8000.' }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, config])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  return (
    <div className={styles.layout}>
      {/* Chat window */}
      <div className={styles.chatBox}>
        <div className={styles.chatHeader}>
          <span className={styles.chatTitle}>🤖 AI Assistant</span>
          <span className={styles.providerTag}>
            {config.provider === 'groq' ? 'Groq LLM' : 'Ollama (Local)'}
          </span>
        </div>

        <div className={styles.messages}>
          {messages.map((m, i) => (
            <div key={i} className={`${styles.msg} ${styles[m.role]}`}>
              <div className={`${styles.avatar} ${styles[m.role]}`}>
                {m.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className={`${styles.bubble} ${styles[m.role]}`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className={`${styles.msg} ${styles.bot}`}>
              <div className={`${styles.avatar} ${styles.bot}`}>🤖</div>
              <div className={`${styles.bubble} ${styles.bot} ${styles.thinking}`}>
                <span className="spinner" /> Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className={styles.inputRow}>
          <input
            className={styles.chatInput}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about support tickets… (Enter to send)"
            disabled={loading}
          />
          <button
            className={styles.sendBtn}
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
          >
            {loading ? <span className="spinner" /> : 'Send →'}
          </button>
        </div>
      </div>

      {/* Sidebar */}
      <div className={styles.sidebar}>
        {/* Suggestions */}
        <div className={styles.sideCard}>
          <div className={styles.sideTitle}>💡 Suggested Questions</div>
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className={styles.sugBtn} onClick={() => sendMessage(s)}>
              {s}
            </button>
          ))}
        </div>

        {/* Config */}
        <div className={styles.sideCard}>
          <div className={styles.sideTitle}>⚙️ LLM Configuration</div>

          <label className={styles.cfgLabel}>Provider</label>
          <select
            className={styles.cfgSelect}
            value={config.provider}
            onChange={e => setConfig(c => ({ ...c, provider: e.target.value }))}
          >
            <option value="groq">Groq (Cloud)</option>
            <option value="ollama">Ollama (Local)</option>
          </select>

          {config.provider === 'groq' && (
            <>
              <label className={styles.cfgLabel}>Groq API Key</label>
              <input
                className={styles.cfgInput}
                type="password"
                placeholder="gsk_…"
                value={config.groqKey}
                onChange={e => setConfig(c => ({ ...c, groqKey: e.target.value }))}
              />
              <label className={styles.cfgLabel}>Model</label>
              <select
                className={styles.cfgSelect}
                value={config.groqModel}
                onChange={e => setConfig(c => ({ ...c, groqModel: e.target.value }))}
              >
                <option value="llama-3.1-8b-instant">llama-3.1-8b-instant</option>
                <option value="llama3-8b-8192">llama3-8b-8192</option>
                <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
                <option value="gemma2-9b-it">gemma2-9b-it</option>
              </select>
            </>
          )}

          {config.provider === 'ollama' && (
            <>
              <label className={styles.cfgLabel}>Ollama Host</label>
              <input
                className={styles.cfgInput}
                value={config.ollamaHost}
                onChange={e => setConfig(c => ({ ...c, ollamaHost: e.target.value }))}
              />
              <label className={styles.cfgLabel}>Model</label>
              <input
                className={styles.cfgInput}
                value={config.ollamaModel}
                onChange={e => setConfig(c => ({ ...c, ollamaModel: e.target.value }))}
              />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
