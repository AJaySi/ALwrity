"""Google Search Console Service for ALwrity."""

import os
import json
import sqlite3
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from loguru import logger

from services.database import get_user_db_path

from dotenv import load_dotenv

class GSCService:
    """Service for Google Search Console integration."""
    
    def __init__(self, db_path: str = None):
        """Initialize GSC service."""
        # db_path is deprecated in favor of dynamic user_id based paths
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
            
        # Load client config from file or environment variables
        self.client_config = self._load_client_config()
        
        if self.client_config:
            logger.info("GSC client configuration loaded successfully")
        else:
            logger.warning(f"GSC credentials not found in {self.credentials_file} or environment variables")
            
        self.scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
        # Note: Tables are initialized lazily per user
        logger.info("GSC Service initialized successfully")

    def _load_client_config(self) -> Optional[Dict[str, Any]]:
        """Load Google client configuration from environment variables or file."""
        # Reload environment variables to catch any runtime changes (e.g. .env updates)
        load_dotenv(override=True)

        # 1. Check Environment Variables (Priority)
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if client_id and client_secret:
            redirect_uri = os.getenv('GSC_REDIRECT_URI', 'http://localhost:8000/gsc/callback')
            logger.info("Loading GSC credentials from environment variables")
            # Construct the config dictionary expected by google_auth_oauthlib
            return {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "project_id": os.getenv("GOOGLE_PROJECT_ID", "alwrity"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [
                        "http://localhost:5173/onboarding",
                        redirect_uri
                    ],
                    "javascript_origins": [
                        "http://localhost:5173",
                        "http://localhost:8000"
                    ]
                }
            }

        # 2. Fallback to File
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loading GSC credentials from file: {self.credentials_file}")
                    return config
            except Exception as e:
                logger.warning(f"Failed to load GSC credentials from file: {e}")
        
        return None
    
    def _get_db_path(self, user_id: str) -> str:
        return get_user_db_path(user_id)
    
    def _init_gsc_tables(self, user_id: str):
        """Initialize GSC-related database tables."""
        try:
            db_path = self._get_db_path(user_id)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            with sqlite3.connect(db_path) as conn:
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
                
                # GSC OAuth states table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gsc_oauth_states (
                        state TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                # logger.debug(f"GSC database tables initialized for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error initializing GSC tables for user {user_id}: {e}")
            raise
    
    def save_user_credentials(self, user_id: str, credentials: Credentials) -> bool:
        """Save user's GSC credentials to database."""
        try:
            self._init_gsc_tables(user_id)
            db_path = self._get_db_path(user_id)
            
            if not self.client_config:
                logger.error("Cannot save credentials: Client configuration not loaded")
                return False
            
            web_config = self.client_config.get('web', {})
            
            credentials_json = json.dumps({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri or web_config.get('token_uri'),
                'client_id': credentials.client_id or web_config.get('client_id'),
                'client_secret': credentials.client_secret or web_config.get('client_secret'),
                'scopes': credentials.scopes
            })
            
            with sqlite3.connect(db_path) as conn:
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
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return None
                
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                # Check if table exists first to avoid error on fresh DB
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gsc_credentials'")
                if not cursor.fetchone():
                    return None
                    
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
            
            # Retry loading config if missing (in case .env was added later)
            if not self.client_config:
                self.client_config = self._load_client_config()

            if not self.client_config:
                raise FileNotFoundError("GSC credentials not found in file or environment variables.")
            
            redirect_uri = os.getenv('GSC_REDIRECT_URI', 'http://localhost:8000/gsc/callback')
            
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=redirect_uri
            )
            
            # Use a custom state that includes user_id for routing the callback to the correct DB
            random_state = secrets.token_urlsafe(32)
            state = f"{user_id}:{random_state}"
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state=state
            )
            
            # Store state for verification in the user-specific DB
            self._init_gsc_tables(user_id)
            db_path = self._get_db_path(user_id)
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO gsc_oauth_states (state, user_id) 
                    VALUES (?, ?)
                ''', (state, user_id))
                conn.commit()
            
            logger.info(f"OAuth URL generated successfully for user: {user_id}")
            return authorization_url
            
        except Exception as e:
            logger.error(f"Error generating OAuth URL for user {user_id}: {e}")
            raise

    def handle_oauth_callback(self, authorization_code: str, state: str) -> bool:
        """Handle OAuth callback and save credentials."""
        try:
            logger.info(f"Handling GSC OAuth callback with state: {state[:20]}...")
            
            # Extract user_id from state
            if ':' not in state:
                logger.error(f"Invalid GSC state format: {state}")
                return False
                
            user_id = state.split(':')[0]
            db_path = self._get_db_path(user_id)
            
            if not os.path.exists(db_path):
                logger.error(f"User database not found for user {user_id}")
                return False

            # Verify state in user's DB
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM gsc_oauth_states WHERE state = ?', (state,))
                result = cursor.fetchone()
                
                if not result:
                    logger.error(f"Invalid or expired GSC OAuth state for user {user_id}")
                    return False
                
                # Clean up state
                cursor.execute('DELETE FROM gsc_oauth_states WHERE state = ?', (state,))
                conn.commit()
            
            # Exchange code for credentials
            if not self.client_config:
                logger.error("Cannot handle callback: Client configuration not loaded")
                return False

            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=os.getenv('GSC_REDIRECT_URI', 'http://localhost:8000/gsc/callback')
            )
            
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Save credentials
            return self.save_user_credentials(user_id, credentials)
            
        except Exception as e:
            logger.error(f"Error handling GSC OAuth callback: {e}")
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
        
        except ValueError as e:
            # Log as warning only, as this is expected for unconnected users
            # logger.warning(f"Cannot create GSC service for user {user_id}: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error creating authenticated GSC service for user {user_id}: {e}")
            raise
    
    def get_site_list(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of sites from GSC."""
        try:
            try:
                service = self.get_authenticated_service(user_id)
            except ValueError:
                # User not connected or credentials invalid
                logger.warning(f"User {user_id} not connected to GSC. Returning empty site list.")
                return []

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
            # Return empty list instead of raising to prevent frontend 500s
            return []
    
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
            
            try:
                service = self.get_authenticated_service(user_id)
            except ValueError:
                logger.warning(f"User {user_id} not connected to GSC. Returning empty analytics.")
                return {'error': 'User not connected to GSC', 'rows': [], 'rowCount': 0}

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
            
            # Step 2: Get daily metrics for charting (ensure we have rows)
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['date'],  # Use date dimension to get time-series data
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
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return True
                
            with sqlite3.connect(db_path) as conn:
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
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return True
                
            with sqlite3.connect(db_path) as conn:
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
            db_path = self._get_db_path(user_id)
            if not os.path.exists(db_path):
                return None
                
            with sqlite3.connect(db_path) as conn:
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
            self._init_gsc_tables(user_id)
            db_path = self._get_db_path(user_id)
            
            expires_at = datetime.now() + timedelta(hours=1)  # Cache for 1 hour
            
            with sqlite3.connect(db_path) as conn:
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
