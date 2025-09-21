"""
Simplified Database Manager for MVP
Uses in-memory storage for development
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class DatabaseManager:
    """Mock database manager using in-memory storage"""
    
    def __init__(self):
        self.patients = {}
        self.consultations = {}
        self.summaries = {}
        self.sessions = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize database connection"""
        self.initialized = True
        print("✅ Database initialized (in-memory mock)")
    
    async def close(self):
        """Close database connection"""
        print("✅ Database connection closed")
    
    async def health_check(self) -> str:
        """Database health check"""
        return "healthy" if self.initialized else "unhealthy"
    
    async def create_consultation_session(self, 
                                        patient_id: str, 
                                        transcription: Any,
                                        dossier: Dict) -> str:
        """Create new consultation session"""
        
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "patient_id": patient_id,
            "transcription": transcription,
            "dossier": dossier,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        self.sessions[session_id] = session_data
        self.consultations[session_id] = session_data
        
        return session_id
    
    async def store_transcription_chunk(self, session_id: str, chunk: Any):
        """Store transcription chunk"""
        if session_id in self.sessions:
            if "chunks" not in self.sessions[session_id]:
                self.sessions[session_id]["chunks"] = []
            self.sessions[session_id]["chunks"].append(chunk)
    
    async def update_consultation_session(self, session_id: str, data: Dict[str, Any]):
        """Update an existing consultation session with new data
        
        Merges the provided data into both session and consultation records.
        Adds/refreshes an 'updated_at' timestamp and marks status as 'completed' if provided data looks final.
        """
        if session_id not in self.sessions:
            # If session does not exist, create a minimal record to avoid AttributeError in MVP
            self.sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
        if session_id not in self.consultations:
            self.consultations[session_id] = {
                "session_id": session_id,
                "created_at": datetime.utcnow(),
                "status": "active"
            }

        # Merge updates
        self.sessions[session_id].update(data or {})
        self.consultations[session_id].update(data or {})

        # Set bookkeeping fields
        self.sessions[session_id]["updated_at"] = datetime.utcnow()
        self.consultations[session_id]["updated_at"] = self.sessions[session_id]["updated_at"]

        # Heuristic: mark as completed if summaries or redacted text/transcription present
        if any(k in (data or {}) for k in ["clinician_summary", "patient_summary", "redacted_text", "transcription"]):
            self.sessions[session_id]["status"] = "completed"
            self.consultations[session_id]["status"] = "completed"
    
    async def get_consultation_data(self, session_id: str) -> Optional[Dict]:
        """Retrieve consultation data"""
        return self.consultations.get(session_id)
    
    async def store_summaries(self, 
                            session_id: str, 
                            clinician_summary: Any,
                            patient_summary: Any):
        """Store generated summaries"""
        
        summary_id = str(uuid.uuid4())
        
        summary_data = {
            "summary_id": summary_id,
            "session_id": session_id,
            "clinician_summary": clinician_summary,
            "patient_summary": patient_summary,
            "created_at": datetime.utcnow()
        }
        
        self.summaries[summary_id] = summary_data
        
        # Also update session with summary reference
        if session_id in self.sessions:
            self.sessions[session_id]["summary_id"] = summary_id
    
    async def get_consultation_context(self, session_id: str) -> Dict:
        """Get consultation context for queries"""
        
        session_data = self.sessions.get(session_id, {})
        consultation_data = self.consultations.get(session_id, {})
        
        return {
            "session_id": session_id,
            "transcription": session_data.get("transcription"),
            "dossier": session_data.get("dossier"),
            "chunks": session_data.get("chunks", []),
            "consultation": consultation_data
        }