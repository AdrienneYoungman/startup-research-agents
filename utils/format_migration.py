def format_migration():
    # Read migration file
    with open('supabase/migrations/20240320000000_create_tables.sql', 'r') as f:
        migration_sql = f.read()
    
    # Print formatted SQL
    print("\nCopy and paste the following SQL into your Supabase SQL editor:\n")
    print("```sql")
    print(migration_sql)
    print("```\n")
    print("Instructions:")
    print("1. Go to your Supabase dashboard")
    print("2. Click on 'SQL Editor' in the left sidebar")
    print("3. Click 'New Query'")
    print("4. Paste the SQL above")
    print("5. Click 'Run' to execute the migration")

if __name__ == "__main__":
    format_migration() 