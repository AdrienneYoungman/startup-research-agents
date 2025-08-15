from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import requests
import openai

class InterviewAgent:
    def __init__(self, session_id: str, session_data: Dict):
        self.session_id = session_id
        self.session_data = session_data
        self.responses = []
        self.current_problem_index = 0
        self.last_user_response = None
        self.stage = "domain_question"
        self.current_problem = None
        self.is_waiting_for_scale = False

        # Validate founder inputs
        founder_inputs = self.session_data.get("founder_inputs", {})
        required_fields = {
            "problem_domain": str,
            "problems": list,
            "value_prop": str,
            "target_action": str
        }
        missing = [f for f in required_fields if f not in founder_inputs]
        if missing:
            raise ValueError(f"Missing required fields in founder inputs: {', '.join(missing)}")
        for field, expected_type in required_fields.items():
            if not isinstance(founder_inputs[field], expected_type):
                raise ValueError(f"Field '{field}' must be of type {expected_type.__name__}")
        if not founder_inputs["problems"]:
            raise ValueError("Problems list cannot be empty")

        # Load config
        script_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'interview_script.json')
        chatgpt_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'chatgpt_config.json')
        with open(script_path, 'r') as f:
            self.interview_script = json.load(f)
        with open(chatgpt_path, 'r') as f:
            self.chatgpt_config = json.load(f)

        # Set up OpenAI config
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.project_id = os.getenv('OPENAI_PROJECT_ID')
        if not self.api_key or not self.project_id:
            raise Exception("Missing OPENAI_API_KEY or OPENAI_PROJECT_ID in environment variables")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Project": self.project_id
        }

        # Check OpenAI connection
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={"model": "gpt-4", "messages": [{"role": "system", "content": "Test connection"}], "max_tokens": 5},
                timeout=10
            )
            if response.status_code != 200:
                raise Exception(response.json().get('error', {}).get('message', 'Unknown error'))
        except Exception as e:
            raise Exception(f"OpenAI API connection failed: {str(e)}")

        self.messages = [{"role": "system", "content": self._create_system_prompt()}]

    def _create_system_prompt(self) -> str:
        founder_inputs = self.session_data['founder_inputs']
        prompt = f"""You are an AI research assistant conducting user interviews using The Mom Test.

Your role:
- Ask about past behavior
- Avoid hypotheticals
- Focus on specific experiences
- Dig deeper when needed

The founder is working on a solution in this space:
{founder_inputs['problem_domain']}

Problems to test:
{chr(10).join(f"- {p}" for p in founder_inputs['problems'])}

Value prop:
{founder_inputs['value_prop']}

Target action:
{founder_inputs['target_action']}

Follow-up action:
{founder_inputs.get('follow_up_action', 'N/A')}"""

        if founder_inputs.get('is_paid_service'):
            prompt += f"""

This is a paid service. Pricing model: {founder_inputs.get('pricing_model', 'unspecified')}
Price points to test:
{chr(10).join(f"- ${p:.2f}" for p in founder_inputs.get('price_points', []))}

Pricing questions:
{chr(10).join(f"- {q}" for q in founder_inputs.get('pricing_questions', []))}

Tips:
- Ask about current spend
- Understand their budget
- Gauge reactions to price points
- Explore decision-making process
"""
        return prompt

    def _get_chatgpt_response(self):
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                stream=True,
                temperature=0.7,
                max_tokens=500
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Error getting ChatGPT response: {str(e)}")
            yield "I apologize, but I'm having trouble processing your response. Could you please try again?"

    def start_interview(self) -> str:
        problems = self.session_data['founder_inputs']['problems']
        
        if not problems:
            return "No problems provided by the founder. Please go back and add at least one."

        self.current_problem = problems[self.current_problem_index]
        domain = self.session_data['founder_inputs'].get('problem_domain', 'this space')
        self.stage = "domain_question"

        # Only include system prompt in GPT message history for now
        self.messages = [
            {"role": "system", "content": self._create_system_prompt()}
        ]

        # Prepare both intro and context question for UI display
        intro = self.interview_script["intro"]
        context_question = self.interview_script["context_question"].replace("{domain}", domain)

        # Return both together (your app will show this as the assistant's first message)
        return f"{intro}\n\n{context_question}"

    def get_response(self, user_input: str) -> str:
        try:
            self.last_user_response = user_input.strip()
            self.messages.append({"role": "user", "content": user_input})

            if self.stage == "domain_question":
                self.stage = "problem_intro"
                prompt = self.interview_script["problem_statement_intro"]
                self.messages.append({"role": "assistant", "content": prompt})
                return prompt

            elif self.stage == "problem_intro":
                self.stage = "problem_resonance"
                problem_text = self.current_problem
                prompt = self.interview_script["problem_validation"]["resonance_prompt"].replace("{problem_statement}", problem_text)
                self.messages.append({"role": "assistant", "content": prompt})
                return prompt

            elif self.stage == "problem_resonance":
                try:
                    score = int(self.last_user_response.strip())
                    if score < 1 or score > 5:
                        raise ValueError
                    self.resonance_score = score
                    self.record_response({
                        "type": "problem_resonance",
                        "problem": self.current_problem,
                        "resonance_score": score
                    })
                except ValueError:
                    clarification = "Could you please give a number from 1 to 5 to show how much this resonates with your experience?"
                    self.messages.append({"role": "assistant", "content": clarification})
                    return clarification

                self.stage = "problem_explanation"
                prompt = self.interview_script["problem_validation"]["explanation_prompt"]
                self.messages.append({"role": "assistant", "content": prompt})
                return prompt

            elif self.stage == "problem_explanation":
                self.record_response({
                    "type": "problem_explanation",
                    "text": self.last_user_response
                })

                if self.resonance_score >= 3:
                    self.stage = "value_prop"
                    prompt = self.interview_script["problem_validation"]["action_prompt"]
                    self.messages.append({"role": "assistant", "content": prompt})
                    return prompt
                else:
                    self.stage = "value_prop"

            if self.stage == "value_prop":
                self.record_response({
                    "type": "value_prop_interest",
                    "value_prop": self.session_data['founder_inputs'].get('value_prop', ''),
                    "action": self.session_data['founder_inputs'].get('target_action', ''),
                    "response": self.last_user_response
                })

                self.stage = "price_test"
                target_action = self.session_data['founder_inputs'].get('target_action', 'sign up')
                value_prop = self.session_data['founder_inputs'].get('value_prop', 'a product that solves the problem')
                prompt = self.interview_script["value_prop_test"]["pitch_prompt"].replace("{value_prop}", value_prop).replace("{target_action}", target_action)
                self.messages.append({"role": "assistant", "content": prompt})
                return prompt

            elif self.stage == "price_test":
                if "buy" in self.session_data['founder_inputs'].get('target_action', '').lower():
                    self.record_response({
                        "type": "price_sensitivity",
                        "response": self.last_user_response
                    })
                    prompt = self.interview_script["value_prop_test"]["price_prompt"]
                    self.messages.append({"role": "assistant", "content": prompt})
                    return prompt
                self.stage = "intent"

            if self.stage == "intent":
                follow_up = self.session_data['founder_inputs'].get('follow_up_action', 'get early access')
                prompt = self.interview_script["intent_prompt"].replace("{follow_up_action}", follow_up)

                self.record_response({
                    "type": "opt_in_intent",
                    "response": self.last_user_response
                })

                self.stage = "closing"
                self.messages.append({"role": "assistant", "content": prompt})
                return prompt

            elif self.stage == "closing":
                self.stage = "complete"
                self.messages.append({"role": "assistant", "content": self.interview_script["closing"]})

                summary = self.get_summary_from_gpt()
                self.record_response({"type": "interview_summary", "summary": summary})

                self.current_problem_index += 1
                problems = self.session_data['founder_inputs'].get('problems', [])

                if self.current_problem_index < len(problems):
                    self.current_problem = problems[self.current_problem_index]
                    self.stage = "problem_intro"

                    transition = f"Thanks for that. Let's look at the next one — this is {self.current_problem_index + 1} of {len(problems)}."
                    prompt = self.interview_script["problem_statement_intro"]
                    self.messages.append({"role": "assistant", "content": transition})
                    self.messages.append({"role": "assistant", "content": prompt})
                    return f"{transition}\n\n{prompt}"
                else:
                    closing_message = "That's all for now — thanks so much for your time and thoughtful answers. You've really helped the founder understand which problems matter most."
                    self.messages.append({"role": "assistant", "content": closing_message})
                    return closing_message

        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            return "I apologize, but I'm having trouble processing your response. Could you please try again?"

    def record_response(self, response_data: Dict) -> None:
        response_data["timestamp"] = datetime.now().isoformat()
        self.responses.append(response_data)

    def export_responses(self) -> str:
        return json.dumps({
            "session_id": self.session_id,
            "founder_inputs": self.session_data['founder_inputs'],
            "responses": self.responses,
            "completed_at": datetime.now().isoformat()
        }, indent=2)

    def is_complete(self) -> bool:
        return self.current_problem_index >= len(self.session_data['founder_inputs'].get('problems', []))

    def current_problem_number(self) -> str:
        total = len(self.session_data['founder_inputs'].get('problems', []))
        return f"{self.current_problem_index + 1} of {total}"

    def get_summary_from_gpt(self) -> str:
        self.messages.append({
            "role": "user",
            "content": "Based on this interview, summarize the key problems, actions taken, and reactions to the solution in one founder-friendly paragraph."
        })
        summary_text = ""
        for chunk in self._get_chatgpt_response():
            summary_text += chunk
        return summary_text.strip()

    def get_summary(self) -> Dict:
        problems = self.session_data['founder_inputs']['problems']
        return {
            "session_id": self.session_id,
            "total_problems": len(problems),
            "total_responses": len(self.responses),
            "problem_responses": sum(1 for r in self.responses if 'problem' in r),
            "final_willingness": sum(1 for r in self.responses if r.get('type') == 'final_willingness'),
            "start_time": self.responses[0]['timestamp'] if self.responses else None,
            "end_time": self.responses[-1]['timestamp'] if self.responses else None
        }