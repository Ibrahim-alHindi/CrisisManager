"""
Test scenarios for Crisis Response Coordinator Agent
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.coordinator_agent import CrisisCoordinator


def test_medical_emergencies():
    """Test medical emergency classification and response"""
    print("\n🏥 Testing Medical Emergencies...")
    
    coordinator = CrisisCoordinator()
    
    test_cases = [
        "My father is having chest pain and difficulty breathing",
        "Someone is choking and can't breathe",
        "Severe bleeding from a deep cut",
        "I think my mother is having a stroke, her face is drooping"
    ]
    
    for case in test_cases:
        print(f"\n  Testing: '{case[:50]}...'")
        classification = coordinator.classify_crisis(case)
        
        assert classification['category'] == 'medical_emergency', \
            f"Expected medical_emergency, got {classification['category']}"
        assert classification['severity'] in ['critical', 'high'], \
            f"Expected high severity, got {classification['severity']}"
        
        print(f"  ✅ Classified as {classification['category']} / {classification['severity']}")
    
    print("\n✅ All medical emergency tests passed!")


def test_mental_health_crises():
    """Test mental health crisis classification and response"""
    print("\n🧠 Testing Mental Health Crises...")
    
    coordinator = CrisisCoordinator()
    
    test_cases = [
        ("I'm having a panic attack", "medium"),
        ("I want to kill myself", "critical"),
        ("Feeling extremely anxious and overwhelmed", "medium"),
        ("I don't want to live anymore", "critical")
    ]
    
    for case, expected_severity in test_cases:
        print(f"\n  Testing: '{case[:50]}...'")
        classification = coordinator.classify_crisis(case)
        
        assert classification['category'] == 'mental_health_crisis', \
            f"Expected mental_health_crisis, got {classification['category']}"
        
        print(f"  ✅ Classified as {classification['category']} / {classification['severity']}")
    
    print("\n✅ All mental health crisis tests passed!")


def test_disaster_emergencies():
    """Test disaster emergency classification and response"""
    print("\n🌍 Testing Disaster Emergencies...")
    
    coordinator = CrisisCoordinator()
    
    test_cases = [
        "Earthquake just hit, building is shaking",
        "Flash flood warning, water rising quickly",
        "Fire in the building, smoke everywhere",
        "Hurricane approaching, strong winds"
    ]
    
    for case in test_cases:
        print(f"\n  Testing: '{case[:50]}...'")
        classification = coordinator.classify_crisis(case)
        
        assert classification['category'] == 'disaster_emergency', \
            f"Expected disaster_emergency, got {classification['category']}"
        
        print(f"  ✅ Classified as {classification['category']} / {classification['severity']}")
    
    print("\n✅ All disaster emergency tests passed!")


def test_full_workflow():
    """Test complete crisis handling workflow"""
    print("\n🔄 Testing Full Workflow...")
    
    coordinator = CrisisCoordinator()
    
    crisis = "My father is having severe chest pain"
    
    print(f"\n  Input: '{crisis}'")
    
    # Test classification
    classification = coordinator.classify_crisis(crisis)
    print(f"  ✅ Classification: {classification['category']}")
    
    # Test protocol retrieval
    protocol = coordinator.get_relevant_protocol(classification)
    assert protocol is not None, "Protocol should be retrieved"
    print(f"  ✅ Protocol retrieved: {protocol['name']}")
    
    # Test full response
    response = coordinator.handle_crisis(crisis)
    assert len(response) > 0, "Response should not be empty"
    assert "CASE-" in response, "Response should include case ID"
    print(f"  ✅ Full response generated ({len(response)} characters)")
    
    # Test case tracking
    assert coordinator.case_counter > 0, "Case counter should increment"
    print(f"  ✅ Case tracked: {coordinator.case_counter} cases")
    
    print("\n✅ Full workflow test passed!")


def test_state_management():
    """Test case state management"""
    print("\n📊 Testing State Management...")
    
    coordinator = CrisisCoordinator()
    
    # Create multiple cases
    cases = [
        "Chest pain emergency",
        "Panic attack",
        "Earthquake"
    ]
    
    for crisis in cases:
        coordinator.handle_crisis(crisis)
    
    # Verify state
    assert coordinator.case_counter == len(cases), \
        f"Expected {len(cases)} cases, got {coordinator.case_counter}"
    
    assert len(coordinator.active_cases) == len(cases), \
        f"Expected {len(cases)} active cases, got {len(coordinator.active_cases)}"
    
    # Check case structure
    first_case = list(coordinator.active_cases.values())[0]
    assert 'id' in first_case
    assert 'timestamp' in first_case
    assert 'classification' in first_case
    assert 'follow_up_scheduled' in first_case
    
    print(f"  ✅ Created {coordinator.case_counter} cases")
    print(f"  ✅ All cases tracked in state")
    print(f"  ✅ Case structure validated")
    
    print("\n✅ State management test passed!")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("🧪 CRISIS RESPONSE COORDINATOR - TEST SUITE")
    print("="*70)
    
    try:
        test_medical_emergencies()
        test_mental_health_crises()
        test_disaster_emergencies()
        test_full_workflow()
        test_state_management()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
