from typing import Dict, List, Optional, Union
import uuid
import json
from datetime import datetime

class FounderAgent:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.founder_inputs: Dict[str, Union[str, List[str]]] = {}
        self.session_data = {}
        
    def start_conversation(self) -> str:
        return (
            "Hi! I'm your dedicated research agent. I'm here to help you validate or invalidate your ideas."
            " Ready to dive in?"
        )
    
    def collect_founder_input(self, inputs: Dict[str, Union[str, List[str]]]) -> str:
        """Collect and validate founder inputs"""
        required_fields = [
            "idea_summary",
            "target_user",
            "problems",
            "current_alternatives",
            "problem_severity",
            "validation_signal",
            "founder_name",
            "desired_action"
        ]
        
        # Validate all required fields are present
        missing_fields = [field for field in required_fields if field not in inputs]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate problems is a non-empty list
        if not isinstance(inputs["problems"], list) or not inputs["problems"]:
            return "The 'problems' field must be a non-empty list of strings."
        
        self.founder_inputs = inputs
        return self._generate_reflection()
    
    def _generate_reflection(self) -> str:
        """Generate a reflection of the founder's inputs"""
        problems = "\n- " + "\n- ".join(self.founder_inputs["problems"])
        return (
            f"Got it. So you're building {self.founder_inputs['idea_summary']} for "
            f"{self.founder_inputs['target_user']} to explore the following potential problems:{problems}.\n"
            f"Right now, your users are dealing with these using: {self.founder_inputs['current_alternatives']}.\n"
            f"You believe this is {self.founder_inputs['problem_severity']} for your target audience.\n"
            f"You'll consider the problem validated if: {self.founder_inputs['validation_signal']}.\n"
            "Is that correct?"
        )
    
    def create_interview_session(self) -> Dict:
        """Create and store the interview session data"""
        self.session_data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "founder_inputs": self.founder_inputs
        }
        return self.session_data
    
    def get_interview_link(self) -> str:
        """Generate instructions for accessing the interview"""
        return (
            f"To start the interview:\n"
            f"1. Go to the 'MomBot' page in the sidebar\n"
            f"2. Enter this Session ID: {self.session_id}\n"
            f"3. Click 'Submit' to begin the interview"
        )
    
    def export_session_data(self) -> str:
        """Export session data as JSON"""
        return json.dumps(self.session_data, indent=2)