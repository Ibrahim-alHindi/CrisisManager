"""
Demo script for Crisis Response Coordinator Agent
Run this to see the agent in action locally
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.coordinator_agent import CrisisCoordinator


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🚨 CRISIS RESPONSE COORDINATOR AGENT")
    print("="*70)
    print("\nAgents Intensive Capstone Project")
    print("Track: Agents for Good")
    print("Author: Mohamed Ibrahim A\n")
    print("="*70 + "\n")


def run_demo_scenarios():
    """Run predefined demo scenarios"""
    
    print("🎬 Running Demo Scenarios...\n")
    
    # Initialize coordinator
    coordinator = CrisisCoordinator()
    
    # Demo scenarios
    scenarios = [
        {
            "title": "Medical Emergency: Cardiac Event",
            "input": "My father is having severe chest pain and difficulty breathing",
            "country": "USA"
        },
        {
            "title": "Mental Health: Panic Attack",
            "input": "I'm having a panic attack and can't calm down",
            "country": "USA"
        },
        {
            "title": "Disaster: Earthquake",
            "input": "Earthquake just hit our area, building is shaking",
            "country": "USA"
        },
        {
            "title": "Mental Health: Suicidal Crisis",
            "input": "I feel hopeless and don't want to live anymore",
            "country": "USA"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {i}: {scenario['title']}")
        print(f"{'='*70}\n")
        print(f"🗣️  USER INPUT: \"{scenario['input']}\"\n")
        
        # Get response
        response = coordinator.handle_crisis(scenario['input'], scenario['country'])
        print(response)
        
        print("\n" + "-"*70)
        input("\nPress Enter to continue to next scenario...")
    
    print("\n" + "="*70)
    print("✅ Demo completed successfully!")
    print("="*70 + "\n")


def run_interactive_mode():
    """Run interactive crisis response mode"""
    
    print("\n🤖 Interactive Crisis Response Mode")
    print("="*70)
    print("\nEnter crisis scenarios to get immediate guidance.")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    coordinator = CrisisCoordinator()
    
    while True:
        try:
            user_input = input("\n🗣️  Describe the crisis: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Crisis Response Coordinator.")
                print("Remember: Always call emergency services for life-threatening situations.\n")
                break
            
            if not user_input:
                print("⚠️  Please enter a crisis description.")
                continue
            
            print("\n" + "="*70)
            response = coordinator.handle_crisis(user_input, country="USA")
            print(response)
            print("="*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended. Stay safe!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or contact support.\n")


def show_statistics():
    """Show system statistics"""
    
    coordinator = CrisisCoordinator()
    
    print("\n📊 SYSTEM STATISTICS")
    print("="*70)
    
    # Count protocols
    total_protocols = sum(len(v) for v in coordinator.protocols.values())
    
    print(f"\n✅ Total Crisis Protocols: {total_protocols}")
    print(f"   - Medical Emergencies: {len(coordinator.protocols.get('medical_emergencies', []))}")
    print(f"   - Mental Health Crises: {len(coordinator.protocols.get('mental_health_crises', []))}")
    print(f"   - Disaster Emergencies: {len(coordinator.protocols.get('disaster_emergencies', []))}")
    
    print(f"\n✅ Countries Supported: {len(coordinator.helplines.get('global_helplines', {}).get('emergency_services', {}))}")
    
    print(f"\n✅ Agent Types: 4")
    print(f"   - Coordinator Agent (Main Orchestrator)")
    print(f"   - Medical Emergency Agent")
    print(f"   - Mental Health Agent")
    print(f"   - Disaster Response Agent")
    
    print("\n✅ ADK Concepts Demonstrated: 5")
    print("   1. Multi-Agent Orchestration")
    print("   2. Retrieval-Augmented Generation (RAG)")
    print("   3. Tool Use & Function Calling")
    print("   4. State Management & Memory")
    print("   5. Advanced Prompt Engineering")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    
    print_banner()
    
    while True:
        print("\nWhat would you like to do?\n")
        print("1. 🎬 Run Demo Scenarios")
        print("2. 🤖 Interactive Mode")
        print("3. 📊 View Statistics")
        print("4. ❌ Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            run_demo_scenarios()
        elif choice == '2':
            run_interactive_mode()
        elif choice == '3':
            show_statistics()
        elif choice == '4':
            print("\n👋 Goodbye! Stay safe!\n")
            break
        else:
            print("\n⚠️  Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Session ended. Stay safe!\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.\n")
