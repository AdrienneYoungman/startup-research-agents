def format_migration():
    with open('supabase/migrations/20240321000007_remove_not_null_constraint.sql', 'r') as f:
        sql = f.read()
    
    print("\nCopy and paste the following SQL into the Supabase SQL Editor:\n")
    print("=" * 80)
    print(sql)
    print("=" * 80)
    print("\nInstructions:")
    print("1. Go to the Supabase dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Create a new query")
    print("4. Paste the SQL above")
    print("5. Click 'Run' to execute the migration")
    print("\nAfter running, you should see a list of all columns in the founder_inputs table.")

if __name__ == "__main__":
    format_migration() 