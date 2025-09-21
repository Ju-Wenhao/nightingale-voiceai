"""
Nightingale VoiceAI Main Application Entry Point

This module orchestrates the entire patient experience pipeline across
pre-care, during-care, and post-care stages with security and provenance.
"""

import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any

from auth.consent_manager import ConsentManager
from redaction.phi_redactor import PHIRedactor  
from transcription.audio_processor import AudioProcessor
from provenance.provenance_engine import ProvenanceEngine
from summarization.summary_generator import SummaryGenerator
from database.db_manager import DatabaseManager
from config.settings import Settings

# Pydantic models for request/response
class AuthenticationRequest(BaseModel):
    patient_id: str
    consent_flags: Dict[str, Any]

# Initialize core components
settings = Settings()
security = HTTPBearer()
consent_manager = ConsentManager()
phi_redactor = PHIRedactor()
audio_processor = AudioProcessor()
provenance_engine = ProvenanceEngine()
summary_generator = SummaryGenerator()
db_manager = DatabaseManager()

"""
Logging configuration
- Default to project_root/app_logs/nightingale.log (app_logs is sibling of src)
- Allow overrides via NIGHTINGALE_LOG_DIR and NIGHTINGALE_LOG_FILE
- Use size-based rotation and also log to console
"""
import os
from logging.handlers import RotatingFileHandler

def _project_root() -> str:
    # src/main.py -> src -> project root
    return os.path.dirname(os.path.dirname(__file__))

def _resolve_log_dir() -> str:
    # Highest priority: explicit env
    env_dir = os.environ.get('NIGHTINGALE_LOG_DIR')
    if env_dir:
        return os.path.expanduser(env_dir)
    # Default: sibling folder to src
    return os.path.join(_project_root(), 'app_logs')

log_dir = _resolve_log_dir()
os.makedirs(log_dir, exist_ok=True)

default_log_file = os.path.join(log_dir, 'nightingale.log')
log_file = os.path.expanduser(os.environ.get('NIGHTINGALE_LOG_FILE', default_log_file))

log_level = os.environ.get('NIGHTINGALE_LOG_LEVEL', 'INFO').upper()

file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
console_handler = logging.StreamHandler()

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Nightingale VoiceAI...")
    await db_manager.initialize()
    yield
    # Shutdown
    logger.info("Shutting down Nightingale VoiceAI...")
    await db_manager.close()


app = FastAPI(
    title="Nightingale VoiceAI",
    description="Privacy-first healthcare voice AI with provenance tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_auth_and_consent(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication and consent for all protected endpoints"""
    try:
        # Verify JWT token and extract patient info
        patient_info = await consent_manager.verify_token(credentials.credentials)
        
        # Check consent flags
        if not consent_manager.has_required_consent(patient_info):
            raise HTTPException(status_code=403, detail="Insufficient consent permissions")
            
        return patient_info
    except Exception as e:
        logger.error(f"Authentication/consent verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication or consent")


# Root and basic endpoints
@app.get("/")
async def root():
    """Welcome message for Nightingale VoiceAI"""
    return {
        "message": "🏥 欢迎使用 Nightingale VoiceAI",
        "description": "隐私优先的医疗语音AI系统",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def root_health_check():
    """Basic health check endpoint"""
    try:
        # Test core components
        phi_health = phi_redactor.health_check()
        audio_health = audio_processor.health_check()
        summary_health = summary_generator.health_check()
        db_health = db_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "phi_redactor": phi_health,
                "audio_processor": audio_health, 
                "summary_generator": summary_health,
                "database": db_health
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.post("/api/v1/pre-care/authenticate")
async def authenticate_patient(auth_request: AuthenticationRequest):
    """Pre-care: Authenticate patient and capture consent"""
    try:
        # Generate JWT token with consent flags
        token = await consent_manager.authenticate_patient(
            auth_request.patient_id, 
            auth_request.consent_flags
        )
        
        logger.info(f"Patient authenticated: {auth_request.patient_id[:8]}...")
        return {
            "status": "success",
            "token": token,
            "expires_in": 900  # 15 minutes
        }
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=400, detail="Authentication failed")


@app.post("/api/v1/pre-care/capture-concerns")
async def capture_patient_concerns(
    audio_data: bytes,
    patient_info: dict = Depends(verify_auth_and_consent)
):
    """Pre-care: Capture and process patient concerns via voice"""
    try:
        # Process audio to text
        transcription = await audio_processor.transcribe_audio(audio_data)

        # Redact PHI before LLM processing
        redaction_result = await phi_redactor.redact_phi(transcription.text)
        redacted_text = redaction_result.redacted_text

        # Generate clinician dossier
        dossier = await summary_generator.generate_clinician_dossier(
            redacted_text, 
            transcription.metadata
        )
        
        # Store with provenance
        session_id = await db_manager.create_consultation_session(
            patient_info['patient_id'],
            transcription,
            dossier or {}
        )
        
        logger.info(f"Concerns captured for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "dossier": dossier
        }
        
    except Exception as e:
        logger.error(f"Concern capture failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process patient concerns")


@app.post("/api/v1/during-care/start-recording")
async def start_consultation_recording(
    session_id: str,
    patient_info: dict = Depends(verify_auth_and_consent)
):
    """During care: Start real-time consultation recording"""
    try:
        # Initialize recording session
        recording_session = await audio_processor.start_streaming_session(session_id)
        
        logger.info(f"Started recording for session: {session_id}")
        return {
            "status": "success",
            "recording_session": recording_session,
            "chunk_interval": 30  # seconds
        }
        
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to start consultation recording")


@app.post("/api/v1/during-care/process-audio")
async def process_audio_file(
    audio: UploadFile = File(...),
    patient_id: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """During care: Process complete audio file"""
    try:
        # Verify authentication token
        token = credentials.credentials
        patient_info = await consent_manager.verify_token(token)
        
        # Verify patient ID matches
        if patient_info.patient_id != consent_manager._hash_patient_id(patient_id):
            raise HTTPException(status_code=403, detail="Patient ID mismatch")
        
        # Read audio data
        audio_data = await audio.read()
        
        # Start consultation session
        session_id = await db_manager.create_consultation_session(
            patient_info.patient_id,
            None,  # Will be updated with transcription
            {}   # Will be updated with dossier
        )
        
        # Process audio to text
        transcription = await audio_processor.transcribe_audio(audio_data)

        # Redact PHI before processing (extract redacted text string)
        redaction_result = await phi_redactor.redact_phi(transcription.text)
        redacted_text = redaction_result.redacted_text
        
        # Add provenance mapping
        provenance_data = await provenance_engine.map_provenance(
            redacted_text,
            transcription.timestamps,
            session_id
        )
        
        # Generate summaries
        clinician_summary = await summary_generator.generate_clinician_summary(
            [{"text": redacted_text, "metadata": transcription.metadata}]
        )
        
        patient_summary = await summary_generator.generate_patient_summary(
            [{"text": redacted_text, "metadata": transcription.metadata}]
        )
        
        # Store results
        consultation_data = {
            "session_id": session_id,
            "transcription": transcription,
            "redacted_text": redacted_text,
            "provenance": provenance_data,
            "clinician_summary": clinician_summary,
            "patient_summary": patient_summary
        }
        
        await db_manager.update_consultation_session(session_id, consultation_data)
        
        logger.info(f"Audio processed successfully for session: {session_id}")
        return {
            "status": "success",
            "session_id": session_id,
            "transcription": transcription.text,
            "clinician_summary": clinician_summary,
            "patient_summary": patient_summary,
            "processing_metadata": {
                "audio_duration": transcription.metadata.get("duration", 0),
                "word_count": len(redacted_text.split()),
                "processed_at": datetime.now().isoformat()
            }
        }
        
    except ValueError as ve:
        # Handle authentication/authorization errors specifically
        if "expired" in str(ve).lower() or "invalid" in str(ve).lower():
            logger.error(f"Audio processing failed: {ve}")
            raise HTTPException(status_code=401, detail=str(ve))
        else:
            logger.error(f"Audio processing failed: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process audio file")


@app.post("/api/v1/during-care/process-chunk")
async def process_audio_chunk(
    session_id: str,
    chunk_data: bytes,
    chunk_metadata: dict,
    patient_info: dict = Depends(verify_auth_and_consent)
):
    """During care: Process real-time audio chunks"""
    try:
        # Transcribe chunk
        chunk_transcription = await audio_processor.transcribe_chunk(
            chunk_data, 
            chunk_metadata
        )
        
        # Redact PHI
        redacted_chunk = await phi_redactor.redact_phi(chunk_transcription.text)
        redacted_chunk_text = redacted_chunk.redacted_text
        
        # Add provenance mapping
        provenance_chunk = await provenance_engine.map_provenance(
            redacted_chunk_text,
            chunk_transcription.timestamps,
            session_id
        )
        
        # Store chunk
        await db_manager.store_transcription_chunk(session_id, provenance_chunk)
        
        return {
            "status": "success",
            "chunk_id": provenance_chunk.chunk_id,
            "transcription": provenance_chunk.text
        }
        
    except Exception as e:
        logger.error(f"Chunk processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process audio chunk")


@app.post("/api/v1/during-care/generate-summaries")
async def generate_consultation_summaries(
    session_id: str,
    patient_info: dict = Depends(verify_auth_and_consent)
):
    """During care: Generate dual summaries with provenance"""
    try:
        # Retrieve full consultation data
        consultation_data = await db_manager.get_consultation_data(session_id)

        # Build transcript data list expected by summary generator
        transcript_data = []
        if consultation_data:
            if isinstance(consultation_data.get("redacted_text"), str) and consultation_data.get("redacted_text"):
                meta = {}
                trans_obj = consultation_data.get("transcription")
                if trans_obj is not None and hasattr(trans_obj, "metadata"):
                    meta = getattr(trans_obj, "metadata", {}) or {}
                transcript_data.append({"text": consultation_data.get("redacted_text", ""), "metadata": meta})
            elif consultation_data.get("transcription") is not None:
                trans_obj = consultation_data.get("transcription")
                text_val = getattr(trans_obj, "text", "") if hasattr(trans_obj, "text") else ""
                meta = getattr(trans_obj, "metadata", {}) if hasattr(trans_obj, "metadata") else {}
                transcript_data.append({"text": text_val, "metadata": meta})

        if not transcript_data:
            transcript_data = [{"text": "", "metadata": {}}]

        # Generate clinician summary
        clinician_summary = await summary_generator.generate_clinician_summary(
            transcript_data,
            include_provenance=True
        )

        # Generate patient summary  
        patient_summary = await summary_generator.generate_patient_summary(
            transcript_data,
            include_provenance=True,
            patient_info=patient_info
        )
        
        # Store summaries
        await db_manager.store_summaries(session_id, clinician_summary, patient_summary)
        
        logger.info(f"Summaries generated for session: {session_id}")
        return {
            "status": "success",
            "clinician_summary": clinician_summary,
            "patient_summary": patient_summary
        }
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summaries")


@app.post("/api/v1/post-care/query")
async def post_care_query(
    query: str,
    session_id: str,
    patient_info: dict = Depends(verify_auth_and_consent)
):
    """Post-care: Query consultation data with context awareness"""
    try:
        # Retrieve consultation context
        context = await db_manager.get_consultation_context(session_id)
        
        # Process query with memory
        response = await summary_generator.process_patient_query(
            query,
            context,
            patient_info
        )
        
        logger.info(f"Post-care query processed for session: {session_id}")
        return {
            "status": "success",
            "response": response.get("response"),
            "sources": response.get("provenance_refs")
        }
        
    except Exception as e:
        logger.error(f"Post-care query failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")


@app.get("/api/v1/health")
async def api_health():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "database": await db_manager.health_check(),
            "phi_redactor": phi_redactor.health_check(),
            "audio_processor": audio_processor.health_check()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )