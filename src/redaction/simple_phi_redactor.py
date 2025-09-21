"""
Simplified PHI Redactor - No External Dependencies
Basic regex-based PHI detection for MVP demonstration
"""

import re
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RedactionResult:
    """Result of PHI redaction operation"""
    original_text: str
    redacted_text: str
    detected_phi: List[Dict[str, str]]
    confidence_score: float


class SimplePHIRedactor:
    """Simplified PHI detection using only regex patterns"""
    
    def __init__(self):
        # PHI patterns for regex matching
        self.phi_patterns = {
            'ssn': r'\b(?:\d{3}-?\d{2}-?\d{4})\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date_birth': r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
            'mrn': r'\b(?:MRN|mrn|Medical Record Number)[\s:]*(\d{6,10})\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b'
        }
        
        # Simple name patterns
        self.name_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\bDr\.\s+[A-Z][a-z]+\b',         # Dr. Name
            r'\bPatient\s+[A-Z][a-z]+\b'       # Patient Name
        ]
        
        # Replacement tokens
        self.replacements = {
            'ssn': '[SSN_REDACTED]',
            'phone': '[PHONE_REDACTED]', 
            'email': '[EMAIL_REDACTED]',
            'date_birth': '[DOB_REDACTED]',
            'mrn': '[MRN_REDACTED]',
            'address': '[ADDRESS_REDACTED]',
            'name': '[NAME_REDACTED]'
        }

    async def redact_phi(self, text: str) -> RedactionResult:
        """Main PHI redaction function using regex only"""
        detected_phi = []
        redacted_text = text
        
        try:
            # 1. Pattern-based detection
            pattern_detections = self._detect_patterns(text)
            detected_phi.extend(pattern_detections)
            
            # Apply pattern-based redactions
            for detection in pattern_detections:
                redacted_text = redacted_text.replace(
                    detection['original'],
                    detection['replacement']
                )
            
            # 2. Simple name detection
            name_detections = self._detect_names(redacted_text)
            detected_phi.extend(name_detections)
            
            # Apply name redactions
            for detection in name_detections:
                redacted_text = redacted_text.replace(
                    detection['original'],
                    detection['replacement']
                )
            
            # 3. Calculate simple confidence score
            confidence = 1.0 if detected_phi else 1.0  # Always confident in regex
            
            # 4. Audit log
            logger.info(f"PHI redaction: {len(detected_phi)} entities detected")
            
            return RedactionResult(
                original_text=text,
                redacted_text=redacted_text,
                detected_phi=detected_phi,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"PHI redaction failed: {e}")
            return RedactionResult(
                original_text=text,
                redacted_text="[TEXT_REDACTION_FAILED]",
                detected_phi=[],
                confidence_score=0.0
            )

    def _detect_patterns(self, text: str) -> List[Dict[str, str]]:
        """Detect PHI using regex patterns"""
        detections = []
        
        for phi_type, pattern in self.phi_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'type': phi_type,
                    'original': match.group(),
                    'replacement': self.replacements.get(phi_type, '[PHI_REDACTED]'),
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'method': 'regex'
                })
        
        return detections

    def _detect_names(self, text: str) -> List[Dict[str, str]]:
        """Detect names using simple patterns"""
        detections = []
        
        for pattern in self.name_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name_text = match.group()
                # Skip common medical terms
                if not self._is_medical_term(name_text):
                    detections.append({
                        'type': 'name',
                        'original': name_text,
                        'replacement': self.replacements['name'],
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'method': 'name_pattern'
                    })
        
        return detections

    def _is_medical_term(self, text: str) -> bool:
        """Check if text is a common medical term"""
        medical_terms = {
            'patient reports', 'doctor smith', 'nurse jones', 'headache pain',
            'blood pressure', 'heart rate', 'pain level', 'medical history'
        }
        return text.lower() in medical_terms

    def health_check(self) -> Dict[str, str]:
        """Health check"""
        return {"status": "healthy", "model": "regex-only"}

    async def validate_redaction(self, original: str, redacted: str) -> bool:
        """Validate redaction success"""
        try:
            result = await self.redact_phi(redacted)
            return len(result.detected_phi) == 0
        except:
            return False


# Alias for compatibility
PHIRedactor = SimplePHIRedactor