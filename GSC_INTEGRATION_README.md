# Google Search Console (GSC) Integration for ALwrity

This document describes the complete Google Search Console integration implemented for ALwrity, allowing users to connect their GSC accounts and fetch real website analytics data.

## 🚀 Features

### Backend Features
- **OAuth2 Authentication**: Secure Google OAuth2 flow for GSC access
- **User Credential Management**: Encrypted storage of user OAuth tokens
- **Data Caching**: SQLite-based caching system for GSC data
- **Multi-user Support**: Each user can connect their own GSC account
- **Real-time Analytics**: Fetch live search analytics, sitemaps, and site data
- **Comprehensive Logging**: Detailed logging throughout the system

### Frontend Features
- **GSC Login Button**: Seamless OAuth connection flow
- **Status Management**: Real-time connection status display
- **Popup Authentication**: Secure OAuth flow in popup window
- **Error Handling**: Comprehensive error management and user feedback
- **Responsive UI**: Material-UI components matching existing dashboard style

## 📁 File Structure

### Backend Files
```
backend/
├── services/
│   └── gsc_service.py              # Core GSC service with OAuth and data management
├── routers/
│   └── gsc_auth.py                 # FastAPI router for GSC endpoints
├── middleware/
│   └── auth_middleware.py          # Clerk authentication middleware
├── gsc_credentials.json            # Google OAuth2 client credentials
├── env_template.txt                # Environment variables template
└── requirements.txt                # Updated with GSC dependencies
```

### Frontend Files
```
frontend/src/
├── api/
│   └── gsc.ts                      # GSC API client
├── components/SEODashboard/components/
│   ├── GSCLoginButton.tsx          # GSC connection UI component
│   └── GSCAuthCallback.tsx         # OAuth callback handler
├── env_template.txt                # Frontend environment template
└── package.json                    # Updated with Clerk dependencies
```

## 🔧 API Endpoints

### GSC Authentication & Management
- `GET /gsc/auth/url` - Get OAuth authorization URL
- `GET /gsc/callback` - Handle OAuth callback
- `GET /gsc/status` - Check GSC connection status
- `DELETE /gsc/disconnect` - Revoke GSC access

### GSC Data Retrieval
- `GET /gsc/sites` - Get user's GSC sites
- `POST /gsc/analytics` - Fetch search analytics data
- `GET /gsc/sitemaps/{site_url}` - Get sitemaps for a site
- `GET /gsc/health` - Health check endpoint

## 🗄️ Database Schema

### GSC Credentials Table
```sql
CREATE TABLE gsc_credentials (
    user_id TEXT PRIMARY KEY,
    credentials_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### GSC Data Cache Table
```sql
CREATE TABLE gsc_data_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    site_url TEXT NOT NULL,
    data_type TEXT NOT NULL,
    data_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES gsc_credentials (user_id)
);
```

## 🔐 Authentication Flow

1. **User clicks "Connect GSC"** → Frontend requests OAuth URL
2. **Backend generates OAuth URL** → Returns Google authorization URL
3. **User authorizes in popup** → Google redirects to callback
4. **Backend handles callback** → Exchanges code for tokens
5. **Credentials stored securely** → User can now access GSC data
6. **Real data replaces mock data** → Dashboard shows live analytics

## 🛠️ Setup Instructions

### 1. Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual values
   ```

3. **Google OAuth Setup**:
   - Copy your Google OAuth credentials to `gsc_credentials.json`
   - Ensure redirect URIs include both backend and frontend URLs

4. **Start Backend**:
   ```bash
   python app.py
   ```

### 2. Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment**:
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual values
   ```

3. **Start Frontend**:
   ```bash
   npm start
   ```

## 🔑 Environment Variables

### Backend (.env)
```env
# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key_here

# Google Search Console
GSC_REDIRECT_URI=http://localhost:8000/gsc/callback

# Development Settings
DISABLE_AUTH=false
```

### Frontend (.env)
```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# CopilotKit
REACT_APP_COPILOTKIT_API_KEY=your_copilotkit_api_key_here
```

## 📊 Data Types Retrieved

### Search Analytics
- **Clicks**: Number of clicks from search results
- **Impressions**: Number of times site appeared in search
- **CTR**: Click-through rate percentage
- **Position**: Average position in search results

### Site Information
- **Site URLs**: List of verified sites in GSC
- **Permission Levels**: User's access level for each site

### Sitemaps
- **Sitemap Paths**: URLs of submitted sitemaps
- **Submission Dates**: When sitemaps were last submitted
- **Index Status**: Which pages are indexed

## 🔒 Security Features

- **OAuth2 Security**: Google's secure authorization protocol
- **Token Encryption**: Credentials stored securely in database
- **User Isolation**: Each user's data is completely separate
- **Token Refresh**: Automatic token refresh when expired
- **Access Revocation**: Users can disconnect at any time

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest test_gsc_*.py
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
1. Start both backend and frontend servers
2. Navigate to SEO Dashboard
3. Click "Connect GSC"
4. Complete OAuth flow
5. Verify real data appears in dashboard

## 🐛 Troubleshooting

### Common Issues

1. **"Not Found" Error**:
   - Check API endpoint paths match between frontend and backend
   - Ensure backend server is running

2. **"Not Authenticated" Error**:
   - Verify Clerk API keys are correct
   - Check environment variables are loaded

3. **OAuth Popup Blocked**:
   - Allow popups for localhost
   - Check browser popup settings

4. **GSC Data Not Loading**:
   - Verify Google OAuth credentials
   - Check user has verified sites in GSC
   - Review backend logs for errors

## 📈 Performance Optimizations

- **Data Caching**: GSC data cached for 1 hour to reduce API calls
- **Lazy Loading**: Components load data only when needed
- **Error Boundaries**: Graceful error handling prevents crashes
- **Connection Pooling**: Efficient database connections

## 🔄 Future Enhancements

- **Real-time Updates**: WebSocket-based live data updates
- **Advanced Analytics**: More detailed GSC metrics and insights
- **Bulk Operations**: Analyze multiple sites simultaneously
- **Export Features**: Export GSC data to CSV/Excel
- **Scheduled Reports**: Automated GSC reports via email

## 📝 Logging

The system includes comprehensive logging at all levels:

- **Backend**: Detailed logs for OAuth flow, data retrieval, and errors
- **Frontend**: Console logs for API calls and user interactions
- **Database**: Query logging for debugging data issues

## 🤝 Contributing

When contributing to the GSC integration:

1. Follow existing code patterns and style
2. Add comprehensive logging for new features
3. Include error handling for all API calls
4. Update tests for any new functionality
5. Document any new environment variables or setup steps

## 📄 License

This GSC integration is part of the ALwrity project and follows the same licensing terms.
