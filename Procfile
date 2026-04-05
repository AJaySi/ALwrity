web: cd backend && ALWRITY_ENABLED_FEATURES=podcast python -c "
import os
import sys
# Ensure podcast mode
os.environ.setdefault('ALWRITY_ENABLED_FEATURES', 'podcast')
# Set HOST/PORT for Render
port = os.getenv('PORT', '10000')
host = os.getenv('HOST', '0.0.0.0')
print(f'[STARTUP] Starting uvicorn on {host}:{port}', flush=True)
sys.stdout.flush()
import uvicorn
uvicorn.run('app:app', host=host, port=int(port), reload=False)
"
