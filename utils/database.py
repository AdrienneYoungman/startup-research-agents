from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json
from datetime import datetime

class DatabaseService:
    def __init__(self):
        load_dotenv()
        url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise Exception("Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY in environment variables")
        
        self.supabase: Client = create_client(url, key)
        
        # Force schema refresh by running a simple query
        try:
            self.supabase.table('founder_inputs').select('id').limit(1).execute()
        except Exception as e:
            print(f"Schema refresh query failed: {str(e)}")
            # Continue anyway as this might be the first time the table is being created
    
    def create_founder(self, email: str, password_hash: bytes) -> None:
        """Create a new founder account"""
        self.supabase.table('founders').insert({
            'email': email,
            'password_hash': password_hash.hex(),
            'created_at': datetime.now().isoformat()
        }).execute()
    
    def get_founder(self, email: str) -> dict:
        """Get founder by email"""
        response = self.supabase.table('founders').select('*').eq('email', email).execute()
        if response.data:
            # Convert hex string back to bytes
            response.data[0]['password_hash'] = bytes.fromhex(response.data[0]['password_hash'])
            return response.data[0]
        return None
    
    def save_session(self, session_data: dict) -> str:
        """Save session data to database"""
        response = self.supabase.table('sessions').insert(session_data).execute()
        return response.data[0]['session_id']
    
    def get_session(self, session_id: str) -> dict:
        """Get session data from database"""
        response = self.supabase.table('sessions').select('*').eq('session_id', session_id).execute()
        return response.data[0] if response.data else None
    
    def save_responses(self, session_id: str, responses: list) -> None:
        """Save interview responses to database"""
        self.supabase.table('responses').insert({
            'session_id': session_id,
            'responses': json.dumps(responses),
            'created_at': datetime.now().isoformat()
        }).execute()
    
    def get_responses(self, session_id: str) -> list:
        """Get interview responses from database"""
        response = self.supabase.table('responses').select('*').eq('session_id', session_id).execute()
        if response.data:
            return json.loads(response.data[0]['responses'])
        return []
    
    def save_tester_info(self, session_id: str, email: str, opt_in: bool, gdpr_consent: bool) -> None:
        """Save tester information and preferences"""
        self.supabase.table('testers').insert({
            'session_id': session_id,
            'email': email,
            'opt_in': opt_in,
            'gdpr_consent': gdpr_consent,
            'created_at': datetime.now().isoformat()
        }).execute()
    
    def get_tester_info(self, session_id: str) -> dict:
        """Get tester information"""
        response = self.supabase.table('testers').select('*').eq('session_id', session_id).execute()
        return response.data[0] if response.data else None
    
    def save_analysis(self, session_id: str, analysis: dict) -> None:
        """Save analysis results to database"""
        self.supabase.table('analyses').insert({
            'session_id': session_id,
            'analysis': json.dumps(analysis),
            'created_at': datetime.now().isoformat()
        }).execute()
    
    def get_analysis(self, session_id: str) -> dict:
        """Get analysis results from database"""
        response = self.supabase.table('analyses').select('*').eq('session_id', session_id).execute()
        if response.data:
            return json.loads(response.data[0]['analysis'])
        return None
    
    def save_founder_inputs(self, founder_email: str, inputs: dict) -> dict:
        """Save founder inputs to the database"""
        try:
            # Validate required fields
            required_fields = ['problem_domain', 'problems', 'value_prop', 'target_action']
            for field in required_fields:
                if field not in inputs:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate field types
            if not isinstance(inputs['problems'], list):
                raise ValueError("Problems must be a list")
            
            # Validate problems list is not empty
            if not inputs['problems']:
                raise ValueError("Problems list cannot be empty")
            
            # Validate pricing information if it's a paid service
            if inputs.get('is_paid_service', False):
                if not inputs.get('pricing_model'):
                    raise ValueError("Pricing model is required for paid services")
                if not inputs.get('price_points'):
                    raise ValueError("At least one price point is required for paid services")
                if not isinstance(inputs['price_points'], list):
                    raise ValueError("Price points must be a list")
                if not all(isinstance(price, (int, float)) for price in inputs['price_points']):
                    raise ValueError("Price points must be numbers")
            
            # Prepare data for insertion
            data = {
                'founder_email': founder_email,
                'problem_domain': inputs['problem_domain'],
                'problems': inputs['problems'],
                'value_prop': inputs['value_prop'],
                'target_action': inputs['target_action'],
                'follow_up_action': inputs.get('follow_up_action', ''),
                'is_paid_service': inputs.get('is_paid_service', False),
                'pricing_model': inputs.get('pricing_model', ''),
                'price_points': inputs.get('price_points', []),
                'pricing_questions': inputs.get('pricing_questions', [])
            }
            
            # Insert or update founder inputs
            response = self.supabase.table('founder_inputs').upsert(
                data,
                on_conflict='founder_email'
            ).execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error saving founder inputs: {str(e)}")
            raise

    def get_founder_inputs(self, founder_email: str) -> Optional[Dict]:
        """Get the most recent founder inputs for a given email."""
        result = self.supabase.table("founder_inputs") \
            .select("*") \
            .eq("founder_email", founder_email) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        if not result.data:
            return None
            
        return result.data[0]["inputs"] 