"""
Crisis Response Coordinator Agent
Main orchestrator that classifies crises and delegates to specialist agents
Demonstrates: Multi-agent orchestration, prompt engineering, state management
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai


class CrisisCoordinator:
    """
    Main coordinator agent that:
    1. Classifies incoming crisis reports
    2. Assesses severity levels
    3. Delegates to appropriate specialist agents
    4. Maintains case state and follow-up schedules
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the coordinator with Gemini API"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
            print("⚠️  Warning: No API key provided. Running in demo mode.")
        
        # Load crisis protocols and helplines
        self.protocols = self._load_protocols()
        self.helplines = self._load_helplines()
        
        # State management with persistent storage
        self.cases_file = os.path.join(
            os.path.dirname(__file__), '..', '..', 'cases.json'
        )
        self.active_cases = {}
        self.case_counter = 0
        self._load_cases()
        
    def _load_protocols(self) -> Dict:
        """Load crisis protocols from JSON file"""
        try:
            protocol_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'crisis_protocols.json'
            )
            with open(protocol_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  Warning: Crisis protocols file not found")
            return {}
    
    def _load_helplines(self) -> Dict:
        """Load helpline database from JSON file"""
        try:
            helpline_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'helplines.json'
            )
            with open(helpline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  Warning: Helplines file not found")
            return {}
    
    def _load_cases(self):
        """Load existing cases from JSON file"""
        try:
            if os.path.exists(self.cases_file):
                with open(self.cases_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cases_list = data.get('cases', [])
                    # Reconstruct active_cases dict
                    for case in cases_list:
                        self.active_cases[case['id']] = case
                    # Update counter
                    self.case_counter = data.get('metadata', {}).get('total_cases', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is invalid, start fresh
            pass
    
    def _save_cases(self):
        """Save cases to JSON file"""
        try:
            data = {
                'cases': list(self.active_cases.values()),
                'metadata': {
                    'total_cases': self.case_counter,
                    'last_updated': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            with open(self.cases_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Warning: Could not save cases: {e}")
    
    def classify_crisis(self, user_input: str, country: str = "USA") -> Dict:
        """
        Classify the crisis type and severity using Gemini
        
        ADK Concept: Advanced Prompt Engineering with few-shot examples
        """
        
        classification_prompt = f"""You are a crisis classification expert. Analyze the following crisis report and classify it.

User Report: "{user_input}"

Classify this crisis into ONE of these categories:
1. medical_emergency (heart attack, stroke, severe bleeding, choking, etc.)
2. mental_health_crisis (panic attack, suicidal thoughts, PTSD, severe anxiety)
3. disaster_emergency (earthquake, flood, fire, hurricane, etc.)
4. other (general distress, non-emergency)

Also assess severity:
- critical (immediate life threat, requires emergency services NOW)
- high (serious situation, needs urgent attention)
- medium (concerning but not immediately life-threatening)
- low (general support needed)

Respond in this EXACT JSON format:
{{
    "category": "medical_emergency|mental_health_crisis|disaster_emergency|other",
    "severity": "critical|high|medium|low",
    "keywords": ["keyword1", "keyword2"],
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Examples:

Input: "My father is having chest pain and can't breathe"
Output: {{"category": "medical_emergency", "severity": "critical", "keywords": ["chest pain", "breathing difficulty"], "confidence": 0.95, "reasoning": "Potential cardiac emergency"}}

Input: "I'm feeling really anxious and having panic attacks"
Output: {{"category": "mental_health_crisis", "severity": "medium", "keywords": ["anxiety", "panic attacks"], "confidence": 0.90, "reasoning": "Panic attack symptoms"}}

Input: "Earthquake just hit, building shaking"
Output: {{"category": "disaster_emergency", "severity": "high", "keywords": ["earthquake", "building shaking"], "confidence": 0.98, "reasoning": "Active seismic event"}}

Now classify this:
Input: "{user_input}"
Output:"""

        if self.model:
            try:
                response = self.model.generate_content(classification_prompt)
                # Extract JSON from response
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                
                classification = json.loads(response_text.strip())
                classification['country'] = country
                return classification
            except Exception as e:
                print(f"⚠️  Classification error: {e}")
                return self._fallback_classification(user_input, country)
        else:
            return self._fallback_classification(user_input, country)
    
    def _fallback_classification(self, user_input: str, country: str) -> Dict:
        """Simple keyword-based classification fallback"""
        user_lower = user_input.lower()
        
        # Medical keywords
        medical_keywords = ['chest pain', 'heart attack', 'stroke', 'bleeding', 'choking', 
                          'breathing', 'unconscious', 'seizure', 'broken bone']
        
        # Mental health keywords
        mental_keywords = ['suicide', 'kill myself', 'panic attack', 'panic', 'anxiety', 'anxious',
                         'depressed', 'depression', 'self-harm', 'ptsd', 'trauma', 'want to die',
                         'overwhelmed', 'stressed', 'mental health', 'nervous', 'worried',
                         "don't want to live", 'no reason to live', 'hopeless']
        
        # Disaster keywords
        disaster_keywords = ['earthquake', 'flood', 'fire', 'hurricane', 'tornado', 
                           'tsunami', 'explosion', 'building collapse']
        
        if any(kw in user_lower for kw in medical_keywords):
            return {
                "category": "medical_emergency",
                "severity": "critical",
                "keywords": [kw for kw in medical_keywords if kw in user_lower],
                "confidence": 0.75,
                "reasoning": "Keyword-based medical classification",
                "country": country
            }
        elif any(kw in user_lower for kw in mental_keywords):
            severity = "critical" if any(kw in user_lower for kw in ['suicide', 'kill myself']) else "medium"
            return {
                "category": "mental_health_crisis",
                "severity": severity,
                "keywords": [kw for kw in mental_keywords if kw in user_lower],
                "confidence": 0.75,
                "reasoning": "Keyword-based mental health classification",
                "country": country
            }
        elif any(kw in user_lower for kw in disaster_keywords):
            return {
                "category": "disaster_emergency",
                "severity": "high",
                "keywords": [kw for kw in disaster_keywords if kw in user_lower],
                "confidence": 0.75,
                "reasoning": "Keyword-based disaster classification",
                "country": country
            }
        else:
            return {
                "category": "other",
                "severity": "low",
                "keywords": [],
                "confidence": 0.5,
                "reasoning": "No specific crisis keywords detected",
                "country": country
            }
    
    def get_relevant_protocol(self, classification: Dict) -> Optional[Dict]:
        """
        Retrieve relevant crisis protocol based on classification
        
        ADK Concept: RAG (Retrieval-Augmented Generation) - simplified version
        In production, this would use vector embeddings and semantic search
        """
        category = classification['category']
        keywords = classification['keywords']
        
        # Map categories to protocol sections
        protocol_map = {
            'medical_emergency': 'medical_emergencies',
            'mental_health_crisis': 'mental_health_crises',
            'disaster_emergency': 'disaster_emergencies'
        }
        
        protocol_section = protocol_map.get(category)
        if not protocol_section or protocol_section not in self.protocols:
            return None
        
        # Find best matching protocol based on keywords
        protocols = self.protocols[protocol_section]
        best_match = None
        best_score = 0
        
        for protocol in protocols:
            # Calculate keyword overlap score
            protocol_keywords = set(kw.lower() for kw in protocol.get('keywords', []))
            user_keywords = set(kw.lower() for kw in keywords)
            
            overlap = len(protocol_keywords.intersection(user_keywords))
            if overlap > best_score:
                best_score = overlap
                best_match = protocol
        
        return best_match
    
    def get_helplines(self, classification: Dict) -> Dict:
        """Get relevant helplines based on crisis type and country"""
        country = classification.get('country', 'USA')
        category = classification['category']
        
        helplines = {}
        
        # Get emergency services
        if 'global_helplines' in self.helplines:
            emergency = self.helplines['global_helplines'].get('emergency_services', {})
            helplines['emergency_services'] = emergency.get(country, emergency.get('USA', {}))
            
            # Get category-specific helplines
            if category == 'mental_health_crisis':
                mental_health = self.helplines['global_helplines'].get('mental_health', {})
                helplines['crisis_support'] = mental_health.get(country, mental_health.get('USA', []))
        
        return helplines
    
    def handle_crisis(self, user_input: str, country: str = "USA") -> str:
        """
        Main entry point: Handle a crisis report end-to-end
        
        ADK Concept: Multi-agent orchestration and state management
        """
        # Step 1: Classify the crisis
        classification = self.classify_crisis(user_input, country)
        
        # Step 2: Retrieve relevant protocol (RAG)
        protocol = self.get_relevant_protocol(classification)
        
        # Step 3: Get helplines
        helplines = self.get_helplines(classification)
        
        # Step 4: Create case record (State Management)
        case_id = self._create_case(user_input, classification, protocol)
        
        # Step 5: Generate response
        response = self._generate_response(classification, protocol, helplines, case_id)
        
        return response
    
    def _create_case(self, user_input: str, classification: Dict, protocol: Optional[Dict]) -> str:
        """Create and store case record for follow-up tracking"""
        self.case_counter += 1
        case_id = f"CASE-{self.case_counter:05d}"
        
        self.active_cases[case_id] = {
            'id': case_id,
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'classification': classification,
            'protocol_used': protocol.get('id') if protocol else None,
            'status': 'active',
            'follow_up_scheduled': self._calculate_follow_up(classification['severity'])
        }
        
        # Save to persistent storage
        self._save_cases()
        
        return case_id
    
    def _calculate_follow_up(self, severity: str) -> str:
        """Calculate when to follow up based on severity"""
        from datetime import timedelta
        
        follow_up_times = {
            'critical': timedelta(hours=2),
            'high': timedelta(hours=6),
            'medium': timedelta(days=1),
            'low': timedelta(days=3)
        }
        
        follow_up = datetime.now() + follow_up_times.get(severity, timedelta(days=1))
        return follow_up.isoformat()
    
    def _generate_response(self, classification: Dict, protocol: Optional[Dict], 
                          helplines: Dict, case_id: str) -> str:
        """Generate formatted crisis response"""
        
        severity_icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️'
        }
        
        category_icons = {
            'medical_emergency': '🏥',
            'mental_health_crisis': '🧠',
            'disaster_emergency': '🌍',
            'other': '💬'
        }
        
        severity = classification['severity']
        category = classification['category']
        
        response = f"\n{severity_icons.get(severity, '⚠️')} {category_icons.get(category, '💬')} "
        response += f"{category.replace('_', ' ').upper()} DETECTED - {severity.upper()} SEVERITY\n"
        response += f"{'='*70}\n\n"
        
        # Add immediate actions from protocol
        if protocol and 'protocol' in protocol:
            response += "🔴 IMMEDIATE ACTIONS:\n"
            actions = protocol['protocol'].get('immediate_actions', [])
            for i, action in enumerate(actions[:6], 1):  # Limit to 6 actions
                response += f"{i}. {action}\n"
            response += "\n"
        
        # Add emergency helplines
        if helplines.get('emergency_services'):
            response += "📞 EMERGENCY CONTACTS:\n"
            emergency = helplines['emergency_services']
            if 'emergency' in emergency:
                response += f"   Emergency Services: {emergency['emergency']}\n"
            if 'suicide_prevention' in emergency:
                response += f"   Suicide Prevention: {emergency['suicide_prevention']}\n"
            if 'crisis_text' in emergency:
                response += f"   Crisis Text Line: {emergency['crisis_text']}\n"
            response += "\n"
        
        # Add protocol details
        if protocol:
            response += f"📋 Protocol: {protocol.get('name', 'General Crisis Response')}\n"
            response += f"📚 Source: {protocol.get('source', 'Crisis Response Guidelines')}\n\n"
        
        # Add warnings if present
        if protocol and 'protocol' in protocol and 'do_not' in protocol['protocol']:
            response += "⛔ DO NOT:\n"
            for warning in protocol['protocol']['do_not'][:4]:
                response += f"   ✗ {warning}\n"
            response += "\n"
        
        # Add case tracking info
        response += f"📊 Case ID: {case_id}\n"
        response += f"⏰ Follow-up scheduled: {self.active_cases[case_id]['follow_up_scheduled'][:16]}\n"
        response += f"🤖 Confidence: {classification.get('confidence', 0.8):.0%}\n\n"
        
        # Add disclaimer
        response += "⚠️  IMPORTANT: This is an AI assistant. Always call emergency services for life-threatening situations.\n"
        response += "   This system provides guidance but does NOT replace professional medical or crisis intervention.\n"
        
        return response
    
    def get_case_status(self, case_id: str) -> Optional[Dict]:
        """Retrieve case information for follow-up"""
        return self.active_cases.get(case_id)
    
    def list_active_cases(self) -> List[Dict]:
        """List all active cases"""
        return list(self.active_cases.values())


# Demo usage
if __name__ == "__main__":
    print("🚨 Crisis Response Coordinator Agent - Demo Mode\n")
    
    coordinator = CrisisCoordinator()
    
    # Test scenarios
    test_cases = [
        ("My father is having severe chest pain and difficulty breathing", "USA"),
        ("I'm having a panic attack and can't calm down", "USA"),
        ("Earthquake just hit, building is shaking violently", "USA"),
        ("I'm feeling suicidal and don't want to live anymore", "USA")
    ]
    
    for user_input, country in test_cases:
        print(f"\n{'='*70}")
        print(f"USER INPUT: {user_input}")
        print(f"{'='*70}")
        
        response = coordinator.handle_crisis(user_input, country)
        print(response)
        print("\n")
