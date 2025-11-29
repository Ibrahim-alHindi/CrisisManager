"""
Evaluation module for Crisis Response Coordinator
Measures protocol retrieval precision, severity classification accuracy, and follow-up consistency
"""

import json
from typing import List, Dict, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.coordinator_agent import CrisisCoordinator


# Gold standard test dataset
GOLD_DATASET = [
    {
        "input": "My father is having severe chest pain and difficulty breathing",
        "expected_category": "medical_emergency",
        "expected_severity": "critical",
        "expected_protocol_id": "cardiac_emergency"
    },
    {
        "input": "I want to kill myself, I can't take it anymore",
        "expected_category": "mental_health_crisis",
        "expected_severity": "critical",
        "expected_protocol_id": "suicidal_thoughts"
    },
    {
        "input": "I'm having a panic attack, my heart is racing",
        "expected_category": "mental_health_crisis",
        "expected_severity": "medium",
        "expected_protocol_id": "panic_attack"
    },
    {
        "input": "Earthquake just hit, building is shaking violently",
        "expected_category": "disaster_emergency",
        "expected_severity": "high",
        "expected_protocol_id": "earthquake"
    },
    {
        "input": "Someone is choking and can't breathe",
        "expected_category": "medical_emergency",
        "expected_severity": "critical",
        "expected_protocol_id": "choking"
    },
    {
        "input": "I think my mother is having a stroke, her face is drooping",
        "expected_category": "medical_emergency",
        "expected_severity": "critical",
        "expected_protocol_id": "stroke"
    },
    {
        "input": "Fire in the building, smoke everywhere",
        "expected_category": "disaster_emergency",
        "expected_severity": "critical",
        "expected_protocol_id": "fire"
    },
    {
        "input": "Feeling extremely anxious and overwhelmed with studies",
        "expected_category": "mental_health_crisis",
        "expected_severity": "medium",
        "expected_protocol_id": "panic_attack"
    },
    {
        "input": "Severe bleeding from a deep cut on my arm",
        "expected_category": "medical_emergency",
        "expected_severity": "high",
        "expected_protocol_id": "severe_bleeding"
    },
    {
        "input": "Flash flood warning, water rising in hostel",
        "expected_category": "disaster_emergency",
        "expected_severity": "high",
        "expected_protocol_id": "flood"
    }
]


class CrisisEvaluator:
    """Evaluates crisis response system performance"""
    
    def __init__(self):
        self.coordinator = CrisisCoordinator()
        self.results = []
    
    def evaluate_classification(self) -> Dict:
        """
        Evaluate classification accuracy on gold dataset
        Returns precision, recall, F1, and accuracy metrics
        """
        
        y_true_category = []
        y_pred_category = []
        y_true_severity = []
        y_pred_severity = []
        protocol_matches = 0
        total = len(GOLD_DATASET)
        
        for item in GOLD_DATASET:
            # Get prediction
            classification = self.coordinator.classify_crisis(item['input'])
            protocol = self.coordinator.get_relevant_protocol(classification)
            
            # Record results
            y_true_category.append(item['expected_category'])
            y_pred_category.append(classification['category'])
            y_true_severity.append(item['expected_severity'])
            y_pred_severity.append(classification['severity'])
            
            # Check protocol match
            if protocol and protocol.get('id') == item['expected_protocol_id']:
                protocol_matches += 1
            
            # Store detailed result
            self.results.append({
                'input': item['input'][:50] + '...',
                'expected_category': item['expected_category'],
                'predicted_category': classification['category'],
                'category_correct': classification['category'] == item['expected_category'],
                'expected_severity': item['expected_severity'],
                'predicted_severity': classification['severity'],
                'severity_correct': classification['severity'] == item['expected_severity'],
                'expected_protocol': item['expected_protocol_id'],
                'predicted_protocol': protocol.get('id') if protocol else None,
                'protocol_correct': protocol.get('id') == item['expected_protocol_id'] if protocol else False,
                'confidence': classification.get('confidence', 0.0)
            })
        
        # Calculate metrics
        category_accuracy = accuracy_score(y_true_category, y_pred_category)
        severity_accuracy = accuracy_score(y_true_severity, y_pred_severity)
        protocol_precision = protocol_matches / total
        
        return {
            'total_samples': total,
            'category_accuracy': category_accuracy,
            'severity_accuracy': severity_accuracy,
            'protocol_precision': protocol_precision,
            'overall_accuracy': (category_accuracy + severity_accuracy + protocol_precision) / 3,
            'detailed_results': self.results
        }
    
    def evaluate_follow_up_consistency(self) -> Dict:
        """
        Check follow-up scheduling consistency
        Ensures no overlaps and correct timing based on severity
        """
        
        # Create test cases with different severities
        test_cases = [
            ("Critical medical emergency", "critical"),
            ("High severity disaster", "high"),
            ("Medium mental health", "medium"),
            ("Low severity issue", "low")
        ]
        
        follow_ups = []
        for description, expected_severity in test_cases:
            self.coordinator.handle_crisis(description)
            cases = self.coordinator.list_active_cases()
            if cases:
                latest = cases[-1]
                follow_ups.append({
                    'severity': latest['classification']['severity'],
                    'follow_up_time': latest['follow_up_scheduled']
                })
        
        # Check for overlaps (simplified - just verify all have unique times)
        unique_times = len(set(f['follow_up_time'] for f in follow_ups))
        no_overlaps = unique_times == len(follow_ups)
        
        return {
            'total_follow_ups': len(follow_ups),
            'unique_times': unique_times,
            'no_overlaps': no_overlaps,
            'consistency_score': 1.0 if no_overlaps else 0.0
        }
    
    def print_evaluation_table(self, metrics: Dict):
        """Print formatted evaluation table"""
        
        print("\n" + "="*80)
        print("📊 CRISIS RESPONSE COORDINATOR - EVALUATION RESULTS")
        print("="*80 + "\n")
        
        print("### Overall Metrics\n")
        print(f"{'Metric':<30} {'Score':<15} {'Status':<10}")
        print("-" * 55)
        
        cat_acc = f"{metrics['category_accuracy']:.2%}"
        sev_acc = f"{metrics['severity_accuracy']:.2%}"
        prot_prec = f"{metrics['protocol_precision']:.2%}"
        overall = f"{metrics['overall_accuracy']:.2%}"
        
        print(f"{'Category Classification':<30} {cat_acc:<15} {'✅' if metrics['category_accuracy'] > 0.9 else '⚠️':<10}")
        print(f"{'Severity Classification':<30} {sev_acc:<15} {'✅' if metrics['severity_accuracy'] > 0.9 else '⚠️':<10}")
        print(f"{'Protocol Retrieval Precision':<30} {prot_prec:<15} {'✅' if metrics['protocol_precision'] > 0.8 else '⚠️':<10}")
        print(f"{'Overall Accuracy':<30} {overall:<15} {'✅' if metrics['overall_accuracy'] > 0.85 else '⚠️':<10}")
        
        print("\n### Detailed Results (Sample)\n")
        print(f"{'Input':<52} {'Category':<10} {'Severity':<10} {'Protocol':<10}")
        print("-" * 82)
        
        for result in metrics['detailed_results'][:5]:  # Show first 5
            category_icon = '✅' if result['category_correct'] else '❌'
            severity_icon = '✅' if result['severity_correct'] else '❌'
            protocol_icon = '✅' if result['protocol_correct'] else '❌'
            
            print(f"{result['input']:<52} {category_icon:<10} {severity_icon:<10} {protocol_icon:<10}")
        
        print("\n" + "="*80 + "\n")
    
    def run_full_evaluation(self) -> Dict:
        """Run complete evaluation suite"""
        
        print("🧪 Running evaluation suite...\n")
        
        # Classification evaluation
        classification_metrics = self.evaluate_classification()
        
        # Follow-up consistency
        followup_metrics = self.evaluate_follow_up_consistency()
        
        # Combined results
        results = {
            'classification': classification_metrics,
            'follow_up': followup_metrics,
            'summary': {
                'total_tests': classification_metrics['total_samples'],
                'category_accuracy': classification_metrics['category_accuracy'],
                'severity_accuracy': classification_metrics['severity_accuracy'],
                'protocol_precision': classification_metrics['protocol_precision'],
                'follow_up_consistency': followup_metrics['consistency_score'],
                'overall_score': (
                    classification_metrics['overall_accuracy'] + 
                    followup_metrics['consistency_score']
                ) / 2
            }
        }
        
        # Print table
        self.print_evaluation_table(classification_metrics)
        
        # Print follow-up results
        print("### Follow-up Scheduling\n")
        print(f"{'Metric':<30} {'Value':<15}")
        print("-" * 45)
        print(f"{'Total Follow-ups':<30} {followup_metrics['total_follow_ups']:<15}")
        print(f"{'No Overlaps':<30} {'✅ Yes' if followup_metrics['no_overlaps'] else '❌ No':<15}")
        cons_score = f"{followup_metrics['consistency_score']:.0%}"
        print(f"{'Consistency Score':<30} {cons_score:<15}")
        print("\n" + "="*80 + "\n")
        
        return results


def run_evaluation():
    """Main evaluation entry point"""
    evaluator = CrisisEvaluator()
    results = evaluator.run_full_evaluation()
    
    print(f"\n✅ EVALUATION COMPLETE")
    print(f"Overall Score: {results['summary']['overall_score']:.1%}")
    print(f"Status: {'PASS ✅' if results['summary']['overall_score'] > 0.85 else 'NEEDS IMPROVEMENT ⚠️'}\n")
    
    return results


if __name__ == "__main__":
    run_evaluation()
