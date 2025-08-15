import os
from supabase import create_client, Client
from dotenv import load_dotenv

def apply_migration():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase URL or anon key in environment variables")
    
    # Initialize Supabase client
    supabase: Client = create_client(url, key)
    
    # Read migration file
    with open('supabase/migrations/20240320000000_create_tables.sql', 'r') as f:
        migration_sql = f.read()
    
    try:
        # Execute migration
        result = supabase.rpc('exec_sql', {'sql': migration_sql}).execute()
        print("Migration applied successfully!")
        return result
    except Exception as e:
        print(f"Error applying migration: {str(e)}")
        raise

if __name__ == "__main__":
    apply_migration() 