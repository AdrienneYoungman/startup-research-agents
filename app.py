import streamlit as st
from agents.founder_agent import FounderAgent
from agents.interview_agent import InterviewAgent
from agents.analysis_agent import AnalysisAgent
from utils.database import DatabaseService
import json
from datetime import datetime
import secrets
import re
import hashlib
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIREMENTS = {
    "uppercase": r'[A-Z]',
    "lowercase": r'[a-z]',
    "number": r'[0-9]',
    "special": r'[!@#$%^&*(),.?":{}|<>]'
}

def validate_password(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    for requirement, pattern in PASSWORD_REQUIREMENTS.items():
        if not re.search(pattern, password):
            return False, f"Password must contain at least one {requirement} character"
    return True, ""

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + key

def verify_password(stored_password, provided_password):
    salt = stored_password[:32]
    stored_key = stored_password[32:]
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return key == stored_key

def update_founder_inputs_to_session(**kwargs):
    if 'founder_inputs' not in st.session_state:
        st.session_state.founder_inputs = {
            'problem_domain': '',
            'problems': [],
            'value_prop': '',
            'target_action': '',
            'follow_up_action': '',
            'is_paid_service': False,
            'pricing_model': '',
            'price_points': [],
            'pricing_questions': []
        }
    st.session_state.founder_inputs = {**st.session_state.founder_inputs, **kwargs}

def main():
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseService()
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'founder_email' not in st.session_state:
        st.session_state.founder_email = None

    session_id = st.query_params.get("session_id", None)

    if session_id:
        st.session_state.current_session_id = session_id
        interview_page()
    else:
        if not st.session_state.is_admin:
            founder_auth_page()
        else:
            admin_pages()

    # 👇 Dev tools — always available
    st.sidebar.markdown("### 🛠 Dev Tools")
    if st.sidebar.button("🔄 Clear Session"):
        st.session_state.clear()
        st.rerun()

def founder_auth_page():
    st.title("Founder Login or Sign Up")

    # Optional debug display
    st.write("DEBUG: founder_email =", st.session_state.get("founder_email"))
    st.write("DEBUG: is_admin =", st.session_state.get("is_admin"))

    # ✅ Handle internal logout without query params
    if st.session_state.get("force_logout", False):
        st.session_state.clear()
        st.rerun()

    # ✅ Fully logged in → go to admin
    if st.session_state.get("founder_email") and st.session_state.get("is_admin"):
        st.success(f"Logged in as {st.session_state['founder_email']}")
        admin_pages()
        return

    # ✅ Partially logged in → allow continue or logout
    if st.session_state.get("founder_email") and not st.session_state.get("is_admin"):
        st.success(f"Logged in as {st.session_state['founder_email']}")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Continue to Admin"):
                st.session_state.is_admin = True
                st.rerun()

        with col2:
            if st.button("Log out"):
                st.session_state.force_logout = True
                st.rerun()
        return

    # ✅ Show login and signup
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                db = DatabaseService()
                founder = db.get_founder(email)
                if founder and verify_password(founder['password_hash'], password):
                    st.session_state.clear()
                    st.session_state.founder_email = email
                    st.session_state.is_admin = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

    with tab_signup:
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        if st.button("Create Account"):
            valid, msg = validate_password(new_password)
            if not valid:
                st.error(msg)
            else:
                try:
                    db = DatabaseService()
                    existing = db.get_founder(new_email)
                    if existing:
                        st.error("Account already exists.")
                    else:
                        hashed_pw = hash_password(new_password)
                        db.create_founder_account(new_email, hashed_pw)
                        st.success("Account created. Please log in.")
                        st.session_state["login_email"] = new_email
                        st.rerun()
                except Exception as e:
                    st.error(f"Sign-up error: {str(e)}")

def admin_pages():
    st.title("Mom Test Admin")
    
    # Initialize agents if needed
    if 'founder_agent' not in st.session_state:
        st.session_state.founder_agent = None
    if 'interview_agent' not in st.session_state:
        st.session_state.interview_agent = None
    if 'analysis_agent' not in st.session_state:
        st.session_state.analysis_agent = None
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Founder Input", "Analysis"]
    )
    
    if page == "Founder Input":
        founder_inputs_page()
    else:
        analysis_page()

def founder_inputs_page():
    st.title("Founder Inputs")
    
    # Initialize session state for form data if not exists
    if 'founder_inputs' not in st.session_state:
        update_founder_inputs_to_session(
            problem_domain='',
            problems=[],
            value_prop='',
            target_action='',
            follow_up_action='',
            is_paid_service=False,
            pricing_model='',
            price_points=[],
            pricing_questions=[]
        )
    
    # Problem Domain
    problem_domain = st.text_input(
        "What industry or area are you focusing on?",
        value=st.session_state.founder_inputs['problem_domain'],
        help="Example: Leadership Coaching, User Research, AI Automation etc."
    )
    
    # Problems List
    st.write("### What specific problems are you solving?")
    st.write("Describe up to 3 key problems your target users face. Be specific about their pain points.")
    problems = []
    for i in range(3):  # Allow up to 3 problems
        problem = st.text_input(
            f"Problem {i+1}",
            value=st.session_state.founder_inputs['problems'][i] if i < len(st.session_state.founder_inputs['problems']) else '',
            key=f"problem_{i}",
            help="Example: 'Founders don\'t get truly honest feedback on their ideas because their friends 'like' them and therefore lie. :)'"
        )
        if problem:
            problems.append(problem)
    
    # Value Proposition
    value_prop = st.text_area(
        "What product / service do you offer and what makes it compelling??",
        value=st.session_state.founder_inputs['value_prop'],
        help="Explain how your product or service addresses the problems you identified above"
    )
    
    # Pricing Section
    st.write("### Pricing Information")
    is_paid_service = st.checkbox(
        "Is this a paid service?",
        value=st.session_state.founder_inputs['is_paid_service'],
        help="Check this if you want to test willingness to pay"
    )
    
    pricing_model = ""
    if is_paid_service:
        pricing_model = st.selectbox(
            "What is your pricing model?",
            options=["Subscription", "One-time", "Freemium", "Usage-based", "Other"],
            index=0 if st.session_state.founder_inputs['pricing_model'] == '' else 
                ["Subscription", "One-time", "Freemium", "Usage-based", "Other"].index(
                    st.session_state.founder_inputs['pricing_model']
                ),
            help="Select the pricing model you plan to use",
            key="pricing_model"
        )
    
    st.write("### Price Points to Test")
    st.write("Enter up to 3 different price points you'd like to test")
    price_points = []
    for i in range(3):
        price = st.number_input(
            f"Price Point {i+1}",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            value=st.session_state.founder_inputs['price_points'][i] if i < len(st.session_state.founder_inputs['price_points']) else 0.0,
            key=f"price_{i}",
            help="Enter the price amount"
        )
        if price > 0:
            price_points.append(price)
    
    st.write("### Action / Willingness to Act Questions")
    st.write("Add questions to test willingness to act")
    pricing_questions = []
    for i in range(2):
        question = st.text_input(
            f"Action Question {i+1}",
            value=st.session_state.founder_inputs['pricing_questions'][i] if i < len(st.session_state.founder_inputs['pricing_questions']) else '',
            key=f"action_question_{i}",
            help="Example: 'Would you be willing to take action X for this solution?'"
        )
        if question:
            pricing_questions.append(question)
    
    # Target Action
    target_action = st.text_input(
        "What action do you want users to take?",
        value=st.session_state.founder_inputs['target_action'],
        help="Example: 'Sign up for early access', 'Schedule a demo', 'Download the app'"
    )
    
    # Follow-up Action (Optional)
    follow_up_action = st.text_input(
        "What's the next step after the initial action? (Optional)",
        value=st.session_state.founder_inputs['follow_up_action'],
        help="Example: 'Complete onboarding', 'Invite team members', 'Start free trial'"
    )
    
    # Submit Button
    if st.button("Create Interview Session"):
        # Validate inputs
        if not problem_domain.strip():
            st.error("Please specify the industry or area you're focusing on")
            return
        
        if not problems:
            st.error("Please describe at least one problem you're solving")
            return
        
        if not value_prop.strip():
            st.error("Please explain how your solution addresses these problems")
            return
        
        if not target_action.strip():
            st.error("Please specify what action you want users to take")
            return
        
        if is_paid_service and not price_points:
            st.error("Please specify at least one price point to test")
            return
        
        # Save inputs to session state
        st.session_state.founder_inputs = {
            'problem_domain': problem_domain,
            'problems': problems,
            'value_prop': value_prop,
            'target_action': target_action,
            'follow_up_action': follow_up_action,
            'is_paid_service': is_paid_service,
            'pricing_model': pricing_model,
            'price_points': price_points,
            'pricing_questions': pricing_questions
        }
        
        try:
            # Save to database
            db = DatabaseService()
            db.save_founder_inputs(st.session_state.founder_email, st.session_state.founder_inputs)
            
            # Generate session URL
            session_id = str(uuid.uuid4())
            st.session_state.session_id = session_id
            
            # Save session
            db.save_session({
                'session_id': session_id,
                'founder_email': st.session_state.founder_email,
                'founder_inputs': json.dumps(st.session_state.founder_inputs),
                'created_at': datetime.now().isoformat()
            })
            
            # Show success message and URL
            st.success("✅ Interview session created successfully!")
            st.write("Share this link with your testers:")
            st.code(f"http://localhost:8502/?session_id={session_id}")
            
        except Exception as e:
            st.error(f"Error saving founder inputs: {str(e)}")

def interview_page():
    st.title("Chat with MomBot")
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Get session data
    try:
        session_data = st.session_state.db.get_session(st.session_state.current_session_id)
        
        if session_data and 'founder_inputs' in session_data:
            # Initialize interview agent if not already done
            if 'interview_agent' not in st.session_state:
                # Ensure founder_inputs is properly formatted
                if isinstance(session_data['founder_inputs'], str):
                    session_data['founder_inputs'] = json.loads(session_data['founder_inputs'])
                
                # Initialize the interview agent with the correct arguments
                st.session_state.interview_agent = InterviewAgent(
                    session_id=st.session_state.current_session_id,
                    session_data=session_data
                )
                
                # Add initial message to chat history
                initial_message = st.session_state.interview_agent.start_interview()
                st.session_state.chat_history = [{
                    "role": "assistant",
                    "content": initial_message
                }]
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            # Chat input with error handling
            try:
                if prompt := st.chat_input("Type your response here..."):
                    # Add user message to chat history
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # Get and display assistant response with streaming
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        # Get streaming response from interview agent
                        for response_chunk in st.session_state.interview_agent.get_response(prompt):
                            full_response += response_chunk
                            message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Chat error: {e}")
                
                # Check if interview is complete
                if st.session_state.interview_agent.is_complete():
                    # Show email collection and opt-in form
                    with st.form("tester_info"):
                        st.write("### Thank you for completing the interview!")
                        email = st.text_input("Email (optional)", help="Add your email if you'd like to be contacted about the results")
                        opt_in = st.checkbox(
                            "I'd like to receive opportunities to participate in paid research for other founders",
                            help="By checking this box, you agree to receive occasional emails about paid research opportunities"
                        )
                        gdpr_consent = st.checkbox(
                            "I consent to my data being processed in accordance with GDPR guidelines",
                            help="Your data will be stored securely and you can request its deletion at any time"
                        )
                        
                        if st.form_submit_button("Submit"):
                            if email or opt_in:
                                try:
                                    st.session_state.db.save_tester_info(
                                        st.session_state.current_session_id,
                                        email,
                                        opt_in,
                                        gdpr_consent
                                    )
                                    st.success("Thank you for your participation!")
                                except Exception as e:
                                    st.error(f"Error saving information: {str(e)}")
                            else:
                                st.success("Thank you for your participation!")
        else:
            st.error("Session data is incomplete. Please check the session ID or create a new session.")
    except Exception as e:
        st.error(f"Error retrieving session: {str(e)}")
        st.write("Debug info:")
        st.write(f"Session ID: {st.session_state.current_session_id}")
        st.write(f"Session data: {session_data if 'session_data' in locals() else 'Not loaded'}")

def analysis_page():
    st.header("Analysis")
    
    session_id = st.text_input("Enter Session ID")
    
    if session_id:
        # Load session data
        session_data = st.session_state.db.get_session(session_id)
        responses = st.session_state.db.get_responses(session_id)
        
        if not session_data or not responses:
            st.error("Session or responses not found")
            return
        
        interview_data = {
            "session_id": session_id,
            "founder_inputs": session_data["founder_inputs"],
            "responses": responses
        }
        
        if st.session_state.analysis_agent is None:
            st.session_state.analysis_agent = AnalysisAgent(session_id, interview_data)
        
        if st.button("Generate Analysis"):
            with st.spinner("Analyzing responses..."):
                analysis = st.session_state.analysis_agent.analyze_responses()
                st.session_state.db.save_analysis(session_id, analysis)
                
                st.write("### Key Insights")
                st.write(analysis["key_insights"])
                
                st.write("### Validation Signals")
                st.write(analysis["validation_signals"])
                
                st.write("### Next Steps")
                st.write(analysis["next_steps"])
                
                st.write("### Potential Risks")
                st.write(analysis["risks"])
        
        if st.button("Generate Full Report"):
            with st.spinner("Generating report..."):
                report = st.session_state.analysis_agent.generate_report()
                st.write(report)

def display_chat(interview_agent):
    """Display chat interface and handle user input"""
    st.title("User Interview")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Type your response here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get streaming response from interview agent
            for response_chunk in interview_agent.get_response(prompt):
                full_response += response_chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main() 