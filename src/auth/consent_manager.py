"""
Authentication and Consent Management Module

Handles patient authentication, consent verification, and JWT token management
with strict consent enforcement as required by healthcare regulations.
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ConsentFlags:
    """Patient consent permissions"""
    audio_recording: bool = False
    transcription: bool = False
    ai_processing: bool = False
    data_storage: bool = False
    summary_generation: bool = False


@dataclass
class PatientInfo:
    """Patient information stored in JWT"""
    patient_id: str
    session_id: str
    consent: ConsentFlags
    authenticated_at: datetime
    expires_at: datetime


class ConsentManager:
    """Manages patient authentication and consent verification"""
    
    def __init__(self):
        # In production, load from secure environment variables
        self.secret_key = "nightingale_jwt_secret_key_change_in_production"
        self.algorithm = "HS256"
        self.token_expiry_minutes = 60  # Increased to 60 minutes
        
    async def authenticate_patient(self, patient_id: str, consent_flags: Dict[str, bool]) -> str:
        """
        Authenticate patient and generate JWT with consent flags
        
        Args:
            patient_id: Unique patient identifier (will be hashed)
            consent_flags: Dictionary of consent permissions
            
        Returns:
            JWT token containing patient info and consent
        """
        try:
            # Hash patient ID for privacy
            hashed_patient_id = self._hash_patient_id(patient_id)
            
            # Parse consent flags
            consent = ConsentFlags(**consent_flags)
            
            # Validate minimum required consent
            if not self._validate_minimum_consent(consent):
                raise ValueError("Insufficient consent for system operation")
            
            # Create patient info
            now = datetime.utcnow()
            patient_info = PatientInfo(
                patient_id=hashed_patient_id,
                session_id=self._generate_session_id(),
                consent=consent,
                authenticated_at=now,
                expires_at=now + timedelta(minutes=self.token_expiry_minutes)
            )
            
            # Generate JWT token with proper UTC timestamps
            import time
            current_timestamp = int(time.time())
            expiry_timestamp = current_timestamp + (self.token_expiry_minutes * 60)
            
            token_payload = {
                "patient_id": patient_info.patient_id,
                "session_id": patient_info.session_id,
                "consent": asdict(patient_info.consent),
                "iat": current_timestamp,
                "exp": expiry_timestamp
            }
            
            # Log token creation for debugging
            logger.info(f"Token creation - Now (timestamp): {current_timestamp}, Expires (timestamp): {expiry_timestamp}, Duration: {self.token_expiry_minutes}min")
            
            token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            # Audit log (no PHI stored)
            logger.info(f"Patient authenticated: {patient_info.patient_id[:8]}...")
            
            return token
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def verify_token(self, token: str) -> PatientInfo:
        """
        Verify JWT token and extract patient information
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            PatientInfo object with consent flags
        """
        try:
            # Use proper timestamp comparison to avoid timezone issues
            import time
            current_timestamp = time.time()
            
            # Decode and verify token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                leeway=30  # Allow 30 seconds clock skew
            )
            
            # Log token timing for debugging
            exp_timestamp = payload.get('exp')
            logger.info(f"Token verification - Current (timestamp): {current_timestamp}, Expires (timestamp): {exp_timestamp}")
            
            # Additional manual check: compare timestamps directly
            if exp_timestamp and current_timestamp > exp_timestamp:
                time_diff = current_timestamp - exp_timestamp
                logger.warning(f"Token expired: current={current_timestamp}, exp={exp_timestamp}, diff={time_diff}s")
                raise jwt.ExpiredSignatureError("Token has expired")
            
            # Extract patient information
            consent = ConsentFlags(**payload['consent'])
            patient_info = PatientInfo(
                patient_id=payload['patient_id'],
                session_id=payload['session_id'],
                consent=consent,
                authenticated_at=datetime.utcfromtimestamp(payload['iat']),
                expires_at=datetime.utcfromtimestamp(payload['exp'])
            )
                
            return patient_info
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token presented")
            raise ValueError("Authentication token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise ValueError("Invalid authentication token")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise

    def has_required_consent(self, patient_info: PatientInfo) -> bool:
        """
        Check if patient has provided required consent for system operation
        
        Args:
            patient_info: Patient information with consent flags
            
        Returns:
            True if patient has sufficient consent
        """
        consent = patient_info.consent
        
        # Define minimum required consent for basic operation
        required_flags = [
            consent.audio_recording,    # Must consent to recording
            consent.transcription,      # Must consent to transcription
            consent.ai_processing,      # Must consent to AI processing
        ]
        
        return all(required_flags)

    def check_operation_consent(self, patient_info: PatientInfo, operation: str) -> bool:
        """
        Check consent for specific operations
        
        Args:
            patient_info: Patient information
            operation: Operation type to check
            
        Returns:
            True if operation is allowed by consent
        """
        consent = patient_info.consent
        
        operation_requirements = {
            'record_audio': consent.audio_recording,
            'transcribe': consent.transcription,
            'ai_process': consent.ai_processing,
            'store_data': consent.data_storage,
            'generate_summary': consent.summary_generation,
        }
        
        return operation_requirements.get(operation, False)

    def _hash_patient_id(self, patient_id: str) -> str:
        """Hash patient ID for privacy protection"""
        import hashlib
        return hashlib.sha256(patient_id.encode()).hexdigest()[:16]

    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        import uuid
        return str(uuid.uuid4())

    def _validate_minimum_consent(self, consent: ConsentFlags) -> bool:
        """Validate that minimum required consent is provided"""
        # For basic system operation, require these consents
        return (
            consent.audio_recording and
            consent.transcription and
            consent.ai_processing
        )

    async def refresh_token(self, current_token: str) -> str:
        """
        Refresh an existing token with new expiry
        
        Args:
            current_token: Current valid JWT token
            
        Returns:
            New JWT token with extended expiry
        """
        try:
            # Verify current token
            patient_info = await self.verify_token(current_token)
            
            # Check if token is still valid for refresh (within 5 minutes of expiry)
            time_to_expiry = patient_info.expires_at - datetime.utcnow()
            if time_to_expiry.total_seconds() > 300:  # More than 5 minutes left
                raise ValueError("Token does not need refresh yet")
            
            # Generate new token with same consent but new expiry
            now = datetime.utcnow()
            token_payload = {
                "patient_id": patient_info.patient_id,
                "session_id": patient_info.session_id,
                "consent": asdict(patient_info.consent),
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=self.token_expiry_minutes)).timestamp())
            }
            
            new_token = jwt.encode(token_payload, self.secret_key, algorithm=self.algorithm)
            
            logger.info(f"Token refreshed for patient: {patient_info.patient_id[:8]}...")
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise

    async def revoke_consent(self, token: str, consent_type: str) -> bool:
        """
        Revoke specific consent - this would typically invalidate the session
        
        Args:
            token: Current JWT token
            consent_type: Type of consent to revoke
            
        Returns:
            True if consent revoked successfully
        """
        try:
            patient_info = await self.verify_token(token)
            
            # In production, this would update database and invalidate session
            logger.info(f"Consent revoked: {consent_type} for patient {patient_info.patient_id[:8]}...")
            
            # For this MVP, consent revocation ends the session
            return True
            
        except Exception as e:
            logger.error(f"Consent revocation failed: {e}")
            return False

    def get_audit_info(self, token: str) -> Dict[str, str]:
        """
        Get audit information from token (for logging purposes)
        
        Args:
            token: JWT token
            
        Returns:
            Audit information dictionary
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return {
                "patient_id": payload['patient_id'][:8] + "...",  # Truncated for privacy
                "session_id": payload['session_id'],
                "issued_at": datetime.fromtimestamp(payload['iat']).isoformat(),
                "expires_at": datetime.fromtimestamp(payload['exp']).isoformat(),
                "consent_flags": str(len([k for k, v in payload['consent'].items() if v]))
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit info: {e}")
            return {"error": "Invalid token"}