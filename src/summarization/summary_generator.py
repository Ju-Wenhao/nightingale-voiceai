"""
Simplified Summary Generator for MVP
Mock summary generation until we integrate LLM
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import asyncio


@dataclass
class SummaryResult:
    """Summary generation result"""
    content: List[Dict[str, Any]]
    summary_type: str
    provenance_count: int
    metadata: Dict[str, Any]


class SummaryGenerator:
    """Mock summary generator for development"""
    
    def health_check(self) -> dict:
        """Basic health check for summary generator"""
        return {"status": "healthy", "model": "mock"}
    
    async def generate_clinician_summary(self, 
                                       transcript_data: List[Dict], 
                                       include_provenance: bool = True) -> SummaryResult:
        """Generate mock clinician summary"""
        
        await asyncio.sleep(0.2)  # Simulate LLM processing
        
        # Mock clinician summary content
        content = [
            {
                "bullet": "Patient reports severe headaches, 3-week duration",
                "provenance_id": "S1" if include_provenance else None,
                "source_span": {
                    "start_time": 30.0,
                    "end_time": 36.5,
                    "transcript_ref": "T1"
                } if include_provenance else None
            },
            {
                "bullet": "Pain intensity 7-8/10, throbbing quality",
                "provenance_id": "S2" if include_provenance else None,
                "source_span": {
                    "start_time": 37.0,
                    "end_time": 42.3,
                    "transcript_ref": "T2"
                } if include_provenance else None
            },
            {
                "bullet": "Associated symptoms: photophobia, mild nausea",
                "provenance_id": "S3" if include_provenance else None,
                "source_span": {
                    "start_time": 90.0,
                    "end_time": 95.7,
                    "transcript_ref": "T3"
                } if include_provenance else None
            }
        ]
        
        return SummaryResult(
            content=content,
            summary_type="clinician",
            provenance_count=len([c for c in content if c.get("provenance_id")]),
            metadata={"mock": True, "model": "mock-clinician-v1"}
        )
    
    async def generate_patient_summary(self, 
                                     transcript_data: List[Dict],
                                     include_provenance: bool = True,
                                     patient_info: Dict | None = None) -> SummaryResult:
        """Generate mock patient summary"""
        
        await asyncio.sleep(0.2)  # Simulate LLM processing
        
        # Mock patient summary content
        content = [
            {
                "bullet": "You've been experiencing severe headaches for about 3 weeks now",
                "provenance_id": "S1" if include_provenance else None,
                "source_span": {
                    "start_time": 30.0,
                    "end_time": 36.5,
                    "transcript_ref": "T1"
                } if include_provenance else None
            },
            {
                "bullet": "The pain you described as 7-8 out of 10 is quite intense",
                "provenance_id": "S2" if include_provenance else None,
                "source_span": {
                    "start_time": 37.0,
                    "end_time": 42.3,
                    "transcript_ref": "T2"
                } if include_provenance else None
            },
            {
                "bullet": "The light sensitivity and nausea you mentioned are common with migraines",
                "provenance_id": "S3" if include_provenance else None,
                "source_span": {
                    "start_time": 90.0,
                    "end_time": 95.7,
                    "transcript_ref": "T3"
                } if include_provenance else None
            }
        ]
        
        return SummaryResult(
            content=content,
            summary_type="patient",
            provenance_count=len([c for c in content if c.get("provenance_id")]),
            metadata={"mock": True, "model": "mock-patient-v1"}
        )
    
    async def generate_clinician_dossier(self, text: str, metadata: Dict) -> Dict:
        """Generate mock clinician dossier"""
        await asyncio.sleep(0.1)
        
        return {
            "chief_complaint": "Severe headaches, 3-week duration",
            "key_symptoms": ["headache", "photophobia", "nausea"],
            "severity": "7-8/10",
            "duration": "3 weeks",
            "priority": "moderate",
            "mock": True
        }
    
    async def process_patient_query(self, query: str, context: Dict, patient_info: Dict) -> Dict:
        """Mock patient query processing"""
        await asyncio.sleep(0.15)
        
        return {
            "response": f"Based on your consultation, regarding '{query}', the main points discussed were related to your headache symptoms and treatment options.",
            "provenance_refs": ["S1", "S2"],
            "confidence": 0.85,
            "mock": True
        }