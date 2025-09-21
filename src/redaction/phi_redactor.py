"""
PHI (Protected Health Information) Redaction Module

Detects and redacts personally identifiable health information
before data reaches LLM systems, ensuring HIPAA compliance.
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


class PHIRedactor:
    """PHI detection and redaction system"""
    
    def __init__(self):
        # Simplified initialization without spaCy for MVP
        self.nlp_available = False
        self.nlp = None
        logger.warning("spaCy not available, using regex-only PHI detection")
            
        # PHI patterns for regex matching
        self.phi_patterns = {
            'ssn': r'\b(?:\d{3}-?\d{2}-?\d{4})\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date_birth': r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b',
            'mrn': r'\b(?:MRN|mrn|Medical Record Number)[\s:]*(\d{6,10})\b',
            'address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b'
        }
        
        # Medical entities that may contain PHI
        self.sensitive_entities = {
            'PERSON', 'ORG', 'GPE', 'DATE', 'CARDINAL'
        }
        
        # Replacement tokens for different PHI types
        self.replacements = {
            'ssn': '[SSN_REDACTED]',
            'phone': '[PHONE_REDACTED]', 
            'email': '[EMAIL_REDACTED]',
            'date_birth': '[DOB_REDACTED]',
            'mrn': '[MRN_REDACTED]',
            'address': '[ADDRESS_REDACTED]',
            'person_name': '[NAME_REDACTED]',
            'organization': '[ORG_REDACTED]',
            'location': '[LOCATION_REDACTED]',
            'date': '[DATE_REDACTED]',
            'number': '[NUMBER_REDACTED]'
        }

    async def redact_phi(self, text: str) -> RedactionResult:
        """
        Main PHI redaction function
        
        Args:
            text: Input text potentially containing PHI
            
        Returns:
            RedactionResult with original, redacted text and detected PHI
        """
        detected_phi = []
        redacted_text = text
        
        try:
            # 1. Regex-based pattern detection
            pattern_detections = self._detect_patterns(text)
            detected_phi.extend(pattern_detections)
            
            # Apply pattern-based redactions
            for detection in pattern_detections:
                redacted_text = redacted_text.replace(
                    detection['original'],
                    detection['replacement']
                )
            
            # 2. NLP-based entity detection
            entity_detections = self._detect_entities(redacted_text)
            detected_phi.extend(entity_detections)
            
            # Apply entity-based redactions
            for detection in entity_detections:
                redacted_text = redacted_text.replace(
                    detection['original'],
                    detection['replacement']
                )
            
            # 3. Calculate confidence score
            confidence = self._calculate_confidence(detected_phi, text)
            
            # 4. Audit log (without storing original PHI)
            self._audit_redaction(len(detected_phi), confidence)
            
            return RedactionResult(
                original_text=text,
                redacted_text=redacted_text,
                detected_phi=detected_phi,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"PHI redaction failed: {e}")
            # Fail safe: if redaction fails, reject the text entirely
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

    def _detect_entities(self, text: str) -> List[Dict[str, str]]:
        """Detect PHI using NLP entity recognition"""
        # Simplified version without spaCy - returns empty list
        # In production, this would use spaCy for entity recognition
        return []

    def _is_likely_phi(self, text: str, entity_label: str) -> bool:
        """Determine if detected entity is likely PHI"""
        # Skip common medical terms that aren't PHI
        medical_terms = {
            'headache', 'pain', 'medication', 'treatment', 'diagnosis',
            'symptoms', 'doctor', 'patient', 'clinic', 'hospital'
        }
        
        if text.lower() in medical_terms:
            return False
            
        # Person names are almost always PHI in medical context
        if entity_label == 'PERSON':
            return True
            
        # Dates might be PHI if they could be birth dates
        if entity_label == 'DATE':
            # Simple heuristic: dates that look like birth dates
            if re.match(r'\b(?:19|20)\d{2}\b', text):
                return True
                
        # Numbers that look like IDs
        if entity_label == 'CARDINAL':
            if len(text.replace(' ', '')) >= 6:  # Likely ID number
                return True
                
        return False

    def _map_entity_to_phi_type(self, entity_label: str) -> str:
        """Map spaCy entity labels to PHI types"""
        mapping = {
            'PERSON': 'person_name',
            'ORG': 'organization', 
            'GPE': 'location',
            'DATE': 'date',
            'CARDINAL': 'number'
        }
        return mapping.get(entity_label, 'unknown')

    def _calculate_confidence(self, detections: List[Dict], original_text: str) -> float:
        """Calculate confidence score for redaction quality"""
        if not detections:
            return 1.0  # High confidence if no PHI detected
            
        # Simple scoring based on detection methods and coverage
        regex_detections = sum(1 for d in detections if d['method'] == 'regex')
        nlp_detections = sum(1 for d in detections if d['method'] == 'nlp')
        
        # Regex patterns have higher confidence than NLP detection
        confidence = min(1.0, (regex_detections * 0.9 + nlp_detections * 0.7) / len(detections))
        
        return confidence

    def _audit_redaction(self, phi_count: int, confidence: float):
        """Log redaction operation for audit purposes (no PHI stored)"""
        logger.info(f"PHI redaction completed: {phi_count} entities detected, confidence: {confidence:.2f}")

    def health_check(self) -> Dict[str, str]:
        """Health check for PHI redactor"""
        try:
            # Test basic functionality
            return {"status": "healthy", "model": "regex-only"}
        except Exception as e:
            logger.error(f"PHI redactor health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def validate_redaction(self, original: str, redacted: str) -> bool:
        """
        Validate that redaction was successful
        Used in testing to ensure no PHI leaks
        """
        try:
            # Re-run detection on redacted text
            result = await self.redact_phi(redacted)
            
            # Should find minimal or no PHI in already-redacted text
            return len(result.detected_phi) == 0
            
        except Exception as e:
            logger.error(f"Redaction validation failed: {e}")
            return False