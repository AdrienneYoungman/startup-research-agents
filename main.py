from agents.founder_agent import FounderAgent
from agents.interview_agent import InterviewAgent
import json

def main():
    # Example usage of the Founder Agent
    print("=== Founder Agent Demo ===")
    founder_agent = FounderAgent()
    
    # Start the conversation
    print(founder_agent.start_conversation())
    
    # Collect founder inputs
    founder_inputs = {
    "idea_summary": "A mobile app that helps people track their daily water intake",
    "target_user": "busy professionals who want to stay hydrated",
    "problem_statements": [
        "people forget to drink enough water throughout the day",
        "people don’t realize when they’re dehydrated",
        "people don’t know how much water they actually need"
    ],
    "current_alternatives": "using water bottles with time markers or setting phone reminders",
    "validation_signal": "users report drinking more water consistently"
    }
    
    # Process founder inputs
    reflection = founder_agent.collect_founder_input(founder_inputs)
    print("\nFounder Agent:", reflection)
    
    # Generate questions
    questions = founder_agent.generate_questions()
    print("\nGenerated Questions:")
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
    
    # Create interview session
    session_data = founder_agent.create_interview_session()
    interview_link = founder_agent.get_interview_link()
    print(f"\nInterview Link: {interview_link}")
    
    # Example usage of the Interview Agent
    print("\n=== Interview Agent Demo ===")
    interview_agent = InterviewAgent(session_data['session_id'], session_data)
    
    # Start interview
    print(interview_agent.start_interview())
    
    # Simulate interview responses
    sample_responses = [
        "I usually forget to drink water when I'm in meetings",
        "The most frustrating part is feeling tired and realizing I haven't had water in hours",
        "I tried using a water bottle with time markers, but I kept forgetting to refill it",
        "I considered using a smart water bottle, but they're too expensive",
        "An ideal solution would be something that reminds me at the right times without being annoying",
        "I'd be willing to pay $5-10 per month for a good solution",
        "I'd switch if the solution was more convenient than my current method"
    ]
    
    # Record responses
    for response in sample_responses:
        question = interview_agent.get_next_question()
        if question:
            print(f"\nQ: {question}")
            print(f"A: {response}")
            interview_agent.record_response(response)
    
    # Export results
    print("\n=== Interview Results ===")
    print(interview_agent.export_responses())
    
    # Get summary
    summary = interview_agent.get_summary()
    print("\n=== Interview Summary ===")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main() 