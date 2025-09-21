"""
Simplified Audio Processor for MVP
Mock audio processing until we install Whisper
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import asyncio


@dataclass
class TranscriptionResult:
    """Audio transcription result"""
    text: str
    confidence: float
    timestamps: List[Dict]
    metadata: Dict[str, Any]


class AudioProcessor:
    """Mock audio processor for development"""
    
    def __init__(self):
        self.sessions = {}
    
    async def transcribe_audio(self, audio_data: bytes) -> TranscriptionResult:
        """Mock transcription - returns demo text"""
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Mock transcription result
        mock_text = "Patient reports headache with pain level 7 out of 10. Duration approximately three days."
        
        return TranscriptionResult(
            text=mock_text,
            confidence=0.95,
            timestamps=[
                {"start_time": 0.0, "end_time": 5.2, "text": "Patient reports headache"},
                {"start_time": 5.3, "end_time": 10.1, "text": "with pain level 7 out of 10"},
                {"start_time": 10.2, "end_time": 15.8, "text": "Duration approximately three days"}
            ],
            metadata={"mock": True, "language": "en"}
        )
    
    async def start_streaming_session(self, session_id: str) -> Dict:
        """Start mock streaming session"""
        self.sessions[session_id] = {"status": "active", "chunks": []}
        return {"session_id": session_id, "status": "started"}
    
    async def transcribe_chunk(self, chunk_data: bytes, metadata: Dict) -> TranscriptionResult:
        """Mock chunk transcription"""
        await asyncio.sleep(0.05)
        
        chunk_text = f"Audio chunk transcribed at {metadata.get('timestamp', 0)}"
        
        return TranscriptionResult(
            text=chunk_text,
            confidence=0.90,
            timestamps=[{"start_time": 0.0, "end_time": 3.0, "text": chunk_text}],
            metadata=metadata
        )
    
    def health_check(self) -> Dict[str, str]:
        """Health check"""
        return {"status": "healthy", "type": "mock_processor"}