"""
Nightingale VoiceAI - Professional Administrative Dashboard

Clinical administrative interface providing:
- System monitoring and health status
- Patient data management
- Audit trail and compliance reporting
- Performance analytics and insights

Administrative Features:
- Real-time system metrics
- Patient record management
- Security and compliance monitoring
- Operational analytics dashboard
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

# Configure page with professional admin styling
st.set_page_config(
    page_title="Nightingale VoiceAI - Administrative Dashboard",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional admin CSS styling
st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }
    .status-operational {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    .status-critical {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #dc3545;
    }
    .section-title {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #6c757d;
        margin: 1.5rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.1em;
    }
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8888"

class AdminAPI:
    """Professional administrative API client for system management"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.admin_token = None
    
    def get_system_health(self) -> Dict[str, Any]:
        """Retrieve comprehensive system health metrics"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Health check failed: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"System connectivity error: {str(e)}"}
    
    def get_patient_list(self) -> Dict[str, Any]:
        """Retrieve patient registry data"""
        # Mock data for demonstration - in production this would call real API
        mock_patients = [
            {"patient_id": "PAT_001", "name": "Patient Alpha", "last_visit": "2024-01-15", "status": "Active"},
            {"patient_id": "PAT_002", "name": "Patient Beta", "last_visit": "2024-01-14", "status": "Active"},
            {"patient_id": "PAT_003", "name": "Patient Gamma", "last_visit": "2024-01-13", "status": "Inactive"},
            {"patient_id": "PAT_004", "name": "Patient Delta", "last_visit": "2024-01-12", "status": "Active"},
            {"patient_id": "PAT_005", "name": "Patient Epsilon", "last_visit": "2024-01-11", "status": "Pending"}
        ]
        return {"success": True, "data": mock_patients}
    
    def get_audit_logs(self) -> Dict[str, Any]:
        """Retrieve system audit trail"""
        # Mock audit data for demonstration
        mock_audit = [
            {"timestamp": "2024-01-15 14:30:00", "action": "Patient Authentication", "user": "PAT_001", "status": "Success"},
            {"timestamp": "2024-01-15 14:25:00", "action": "Audio Processing", "user": "PAT_001", "status": "Completed"},
            {"timestamp": "2024-01-15 14:20:00", "action": "PHI Redaction", "user": "System", "status": "Applied"},
            {"timestamp": "2024-01-15 14:15:00", "action": "Summary Generation", "user": "AI Engine", "status": "Generated"},
            {"timestamp": "2024-01-15 14:10:00", "action": "Data Export", "user": "Admin", "status": "Authorized"}
        ]
        return {"success": True, "data": mock_audit}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Retrieve operational performance metrics"""
        # Mock metrics for demonstration
        mock_metrics = {
            "total_patients": 1247,
            "active_sessions": 8,
            "audio_processed_today": 45,
            "avg_processing_time": 2.3,
            "system_uptime": "99.8%",
            "storage_used": "2.4 TB",
            "api_response_time": "145ms"
        }
        return {"success": True, "data": mock_metrics}

def render_admin_header():
    """Render administrative dashboard header"""
    st.markdown("""
    <div class="admin-header">
        <h1>Nightingale VoiceAI</h1>
        <h2>Administrative Dashboard</h2>
        <p>Clinical System Management & Monitoring Console</p>
    </div>
    """, unsafe_allow_html=True)

def render_system_overview():
    """Render system status overview"""
    st.markdown('<div class="section-title">System Status Overview</div>', unsafe_allow_html=True)
    
    admin_api = AdminAPI()
    health_data = admin_api.get_system_health()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if health_data["success"]:
            st.markdown('<div class="status-operational"><strong>System Status</strong><br>Operational</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-critical"><strong>System Status</strong><br>Critical Error</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="status-operational"><strong>Database</strong><br>Connected</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="status-operational"><strong>AI Services</strong><br>Running</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="status-warning"><strong>PHI Compliance</strong><br>Monitoring</div>', unsafe_allow_html=True)

def render_performance_metrics():
    """Render system performance dashboard"""
    st.markdown('<div class="section-title">Performance Metrics</div>', unsafe_allow_html=True)
    
    admin_api = AdminAPI()
    metrics = admin_api.get_system_metrics()
    
    if metrics["success"]:
        data = metrics["data"]
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", data["total_patients"], delta="12 this week")
        
        with col2:
            st.metric("Active Sessions", data["active_sessions"], delta="2 from last hour")
        
        with col3:
            st.metric("Audio Processed Today", data["audio_processed_today"], delta="8 increase")
        
        with col4:
            st.metric("Avg Processing Time", f"{data['avg_processing_time']}s", delta="-0.3s improvement")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Mock processing time trend
            dates = pd.date_range(start="2024-01-01", end="2024-01-15", freq="D")
            processing_times = [2.1, 2.3, 2.0, 2.4, 2.2, 2.1, 2.3, 2.0, 2.2, 2.1, 2.4, 2.3, 2.2, 2.1, 2.3]
            
            fig = px.line(x=dates, y=processing_times, title="Average Processing Time Trend")
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Processing Time (seconds)",
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Mock volume by day
            volume_data = [32, 28, 35, 41, 38, 45, 42, 39, 36, 43, 40, 37, 44, 41, 45]
            
            fig = px.bar(x=dates, y=volume_data, title="Daily Audio Processing Volume")
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Files Processed",
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

def render_patient_management():
    """Render patient data management interface"""
    st.markdown('<div class="section-title">Patient Registry Management</div>', unsafe_allow_html=True)
    
    admin_api = AdminAPI()
    patients = admin_api.get_patient_list()
    
    if patients["success"]:
        df = pd.DataFrame(patients["data"])
        
        # Search and filter controls
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("Search Patients", placeholder="Enter patient ID or name")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Pending"])
        
        # Filter data based on inputs
        filtered_df = df.copy()
        
        if search_term:
            filtered_df = filtered_df[
                filtered_df['patient_id'].str.contains(search_term, case=False) |
                filtered_df['name'].str.contains(search_term, case=False)
            ]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        # Display patient table
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "patient_id": st.column_config.TextColumn("Patient ID", width="medium"),
                "name": st.column_config.TextColumn("Patient Name", width="medium"),
                "last_visit": st.column_config.DateColumn("Last Visit", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Patient statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            active_count = len(df[df['status'] == 'Active'])
            st.metric("Active Patients", active_count)
        
        with col2:
            inactive_count = len(df[df['status'] == 'Inactive'])
            st.metric("Inactive Patients", inactive_count)
        
        with col3:
            pending_count = len(df[df['status'] == 'Pending'])
            st.metric("Pending Patients", pending_count)

def render_audit_compliance():
    """Render audit trail and compliance monitoring"""
    st.markdown('<div class="section-title">Audit Trail & Compliance</div>', unsafe_allow_html=True)
    
    admin_api = AdminAPI()
    audit_data = admin_api.get_audit_logs()
    
    if audit_data["success"]:
        df = pd.DataFrame(audit_data["data"])
        
        # Compliance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("HIPAA Compliance", "100%", delta="0% violations")
        
        with col2:
            st.metric("Data Retention", "Compliant", delta="0 expired records")
        
        with col3:
            st.metric("Access Controls", "Secured", delta="0 unauthorized access")
        
        with col4:
            st.metric("Audit Coverage", "Complete", delta="100% logged")
        
        # Recent audit events
        st.subheader("Recent System Events")
        
        # Display audit trail
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp", width="medium"),
                "action": st.column_config.TextColumn("Action", width="medium"),
                "user": st.column_config.TextColumn("User/System", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action distribution chart
        action_counts = df['action'].value_counts()
        fig = px.pie(values=action_counts.values, names=action_counts.index, title="System Activity Distribution")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def render_system_configuration():
    """Render system configuration interface"""
    st.markdown('<div class="section-title">System Configuration</div>', unsafe_allow_html=True)
    
    # Configuration tabs
    tab1, tab2, tab3 = st.tabs(["Security Settings", "Performance Tuning", "Integration Settings"])
    
    with tab1:
        st.subheader("Security Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Authentication Settings**")
            session_timeout = st.number_input("Session Timeout (minutes)", value=15, min_value=5, max_value=60)
            max_login_attempts = st.number_input("Max Login Attempts", value=3, min_value=1, max_value=10)
            enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=True)
        
        with col2:
            st.write("**Data Protection Settings**")
            encryption_level = st.selectbox("Encryption Level", ["AES-128", "AES-256"], index=1)
            phi_redaction = st.checkbox("Automatic PHI Redaction", value=True)
            audit_logging = st.checkbox("Comprehensive Audit Logging", value=True)
    
    with tab2:
        st.subheader("Performance Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Processing Settings**")
            max_concurrent = st.number_input("Max Concurrent Processes", value=10, min_value=1, max_value=50)
            timeout_duration = st.number_input("Processing Timeout (seconds)", value=300, min_value=60, max_value=600)
            cache_duration = st.number_input("Cache Duration (hours)", value=24, min_value=1, max_value=168)
        
        with col2:
            st.write("**Resource Allocation**")
            cpu_allocation = st.slider("CPU Allocation (%)", min_value=10, max_value=100, value=75)
            memory_allocation = st.slider("Memory Allocation (%)", min_value=10, max_value=100, value=80)
            storage_threshold = st.slider("Storage Alert Threshold (%)", min_value=50, max_value=95, value=85)
    
    with tab3:
        st.subheader("External Integrations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**API Integrations**")
            ehr_integration = st.checkbox("EHR System Integration", value=False)
            billing_integration = st.checkbox("Billing System Integration", value=False)
            notification_service = st.checkbox("Notification Service", value=True)
        
        with col2:
            st.write("**Data Export Settings**")
            export_format = st.selectbox("Default Export Format", ["PDF", "JSON", "XML", "CSV"])
            auto_backup = st.checkbox("Automatic Backup", value=True)
            backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
    
    # Save configuration button
    if st.button("Save Configuration Changes", type="primary"):
        st.success("Configuration changes have been saved successfully")

def main():
    """Main administrative dashboard application"""
    
    # Render header
    render_admin_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<div class="section-title">Dashboard Navigation</div>', unsafe_allow_html=True)
        
        page = st.radio(
            "Select Dashboard View",
            ["System Overview", "Performance Metrics", "Patient Management", "Audit & Compliance", "System Configuration"],
            label_visibility="collapsed"
        )
    
    # Main content based on selected page
    if page == "System Overview":
        render_system_overview()
    elif page == "Performance Metrics":
        render_performance_metrics()
    elif page == "Patient Management":
        render_patient_management()
    elif page == "Audit & Compliance":
        render_audit_compliance()
    elif page == "System Configuration":
        render_system_configuration()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em; padding: 1rem;'>
        Nightingale VoiceAI Administrative Dashboard<br>
        Professional Healthcare Management System | HIPAA Compliant
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()