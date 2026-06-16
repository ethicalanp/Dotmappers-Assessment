import pandas as pd
from datetime import timedelta

def detect_anomalies(df: pd.DataFrame):
    """Computes statistical and rule-based anomalies in the dataset."""
    anomalies = []
    
    if df.empty:
        return anomalies
        
    # 1. Calculate SLA Violations
    # Relative current date is the maximum timestamp in the dataset
    max_date = df['created_at'].max()
    sla_cutoff = max_date - timedelta(hours=24)
    
    # SLA violations: unresolved (Open/Escalated) High/Critical tickets created >24h before max_date
    sla_violations = df[
        (df['status'].isin(['Open', 'Escalated'])) &
        (df['priority'].isin(['High', 'Critical'])) &
        (df['created_at'] < sla_cutoff)
    ]
    
    for _, row in sla_violations.iterrows():
        age_days = (max_date - row['created_at']).total_seconds() / 86400.0
        anomalies.append({
            "ticket_id": row["ticket_id"],
            "category": row["category"],
            "priority": row["priority"],
            "status": row["status"],
            "created_at": str(row["created_at"]),
            "agent_id": row["agent_id"],
            "issue_summary": row["issue_summary"],
            "anomaly_type": "SLA Violation",
            "reason": f"Ticket is {row['priority']} priority and has been unresolved for {age_days:.1f} days (SLA threshold is 24 hours)."
        })
        
    # 2. Calculate Statistical Outliers for Resolution Time (Resolved tickets only)
    resolved_df = df[df['status'] == 'Resolved'].dropna(subset=['resolution_time_hrs'])
    if not resolved_df.empty:
        mean_res = resolved_df['resolution_time_hrs'].mean()
        std_res = resolved_df['resolution_time_hrs'].std()
        res_threshold = mean_res + 2 * std_res
        
        outliers_res = resolved_df[resolved_df['resolution_time_hrs'] > res_threshold]
        for _, row in outliers_res.iterrows():
            anomalies.append({
                "ticket_id": row["ticket_id"],
                "category": row["category"],
                "priority": row["priority"],
                "status": row["status"],
                "created_at": str(row["created_at"]),
                "agent_id": row["agent_id"],
                "issue_summary": row["issue_summary"],
                "anomaly_type": "Statistical Outlier (Resolution Time)",
                "reason": f"Resolution time is abnormally high ({row['resolution_time_hrs']:.1f} hrs) compared to dataset average ({mean_res:.1f} hrs, standard deviation is {std_res:.1f} hrs)."
            })
            
    # 3. Calculate Statistical Outliers for Response Time
    mean_resp = df['response_time_hrs'].mean()
    std_resp = df['response_time_hrs'].std()
    resp_threshold = mean_resp + 2 * std_resp
    
    outliers_resp = df[df['response_time_hrs'] > resp_threshold]
    for _, row in outliers_resp.iterrows():
        anomalies.append({
            "ticket_id": row["ticket_id"],
            "category": row["category"],
            "priority": row["priority"],
            "status": row["status"],
            "created_at": str(row["created_at"]),
            "agent_id": row["agent_id"],
            "issue_summary": row["issue_summary"],
            "anomaly_type": "Statistical Outlier (Response Time)",
            "reason": f"Response time is abnormally high ({row['response_time_hrs']:.1f} hrs) compared to dataset average ({mean_resp:.1f} hrs, standard deviation is {std_resp:.1f} hrs)."
        })
        
    # 4. Low customer rating alerts (resolved tickets with rating 1 or 2)
    low_ratings = resolved_df[resolved_df['customer_rating'].isin([1, 2])]
    for _, row in low_ratings.iterrows():
        anomalies.append({
            "ticket_id": row["ticket_id"],
            "category": row["category"],
            "priority": row["priority"],
            "status": row["status"],
            "created_at": str(row["created_at"]),
            "agent_id": row["agent_id"],
            "issue_summary": row["issue_summary"],
            "anomaly_type": "Low Rating Alert",
            "reason": f"Customer rating is abnormally low ({int(row['customer_rating'])}/5) on resolved ticket."
        })
        
    return anomalies
