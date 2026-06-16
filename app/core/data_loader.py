import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, "support_tickets.csv")

def load_csv_data(csv_path=CSV_PATH) -> pd.DataFrame:
    """Loads and standardizes support_tickets.csv data."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
        
    df = pd.read_csv(csv_path)
    
    # Strip spaces from column names
    df.columns = [col.strip() for col in df.columns]
    
    # Strip spaces from object/string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # Convert numeric fields
    df['response_time_hrs'] = pd.to_numeric(df['response_time_hrs'], errors='coerce')
    df['resolution_time_hrs'] = pd.to_numeric(df['resolution_time_hrs'], errors='coerce')
    df['customer_rating'] = pd.to_numeric(df['customer_rating'], errors='coerce')
    
    return df

def get_csv_as_string(df: pd.DataFrame) -> str:
    """Converts the parsed dataframe to an ultra-compact CSV string, limiting to 350 rows to fit in LLM context limits."""
    # Drop issue_summary to significantly reduce token size
    df_compact = df.drop(columns=['issue_summary'], errors='ignore').copy()
    
    # Strip TKT- from ticket_id to save 4 chars per row
    if 'ticket_id' in df_compact.columns:
        df_compact['ticket_id'] = df_compact['ticket_id'].astype(str).str.replace('TKT-', '', case=False)
        
    # Strip AGT- from agent_id to save 4 chars per row
    if 'agent_id' in df_compact.columns:
        df_compact['agent_id'] = df_compact['agent_id'].astype(str).str.replace('AGT-', '', case=False)
        
    # Map category to single letters (B=Billing, T=Technical, G=General)
    cat_map = {'Billing': 'B', 'Technical': 'T', 'General': 'G'}
    if 'category' in df_compact.columns:
        df_compact['category'] = df_compact['category'].map(cat_map).fillna(df_compact['category'])
        
    # Map priority to single letters (L=Low, M=Medium, H=High, C=Critical)
    pri_map = {'Low': 'L', 'Medium': 'M', 'High': 'H', 'Critical': 'C'}
    if 'priority' in df_compact.columns:
        df_compact['priority'] = df_compact['priority'].map(pri_map).fillna(df_compact['priority'])
        
    # Map status to single letters (R=Resolved, O=Open, E=Escalated)
    stat_map = {'Resolved': 'R', 'Open': 'O', 'Escalated': 'E'}
    if 'status' in df_compact.columns:
        df_compact['status'] = df_compact['status'].map(stat_map).fillna(df_compact['status'])
        
    # Rename columns to shorter names to save token space
    df_compact = df_compact.rename(columns={
        'response_time_hrs': 'resp',
        'resolution_time_hrs': 'resol',
        'customer_rating': 'rating'
    })
    
    # Format datetimes to drop the year since all records are from 2024 (saves 5 chars per row)
    if 'created_at' in df_compact.columns:
        df_compact['created_at'] = df_compact['created_at'].dt.strftime('%m-%d %H:%M')
        
    # Slice to first 150 rows to fit inside strict free-tier request payload limits (e.g. 4,096 tokens)
    df_compact = df_compact.head(150)
    
    return df_compact.to_csv(index=False)
