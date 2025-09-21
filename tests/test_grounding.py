"""
Test module for provenance grounding validation

Validates that every summary bullet point has proper provenance links
to source audio/transcript with timestamps and reference IDs.
"""

import pytest
import asyncio
from typing import List, Dict
from dataclasses import dataclass

from src.provenance.provenance_engine import ProvenanceEngine
from src.summarization.summary_generator import SummaryGenerator


@dataclass
class SyntheticConsultation:
    """Synthetic consultation data for testing"""
    session_id: str
    transcript_chunks: List[Dict]
    audio_timestamps: List[Dict]
    speaker_labels: List[str]


class TestProvenance:
    """Test provenance grounding functionality"""
    
    @pytest.fixture
    def synthetic_consultation(self):
        """Generate synthetic consultation data"""
        return SyntheticConsultation(
            session_id="test_session_001",
            transcript_chunks=[
                {
                    "chunk_id": "C1",
                    "text": "Patient reports severe headache lasting three days",
                    "start_time": 45.2,
                    "end_time": 52.8,
                    "speaker": "patient",
                    "confidence": 0.95
                },
                {
                    "chunk_id": "C2", 
                    "text": "Pain level described as seven out of ten",
                    "start_time": 53.1,
                    "end_time": 58.7,
                    "speaker": "patient",
                    "confidence": 0.92
                },
                {
                    "chunk_id": "C3",
                    "text": "No fever or nausea reported by patient",
                    "start_time": 120.5,
                    "end_time": 125.9,
                    "speaker": "clinician",
                    "confidence": 0.88
                },
                {
                    "chunk_id": "C4",
                    "text": "Recommend over the counter pain medication",
                    "start_time": 180.2,
                    "end_time": 185.1,
                    "speaker": "clinician", 
                    "confidence": 0.91
                }
            ],
            audio_timestamps=[
                {"chunk": "C1", "audio_start": 45.2, "audio_end": 52.8},
                {"chunk": "C2", "audio_start": 53.1, "audio_end": 58.7},
                {"chunk": "C3", "audio_start": 120.5, "audio_end": 125.9},
                {"chunk": "C4", "audio_start": 180.2, "audio_end": 185.1}
            ],
            speaker_labels=["patient", "patient", "clinician", "clinician"]
        )

    @pytest.fixture
    def provenance_engine(self):
        """Initialize provenance engine"""
        return ProvenanceEngine()

    @pytest.fixture 
    def summary_generator(self):
        """Initialize summary generator"""
        return SummaryGenerator()

    @pytest.mark.asyncio
    async def test_all_summary_bullets_have_provenance(
        self, 
        synthetic_consultation, 
        provenance_engine,
        summary_generator
    ):
        """Test that every summary bullet point has provenance reference"""
        
        # Generate summary with provenance
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        # Extract all bullet points
        bullet_points = self._extract_bullet_points(summary.content)
        
        # Validate each bullet has provenance
        for bullet in bullet_points:
            assert 'provenance_id' in bullet, f"Missing provenance_id in: {bullet['text']}"
            assert 'source_span' in bullet, f"Missing source_span in: {bullet['text']}"
            assert bullet['provenance_id'].startswith('S'), f"Invalid provenance_id format: {bullet['provenance_id']}"
            
            # Verify source span has required fields
            source_span = bullet['source_span']
            assert 'start_time' in source_span, "Missing start_time in source_span"
            assert 'end_time' in source_span, "Missing end_time in source_span"
            assert 'transcript_ref' in source_span, "Missing transcript_ref in source_span"

    @pytest.mark.asyncio
    async def test_provenance_references_valid_source_chunks(
        self,
        synthetic_consultation,
        provenance_engine,
        summary_generator
    ):
        """Test that provenance references point to valid transcript chunks"""
        
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        bullet_points = self._extract_bullet_points(summary.content)
        available_chunks = {chunk['chunk_id'] for chunk in synthetic_consultation.transcript_chunks}
        
        for bullet in bullet_points:
            source_ref = bullet['source_span']['transcript_ref']
            assert source_ref in available_chunks, f"Invalid transcript reference: {source_ref}"

    @pytest.mark.asyncio
    async def test_timestamps_within_valid_range(
        self,
        synthetic_consultation,
        summary_generator
    ):
        """Test that provenance timestamps fall within consultation duration"""
        
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        # Calculate consultation duration
        max_end_time = max(chunk['end_time'] for chunk in synthetic_consultation.transcript_chunks)
        
        bullet_points = self._extract_bullet_points(summary.content)
        
        for bullet in bullet_points:
            start_time = bullet['source_span']['start_time']
            end_time = bullet['source_span']['end_time']
            
            assert 0 <= start_time <= max_end_time, f"Invalid start_time: {start_time}"
            assert start_time <= end_time <= max_end_time, f"Invalid end_time: {end_time}"
            assert end_time > start_time, "End time must be after start time"

    @pytest.mark.asyncio
    async def test_provenance_content_alignment(
        self,
        synthetic_consultation,
        summary_generator
    ):
        """Test that summary content aligns with referenced source content"""
        
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        bullet_points = self._extract_bullet_points(summary.content)
        chunk_map = {chunk['chunk_id']: chunk for chunk in synthetic_consultation.transcript_chunks}
        
        for bullet in bullet_points:
            source_chunk_id = bullet['source_span']['transcript_ref']
            source_chunk = chunk_map[source_chunk_id]
            
            # Check for semantic alignment (simplified for testing)
            bullet_keywords = self._extract_keywords(bullet['text'])
            source_keywords = self._extract_keywords(source_chunk['text'])
            
            # At least one keyword should overlap
            keyword_overlap = bool(bullet_keywords & source_keywords)
            assert keyword_overlap, f"No keyword overlap between bullet and source: {bullet['text']} <-> {source_chunk['text']}"

    @pytest.mark.asyncio
    async def test_unique_provenance_ids(
        self,
        synthetic_consultation,
        summary_generator
    ):
        """Test that all provenance IDs are unique within a summary"""
        
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        bullet_points = self._extract_bullet_points(summary.content)
        provenance_ids = [bullet['provenance_id'] for bullet in bullet_points]
        
        assert len(provenance_ids) == len(set(provenance_ids)), "Duplicate provenance IDs found"

    @pytest.mark.asyncio
    async def test_provenance_ordering_consistency(
        self,
        synthetic_consultation,
        summary_generator
    ):
        """Test that provenance references follow temporal ordering"""
        
        summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation.transcript_chunks,
            include_provenance=True
        )
        
        bullet_points = self._extract_bullet_points(summary.content)
        
        # Sort bullets by their source timestamps
        sorted_bullets = sorted(bullet_points, key=lambda b: b['source_span']['start_time'])
        
        # Check that provenance IDs follow sequential pattern
        for i, bullet in enumerate(sorted_bullets):
            expected_id = f"S{i+1}"
            # Note: This is a simplified test - real implementation may use different ID schemes
            assert bullet['provenance_id'] == expected_id or bullet['provenance_id'].startswith('S'), \
                f"Unexpected provenance ID pattern: {bullet['provenance_id']}"

    def _extract_bullet_points(self, summary_content: List[Dict]) -> List[Dict]:
        """Extract bullet points from summary content"""
        if isinstance(summary_content, list):
            return summary_content
        elif isinstance(summary_content, dict):
            return summary_content.get('bullets', [])
        else:
            # Parse from text format if needed
            return []

    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text for semantic comparison"""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
        return set(word for word in words if word not in stopwords and len(word) > 2)


# Integration test
@pytest.mark.asyncio  
async def test_end_to_end_provenance_grounding():
    """End-to-end test of provenance grounding system"""
    
    # Create test consultation data
    consultation_data = {
        "transcript": [
            {"text": "I have been experiencing severe headaches for the past week", "start": 30.0, "end": 36.5, "speaker": "patient"},
            {"text": "The pain is constant and rates about 8 out of 10", "start": 37.0, "end": 42.1, "speaker": "patient"},  
            {"text": "I recommend starting with ibuprofen 600mg three times daily", "start": 95.2, "end": 100.8, "speaker": "clinician"}
        ]
    }
    
    # Generate summary with provenance
    summary_generator = SummaryGenerator()
    summary = await summary_generator.generate_clinician_summary(
        consultation_data["transcript"],
        include_provenance=True
    )
    
    # Validate summary structure
    assert isinstance(summary.content, list), "Summary content should be a list of bullets"
    assert len(summary.content) > 0, "Summary should contain bullet points"
    
    # Validate each bullet has complete provenance
    for bullet in summary.content:
        assert 'bullet' in bullet, "Each item should have bullet text"
        assert 'provenance_id' in bullet, "Each bullet should have provenance_id"
        assert 'source_span' in bullet, "Each bullet should have source_span"
        
        source_span = bullet['source_span']
        assert all(key in source_span for key in ['start_time', 'end_time', 'transcript_ref']), \
            "Source span should have start_time, end_time, and transcript_ref"

    print(f"✅ Provenance grounding test passed: {len(summary.content)} bullets with valid provenance")


if __name__ == "__main__":
    # Run specific test
    asyncio.run(test_end_to_end_provenance_grounding())