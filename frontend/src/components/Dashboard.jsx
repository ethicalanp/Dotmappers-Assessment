import { useEffect, useRef } from 'react'
import {
  Chart,
  BarElement, ArcElement, CategoryScale, LinearScale,
  Tooltip, Legend, BarController, DoughnutController
} from 'chart.js'
import styles from './Dashboard.module.css'

Chart.register(BarElement, ArcElement, CategoryScale, LinearScale, Tooltip, Legend, BarController, DoughnutController)

const STATS = [
  { key: 'total',    label: 'Total Tickets',     value: '500',  icon: '🎫', color: 'blue' },
  { key: 'open',     label: 'Open Tickets',       value: '96',   icon: '🔓', color: 'amber' },
  { key: 'rating',   label: 'Avg CSAT Rating',    value: '3.48', icon: '⭐', color: 'green' },
  { key: 'anomaly',  label: 'Anomalies Detected', value: null,   icon: '⚠️', color: 'purple' },
]

export default function Dashboard({ anomalyCount }) {
  const catRef   = useRef(null)
  const statRef  = useRef(null)
  const prioRef  = useRef(null)
  const catChart  = useRef(null)
  const statChart = useRef(null)
  const prioChart = useRef(null)

  useEffect(() => {
    const gridColor = '#1e293b'
    const tickColor = '#64748b'

    // Category chart
    if (catRef.current) {
      catChart.current?.destroy()
      catChart.current = new Chart(catRef.current, {
        type: 'bar',
        data: {
          labels: ['Billing', 'Technical', 'General'],
          datasets: [{
            label: 'Tickets',
            data: [165, 172, 163],
            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
            borderRadius: 6, borderSkipped: false
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: gridColor }, ticks: { color: tickColor }, border: { display: false } },
            x: { grid: { display: false }, ticks: { color: tickColor }, border: { display: false } }
          }
        }
      })
    }

    // Status donut
    if (statRef.current) {
      statChart.current?.destroy()
      statChart.current = new Chart(statRef.current, {
        type: 'doughnut',
        data: {
          labels: ['Resolved', 'Open', 'Escalated'],
          datasets: [{
            data: [272, 132, 96],
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderWidth: 0, hoverOffset: 6
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '65%',
          plugins: {
            legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 12, font: { size: 11 } } }
          }
        }
      })
    }

    // Priority horizontal bar
    if (prioRef.current) {
      prioChart.current?.destroy()
      prioChart.current = new Chart(prioRef.current, {
        type: 'bar',
        data: {
          labels: ['Low', 'Medium', 'High', 'Critical'],
          datasets: [{
            label: 'Tickets',
            data: [137, 134, 138, 91],
            backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
            borderRadius: 6, borderSkipped: false
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: tickColor }, border: { display: false } },
            y: { grid: { display: false }, ticks: { color: '#94a3b8' }, border: { display: false } }
          }
        }
      })
    }

    return () => {
      catChart.current?.destroy()
      statChart.current?.destroy()
      prioChart.current?.destroy()
    }
  }, [])

  return (
    <div>
      {/* Stats */}
      <div className={styles.statsGrid}>
        {STATS.map(s => (
          <div key={s.key} className={`${styles.statCard} ${styles[s.color]}`}>
            <div className={`${styles.statIcon} ${styles[s.color]}`}>{s.icon}</div>
            <div className={styles.statValue}>
              {s.key === 'anomaly' ? anomalyCount : s.value}
            </div>
            <div className={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className={styles.chartsGrid}>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Tickets by Category</div>
          <div className={styles.chartWrap}><canvas ref={catRef} /></div>
        </div>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Status Breakdown</div>
          <div className={styles.chartWrap}><canvas ref={statRef} /></div>
        </div>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Priority Breakdown</div>
          <div className={styles.chartWrap}><canvas ref={prioRef} /></div>
        </div>
      </div>
    </div>
  )
}
