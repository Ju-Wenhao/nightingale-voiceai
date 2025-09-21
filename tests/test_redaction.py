"""
Test module for PHI (Protected Health Information) redaction

Tests synthetic PHI detection and redaction to ensure no PHI leaks
into LLM systems or logs, maintaining HIPAA compliance.
"""

import pytest
import asyncio
from typing import List, Dict, Tuple

from src.redaction.phi_redactor import PHIRedactor, RedactionResult


class TestPHIRedaction:
    """Test PHI detection and redaction functionality"""

    @pytest.fixture
    def phi_redactor(self):
        """Initialize PHI redactor"""
        return PHIRedactor()

    @pytest.fixture 
    def synthetic_phi_samples(self):
        """Generate synthetic PHI test cases"""
        return [
            {
                "text": "Patient John Smith was born on 01/15/1985 and lives at 123 Main Street.",
                "expected_phi": ["John Smith", "01/15/1985", "123 Main Street"],
                "phi_types": ["person_name", "date_birth", "address"]
            },
            {
                "text": "MRN: 1234567890, Phone: (555) 123-4567, Email: john.smith@email.com",
                "expected_phi": ["1234567890", "(555) 123-4567", "john.smith@email.com"],
                "phi_types": ["mrn", "phone", "email"]
            },
            {
                "text": "Patient SSN is 123-45-6789 and insurance ID is ABC123456789",
                "expected_phi": ["123-45-6789", "ABC123456789"],
                "phi_types": ["ssn", "number"]
            },
            {
                "text": "Patient reports headache severity 7/10 with onset three days ago",
                "expected_phi": [],  # No PHI in this medical description
                "phi_types": []
            },
            {
                "text": "Dr. Johnson prescribed medication for Mary Williams at Boston General Hospital",
                "expected_phi": ["Dr. Johnson", "Mary Williams", "Boston General Hospital"],
                "phi_types": ["person_name", "person_name", "organization"]
            }
        ]

    @pytest.mark.asyncio
    async def test_basic_phi_detection(self, phi_redactor, synthetic_phi_samples):
        """Test basic PHI pattern detection"""
        
        for sample in synthetic_phi_samples:
            result = await phi_redactor.redact_phi(sample["text"])
            
            # Check that all expected PHI was detected
            detected_phi_texts = [phi["original"] for phi in result.detected_phi]
            
            for expected_phi in sample["expected_phi"]:
                assert any(expected_phi in detected for detected in detected_phi_texts), \
                    f"Failed to detect PHI: {expected_phi} in text: {sample['text']}"

    @pytest.mark.asyncio
    async def test_complete_phi_redaction(self, phi_redactor, synthetic_phi_samples):
        """Test that detected PHI is completely removed from output"""
        
        for sample in synthetic_phi_samples:
            result = await phi_redactor.redact_phi(sample["text"])
            
            # Verify no original PHI remains in redacted text
            for expected_phi in sample["expected_phi"]:
                assert expected_phi not in result.redacted_text, \
                    f"PHI not redacted: {expected_phi} still in: {result.redacted_text}"

    @pytest.mark.asyncio
    async def test_redacted_text_readability(self, phi_redactor):
        """Test that redacted text maintains readability"""
        
        test_text = "Patient John Doe, DOB 03/15/1975, reported severe pain level 8/10."
        result = await phi_redactor.redact_phi(test_text)
        
        # Check that medical content is preserved while PHI is redacted
        assert "severe pain level 8/10" in result.redacted_text, \
            "Medical information should be preserved"
        assert "[NAME_REDACTED]" in result.redacted_text or "[PHI_REDACTED]" in result.redacted_text, \
            "PHI should be replaced with redaction tokens"

    @pytest.mark.asyncio
    async def test_no_phi_false_positives(self, phi_redactor):
        """Test that medical terms are not incorrectly flagged as PHI"""
        
        medical_text = """
        Patient reports chronic headache with severity 7/10. 
        Symptoms include throbbing pain, light sensitivity, and nausea.
        Medical history includes hypertension and diabetes.
        Prescribed ibuprofen 600mg three times daily.
        Follow up appointment scheduled in two weeks.
        """
        
        result = await phi_redactor.redact_phi(medical_text)
        
        # Medical terms should not be redacted
        medical_terms = ["headache", "pain", "hypertension", "diabetes", "ibuprofen"]
        for term in medical_terms:
            assert term in result.redacted_text, f"Medical term incorrectly redacted: {term}"

    @pytest.mark.asyncio
    async def test_confidence_scoring(self, phi_redactor, synthetic_phi_samples):
        """Test PHI detection confidence scoring"""
        
        for sample in synthetic_phi_samples:
            result = await phi_redactor.redact_phi(sample["text"])
            
            # Confidence should be between 0 and 1
            assert 0.0 <= result.confidence_score <= 1.0, \
                f"Invalid confidence score: {result.confidence_score}"
            
            # Higher PHI density should correlate with confidence
            if len(sample["expected_phi"]) > 0:
                assert result.confidence_score > 0.0, \
                    "Should have some confidence when PHI is detected"

    @pytest.mark.asyncio
    async def test_regex_pattern_coverage(self, phi_redactor):
        """Test specific regex patterns for PHI detection"""
        
        pattern_tests = [
            ("SSN: 123-45-6789", "123-45-6789", "ssn"),
            ("Call me at (555) 123-4567", "(555) 123-4567", "phone"),
            ("Email: patient@example.com", "patient@example.com", "email"),
            ("DOB: 01/15/1985", "01/15/1985", "date_birth"),
            ("MRN 9876543210", "9876543210", "mrn"),
            ("Lives at 456 Oak Street", "456 Oak Street", "address")
        ]
        
        for text, expected_phi, phi_type in pattern_tests:
            result = await phi_redactor.redact_phi(text)
            
            # Check detection
            detected_texts = [phi["original"] for phi in result.detected_phi]
            assert any(expected_phi in detected for detected in detected_texts), \
                f"Failed to detect {phi_type}: {expected_phi}"
            
            # Check redaction
            assert expected_phi not in result.redacted_text, \
                f"{phi_type} not properly redacted"

    @pytest.mark.asyncio
    async def test_nlp_entity_detection(self, phi_redactor):
        """Test NLP-based entity detection for PHI"""
        
        entity_tests = [
            ("Patient Sarah Johnson visited the clinic", ["Sarah Johnson"], ["PERSON"]),
            ("Treatment at Massachusetts General Hospital", ["Massachusetts General Hospital"], ["ORG"]),
            ("Appointment scheduled for December 15, 2023", ["December 15, 2023"], ["DATE"]),
            ("Patient ID number 1234567", ["1234567"], ["CARDINAL"])
        ]
        
        for text, expected_entities, entity_types in entity_tests:
            result = await phi_redactor.redact_phi(text)
            
            # At least some entities should be detected as PHI
            if expected_entities:
                assert len(result.detected_phi) > 0, \
                    f"No PHI detected in text with entities: {text}"

    @pytest.mark.asyncio
    async def test_redaction_validation(self, phi_redactor):
        """Test redaction validation functionality"""
        
        original_text = "Patient John Doe, SSN 123-45-6789, reports pain."
        result = await phi_redactor.redact_phi(original_text)
        
        # Validate redaction was successful
        is_valid = await phi_redactor.validate_redaction(original_text, result.redacted_text)
        assert is_valid, "Redaction validation should pass for properly redacted text"

    @pytest.mark.asyncio
    async def test_multiple_phi_types_in_single_text(self, phi_redactor):
        """Test handling multiple types of PHI in one text block"""
        
        complex_text = """
        Patient: John Smith
        DOB: 03/15/1975  
        SSN: 123-45-6789
        Phone: (555) 123-4567
        Address: 789 Pine Street, Boston, MA
        Email: j.smith@email.com
        MRN: 9876543210
        
        Chief complaint: Severe headache lasting 3 days, pain level 8/10.
        No fever or nausea reported.
        """
        
        result = await phi_redactor.redact_phi(complex_text)
        
        # Check that multiple PHI types were detected
        phi_types_detected = set(phi["type"] for phi in result.detected_phi)
        expected_types = {"person_name", "date_birth", "ssn", "phone", "address", "email", "mrn"}
        
        # Should detect most of the PHI types
        overlap = phi_types_detected & expected_types
        assert len(overlap) >= 4, f"Expected multiple PHI types, got: {phi_types_detected}"
        
        # Medical content should be preserved
        assert "headache" in result.redacted_text
        assert "pain level 8/10" in result.redacted_text
        assert "fever" in result.redacted_text or "nausea" in result.redacted_text

    @pytest.mark.asyncio
    async def test_edge_cases(self, phi_redactor):
        """Test edge cases for PHI redaction"""
        
        edge_cases = [
            ("", 0),  # Empty string
            ("No PHI here, just medical info about headaches", 0),  # No PHI
            ("123", 0),  # Too short to be PHI
            ("Patient Patient Patient", 1),  # Repeated words
            ("Call Dr. Smith at 555-PAIN for pain management", 2),  # Mixed PHI and medical terms
        ]
        
        for text, expected_min_phi in edge_cases:
            result = await phi_redactor.redact_phi(text)
            
            # Should handle gracefully without errors
            assert isinstance(result, RedactionResult)
            assert len(result.detected_phi) >= expected_min_phi


# Stress test
@pytest.mark.asyncio
async def test_phi_redaction_performance():
    """Test PHI redaction performance on larger text blocks"""
    
    # Generate a large text block with mixed content
    large_text = """
    Patient Name: John Michael Smith
    Date of Birth: January 15, 1985
    Social Security Number: 123-45-6789
    Phone Number: (555) 123-4567
    Email Address: john.smith@healthclinic.com
    Home Address: 1234 Main Street, Apartment 5B, Boston, Massachusetts 02101
    Medical Record Number: MRN-9876543210
    
    CONSULTATION NOTES:
    Patient presents with chronic migraine headaches occurring 3-4 times per week.
    Pain severity ranges from 6-9 out of 10 on pain scale.
    Episodes typically last 4-6 hours and are accompanied by nausea and light sensitivity.
    Patient reports triggers include stress, lack of sleep, and certain foods.
    
    MEDICAL HISTORY:
    - Hypertension diagnosed in 2018
    - Type 2 Diabetes mellitus since 2019  
    - Family history of cardiovascular disease
    - No known drug allergies
    
    CURRENT MEDICATIONS:
    - Metformin 500mg twice daily for diabetes
    - Lisinopril 10mg once daily for hypertension
    - Sumatriptan 50mg as needed for migraines
    
    ASSESSMENT AND PLAN:
    1. Continue current migraine management with sumatriptan
    2. Consider preventive medication if frequency increases
    3. Lifestyle modifications: regular sleep schedule, stress management
    4. Follow-up appointment in 4 weeks
    5. Patient education on migraine triggers provided
    
    Next appointment: February 15, 2024 at 10:00 AM with Dr. Sarah Johnson
    """ * 5  # Repeat to make it larger
    
    phi_redactor = PHIRedactor()
    
    import time
    start_time = time.time()
    result = await phi_redactor.redact_phi(large_text)
    processing_time = time.time() - start_time
    
    # Performance assertions
    assert processing_time < 5.0, f"PHI redaction took too long: {processing_time:.2f} seconds"
    assert len(result.detected_phi) > 0, "Should detect PHI in large text block"
    assert result.confidence_score > 0.0, "Should have confidence in detection"
    
    print(f"✅ PHI redaction performance test: {processing_time:.3f}s, {len(result.detected_phi)} PHI detected")


if __name__ == "__main__":
    # Run performance test
    asyncio.run(test_phi_redaction_performance())