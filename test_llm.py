#!/usr/bin/env python3
"""Quick test to verify LLM integration works"""

import os
from llm.claude_analyzer import is_llm_enabled, extract_with_llm

# Check if LLM is enabled
if is_llm_enabled():
    print("LLM is ENABLED - Claude API key found!")
    print("\nTesting with sample text...\n")

    sample_resume = """
    Jane Doe, RN BSN
    Registered Nurse with 7+ years in Labor & Delivery

    Skills: Fetal monitoring, EFM, NRP, patient assessment
    Certifications: BLS-AHA, ACLS-AHA, NRP, Advanced Fetal Monitoring
    Education: Bachelor of Science in Nursing (2017)
    """

    print("Extracting from resume text...")
    result = extract_with_llm(sample_resume, "resume")
    print("\nExtracted data:")
    print(result)
    print("\nSUCCESS: LLM is working!")

else:
    print("LLM is DISABLED - Claude API key not found")
    print("Please set ANTHROPIC_API_KEY environment variable")
