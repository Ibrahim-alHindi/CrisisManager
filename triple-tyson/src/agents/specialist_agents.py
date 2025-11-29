"""
Medical Emergency Specialist Agent
Handles medical crises with specialized medical knowledge
Demonstrates: Specialized agent behavior, tool use for medical databases
"""

import json
import os
from typing import Dict, List, Optional
import google.generativeai as genai


class MedicalEmergencyAgent:
    """
    Specialist agent for medical emergencies
    Provides detailed medical emergency guidance
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
        
        self.protocols = self._load_medical_protocols()
    
    def _load_medical_protocols(self) -> Dict:
        """Load medical emergency protocols"""
        try:
            protocol_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'crisis_protocols.json'
            )
            with open(protocol_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('medical_emergencies', [])
        except FileNotFoundError:
            return []
    
    def assess_medical_emergency(self, symptoms: str, classification: Dict) -> Dict:
        """
        Assess medical emergency and provide detailed guidance
        
        Uses medical knowledge base and Gemini for assessment
        """
        
        # Find matching protocol
        protocol = self._find_protocol(classification.get('keywords', []))
        
        if not protocol:
            return {
                'assessment': 'Unable to determine specific medical emergency',
                'action': 'Call emergency services immediately: 911 (USA) / 108 (India)',
                'protocol': None
            }
        
        # Generate detailed assessment using Gemini
        if self.model:
            assessment_prompt = f"""You are a medical emergency specialist AI. 

Symptoms reported: {symptoms}

Protocol matched: {protocol.get('name')}

Provide a brief assessment (2-3 sentences) explaining:
1. What this emergency likely is
2. Why immediate action is critical
3. What could happen if not treated quickly

Keep response clear, calm, and actionable. Do NOT diagnose - only provide emergency guidance."""

            try:
                response = self.model.generate_content(assessment_prompt)
                assessment = response.text.strip()
            except:
                assessment = f"Potential {protocol.get('name')}. Immediate medical attention required."
        else:
            assessment = f"Potential {protocol.get('name')}. Immediate medical attention required."
        
        return {
            'assessment': assessment,
            'protocol': protocol,
            'severity': protocol.get('severity'),
            'immediate_actions': protocol.get('protocol', {}).get('immediate_actions', []),
            'warnings': protocol.get('protocol', {}).get('do_not', [])
        }
    
    def _find_protocol(self, keywords: List[str]) -> Optional[Dict]:
        """Find best matching medical protocol"""
        best_match = None
        best_score = 0
        
        for protocol in self.protocols:
            protocol_keywords = set(kw.lower() for kw in protocol.get('keywords', []))
            user_keywords = set(kw.lower() for kw in keywords)
            
            overlap = len(protocol_keywords.intersection(user_keywords))
            if overlap > best_score:
                best_score = overlap
                best_match = protocol
        
        return best_match
    
    def get_cpr_instructions(self) -> str:
        """Provide CPR instructions"""
        return """
🫀 CPR INSTRUCTIONS (Hands-Only CPR for Adults):

1. Call 911 immediately or have someone else call
2. Place person on firm, flat surface
3. Kneel beside the person
4. Place heel of one hand on center of chest
5. Place other hand on top, interlace fingers
6. Keep arms straight, position shoulders directly over hands
7. Push HARD and FAST:
   - Depth: At least 2 inches (5 cm)
   - Rate: 100-120 compressions per minute
   - Rhythm: "Stayin' Alive" by Bee Gees
8. Continue until:
   - Emergency services arrive
   - Person starts breathing normally
   - You're too exhausted to continue
   - AED is available and ready to use

⚠️  Do NOT stop compressions unless absolutely necessary
⚠️  If untrained, do hands-only CPR (no rescue breaths)

Source: American Heart Association
"""


class MentalHealthAgent:
    """
    Specialist agent for mental health crises
    Provides empathetic, evidence-based mental health support
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
        
        self.protocols = self._load_mental_health_protocols()
    
    def _load_mental_health_protocols(self) -> Dict:
        """Load mental health crisis protocols"""
        try:
            protocol_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'crisis_protocols.json'
            )
            with open(protocol_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('mental_health_crises', [])
        except FileNotFoundError:
            return []
    
    def provide_support(self, user_input: str, classification: Dict) -> Dict:
        """
        Provide mental health crisis support
        
        Uses empathetic language and evidence-based techniques
        """
        
        # Find matching protocol
        protocol = self._find_protocol(classification.get('keywords', []))
        
        # Check for suicidal ideation - highest priority
        is_suicidal = any(kw in user_input.lower() for kw in 
                         ['suicide', 'kill myself', 'end it all', 'want to die', 'no reason to live'])
        
        if is_suicidal:
            return self._handle_suicidal_crisis(user_input, protocol)
        
        # Generate empathetic response
        if self.model and protocol:
            support_prompt = f"""You are a compassionate mental health crisis counselor AI.

User is experiencing: {protocol.get('name')}
User said: "{user_input}"

Provide a brief, empathetic response (3-4 sentences) that:
1. Validates their feelings
2. Offers immediate comfort
3. Encourages them to use crisis resources
4. Reminds them this is temporary

Use warm, supportive language. Be concise and actionable."""

            try:
                response = self.model.generate_content(support_prompt)
                empathetic_message = response.text.strip()
            except:
                empathetic_message = "I hear you, and what you're feeling is valid. You're not alone in this."
        else:
            empathetic_message = "I hear you, and what you're feeling is valid. You're not alone in this."
        
        return {
            'empathetic_response': empathetic_message,
            'protocol': protocol,
            'immediate_techniques': protocol.get('protocol', {}) if protocol else {},
            'crisis_resources': self._get_crisis_resources()
        }
    
    def _handle_suicidal_crisis(self, user_input: str, protocol: Optional[Dict]) -> Dict:
        """Handle suicidal crisis with highest priority"""
        return {
            'severity': 'CRITICAL',
            'empathetic_response': "I'm really glad you reached out. What you're feeling is serious, but help is available right now. You don't have to face this alone.",
            'immediate_action': 'CALL SUICIDE PREVENTION LIFELINE IMMEDIATELY',
            'crisis_lines': {
                'USA': '988 (call or text)',
                'Crisis Text Line': 'Text HOME to 741741',
                'India': '9152987821'
            },
            'protocol': protocol,
            'safety_plan': [
                'Call 988 or your local crisis line NOW',
                'Tell someone you trust how you\'re feeling',
                'Remove access to means of self-harm',
                'Go to emergency room if in immediate danger',
                'You matter, and this feeling is temporary'
            ]
        }
    
    def _find_protocol(self, keywords: List[str]) -> Optional[Dict]:
        """Find best matching mental health protocol"""
        best_match = None
        best_score = 0
        
        for protocol in self.protocols:
            protocol_keywords = set(kw.lower() for kw in protocol.get('keywords', []))
            user_keywords = set(kw.lower() for kw in keywords)
            
            overlap = len(protocol_keywords.intersection(user_keywords))
            if overlap > best_score:
                best_score = overlap
                best_match = protocol
        
        return best_match
    
    def _get_crisis_resources(self) -> Dict:
        """Get mental health crisis resources"""
        return {
            'hotlines': {
                'USA': '988 Suicide & Crisis Lifeline',
                'Text': 'Text HOME to 741741',
                'Veterans': '1-800-273-8255 (Press 1)'
            },
            'apps': [
                'Crisis Text Line (24/7 text support)',
                'BetterHelp (online therapy)',
                'Headspace (meditation & mindfulness)'
            ]
        }


class DisasterResponseAgent:
    """
    Specialist agent for disaster emergencies
    Provides disaster-specific safety protocols
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.protocols = self._load_disaster_protocols()
    
    def _load_disaster_protocols(self) -> Dict:
        """Load disaster response protocols"""
        try:
            protocol_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'crisis_protocols.json'
            )
            with open(protocol_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('disaster_emergencies', [])
        except FileNotFoundError:
            return []
    
    def provide_disaster_guidance(self, disaster_type: str, classification: Dict) -> Dict:
        """Provide disaster-specific safety guidance"""
        
        protocol = self._find_protocol(classification.get('keywords', []))
        
        if not protocol:
            return {
                'guidance': 'Seek shelter immediately and call emergency services',
                'protocol': None
            }
        
        return {
            'disaster_type': protocol.get('name'),
            'protocol': protocol,
            'immediate_actions': protocol.get('protocol', {}).get('during_earthquake') or 
                                protocol.get('protocol', {}).get('immediate_actions', []),
            'after_disaster': protocol.get('protocol', {}).get('after_earthquake') or
                            protocol.get('protocol', {}).get('after_hurricane', []),
            'warnings': protocol.get('protocol', {}).get('do_not', [])
        }
    
    def _find_protocol(self, keywords: List[str]) -> Optional[Dict]:
        """Find best matching disaster protocol"""
        best_match = None
        best_score = 0
        
        for protocol in self.protocols:
            protocol_keywords = set(kw.lower() for kw in protocol.get('keywords', []))
            user_keywords = set(kw.lower() for kw in keywords)
            
            overlap = len(protocol_keywords.intersection(user_keywords))
            if overlap > best_score:
                best_score = overlap
                best_match = protocol
        
        return best_match


# Demo
if __name__ == "__main__":
    print("🏥 Medical Emergency Agent Demo\n")
    medical_agent = MedicalEmergencyAgent()
    
    result = medical_agent.assess_medical_emergency(
        "chest pain and difficulty breathing",
        {'keywords': ['chest pain', 'breathing difficulty']}
    )
    print(f"Assessment: {result['assessment']}\n")
    
    print("\n🧠 Mental Health Agent Demo\n")
    mental_agent = MentalHealthAgent()
    
    result = mental_agent.provide_support(
        "I'm having a panic attack",
        {'keywords': ['panic attack', 'anxiety']}
    )
    print(f"Support: {result['empathetic_response']}\n")
