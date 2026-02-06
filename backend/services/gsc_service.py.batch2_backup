"""Google Search Console Service for ALwrity."""

import os
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from loguru import logger

class GSCService:
    """Service for Google Search Console integration."""
    
    def __init__(self, db_path: str = "alwrity.db"):
        """Initialize GSC service with database connection."""
        self.db_path = db_path
        # Resolve credentials file robustly: env override or project-relative default
        env_credentials_path = os.getenv("GSC_CREDENTIALS_FILE")
        if env_credentials_path:
            self.credentials_file = env_credentials_path
        else:
            # Default to <backend>/gsc_credentials.json regardless of CWD
            services_dir = os.path.dirname(__file__)
            backend_dir = os.path.abspath(os.path.join(services_dir, os.pardir))
            self.credentials_file = os.path.join(backend_dir, "gsc_credentials.json")
        logger.info(f"GSC credentials file path set to: {self.credentials_file}")
        self.scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
        self._init_gsc_tables()
        logger.info("GSC Service initialized successfully")
    
    def _init_gsc_tables(self):
        """Initialize GSC-related database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # GSC credentials table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gsc_credentials (
                        user_id TEXT PRIMARY KEY,
                        credentials_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # GSC data cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gsc_data_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        site_url TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        data_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES gsc_credentials (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("GSC database tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing GSC tables: {e}")
            raise
    
    def save_user_credentials(self, user_id: str, credentials: Credentials) -> bool:
        """Save user's GSC credentials to database."""
        try:
            # Read client credentials from file to ensure we have all required fields
            with open(self.credentials_file, 'r') as f:
                client_config = json.load(f)
            
            web_config = client_config.get('web', {})
            
            credentials_json = json.dumps({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri or web_config.get('token_uri'),
                'client_id': credentials.client_id or web_config.get('client_id'),
                'client_secret': credentials.client_secret or web_config.get('client_secret'),
                'scopes': credentials.scopes
            })
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO gsc_credentials 
                    (user_id, credentials_json, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, credentials_json))
                conn.commit()
            
            logger.info(f"GSC credentials saved for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving GSC credentials for user {user_id}: {e}")
            return False
    
    def load_user_credentials(self, user_id: str) -> Optional[Credentials]:
        """Load user's GSC credentials from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT credentials_json FROM gsc_credentials 
                    WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                credentials_data = json.loads(result[0])
                
                # Check for required fields, but allow connection without refresh token
                required_fields = ['token_uri', 'client_id', 'client_secret']
                missing_fields = [field for field in required_fields if not credentials_data.get(field)]
                
                if missing_fields:
                    logger.warning(f"GSC credentials for user {user_id} missing required fields: {missing_fields}")
                    return None
                
                credentials = Credentials.from_authorized_user_info(credentials_data, self.scopes)
                
                # Refresh token if needed and possible
                if credentials.expired:
                    if credentials.refresh_token:
                        try:
                            credentials.refresh(GoogleRequest())
                            self.save_user_credentials(user_id, credentials)
                        except Exception as e:
                            logger.error(f"Failed to refresh GSC token for user {user_id}: {e}")
                            return None
                    else:
                        logger.warning(f"GSC token expired for user {user_id} but no refresh token available - user needs to re-authorize")
                        return None
                
                return credentials
                
        except Exception as e:
            logger.error(f"Error loading GSC credentials for user {user_id}: {e}")
            return None
    
    def get_oauth_url(self, user_id: str) -> str:
        """Get OAuth authorization URL for GSC."""
        try:
            logger.info(f"Generating OAuth URL for user: {user_id}")
            
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(f"GSC credentials file not found: {self.credentials_file}")
            
            redirect_uri = os.getenv('GSC_REDIRECT_URI', 'http://localhost:8000/gsc/callback')
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
                redirect_uri=redirect_uri
            )
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent screen to get refresh token
            )
            
            logger.info(f"OAuth URL generated for user: {user_id}")
            
            # Store state for verification
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gsc_oauth_states (
                        state TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO gsc_oauth_states (state, user_id) 
                    VALUES (?, ?)
                ''', (state, user_id))
                conn.commit()
            
            logger.info(f"OAuth URL generated successfully for user: {user_id}")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error generating OAuth URL for user {user_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            raise
    
    def handle_oauth_callback(self, authorization_code: str, state: str) -> bool:
        """Handle OAuth callback and save credentials."""
        try:
            logger.info(f"Handling OAuth callback with state: {state}")
            
            # Verify state
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id FROM gsc_oauth_states WHERE state = ?
                ''', (state,))
                
                result = cursor.fetchone()
                
                if not result:
                    # Check if this is a duplicate callback by looking for recent credentials
                    cursor.execute('SELECT user_id, credentials_json FROM gsc_credentials ORDER BY updated_at DESC LIMIT 1')
                    recent_credentials = cursor.fetchone()
                    
                    if recent_credentials:
                        logger.info("Duplicate callback detected - returning success")
                        return True
                    
                    # If no recent credentials, try to find any recent state
                    cursor.execute('SELECT state, user_id FROM gsc_oauth_states ORDER BY created_at DESC LIMIT 1')
                    recent_state = cursor.fetchone()
                    if recent_state:
                        user_id = recent_state[1]
                        # Clean up the old state
                        cursor.execute('DELETE FROM gsc_oauth_states WHERE state = ?', (recent_state[0],))
                        conn.commit()
                    else:
                        raise ValueError("Invalid OAuth state")
                else:
                    user_id = result[0]
                
                # Clean up state
                cursor.execute('DELETE FROM gsc_oauth_states WHERE state = ?', (state,))
                conn.commit()
            
            # Exchange code for credentials
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=self.scopes,
                redirect_uri=os.getenv('GSC_REDIRECT_URI', 'http://localhost:8000/gsc/callback')
            )
            
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Save credentials
            success = self.save_user_credentials(user_id, credentials)
            
            if success:
                logger.info(f"OAuth callback handled successfully for user: {user_id}")
            else:
                logger.error(f"Failed to save credentials for user: {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            return False
    
    def get_authenticated_service(self, user_id: str):
        """Get authenticated GSC service for user."""
        try:
            credentials = self.load_user_credentials(user_id)
            if not credentials:
                raise ValueError("No valid credentials found")
            
            service = build('searchconsole', 'v1', credentials=credentials)
            logger.info(f"Authenticated GSC service created for user: {user_id}")
            return service
            
        except Exception as e:
            logger.error(f"Error creating authenticated GSC service for user {user_id}: {e}")
            raise
    
    def get_site_list(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of sites from GSC."""
        try:
            service = self.get_authenticated_service(user_id)
            sites = service.sites().list().execute()
            
            site_list = []
            for site in sites.get('siteEntry', []):
                site_list.append({
                    'siteUrl': site.get('siteUrl'),
                    'permissionLevel': site.get('permissionLevel')
                })
            
            logger.info(f"Retrieved {len(site_list)} sites for user: {user_id}")
            return site_list
            
        except Exception as e:
            logger.error(f"Error getting site list for user {user_id}: {e}")
            raise
    
    def get_search_analytics(self, user_id: str, site_url: str, 
                           start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get search analytics data from GSC."""
        try:
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Check cache first
            cache_key = f"{user_id}_{site_url}_{start_date}_{end_date}"
            cached_data = self._get_cached_data(user_id, site_url, 'analytics', cache_key)
            if cached_data:
                logger.info(f"Returning cached analytics data for user: {user_id}")
                return cached_data
            
            service = self.get_authenticated_service(user_id)
            if not service:
                logger.error(f"Failed to get authenticated GSC service for user: {user_id}")
                return {'error': 'Authentication failed', 'rows': [], 'rowCount': 0}
            
            # Step 1: Verify data presence first (as per GSC API documentation)
            verification_request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['date']  # Only date dimension for verification
            }
            
            logger.info(f"GSC Data verification request for user {user_id}: {verification_request}")
            
            try:
                verification_response = service.searchanalytics().query(
                    siteUrl=site_url,
                    body=verification_request
                ).execute()
                
                logger.info(f"GSC Data verification response for user {user_id}: {verification_response}")
                
                # Check if we have any data
                verification_rows = verification_response.get('rows', [])
                if not verification_rows:
                    logger.warning(f"No GSC data available for user {user_id} in date range {start_date} to {end_date}")
                    return {'error': 'No data available for this date range', 'rows': [], 'rowCount': 0}
                
                logger.info(f"GSC Data verification successful - found {len(verification_rows)} days with data")
                
            except Exception as verification_error:
                logger.error(f"GSC Data verification failed for user {user_id}: {verification_error}")
                return {'error': f'Data verification failed: {str(verification_error)}', 'rows': [], 'rowCount': 0}
            
            # Step 2: Get overall metrics (no dimensions)
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': [],  # No dimensions for overall metrics
                'rowLimit': 1000
            }
            
            logger.info(f"GSC API request for user {user_id}: {request}")
            
            try:
                response = service.searchanalytics().query(
                    siteUrl=site_url,
                    body=request
                ).execute()
                
                logger.info(f"GSC API response for user {user_id}: {response}")
            except Exception as api_error:
                logger.error(f"GSC API call failed for user {user_id}: {api_error}")
                return {'error': str(api_error), 'rows': [], 'rowCount': 0}
            
            # Step 3: Get query-level data for insights (as per documentation)
            query_request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],  # Get query-level data
                'rowLimit': 1000
            }
            
            logger.info(f"GSC Query-level request for user {user_id}: {query_request}")
            
            try:
                query_response = service.searchanalytics().query(
                    siteUrl=site_url,
                    body=query_request
                ).execute()
                
                logger.info(f"GSC Query-level response for user {user_id}: {query_response}")
                
                # Combine overall metrics with query-level data
                analytics_data = {
                    'overall_metrics': {
                        'rows': response.get('rows', []),
                        'rowCount': response.get('rowCount', 0)
                    },
                    'query_data': {
                        'rows': query_response.get('rows', []),
                        'rowCount': query_response.get('rowCount', 0)
                    },
                    'verification_data': {
                        'rows': verification_rows,
                        'rowCount': len(verification_rows)
                    },
                    'startDate': start_date,
                    'endDate': end_date,
                    'siteUrl': site_url
                }
                
                self._cache_data(user_id, site_url, 'analytics', analytics_data, cache_key)
                
                logger.info(f"Retrieved comprehensive analytics data for user: {user_id}, site: {site_url}")
                return analytics_data
                
            except Exception as query_error:
                logger.error(f"GSC Query-level request failed for user {user_id}: {query_error}")
                # Fall back to overall metrics only
                analytics_data = {
                    'overall_metrics': {
                        'rows': response.get('rows', []),
                        'rowCount': response.get('rowCount', 0)
                    },
                    'query_data': {'rows': [], 'rowCount': 0},
                    'verification_data': {
                        'rows': verification_rows,
                        'rowCount': len(verification_rows)
                    },
                    'startDate': start_date,
                    'endDate': end_date,
                    'siteUrl': site_url,
                    'warning': f'Query-level data unavailable: {str(query_error)}'
                }
                
                self._cache_data(user_id, site_url, 'analytics', analytics_data, cache_key)
                return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting search analytics for user {user_id}: {e}")
            raise
    
    def get_sitemaps(self, user_id: str, site_url: str) -> List[Dict[str, Any]]:
        """Get sitemaps from GSC."""
        try:
            service = self.get_authenticated_service(user_id)
            response = service.sitemaps().list(siteUrl=site_url).execute()
            
            sitemaps = []
            for sitemap in response.get('sitemap', []):
                sitemaps.append({
                    'path': sitemap.get('path'),
                    'lastSubmitted': sitemap.get('lastSubmitted'),
                    'contents': sitemap.get('contents', [])
                })
            
            logger.info(f"Retrieved {len(sitemaps)} sitemaps for user: {user_id}, site: {site_url}")
            return sitemaps
            
        except Exception as e:
            logger.error(f"Error getting sitemaps for user {user_id}: {e}")
            raise
    
    def revoke_user_access(self, user_id: str) -> bool:
        """Revoke user's GSC access."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete credentials
                cursor.execute('DELETE FROM gsc_credentials WHERE user_id = ?', (user_id,))
                
                # Delete cached data
                cursor.execute('DELETE FROM gsc_data_cache WHERE user_id = ?', (user_id,))
                
                # Delete OAuth states
                cursor.execute('DELETE FROM gsc_oauth_states WHERE user_id = ?', (user_id,))
                
                conn.commit()
            
            logger.info(f"GSC access revoked for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking GSC access for user {user_id}: {e}")
            return False
    
    def clear_incomplete_credentials(self, user_id: str) -> bool:
        """Clear incomplete GSC credentials that are missing required fields."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM gsc_credentials WHERE user_id = ?', (user_id,))
                conn.commit()
            
            logger.info(f"Cleared incomplete GSC credentials for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing incomplete credentials for user {user_id}: {e}")
            return False
    
    def _get_cached_data(self, user_id: str, site_url: str, data_type: str, cache_key: str) -> Optional[Dict]:
        """Get cached data if not expired."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT data_json FROM gsc_data_cache 
                    WHERE user_id = ? AND site_url = ? AND data_type = ? 
                    AND expires_at > CURRENT_TIMESTAMP
                ''', (user_id, site_url, data_type))
                
                result = cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None
    
    def _cache_data(self, user_id: str, site_url: str, data_type: str, data: Dict, cache_key: str):
        """Cache data with expiration."""
        try:
            expires_at = datetime.now() + timedelta(hours=1)  # Cache for 1 hour
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO gsc_data_cache 
                    (user_id, site_url, data_type, data_json, expires_at) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, site_url, data_type, json.dumps(data), expires_at))
                conn.commit()
            
            logger.info(f"Data cached for user: {user_id}, type: {data_type}")
            
        except Exception as e:
            logger.error(f"Error caching data: {e}")
