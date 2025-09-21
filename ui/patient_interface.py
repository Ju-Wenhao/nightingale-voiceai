"""
Nightingale VoiceAI - Professional Patient Portal Interface

A professional healthcare voice AI system interface supporting:
- Digital consent form management
- Secure patient authentication
- Audio upload and processing
- Real-time summary generation and review

Clinical Grade Interface Design:
- HIPAA compliant workflows
- Professional medical terminology
- Clean, accessible user experience
- Comprehensive error handling
"""

import streamlit as st
import requests
import json
import time
import io
from typing import Dict, Any, Optional
from datetime import datetime

# Configure page with professional styling
st.set_page_config(
    page_title="Nightingale VoiceAI - Patient Portal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section-header {
        background-color: #ecf0f1;
        padding: 0.5rem 1rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
        font-weight: 600;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8888"

class NightingaleAPI:
    """Professional API client for Nightingale VoiceAI backend services"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    @property
    def token(self):
        """Get the authentication token from session state"""
        return getattr(st.session_state, 'auth_token', None)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health verification"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            return {"success": True, "data": response.json() if response.status_code == 200 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate(self, patient_id: str, consent_data: Dict[str, bool]) -> Dict[str, Any]:
        """Authenticate patient with consent verification"""
        try:
            payload = {
                "patient_id": patient_id,
                "consent_flags": consent_data
            }
            
            response = requests.post(f"{self.base_url}/api/v1/pre-care/authenticate", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Store token in session state instead of instance variable
                st.session_state.auth_token = result.get("token")
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": f"Authentication failed with status: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Network connectivity error: {str(e)}"}
    
    def process_audio(self, patient_id: str, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """Process audio file through healthcare pipeline"""
        try:
            token = getattr(st.session_state, 'auth_token', None)
            if not token:
                return {"success": False, "error": "Authentication token required"}
            
            files = {"audio": (filename, io.BytesIO(audio_data), "audio/wav")}
            data = {"patient_id": patient_id}
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.post(
                f"{self.base_url}/api/v1/during-care/process-audio",
                files=files,
                data=data,
                headers=headers,
                timeout=300
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 401 or response.status_code == 403:
                return {"success": False, "error": "Authentication expired. Please re-authenticate.", "auth_error": True}
            else:
                return {"success": False, "error": f"Audio processing failed with status: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Processing error: {str(e)}"}
    
    def get_summary(self, patient_id: str, summary_type: str = "patient") -> Dict[str, Any]:
        """Retrieve patient summary from system"""
        try:
            token = getattr(st.session_state, 'auth_token', None)
            if not token:
                return {"success": False, "error": "Authentication token required"}
            
            headers = {"Authorization": f"Bearer {token}"}
            params = {"patient_id": patient_id, "summary_type": summary_type}
            
            response = requests.get(
                f"{self.base_url}/api/v1/post-care/summary",
                params=params,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Summary retrieval failed with status: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Retrieval error: {str(e)}"}

# Initialize session state variables
def init_session_state():
    """Initialize application session state variables"""
    defaults = {
        'authenticated': False,
        'patient_id': '',
        'consent_data': {},
        'processing_complete': False,
        'current_step': 'consent',
        'api_client': NightingaleAPI(),
        'auth_token': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def render_system_status():
    """Display system connectivity status"""
    with st.sidebar:
        st.markdown('<div class="section-header">System Status</div>', unsafe_allow_html=True)
        
        # Check API connectivity
        health_result = st.session_state.api_client.health_check()
        
        if health_result["success"]:
            st.markdown('<div class="status-success">Backend Service: Connected</div>', unsafe_allow_html=True)
            if health_result["data"]:
                st.write("**Service Information:**")
                for key, value in health_result["data"].items():
                    if key != "components":
                        st.write(f"- {key.title()}: {value}")
        else:
            st.markdown('<div class="status-error">Backend Service: Disconnected</div>', unsafe_allow_html=True)
            st.error(f"Connection Error: {health_result['error']}")
        
        # Display authentication status
        if st.session_state.authenticated:
            st.markdown('<div class="status-success">Patient Authentication: Verified</div>', unsafe_allow_html=True)
            st.write(f"**Patient ID:** {st.session_state.patient_id}")
        else:
            st.markdown('<div class="status-warning">Patient Authentication: Pending</div>', unsafe_allow_html=True)

def render_consent_form():
    """Render digital consent form interface"""
    st.markdown('<div class="section-header">Digital Consent Form</div>', unsafe_allow_html=True)
    
    st.write("""
    **INFORMED CONSENT FOR HEALTHCARE VOICE AI PROCESSING**
    
    Please review and provide consent for the following data processing activities:
    """)
    
    consent_items = {
        "data_processing": "I consent to the processing of my voice data for healthcare analysis",
        "phi_handling": "I consent to the secure handling of my Protected Health Information (PHI)",
        "ai_analysis": "I consent to AI-powered analysis of my healthcare communications", 
        "summary_generation": "I consent to the generation of clinical summaries from my data",
        "secure_storage": "I consent to secure, temporary storage of my voice recordings"
    }
    
    with st.form("consent_form"):
        st.subheader("Required Consent Items")
        
        # Create checkboxes
        data_processing = st.checkbox("I consent to the processing of my voice data for healthcare analysis")
        phi_handling = st.checkbox("I consent to the secure handling of my Protected Health Information (PHI)")
        ai_analysis = st.checkbox("I consent to AI-powered analysis of my healthcare communications")
        summary_generation = st.checkbox("I consent to the generation of clinical summaries from my data")
        secure_storage = st.checkbox("I consent to secure, temporary storage of my voice recordings")
        
        st.subheader("Patient Identification")
        patient_id = st.text_input(
            "Patient ID",
            placeholder="Enter your patient identification number",
            help="Enter the patient ID provided by your healthcare provider"
        )
        
        # Submit button (always enabled, validation happens on submit)
        submitted = st.form_submit_button("Submit Consent Form", type="primary")
        
        if submitted:
            # Check all conditions
            all_consents = [data_processing, phi_handling, ai_analysis, summary_generation, secure_storage]
            all_consented = all(all_consents)
            patient_id_provided = bool(patient_id and patient_id.strip())
            
            if all_consented and patient_id_provided:
                # Map to backend expected format
                consent_data = {
                    "audio_recording": data_processing,  # Map data_processing to audio_recording
                    "transcription": phi_handling,       # Map phi_handling to transcription
                    "ai_processing": ai_analysis,        # Map ai_analysis to ai_processing
                    "data_storage": secure_storage,      # Map secure_storage to data_storage
                    "summary_generation": summary_generation  # This matches
                }
                st.session_state.consent_data = consent_data
                st.session_state.patient_id = patient_id.strip()
                st.session_state.current_step = 'authentication'
                st.success("Consent form submitted successfully!")
                time.sleep(1)
                st.rerun()
            else:
                if not all_consented:
                    st.error("Please check all required consent items.")
                if not patient_id_provided:
                    st.error("Please enter your Patient ID.")

def render_authentication():
    """Render patient authentication interface"""
    st.markdown('<div class="section-header">Patient Authentication</div>', unsafe_allow_html=True)
    
    st.write(f"""
    **Patient ID:** {st.session_state.patient_id}
    
    **Consent Summary:**
    """)
    
    # Display consent summary
    consent_summary = []
    for key, consented in st.session_state.consent_data.items():
        status = "Granted" if consented else "Denied"
        consent_summary.append(f"- {key.replace('_', ' ').title()}: {status}")
    
    st.write('\n'.join(consent_summary))
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Authenticate Patient", type="primary"):
            with st.spinner("Authenticating patient credentials..."):
                result = st.session_state.api_client.authenticate(
                    st.session_state.patient_id,
                    st.session_state.consent_data
                )
                
                if result["success"]:
                    st.session_state.authenticated = True
                    st.session_state.current_step = 'audio_processing'
                    # Display token info for debugging
                    token_info = result.get("data", {})
                    if "expires_in" in token_info:
                        st.success(f"Patient authentication successful (Token valid for {token_info['expires_in']} seconds)")
                    else:
                        st.success("Patient authentication successful")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Authentication failed: {result['error']}")
    
    with col2:
        if st.button("Modify Consent"):
            st.session_state.current_step = 'consent'
            st.rerun()

def render_audio_processing():
    """Render audio upload and processing interface"""
    st.markdown('<div class="section-header">Audio Processing</div>', unsafe_allow_html=True)
    
    # Show authentication status
    if st.session_state.api_client.token:
        st.success("✓ Authenticated - Ready for audio processing")
    else:
        st.warning("⚠ Authentication token not found - Please re-authenticate")
        if st.button("Return to Authentication"):
            st.session_state.authenticated = False
            st.session_state.current_step = 'authentication'
            st.rerun()
        return
    
    st.write("""
    **Instructions for Audio Upload:**
    
    1. Select a high-quality audio file (WAV, MP3, M4A formats supported)
    2. Ensure clear audio quality for optimal transcription accuracy
    3. Maximum file size: 100MB
    4. Processing time varies based on file duration
    """)
    
    uploaded_file = st.file_uploader(
        "Select Audio File",
        type=['wav', 'mp3', 'm4a'],
        help="Upload your audio file for processing"
    )
    
    if uploaded_file:
        st.write("**File Information:**")
        st.write(f"- Filename: {uploaded_file.name}")
        st.write(f"- File size: {uploaded_file.size / 1024 / 1024:.2f} MB")
        st.write(f"- File type: {uploaded_file.type}")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Process Audio File", type="primary"):
                with st.spinner("Processing audio through healthcare pipeline..."):
                    progress_bar = st.progress(0)
                    
                    # Simulate processing steps
                    steps = [
                        "Uploading audio file...",
                        "Transcribing audio content...", 
                        "Applying PHI redaction...",
                        "Generating clinical analysis...",
                        "Creating patient summary..."
                    ]
                    
                    for i, step in enumerate(steps):
                        st.write(f"Step {i+1}/5: {step}")
                        progress_bar.progress((i + 1) / len(steps))
                        time.sleep(2)
                    
                    # Process the audio
                    result = st.session_state.api_client.process_audio(
                        st.session_state.patient_id,
                        uploaded_file.read(),
                        uploaded_file.name
                    )
                    
                    if result["success"]:
                        st.session_state.processing_complete = True
                        st.session_state.current_step = 'summary'
                        st.success("Audio processing completed successfully")
                        time.sleep(1)
                        st.rerun()
                    else:
                        if result.get("auth_error"):
                            st.error("Authentication expired. Redirecting to authentication page...")
                            st.session_state.authenticated = False
                            st.session_state.current_step = 'authentication'
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Processing failed: {result['error']}")
        
        with col2:
            if st.button("Return to Authentication"):
                st.session_state.current_step = 'authentication'
                st.rerun()

def render_summary_view():
    """Render summary and results interface"""
    st.markdown('<div class="section-header">Clinical Summary</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Patient Summary", "Clinical Notes"])
    
    with tab1:
        st.subheader("Patient Summary")
        
        if st.button("Generate Patient Summary", type="primary"):
            with st.spinner("Generating patient summary..."):
                result = st.session_state.api_client.get_summary(
                    st.session_state.patient_id,
                    "patient"
                )
                
                if result["success"] and result["data"]:
                    summary_data = result["data"]
                    
                    st.write("**Summary Generated:**", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    if "summary" in summary_data:
                        st.markdown("**Clinical Summary:**")
                        st.write(summary_data["summary"])
                    
                    if "key_points" in summary_data:
                        st.markdown("**Key Clinical Points:**")
                        for point in summary_data["key_points"]:
                            st.write(f"• {point}")
                    
                    if "recommendations" in summary_data:
                        st.markdown("**Clinical Recommendations:**")
                        for rec in summary_data["recommendations"]:
                            st.write(f"• {rec}")
                    
                else:
                    st.warning("No summary data available. Please ensure audio processing is complete.")
    
    with tab2:
        st.subheader("Clinical Notes")
        
        if st.button("Generate Clinical Notes"):
            with st.spinner("Generating clinical documentation..."):
                result = st.session_state.api_client.get_summary(
                    st.session_state.patient_id,
                    "clinician"
                )
                
                if result["success"] and result["data"]:
                    clinical_data = result["data"]
                    
                    st.write("**Documentation Generated:**", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    if "clinical_notes" in clinical_data:
                        st.markdown("**Clinical Documentation:**")
                        st.write(clinical_data["clinical_notes"])
                    
                    if "diagnosis_codes" in clinical_data:
                        st.markdown("**Relevant Diagnosis Codes:**")
                        for code in clinical_data["diagnosis_codes"]:
                            st.write(f"• {code}")
                
                else:
                    st.warning("Clinical notes not available. Please ensure audio processing is complete.")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Process New Audio"):
            st.session_state.current_step = 'audio_processing'
            st.rerun()
    
    with col2:
        if st.button("New Patient Session"):
            # Reset session
            for key in ['authenticated', 'patient_id', 'consent_data', 'processing_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 'consent'
            st.rerun()
    
    with col3:
        if st.button("Export Summary", help="Download summary as PDF/document"):
            st.info("Export functionality will be available in future releases")

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Render header
    st.markdown("""
    <div class="main-header">
        <h1>Nightingale VoiceAI - Patient Portal</h1>
        <p>Professional Healthcare Voice Processing System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render system status in sidebar
    render_system_status()
    
    # Navigation menu in sidebar
    with st.sidebar:
        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        
        steps = {
            'consent': 'Digital Consent',
            'authentication': 'Patient Authentication', 
            'audio_processing': 'Audio Processing',
            'summary': 'Clinical Summary'
        }
        
        for step_key, step_name in steps.items():
            if st.session_state.current_step == step_key:
                st.write(f"**→ {step_name}**")
            else:
                st.write(f"   {step_name}")
    
    # Main content area based on current step
    if st.session_state.current_step == 'consent':
        render_consent_form()
    elif st.session_state.current_step == 'authentication':
        if st.session_state.authenticated:
            st.session_state.current_step = 'audio_processing'
            st.rerun()
        else:
            render_authentication()
    elif st.session_state.current_step == 'audio_processing':
        render_audio_processing()
    elif st.session_state.current_step == 'summary':
        render_summary_view()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em; padding: 1rem;'>
        Nightingale VoiceAI Professional Healthcare System<br>
        HIPAA Compliant | Secure | Professional Grade
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()