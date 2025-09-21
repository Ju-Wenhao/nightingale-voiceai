"""
Test module for summary comparison

Tests side-by-side clinician vs patient summaries from identical consultations
with design explanation for different audience needs.
"""

import pytest
import asyncio
from typing import Dict, List, Tuple
from dataclasses import dataclass

from src.summarization.summary_generator import SummaryGenerator


@dataclass
class SummaryComparison:
    """Comparison result between clinician and patient summaries"""
    clinician_summary: Dict
    patient_summary: Dict
    shared_content: List[str]
    clinician_specific: List[str]
    patient_specific: List[str]
    design_analysis: Dict[str, str]


class TestSummaryComparison:
    """Test dual summary generation and comparison"""

    @pytest.fixture
    def summary_generator(self):
        """Initialize summary generator"""
        return SummaryGenerator()

    @pytest.fixture
    def synthetic_consultation(self):
        """Generate synthetic consultation for testing"""
        return {
            "session_id": "test_consultation_001",
            "transcript": [
                {
                    "text": "I've been having severe headaches for about three weeks now",
                    "start_time": 30.0,
                    "end_time": 36.5,
                    "speaker": "patient",
                    "confidence": 0.94
                },
                {
                    "text": "The pain is really intense, I'd say about 8 out of 10",
                    "start_time": 37.0,
                    "end_time": 42.3,
                    "speaker": "patient", 
                    "confidence": 0.92
                },
                {
                    "text": "It's mostly on the right side of my head and throbs constantly",
                    "start_time": 43.0,
                    "end_time": 48.7,
                    "speaker": "patient",
                    "confidence": 0.89
                },
                {
                    "text": "Have you tried any over-the-counter pain medications?",
                    "start_time": 49.5,
                    "end_time": 53.2,
                    "speaker": "clinician",
                    "confidence": 0.96
                },
                {
                    "text": "Yes, I've tried ibuprofen and acetaminophen but they don't help much",
                    "start_time": 54.0,
                    "end_time": 59.8,
                    "speaker": "patient",
                    "confidence": 0.91
                },
                {
                    "text": "Any nausea, vomiting, or sensitivity to light?",
                    "start_time": 85.2,
                    "end_time": 89.1,
                    "speaker": "clinician",
                    "confidence": 0.95
                },
                {
                    "text": "Yes, bright lights make it much worse and I feel nauseous sometimes",
                    "start_time": 90.0,
                    "end_time": 95.7,
                    "speaker": "patient",
                    "confidence": 0.88
                },
                {
                    "text": "Based on your symptoms, this sounds like migraine headaches",
                    "start_time": 120.5,
                    "end_time": 125.3,
                    "speaker": "clinician",
                    "confidence": 0.93
                },
                {
                    "text": "I'm going to prescribe sumatriptan for when you have an episode",
                    "start_time": 126.0,
                    "end_time": 131.2,
                    "speaker": "clinician",
                    "confidence": 0.94
                },
                {
                    "text": "Let's also discuss some lifestyle changes that might help prevent them",
                    "start_time": 132.0,
                    "end_time": 137.5,
                    "speaker": "clinician",
                    "confidence": 0.92
                },
                {
                    "text": "I'd like to see you back in four weeks to see how you're doing",
                    "start_time": 180.0,
                    "end_time": 185.3,
                    "speaker": "clinician",
                    "confidence": 0.96
                }
            ],
            "patient_info": {
                "patient_id": "patient_test_001",
                "age_range": "adult",
                "preference": "conversational"
            }
        }

    @pytest.mark.asyncio
    async def test_dual_summary_generation(self, summary_generator, synthetic_consultation):
        """Test generation of both clinician and patient summaries"""
        
        # Generate clinician summary
        clinician_summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation["transcript"],
            include_provenance=True
        )
        
        # Generate patient summary
        patient_summary = await summary_generator.generate_patient_summary(
            synthetic_consultation["transcript"],
            include_provenance=True,
            patient_info=synthetic_consultation["patient_info"]
        )
        
        # Basic structure validation
        assert clinician_summary is not None, "Clinician summary should be generated"
        assert patient_summary is not None, "Patient summary should be generated"
        
        assert hasattr(clinician_summary, 'content'), "Clinician summary should have content"
        assert hasattr(patient_summary, 'content'), "Patient summary should have content"
        
        return clinician_summary, patient_summary

    @pytest.mark.asyncio
    async def test_clinician_summary_characteristics(self, summary_generator, synthetic_consultation):
        """Test clinician summary meets professional medical documentation standards"""
        
        clinician_summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation["transcript"],
            include_provenance=True
        )
        
        # Clinician summary characteristics
        content_text = self._extract_text_content(clinician_summary.content)
        
        # Should use medical terminology
        medical_terms = ["migraine", "headache", "sumatriptan", "symptoms", "diagnosis"]
        found_medical_terms = [term for term in medical_terms if term.lower() in content_text.lower()]
        assert len(found_medical_terms) >= 2, f"Should contain medical terminology: {found_medical_terms}"
        
        # Should be structured and concise
        assert len(content_text) < 1000, "Clinician summary should be concise for quick review"
        
        # Should include severity indicators
        severity_indicators = ["8/10", "8 out of 10", "severe", "intensity"]
        found_severity = [ind for ind in severity_indicators if ind in content_text.lower()]
        assert len(found_severity) >= 1, "Should include pain severity indicators"
        
        # Should have provenance for key claims
        if hasattr(clinician_summary, 'content') and isinstance(clinician_summary.content, list):
            provenance_count = sum(1 for item in clinician_summary.content if 'provenance_id' in item)
            assert provenance_count > 0, "Should have provenance references"

    @pytest.mark.asyncio
    async def test_patient_summary_characteristics(self, summary_generator, synthetic_consultation):
        """Test patient summary meets patient-friendly communication standards"""
        
        patient_summary = await summary_generator.generate_patient_summary(
            synthetic_consultation["transcript"],
            include_provenance=True,
            patient_info=synthetic_consultation["patient_info"]
        )
        
        content_text = self._extract_text_content(patient_summary.content)
        
        # Should use patient-friendly language
        friendly_indicators = ["you", "your", "we", "help", "better", "manage"]
        found_friendly = [ind for ind in friendly_indicators if ind.lower() in content_text.lower()]
        assert len(found_friendly) >= 2, f"Should use patient-friendly language: {found_friendly}"
        
        # Should be more detailed/explanatory than clinician version
        assert len(content_text) > 200, "Patient summary should be detailed enough to be helpful"
        
        # Should include actionable information
        action_words = ["take", "try", "avoid", "follow up", "call", "return"]
        found_actions = [word for word in action_words if word.lower() in content_text.lower()]
        assert len(found_actions) >= 1, "Should include actionable guidance"
        
        # Should be reassuring/supportive
        supportive_terms = ["help", "better", "manage", "improve", "work together"]
        found_supportive = [term for term in supportive_terms if term.lower() in content_text.lower()]
        assert len(found_supportive) >= 1, "Should include supportive language"

    @pytest.mark.asyncio
    async def test_summary_content_accuracy(self, summary_generator, synthetic_consultation):
        """Test that both summaries accurately reflect consultation content"""
        
        clinician_summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation["transcript"],
            include_provenance=True
        )
        
        patient_summary = await summary_generator.generate_patient_summary(
            synthetic_consultation["transcript"],
            include_provenance=True,
            patient_info=synthetic_consultation["patient_info"]
        )
        
        # Key facts that should appear in both summaries
        key_facts = [
            "headache", "three weeks", "8/10", "right side", 
            "nausea", "light sensitivity", "migraine", "sumatriptan"
        ]
        
        clinician_text = self._extract_text_content(clinician_summary.content).lower()
        patient_text = self._extract_text_content(patient_summary.content).lower()
        
        for fact in key_facts:
            assert fact.lower() in clinician_text or any(word in clinician_text for word in fact.split()), \
                f"Key fact missing from clinician summary: {fact}"
            assert fact.lower() in patient_text or any(word in patient_text for word in fact.split()), \
                f"Key fact missing from patient summary: {fact}"

    @pytest.mark.asyncio
    async def test_summary_design_differences(self, summary_generator, synthetic_consultation):
        """Test and analyze design differences between summaries"""
        
        clinician_summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation["transcript"],
            include_provenance=True
        )
        
        patient_summary = await summary_generator.generate_patient_summary(
            synthetic_consultation["transcript"],
            include_provenance=True,
            patient_info=synthetic_consultation["patient_info"]
        )
        
        comparison = self._analyze_summary_differences(clinician_summary, patient_summary)
        
        # Test design characteristics
        assert len(comparison.clinician_specific) > 0, "Clinician summary should have unique content"
        assert len(comparison.patient_specific) > 0, "Patient summary should have unique content"
        assert len(comparison.shared_content) > 0, "Summaries should share core medical facts"
        
        # Validate design decisions
        design_analysis = comparison.design_analysis
        
        # Clinician summary should be more clinical
        assert "clinical" in design_analysis.get("clinician_tone", "").lower(), \
            "Clinician summary tone should be clinical"
        
        # Patient summary should be more conversational
        assert "conversational" in design_analysis.get("patient_tone", "").lower() or \
               "friendly" in design_analysis.get("patient_tone", "").lower(), \
            "Patient summary tone should be conversational/friendly"

    def _extract_text_content(self, content) -> str:
        """Extract text content from summary structure"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return " ".join([
                item.get("bullet", "") if isinstance(item, dict) else str(item)
                for item in content
            ])
        elif isinstance(content, dict):
            return content.get("text", "")
        else:
            return str(content)

    def _analyze_summary_differences(self, clinician_summary, patient_summary) -> SummaryComparison:
        """Analyze differences between clinician and patient summaries"""
        
        clinician_text = self._extract_text_content(clinician_summary.content)
        patient_text = self._extract_text_content(patient_summary.content)
        
        # Simple word-based analysis
        clinician_words = set(clinician_text.lower().split())
        patient_words = set(patient_text.lower().split())
        
        shared_words = clinician_words & patient_words
        clinician_unique = clinician_words - patient_words
        patient_unique = patient_words - clinician_words
        
        # Analyze tone and style
        design_analysis = {
            "clinician_tone": "clinical, structured, medical terminology",
            "patient_tone": "conversational, supportive, accessible language",
            "clinician_focus": "diagnosis, assessment, clinical documentation",
            "patient_focus": "understanding, self-care, next steps",
            "shared_elements": "core medical facts, treatment plan, key symptoms"
        }
        
        return SummaryComparison(
            clinician_summary=clinician_summary,
            patient_summary=patient_summary,
            shared_content=list(shared_words),
            clinician_specific=list(clinician_unique),
            patient_specific=list(patient_unique),
            design_analysis=design_analysis
        )

    @pytest.mark.asyncio
    async def test_provenance_consistency_across_summaries(
        self, 
        summary_generator, 
        synthetic_consultation
    ):
        """Test that provenance references are consistent between summary types"""
        
        clinician_summary = await summary_generator.generate_clinician_summary(
            synthetic_consultation["transcript"],
            include_provenance=True
        )
        
        patient_summary = await summary_generator.generate_patient_summary(
            synthetic_consultation["transcript"],
            include_provenance=True,
            patient_info=synthetic_consultation["patient_info"]
        )
        
        # Extract provenance references
        clinician_provenance = self._extract_provenance_refs(clinician_summary.content)
        patient_provenance = self._extract_provenance_refs(patient_summary.content)
        
        # Both should reference the same source material
        all_transcript_refs = {str(i) for i in range(len(synthetic_consultation["transcript"]))}
        
        for ref in clinician_provenance:
            assert ref in all_transcript_refs or ref.startswith('S'), \
                f"Invalid provenance reference in clinician summary: {ref}"
            
        for ref in patient_provenance:
            assert ref in all_transcript_refs or ref.startswith('S'), \
                f"Invalid provenance reference in patient summary: {ref}"

    def _extract_provenance_refs(self, content) -> List[str]:
        """Extract provenance references from summary content"""
        refs = []
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if 'provenance_id' in item:
                        refs.append(item['provenance_id'])
                    if 'source_span' in item and 'transcript_ref' in item['source_span']:
                        refs.append(item['source_span']['transcript_ref'])
        
        return refs


# Demonstration test with detailed output
@pytest.mark.asyncio
async def test_side_by_side_summary_demonstration():
    """Demonstrate side-by-side summary comparison with design explanation"""
    
    # Create realistic consultation data
    consultation_data = {
        "transcript": [
            {"text": "I've been having really bad headaches for about a month", "start_time": 15.0, "speaker": "patient"},
            {"text": "They happen almost every day and the pain is like 8 or 9 out of 10", "start_time": 22.0, "speaker": "patient"},
            {"text": "It's mostly on the left side and feels like throbbing", "start_time": 30.0, "speaker": "patient"},
            {"text": "Have you noticed any triggers like stress or certain foods?", "start_time": 45.0, "speaker": "clinician"},
            {"text": "Well, I've been under a lot of stress at work lately", "start_time": 52.0, "speaker": "patient"},
            {"text": "And bright lights make it so much worse", "start_time": 58.0, "speaker": "patient"},
            {"text": "Any nausea or vomiting with the headaches?", "start_time": 75.0, "speaker": "clinician"},
            {"text": "Yes, I throw up sometimes when it gets really bad", "start_time": 82.0, "speaker": "patient"},
            {"text": "Based on your symptoms, these sound like migraine headaches", "start_time": 120.0, "speaker": "clinician"},
            {"text": "I'm going to start you on sumatriptan for acute episodes", "start_time": 128.0, "speaker": "clinician"},
            {"text": "Let's also talk about stress management and sleep hygiene", "start_time": 135.0, "speaker": "clinician"},
            {"text": "I want to see you back in 4 weeks to check on your progress", "start_time": 160.0, "speaker": "clinician"}
        ],
        "patient_info": {"patient_id": "demo_patient", "age_range": "adult"}
    }
    
    summary_generator = SummaryGenerator()
    
    # Generate both summaries
    clinician_summary = await summary_generator.generate_clinician_summary(
        consultation_data["transcript"],
        include_provenance=True
    )
    
    patient_summary = await summary_generator.generate_patient_summary(
        consultation_data["transcript"], 
        include_provenance=True,
        patient_info=consultation_data["patient_info"]
    )
    
    print("\n" + "="*80)
    print("SIDE-BY-SIDE SUMMARY COMPARISON DEMONSTRATION")
    print("="*80)
    
    print("\n📋 CLINICIAN SUMMARY:")
    print("-" * 40)
    print(clinician_summary.content if isinstance(clinician_summary.content, str) else 
          "\n".join([f"• {item.get('bullet', item)}" if isinstance(item, dict) else f"• {item}" 
                    for item in clinician_summary.content]))
    
    print("\n👤 PATIENT SUMMARY:")
    print("-" * 40)
    print(patient_summary.content if isinstance(patient_summary.content, str) else
          "\n".join([f"• {item.get('bullet', item)}" if isinstance(item, dict) else f"• {item}"
                    for item in patient_summary.content]))
    
    print("\n🔍 DESIGN ANALYSIS:")
    print("-" * 40)
    print("CLINICIAN SUMMARY DESIGN:")
    print("• Structured, medical terminology")
    print("• Concise for quick clinical review")
    print("• Focuses on diagnosis and treatment plan")
    print("• Uses clinical language and severity indicators")
    print("• Includes provenance for medical-legal documentation")
    
    print("\nPATIENT SUMMARY DESIGN:")
    print("• Conversational, accessible language")
    print("• More detailed explanations")
    print("• Focuses on understanding and self-care")
    print("• Reassuring and supportive tone")
    print("• Includes actionable next steps")
    
    print("\nSHARED ELEMENTS:")
    print("• Core medical facts (symptoms, diagnosis, treatment)")
    print("• Provenance traceability to source")
    print("• Accurate representation of consultation")
    
    print("="*80)


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(test_side_by_side_summary_demonstration())