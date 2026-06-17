import { useState } from 'react'
import styles from './AnomalyList.module.css'

function getBadgeClass(type) {
  if (!type) return styles.sla
  if (type.includes('SLA'))                              return styles.sla
  if (type.includes('Stuck'))                            return styles.stuck
  if (type.includes('Outlier') || type.includes('Statistical')) return styles.outlier
  if (type.includes('Rating'))                           return styles.rating
  return styles.sla
}

function getShortType(type) {
  if (!type) return 'Unknown'
  if (type.includes('SLA'))        return 'SLA Breach'
  if (type.includes('Stuck'))      return 'Stuck Ticket'
  if (type.includes('Outlier') || type.includes('Statistical')) return 'Response Outlier'
  if (type.includes('Rating'))     return 'Low Rating'
  return type
}

export default function AnomalyList({ anomalies }) {
  const [filter, setFilter] = useState('All')

  const types = ['All', ...Array.from(new Set(anomalies.map(a => a.anomaly_type).filter(Boolean)))]
  const filtered = filter === 'All' ? anomalies : anomalies.filter(a => a.anomaly_type === filter)

  return (
    <div>
      {/* Header */}
      <div className={styles.secHeader}>
        <div>
          <h2 className={styles.secTitle}>⚠️ Anomaly Detection Report</h2>
          <p className={styles.secSub}>{anomalies.length} issues found across 500 support tickets</p>
        </div>
        <div className={styles.totalBadge}>{anomalies.length} Total</div>
      </div>

      {/* Filter buttons */}
      <div className={styles.filters}>
        {types.map(t => {
          const count = t === 'All' ? anomalies.length : anomalies.filter(a => a.anomaly_type === t).length
          return (
            <button
              key={t}
              className={`${styles.filterBtn} ${filter === t ? styles.active : ''}`}
              onClick={() => setFilter(t)}
            >
              {getShortType(t)} <span className={styles.filterCount}>({count})</span>
            </button>
          )
        })}
      </div>

      {/* List */}
      {filtered.length === 0 ? (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>✅</div>
          <p>No anomalies found for this filter</p>
        </div>
      ) : (
        <div className={styles.list}>
          {filtered.map((a, i) => (
            <div key={i} className={styles.card}>
              <div className={styles.cardLeft}>
                <div className={styles.ticketId}>{a.ticket_id}</div>
                <span className={`${styles.typeBadge} ${getBadgeClass(a.anomaly_type)}`}>
                  {getShortType(a.anomaly_type)}
                </span>
              </div>
              <div className={styles.cardBody}>
                <p className={styles.reason}>{a.reason}</p>
                {a.issue_summary && (
                  <p className={styles.summary}>"{a.issue_summary}"</p>
                )}
                <div className={styles.meta}>
                  {a.category  && <span className={styles.tag}>📁 {a.category}</span>}
                  {a.priority  && <span className={styles.tag}>🔴 {a.priority}</span>}
                  {a.status    && <span className={styles.tag}>📌 {a.status}</span>}
                  {a.agent_id  && <span className={styles.tag}>👤 {a.agent_id}</span>}
                  {a.created_at && <span className={styles.tag}>🕐 {String(a.created_at).slice(0, 10)}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
