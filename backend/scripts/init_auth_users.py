import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_auth_users():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # MUST use service role for admin tasks
    
    if not url or not key:
        print("❌ Missing Supabase URL or Service Role Key in .env")
        return

    # Use a separate admin client with the service role key
    supabase: Client = create_client(url, key)
    
    # List of demo users from 002_dummy_data.sql
    demo_users = [
        {"id": "11111111-1111-1111-1111-111111111111", "email": "ahmad@chinhin.com", "name": "Ahmad bin Hassan"},
        {"id": "22222222-2222-2222-2222-222222222222", "email": "siti@chinhin.com", "name": "Siti Nurhaliza"},
        {"id": "33333333-3333-3333-3333-333333333333", "email": "raj@chinhin.com", "name": "Raj Kumar"},
        {"id": "44444444-4444-4444-4444-444444444444", "email": "mei.ling@chinhin.com", "name": "Tan Mei Ling"},
        {"id": "55555555-5555-5555-5555-555555555555", "email": "farid@chinhin.com", "name": "Farid Abdullah"},
        {"id": "66666666-6666-6666-6666-666666666666", "email": "priya@chinhin.com", "name": "Priya Devi"},
        {"id": "77777777-7777-7777-7777-777777777777", "email": "wei.chen@chinhin.com", "name": "Lee Wei Chen"},
        {"id": "88888888-8888-8888-8888-888888888888", "email": "aishah@chinhin.com", "name": "Aishah Zainal"},
        {"id": "99999999-9999-9999-9999-999911111111", "email": "muthu@chinhin.com", "name": "Muthu Samy"},
        {"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "email": "admin@chinhin.com", "name": "System Admin"},
    ]
    
    password = "password123"
    
    print(f"🚀 Initializing {len(demo_users)} auth users...")
    
    for user in demo_users:
        try:
            # Check if user already exists in auth
            # We don't have a direct 'get_user_by_email' in admin API via this lib usually, 
            # so we try to create and catch error
            
            # Use admin API to create user
            _ = supabase.auth.admin.create_user({
                "id": user["id"],
                "email": user["email"],
                "password": password,
                "email_confirm": True,
                "user_metadata": {"full_name": user["name"]}
            })
            print(f"✅ Created: {user['email']}")
            
        except Exception as e:
            if "already exists" in str(e).lower() or "unique_violation" in str(e).lower():
                # User might exist, let's try to update password just in case
                try:
                    supabase.auth.admin.update_user_by_id(
                        user["id"],
                        {"password": password}
                    )
                    print(f"ℹ️  Updated Password: {user['email']}")
                except Exception as update_err:
                    print(f"⚠️  Error updating {user['email']}: {update_err}")
            else:
                print(f"❌ Error creating {user['email']}: {e}")

    print("\n✨ Auth initialization complete!")

if __name__ == "__main__":
    init_auth_users()
