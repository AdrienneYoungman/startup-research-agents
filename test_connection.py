from utils.database import DatabaseService
import streamlit as st

def test_connection():
    st.title("Database Connection Test")
    
    try:
        # Initialize database service
        db = DatabaseService()
        st.success("✅ Successfully connected to Supabase!")
        
        # Test tables
        st.subheader("Checking Database Tables")
        
        # Test sessions table
        try:
            db.supabase.table('sessions').select('count').execute()
            st.success("✅ Sessions table exists")
        except Exception as e:
            st.error(f"❌ Sessions table error: {str(e)}")
        
        # Test responses table
        try:
            db.supabase.table('responses').select('count').execute()
            st.success("✅ Responses table exists")
        except Exception as e:
            st.error(f"❌ Responses table error: {str(e)}")
        
        # Test analyses table
        try:
            db.supabase.table('analyses').select('count').execute()
            st.success("✅ Analyses table exists")
        except Exception as e:
            st.error(f"❌ Analyses table error: {str(e)}")
            
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")
        st.info("Please check your .env file and make sure your Supabase credentials are correct.")

if __name__ == "__main__":
    test_connection() 