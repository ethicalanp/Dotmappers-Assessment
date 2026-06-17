import styles from './Header.module.css'

export default function Header({ systemStatus }) {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>📊</div>
          <div>
            <div className={styles.logoName}>TicketAI Dashboard</div>
            <div className={styles.logoSub}>Support Analytics &amp; Anomaly Detection</div>
          </div>
        </div>
        <div className={styles.badge}>
          <div className={`${styles.dot} ${systemStatus.ok ? styles.ok : styles.err}`} />
          <span>{systemStatus.msg}</span>
        </div>
      </div>
    </header>
  )
}
