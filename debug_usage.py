
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.database import Base
from models.subscription_models import APIUsageLog, UserSubscription
from services.subscription import UsageTrackingService, PricingService

# Setup DB connection
# dynamic path resolution as per codebase
DB_PATH = os.path.join(os.getcwd(), 'backend', 'data', 'alwrity.db') 
# Note: The codebase might use user-specific DBs now. 
# Let's check how get_db works or if we need to look at a specific user db.
# user_memories says: Database path updated to `workspace/workspace_{user_id}/db/alwrity.db` to support user isolation.

USER_ID = "user_33Gz1FPI86VDXhRY8QN4ragRFGN"
WORKSPACE_DB_PATH = os.path.join(os.getcwd(), 'workspace', f'workspace_{USER_ID}', 'db', 'alwrity.db')

print(f"Checking specific user DB at: {WORKSPACE_DB_PATH}")

if os.path.exists(WORKSPACE_DB_PATH):
    db_url = f"sqlite:///{WORKSPACE_DB_PATH}"
else:
    print(f"User DB not found at {WORKSPACE_DB_PATH}, falling back to main DB for check (legacy/shared mode)")
    db_url = f"sqlite:///backend/data/alwrity.db"

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print(f"\n--- Checking Usage for User: {USER_ID} ---")
    
    # Check API Usage Logs
    logs_count = db.query(APIUsageLog).filter(APIUsageLog.user_id == USER_ID).count()
    print(f"Total API Usage Logs: {logs_count}")
    
    if logs_count > 0:
        last_log = db.query(APIUsageLog).filter(APIUsageLog.user_id == USER_ID).order_by(APIUsageLog.created_at.desc()).first()
        print(f"Last Activity: {last_log.created_at} - {last_log.endpoint} ({last_log.provider})")
    
    # Check Subscription
    sub = db.query(UserSubscription).filter(UserSubscription.user_id == USER_ID).first()
    if sub:
        print(f"Subscription: {sub.plan_type} (Status: {sub.status})")
    else:
        print("No subscription record found.")

    # Run Service Logic
    print("\n--- Running UsageTrackingService.get_user_usage_stats ---")
    usage_service = UsageTrackingService(db)
    stats = usage_service.get_user_usage_stats(USER_ID)
    print("Stats returned:")
    print(stats)

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
