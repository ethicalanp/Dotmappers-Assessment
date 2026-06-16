import os
import streamlit as st
import pandas as pd
from app.core.data_loader import load_csv_data, get_csv_as_string
from app.services.anomaly_detector import detect_anomalies
from app.services.llm_client import generate_answer, GROQ_API_KEY, GROQ_MODEL, OLLAMA_HOST, OLLAMA_MODEL, LLM_PROVIDER

# Set page config for a premium layout
st.set_page_config(
    page_title="DocuQuery CSV AI - Ticket QA Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .reportview-container {
        background: #f8fafc;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.8rem;
    }
    .chat-bubble {
        padding: 1.2rem;
        border-radius: 0.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .user-bubble {
        background-color: #f1f5f9;
        border-left: 5px solid #475569;
        color: #1e293b;
    }
    .assistant-bubble {
        background-color: #f0f9ff;
        border-left: 5px solid #0284c7;
        color: #0f172a;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #3b82f6;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Load CSV data into session state
if "csv_df" not in st.session_state:
    try:
        st.session_state.csv_df = load_csv_data()
        st.session_state.csv_text = get_csv_as_string(st.session_state.csv_df)
    except Exception as e:
        st.error(f"Error loading CSV dataset: {e}")
        st.session_state.csv_df = pd.DataFrame()
        st.session_state.csv_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

df = st.session_state.csv_df

# Sidebar
with st.sidebar:
    st.header("🛠️ LLM Settings")
    
    # Provider Selector
    provider = st.selectbox(
        "LLM Provider",
        options=["Ollama (Local)", "Groq (Cloud)"],
        index=0 if LLM_PROVIDER == "ollama" else 1
    )
    
    selected_provider = "ollama" if "Ollama" in provider else "groq"
    
    if selected_provider == "groq":
        api_key = st.text_input("Groq API Key", value=GROQ_API_KEY, type="password")
        model = st.text_input("Groq Model", value=GROQ_MODEL)
        host = None
    else:
        api_key = None
        host = st.text_input("Ollama Host", value=OLLAMA_HOST)
        model = st.text_input("Ollama Model", value=OLLAMA_MODEL)
        
    st.divider()
    
    st.info("Loaded active file: **support_tickets.csv** (500 rows)")
    
    if st.session_state.csv_text:
        with st.expander("🔍 View Raw CSV Data String"):
            st.text_area("CSV Text Context", value=st.session_state.csv_text, height=300, disabled=True)

# Main UI Header
st.markdown("<div class='main-title'>📊 Support Tickets AI Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>In-memory CSV analytics, statistical anomaly detection, and natural language QA (No database).</div>", unsafe_allow_html=True)

if df.empty:
    st.warning("Please ensure support_tickets.csv is placed in the project root directory.")
else:
    # 1. Summary Metric Cards
    st.subheader("📋 Dataset Overview")
    
    # Calculate stats
    total_tickets = len(df)
    open_tickets = len(df[df['status'].isin(['Open', 'Escalated'])])
    avg_rating = df['customer_rating'].mean()
    
    # Calculate anomalies list
    anomalies_list = detect_anomalies(df)
    total_anomalies = len(anomalies_list)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_tickets}</div><div class='metric-label'>Total Tickets</div></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-card' style='border-top-color: #f59e0b;'><div class='metric-value'>{open_tickets}</div><div class='metric-label'>Open / Escalated</div></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-card' style='border-top-color: #10b981;'><div class='metric-value'>{avg_rating:.2f} ★</div><div class='metric-label'>Avg Rating</div></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='metric-card' style='border-top-color: #ef4444;'><div class='metric-value'>{total_anomalies}</div><div class='metric-label'>Flagged Anomalies</div></div>", unsafe_allow_html=True)
        
    st.divider()
    
    # 2. Tabs for different functions
    tab_dashboard, tab_qa, tab_anomalies = st.tabs(["📈 Dashboard & Analytics", "💬 Ask the Data (QA)", "🚨 Anomaly Center"])
    
    # Dashboard Tab
    with tab_dashboard:
        st.subheader("Interactive Distributions")
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.write("**Tickets by Category**")
            cat_counts = df['category'].value_counts()
            st.bar_chart(cat_counts)
            
        with c2:
            st.write("**Tickets by Status**")
            status_counts = df['status'].value_counts()
            st.bar_chart(status_counts)
            
        with c3:
            st.write("**Tickets by Priority**")
            priority_counts = df['priority'].value_counts()
            st.bar_chart(priority_counts)
            
        st.write("**Sample Data View**")
        st.dataframe(df.head(10), use_container_width=True)
        
    # QA Tab
    with tab_qa:
        st.subheader("💡 Suggested Questions")
        col1, col2 = st.columns(2)
        
        sample_q1 = "How many tickets are currently open?"
        sample_q2 = "Which agent resolved the most tickets this month?"
        sample_q3 = "Show me all Critical tickets not resolved within 12 hours."
        sample_q4 = "What is the average customer rating for Technical category tickets?"
        
        with col1:
            if st.button(sample_q1, use_container_width=True):
                st.session_state.query_input = sample_q1
            if st.button(sample_q2, use_container_width=True):
                st.session_state.query_input = sample_q2
        with col2:
            if st.button(sample_q3, use_container_width=True):
                st.session_state.query_input = sample_q3
            if st.button(sample_q4, use_container_width=True):
                st.session_state.query_input = sample_q4
                
        st.divider()

        # Chat history rendering
        st.subheader("💬 Q&A Console")
        for chat in st.session_state.chat_history:
            st.markdown(f"<div class='chat-bubble user-bubble'><b>You:</b> {chat['question']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-bubble assistant-bubble'><b>Assistant ({chat['provider']}):</b>\n\n{chat['answer']}</div>", unsafe_allow_html=True)

        query_val = st.session_state.get("query_input", "")
        
        with st.form("query_form", clear_on_submit=True):
            user_query = st.text_input("Enter your question about the CSV dataset:", value=query_val)
            submit_button = st.form_submit_button("Ask")

        # Handle submission
        if submit_button and user_query:
            if "query_input" in st.session_state:
                del st.session_state.query_input
                
            with st.spinner("Analyzing CSV data..."):
                answer = generate_answer(
                    question=user_query,
                    context=st.session_state.csv_text,
                    provider=selected_provider,
                    model=model,
                    api_key=api_key,
                    host=host
                )
                
                # Store in chat history
                st.session_state.chat_history.append({
                    "question": user_query,
                    "answer": answer,
                    "provider": selected_provider
                })
                st.rerun()

        if st.session_state.chat_history:
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
                
    # Anomalies Tab
    with tab_anomalies:
        st.subheader("🚨 Detected System & SLA Anomalies")
        st.write("Calculated dynamically using statistical metrics and business SLA logic on the tickets:")
        
        if not anomalies_list:
            st.success("No anomalies detected in the dataset!")
        else:
            # Group anomalies by type
            sla_list = [a for a in anomalies_list if a["anomaly_type"] == "SLA Violation"]
            res_list = [a for a in anomalies_list if "Resolution Time" in a["anomaly_type"]]
            resp_list = [a for a in anomalies_list if "Response Time" in a["anomaly_type"]]
            rating_list = [a for a in anomalies_list if "Low Rating" in a["anomaly_type"]]
            
            anom_tab1, anom_tab2, anom_tab3, anom_tab4 = st.tabs([
                f"SLA Violations ({len(sla_list)})",
                f"Resolution Outliers ({len(res_list)})",
                f"Response Outliers ({len(resp_list)})",
                f"Rating Alerts ({len(rating_list)})"
            ])
            
            with anom_tab1:
                if sla_list:
                    st.dataframe(pd.DataFrame(sla_list), use_container_width=True)
                else:
                    st.success("No SLA violations found!")
            with anom_tab2:
                if res_list:
                    st.dataframe(pd.DataFrame(res_list), use_container_width=True)
                else:
                    st.success("No resolution time outliers found!")
            with anom_tab3:
                if resp_list:
                    st.dataframe(pd.DataFrame(resp_list), use_container_width=True)
                else:
                    st.success("No response time outliers found!")
            with anom_tab4:
                if rating_list:
                    st.dataframe(pd.DataFrame(rating_list), use_container_width=True)
                else:
                    st.success("No low rating alerts found!")
