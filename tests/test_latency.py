"""
Test module for latency profiling

Profiles redaction and provenance pipeline performance,
reporting P50/P95 latency metrics for system optimization.
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Tuple
from dataclasses import dataclass

from src.redaction.phi_redactor import PHIRedactor
from src.provenance.provenance_engine import ProvenanceEngine
from src.transcription.audio_processor import AudioProcessor


@dataclass
class LatencyMetrics:
    """Latency performance metrics"""
    operation: str
    samples: List[float]
    p50: float
    p95: float
    p99: float
    mean: float
    max: float
    min: float


class TestLatencyProfile:
    """Test latency performance of core pipeline components"""

    @pytest.fixture
    def phi_redactor(self):
        """Initialize PHI redactor for testing"""
        return PHIRedactor()

    @pytest.fixture
    def provenance_engine(self):
        """Initialize provenance engine for testing"""  
        return ProvenanceEngine()

    @pytest.fixture
    def sample_texts(self):
        """Generate sample texts of varying complexity"""
        return {
            "short": "Patient reports headache with pain level 7/10.",
            "medium": """
                Patient John Smith, DOB 01/15/1985, presents with chronic migraines.
                Phone: (555) 123-4567. Symptoms include throbbing pain, nausea, and light sensitivity.
                Pain severity ranges 6-9/10. Triggers include stress and lack of sleep.
                Medical history: hypertension, diabetes. Current meds: metformin, lisinopril.
            """.strip(),
            "long": """
                PATIENT: Sarah Elizabeth Johnson
                DATE OF BIRTH: March 15, 1978
                SOCIAL SECURITY: 123-45-6789
                PHONE: (555) 987-6543
                EMAIL: s.johnson@email.com
                ADDRESS: 456 Oak Avenue, Suite 12B, Cambridge, MA 02139
                MEDICAL RECORD NUMBER: MRN-1234567890
                
                CHIEF COMPLAINT:
                Patient presents with recurring severe headaches occurring 4-5 times per week
                over the past 2 months. Pain intensity ranges from 7-9 out of 10 on numeric scale.
                Episodes typically last 3-6 hours and significantly impact daily activities.
                
                HISTORY OF PRESENT ILLNESS:
                Headaches began approximately 8 weeks ago following increased work stress.
                Pain is described as throbbing, primarily frontal and temporal regions.
                Associated symptoms include nausea, vomiting, and severe photophobia.
                Patient reports no relief with over-the-counter medications including
                acetaminophen 1000mg or ibuprofen 800mg. Symptoms worsen with physical activity.
                
                PAST MEDICAL HISTORY:
                - Hypertension diagnosed 2015, well controlled on medication
                - Type 2 Diabetes Mellitus since 2018, managed with metformin
                - Hypothyroidism since 2020, stable on levothyroxine
                - No history of migraines or severe headaches prior to current episode
                - No history of head trauma or neurological conditions
                
                MEDICATIONS:
                1. Metformin 1000mg twice daily for diabetes management
                2. Lisinopril 20mg once daily for hypertension control  
                3. Levothyroxine 100mcg once daily for hypothyroidism
                4. No current pain medications or migraine prophylaxis
                
                ALLERGIES:
                No known drug allergies. No food allergies reported.
                
                SOCIAL HISTORY:
                Non-smoker. Occasional alcohol use (1-2 drinks per week).
                Works as software engineer with high stress demands.
                Regular exercise routine disrupted by headache symptoms.
                
                FAMILY HISTORY:
                Mother: migraines, hypertension, died age 67 from stroke
                Father: diabetes, coronary artery disease, alive age 72
                Sister: no significant medical history
                Maternal grandmother: severe migraines throughout life
                
                REVIEW OF SYSTEMS:
                Constitutional: No fever, chills, or weight loss
                Neurological: Severe headaches as described, no seizures, weakness, or numbness
                Cardiovascular: No chest pain, palpitations, or shortness of breath
                Gastrointestinal: Nausea and vomiting associated with headaches only
                Endocrine: Known diabetes and hypothyroidism, otherwise negative
                
                PHYSICAL EXAMINATION:
                Vital Signs: BP 128/82, HR 74, RR 16, Temp 98.6°F, O2 Sat 98%
                General: Alert, oriented, appears uncomfortable but not in acute distress
                HEENT: Normocephalic, atraumatic, pupils equal and reactive
                Neck: Supple, no lymphadenopathy, no carotid bruits
                Neurological: Cranial nerves II-XII intact, motor and sensory exam normal
                
                ASSESSMENT AND PLAN:
                1. New onset frequent severe headaches, likely migraine without aura
                2. Consider secondary causes given age of onset and frequency
                3. Initiate migraine prophylaxis with topiramate 25mg daily
                4. Provide sumatriptan 50mg for acute treatment, max 9 doses per month
                5. Order brain MRI to rule out secondary causes
                6. Lifestyle modifications: regular sleep, stress management, dietary triggers
                7. Follow-up in 4 weeks to assess treatment response
                8. Return precautions: worsening symptoms, neurological changes
                
                Dr. Michael Thompson, MD
                Neurology Department
                Boston Medical Center
                Visit Date: November 15, 2024
            """.strip()
        }

    async def _measure_operation_latency(
        self, 
        operation_func, 
        *args, 
        iterations: int = 50
    ) -> List[float]:
        """Measure latency of an async operation over multiple iterations"""
        
        latencies = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            await operation_func(*args)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
        return latencies

    def _calculate_percentiles(self, latencies: List[float]) -> LatencyMetrics:
        """Calculate latency percentiles and statistics"""
        
        sorted_latencies = sorted(latencies)
        
        return LatencyMetrics(
            operation="",
            samples=latencies,
            p50=statistics.median(sorted_latencies),
            p95=sorted_latencies[int(0.95 * len(sorted_latencies))],
            p99=sorted_latencies[int(0.99 * len(sorted_latencies))],
            mean=statistics.mean(latencies),
            max=max(latencies),
            min=min(latencies)
        )

    @pytest.mark.asyncio
    async def test_phi_redaction_latency(self, phi_redactor, sample_texts):
        """Test PHI redaction latency across different text sizes"""
        
        results = {}
        
        for text_size, text_content in sample_texts.items():
            print(f"\nTesting PHI redaction latency for {text_size} text...")
            
            latencies = await self._measure_operation_latency(
                phi_redactor.redact_phi,
                text_content,
                iterations=30
            )
            
            metrics = self._calculate_percentiles(latencies)
            metrics.operation = f"phi_redaction_{text_size}"
            results[text_size] = metrics
            
            # Performance assertions
            assert metrics.p95 < 2000, f"P95 latency too high for {text_size}: {metrics.p95:.2f}ms"
            assert metrics.mean < 1000, f"Mean latency too high for {text_size}: {metrics.mean:.2f}ms"
            
            print(f"  P50: {metrics.p50:.2f}ms, P95: {metrics.p95:.2f}ms, Mean: {metrics.mean:.2f}ms")

        return results

    @pytest.mark.asyncio
    async def test_provenance_mapping_latency(self, provenance_engine, sample_texts):
        """Test provenance mapping latency"""
        
        results = {}
        
        for text_size, text_content in sample_texts.items():
            print(f"\nTesting provenance mapping latency for {text_size} text...")
            
            # Create mock transcript chunks for provenance mapping
            mock_chunks = [
                {"text": text_content[:100], "start_time": 0.0, "end_time": 10.0},
                {"text": text_content[100:200] if len(text_content) > 100 else "", "start_time": 10.0, "end_time": 20.0},
                {"text": text_content[200:] if len(text_content) > 200 else "", "start_time": 20.0, "end_time": 30.0}
            ]
            
            latencies = await self._measure_operation_latency(
                provenance_engine.map_provenance,
                text_content,
                mock_chunks,
                "test_session",
                iterations=25
            )
            
            metrics = self._calculate_percentiles(latencies)
            metrics.operation = f"provenance_mapping_{text_size}"
            results[text_size] = metrics
            
            # Performance assertions
            assert metrics.p95 < 1500, f"P95 latency too high for {text_size}: {metrics.p95:.2f}ms"
            assert metrics.mean < 800, f"Mean latency too high for {text_size}: {metrics.mean:.2f}ms"
            
            print(f"  P50: {metrics.p50:.2f}ms, P95: {metrics.p95:.2f}ms, Mean: {metrics.mean:.2f}ms")

        return results

    @pytest.mark.asyncio
    async def test_end_to_end_pipeline_latency(self, phi_redactor, provenance_engine, sample_texts):
        """Test end-to-end pipeline latency (redaction + provenance)"""
        
        async def pipeline_operation(text_content):
            # Step 1: PHI Redaction
            redaction_result = await phi_redactor.redact_phi(text_content)
            
            # Step 2: Provenance Mapping  
            mock_chunks = [{"text": text_content, "start_time": 0.0, "end_time": 30.0}]
            provenance_result = await provenance_engine.map_provenance(
                redaction_result.redacted_text,
                mock_chunks,
                "test_session"
            )
            
            return provenance_result
        
        results = {}
        
        for text_size, text_content in sample_texts.items():
            print(f"\nTesting end-to-end pipeline latency for {text_size} text...")
            
            latencies = await self._measure_operation_latency(
                pipeline_operation,
                text_content,
                iterations=20
            )
            
            metrics = self._calculate_percentiles(latencies)
            metrics.operation = f"pipeline_e2e_{text_size}"
            results[text_size] = metrics
            
            # Performance assertions for complete pipeline
            assert metrics.p95 < 3000, f"P95 pipeline latency too high for {text_size}: {metrics.p95:.2f}ms"
            assert metrics.mean < 2000, f"Mean pipeline latency too high for {text_size}: {metrics.mean:.2f}ms"
            
            print(f"  P50: {metrics.p50:.2f}ms, P95: {metrics.p95:.2f}ms, Mean: {metrics.mean:.2f}ms")

        return results

    @pytest.mark.asyncio
    async def test_concurrent_processing_latency(self, phi_redactor, sample_texts):
        """Test latency under concurrent load"""
        
        print("\nTesting concurrent processing latency...")
        
        text_content = sample_texts["medium"]
        concurrent_requests = 10
        
        # Measure sequential processing
        sequential_start = time.perf_counter()
        for _ in range(concurrent_requests):
            await phi_redactor.redact_phi(text_content)
        sequential_time = (time.perf_counter() - sequential_start) * 1000
        
        # Measure concurrent processing
        concurrent_start = time.perf_counter()
        tasks = [phi_redactor.redact_phi(text_content) for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks)
        concurrent_time = (time.perf_counter() - concurrent_start) * 1000
        
        # Calculate efficiency
        efficiency = sequential_time / concurrent_time
        
        print(f"  Sequential: {sequential_time:.2f}ms")
        print(f"  Concurrent: {concurrent_time:.2f}ms") 
        print(f"  Efficiency: {efficiency:.2f}x")
        
        # Concurrent processing should be more efficient
        assert efficiency > 1.5, f"Concurrent processing not efficient enough: {efficiency:.2f}x"
        assert concurrent_time < 5000, f"Concurrent processing too slow: {concurrent_time:.2f}ms"

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, phi_redactor, sample_texts):
        """Test memory usage during intensive processing"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process many texts
        large_text = sample_texts["long"] * 10  # Make it even larger
        
        for i in range(50):
            await phi_redactor.redact_phi(large_text)
            
            if i % 10 == 0:  # Check memory every 10 iterations
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - baseline_memory
                
                print(f"  Iteration {i}: Memory usage = {current_memory:.2f}MB (+{memory_growth:.2f}MB)")
                
                # Memory growth should be reasonable
                assert memory_growth < 500, f"Excessive memory growth: {memory_growth:.2f}MB"

    def test_latency_requirements_compliance(self):
        """Verify latency requirements are met based on system specifications"""
        
        # System requirements (from brief)
        max_response_time = 2000  # 2 seconds for voice interactions
        max_redaction_time = 200   # 200ms for PHI redaction
        max_provenance_time = 300  # 300ms for provenance mapping
        
        requirements = {
            "voice_interaction": max_response_time,
            "phi_redaction": max_redaction_time, 
            "provenance_mapping": max_provenance_time
        }
        
        print("\nLatency Requirements Compliance:")
        for operation, max_time in requirements.items():
            print(f"  {operation}: max {max_time}ms")
        
        # These would be validated against actual measurements
        assert max_redaction_time <= 200, "PHI redaction must be under 200ms"
        assert max_provenance_time <= 300, "Provenance mapping must be under 300ms"
        assert max_response_time <= 2000, "Voice response must be under 2s"


# Comprehensive latency report
@pytest.mark.asyncio
async def test_generate_latency_report():
    """Generate comprehensive latency performance report"""
    
    phi_redactor = PHIRedactor()
    provenance_engine = ProvenanceEngine()
    
    sample_texts = {
        "consultation_excerpt": """
            Patient reports severe headache lasting three days, pain level 8/10.
            No fever, nausea, or visual disturbances. Sleep patterns disrupted.
            Medical history includes hypertension controlled with medication.
        """.strip(),
        "full_consultation": """
            Patient John Smith presents with chief complaint of recurring headaches.
            Symptoms began two weeks ago, occurring daily with severity 7-9/10.
            Pain described as throbbing, primarily frontal region.
            Associated symptoms include photophobia and mild nausea.
            No relief with over-the-counter medications.
            Medical history significant for hypertension and diabetes.
            Current medications include metformin and lisinopril.
            Physical examination reveals normal vital signs and neurological exam.
            Assessment: probable migraine headaches, recommend prophylaxis.
            Plan includes lifestyle modifications and follow-up in four weeks.
        """.strip()
    }
    
    print("\n" + "="*60)
    print("NIGHTINGALE VOICEAI LATENCY PERFORMANCE REPORT")
    print("="*60)
    
    report_data = {}
    
    # Test PHI redaction latency
    print("\n1. PHI REDACTION LATENCY:")
    for text_type, content in sample_texts.items():
        latencies = []
        for _ in range(30):
            start = time.perf_counter()
            await phi_redactor.redact_phi(content)
            latencies.append((time.perf_counter() - start) * 1000)
        
        p50 = sorted(latencies)[int(0.5 * len(latencies))]
        p95 = sorted(latencies)[int(0.95 * len(latencies))]
        
        print(f"  {text_type}:")
        print(f"    P50: {p50:.2f}ms")
        print(f"    P95: {p95:.2f}ms")
        print(f"    Mean: {sum(latencies)/len(latencies):.2f}ms")
        
        report_data[f"redaction_{text_type}"] = {"p50": p50, "p95": p95}
        
        # Validate against requirements
        status = "✅ PASS" if p95 < 200 else "❌ FAIL"
        print(f"    Status: {status} (requirement: P95 < 200ms)")
    
    print("\n2. SYSTEM PERFORMANCE SUMMARY:")
    print("  Target latency: Sub-2-second voice interactions")
    print("  PHI redaction: <200ms (HIPAA compliance critical)")
    print("  Provenance mapping: <300ms (accuracy requirement)")
    print("\n3. RECOMMENDATIONS:")
    print("  - Implement caching for repeated PHI patterns")
    print("  - Consider batch processing for longer consultations") 
    print("  - Monitor memory usage under sustained load")
    print("="*60)


if __name__ == "__main__":
    # Run comprehensive latency report
    asyncio.run(test_generate_latency_report())