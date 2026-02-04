"""
Setup Chin Hin database dengan full test data.
Run: python setup_database.py
"""
import sys
from pathlib import Path
from app.db.supabase_client import get_supabase_client

def run_migration(filename: str):
    """Run SQL migration file."""
    migration_path = Path(__file__).parent / "db" / "migrations" / filename
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {filename}")
        return False
    
    print(f"📂 Reading {filename}...")
    sql = migration_path.read_text(encoding="utf-8")
    
    print(f"🚀 Running {filename}...")
    supabase = get_supabase_client()
    
    try:
        # Execute via raw SQL (Supabase REST API limitation, so we'll try table by table)
        # For full migration, better run via Supabase SQL Editor
        # But we can verify tables exist after manual run
        result = supabase.rpc("exec", {"sql": sql}).execute()
        print(f"✅ {filename} completed!")
        return True
    except Exception as e:
        print(f"⚠️ Cannot run via REST API: {e}")
        print(f"💡 Please run this SQL in Supabase SQL Editor:")
        print(f"   https://supabase.com/dashboard/project/nlerjwllnvrpfujuxjnp/editor")
        print(f"\n📋 Copy from: {migration_path}")
        return False

def verify_setup():
    """Verify database tables exist."""
    print("\n🔍 Verifying database setup...")
    supabase = get_supabase_client()
    
    tables = [
        "users",
        "leave_types", 
        "leave_balances",
        "leave_requests",
        "rooms",
        "room_bookings",
        "claim_categories",
        "claims",
        "conversations",
        "messages"
    ]
    
    for table in tables:
        try:
            result = supabase.table(table).select("id").limit(1).execute()
            print(f"✅ {table:20} - OK (rows: {len(result.data)})")
        except Exception as e:
            print(f"❌ {table:20} - MISSING or ERROR")
            return False
    
    return True

def show_test_user():
    """Show test user profile."""
    print("\n👤 Test User Profile:")
    supabase = get_supabase_client()
    
    try:
        user = supabase.table("users").select("*").eq(
            "id", "11111111-1111-1111-1111-111111111111"
        ).execute()
        
        if user.data:
            u = user.data[0]
            print(f"   ID:         {u['id']}")
            print(f"   Name:       {u['full_name']}")
            print(f"   Email:      {u['email']}")
            print(f"   Department: {u['department']}")
            print(f"   Role:       {u['role']}")
            
            # Check balances
            balances = supabase.table("leave_balances").select(
                "*, leave_types(name)"
            ).eq("user_id", u['id']).eq("year", 2026).execute()
            
            print(f"\n   📊 Leave Balances 2026:")
            for bal in balances.data:
                lt_name = bal.get("leave_types", {}).get("name", "Unknown")
                remaining = bal["total_days"] - bal["used_days"] - bal["pending_days"]
                print(f"      {lt_name:15} - {remaining}/{bal['total_days']} days remaining")
        else:
            print("   ⚠️ Test user not found!")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🏢 CHIN HIN DATABASE SETUP")
    print("=" * 60)
    
    # Try to run migrations (will likely fail via REST API)
    print("\n📝 Attempting to run migrations via API...")
    schema_ok = run_migration("001_initial_schema.sql")
    data_ok = run_migration("002_dummy_data.sql")
    
    # If API fails, instruct manual setup
    if not schema_ok or not data_ok:
        print("\n" + "=" * 60)
        print("⚠️ MANUAL SETUP REQUIRED")
        print("=" * 60)
        print("\n1. Go to Supabase SQL Editor:")
        print("   https://supabase.com/dashboard/project/nlerjwllnvrpfujuxjnp/sql")
        print("\n2. Run these files in order:")
        print("   - db/migrations/001_initial_schema.sql")
        print("   - db/migrations/002_dummy_data.sql")
        print("\n3. Re-run this script to verify: python setup_database.py")
        sys.exit(1)
    
    # Verify tables
    if verify_setup():
        print("\n✅ Database setup complete!")
        show_test_user()
    else:
        print("\n❌ Database setup incomplete. Please run migrations manually.")
        sys.exit(1)
