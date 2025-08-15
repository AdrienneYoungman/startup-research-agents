from typing import Dict, List, Optional
import json
from datetime import datetime
import openai
from dotenv import load_dotenv
import os

class AnalysisAgent:
    def __init__(self, session_id: str, interview_data: Dict):
        load_dotenv()
        self.session_id = session_id
        self.interview_data = interview_data
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def analyze_responses(self) -> Dict:
        """Analyze interview responses using ChatGPT"""
        # Prepare the prompt for analysis
        prompt = self._prepare_analysis_prompt()
        
        # Get analysis from ChatGPT
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert startup researcher analyzing user interview responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse and structure the analysis
        analysis = self._parse_analysis(response.choices[0].message.content)
        return analysis
    
    def _prepare_analysis_prompt(self) -> str:
        """Prepare the prompt for ChatGPT analysis"""
        founder_inputs = self.interview_data['founder_inputs']
        responses = self.interview_data['responses']
        
        prompt = f"""
        Analyze these user interview responses for a startup idea:
        
        Startup Idea: {founder_inputs['idea_summary']}
        Target User: {founder_inputs['target_user']}
        Problem: {founder_inputs['problem_statement']}
        
        Interview Responses:
        {json.dumps(responses, indent=2)}
        
        Please provide:
        1. Key insights about the problem and solution
        2. Validation signals (positive and negative)
        3. Suggested next steps for the founder
        4. Potential risks or concerns
        """
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse the ChatGPT analysis into a structured format"""
        # This is a simple parser - in a real implementation, you might want to use
        # more sophisticated parsing or ask ChatGPT to return JSON directly
        sections = analysis_text.split('\n\n')
        
        return {
            "session_id": self.session_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "key_insights": sections[0] if len(sections) > 0 else "",
            "validation_signals": sections[1] if len(sections) > 1 else "",
            "next_steps": sections[2] if len(sections) > 2 else "",
            "risks": sections[3] if len(sections) > 3 else ""
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive report using ChatGPT"""
        analysis = self.analyze_responses()
        
        prompt = f"""
        Create a professional research report based on this analysis:
        
        {json.dumps(analysis, indent=2)}
        
        Include:
        1. Executive Summary
        2. Methodology
        3. Key Findings
        4. Recommendations
        5. Next Steps
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional research analyst creating a startup research report."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content 