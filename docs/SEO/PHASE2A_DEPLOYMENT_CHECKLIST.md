"""
Phase 2A DEPLOYMENT CHECKLIST

Quick reference for deploying Phase 2A (Enterprise SEO + Advanced GSC Integration)

========================================
PRE-DEPLOYMENT VERIFICATION
========================================

Code Quality:
  ✓ enterprise_seo_service.py - Complete with full orchestration
  ✓ gsc_analyzer_service.py - Complete with 8 analysis dimensions
  ✓ seo_tools.py router - Updated with 6 new endpoints
  ✓ Comprehensive test suite - test_enterprise_gsc_services.py
  ✓ Full API documentation - PHASE2A_IMPLEMENTATION.md

Services Added:
  ✓ /api/seo/enterprise/complete-audit (POST)
  ✓ /api/seo/enterprise/quick-audit (POST)
  ✓ /api/seo/enterprise/health (GET)
  ✓ /api/seo/gsc/analyze-search-performance (POST)
  ✓ /api/seo/gsc/content-opportunities (POST)
  ✓ Error handling & logging for all endpoints

========================================
ENVIRONMENT CONFIGURATION NEEDED
========================================

Required Environment Variables:
  □ GOOGLE_CLIENT_ID - From Google Cloud Console
  □ GOOGLE_CLIENT_SECRET - From Google Cloud Console
  □ GSC_REDIRECT_URI - OAuth callback URL
  □ LLM_API_KEY - For AI insights generation (can be optional)

Optional Database Changes:
  □ Add audit_results table for storing audit history
  □ Add gsc_analysis_cache table for caching GSC data
  □ Add user_keywords table for keyword tracking

========================================
DEPLOYMENT STEPS
========================================

1. CODE DEPLOYMENT
   ========================================
   
   # Verify files are in place
   - [ ] backend/services/seo_tools/enterprise_seo_service.py exists
   - [ ] backend/services/seo_tools/gsc_analyzer_service.py exists
   - [ ] backend/routers/seo_tools.py updated with new endpoints
   - [ ] backend/tests/test_enterprise_gsc_services.py exists
   - [ ] docs/SEO/PHASE2A_IMPLEMENTATION.md exists
   - [ ] docs-site/mkdocs.yml updated
   
   # Commands to run
   cd backend
   
   # Verify Python syntax
   python -m py_compile services/seo_tools/enterprise_seo_service.py
   python -m py_compile services/seo_tools/gsc_analyzer_service.py
   
   # Run tests (optional but recommended)
   pytest tests/test_enterprise_gsc_services.py -v
   
   # Check for import errors
   python -c "from services.seo_tools.enterprise_seo_service import EnterpriseSEOService; print('✓ Imports successful')"
   python -c "from services.seo_tools.gsc_analyzer_service import GSCAnalyzerService; print('✓ Imports successful')"


2. ENVIRONMENT SETUP
   ========================================
   
   # Update .env file with required credentials
   Set these environment variables:
   
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GSC_REDIRECT_URI=https://yourdomain.com/gsc/callback
   LLM_API_KEY=your_llm_key_here (optional)
   
   # Verify environment
   python backend/check_gsc_config.py  # Verify GSC credentials


3. DATABASE MIGRATION (Optional)
   ========================================
   
   # If adding new tables for audit history
   python backend/alembic/env.py upgrade head
   
   # Or manually create tables if needed
   See: backend/database/migrations/ for schema


4. SERVICE STARTUP & VERIFICATION
   ========================================
   
   # Start backend (if not already running)
   cd backend
   python start_alwrity_backend.py --dev
   
   # OR if using Gunicorn
   gunicorn -c gunicorn_config.py app:app
   
   # Verify health endpoints
   curl http://localhost:8000/api/seo/health
   curl http://localhost:8000/api/seo/enterprise/health
   curl http://localhost:8000/api/seo/tools/status
   
   # Check for errors in logs
   tail -f logs/seo_tools/latest.log


5. ENDPOINT TESTING
   ========================================
   
   # Test Enterprise Complete Audit
   curl -X POST http://localhost:8000/api/seo/enterprise/complete-audit \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"website_url": "https://example.com"}'
   
   # Test GSC Analysis
   curl -X POST http://localhost:8000/api/seo/gsc/analyze-search-performance \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"site_url": "https://example.com", "date_range_days": 90}'
   
   # Test Content Opportunities
   curl -X POST http://localhost:8000/api/seo/gsc/content-opportunities \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"site_url": "https://example.com", "min_impressions": 100}'
   
   Expected Response: 200 OK with structured data


6. FRONTEND INTEGRATION (If Applicable)
   ========================================
   
   # Add to frontend API client
   - [ ] Update api/seo.ts with new endpoint URLs
   - [ ] Create UI components for enterprise audit
   - [ ] Create UI components for GSC analysis
   - [ ] Create UI components for content opportunities
   - [ ] Add authentication tokens to requests
   - [ ] Handle loading and error states
   
   # Build and test frontend
   cd frontend
   npm run build
   npm start


7. MONITORING & LOGGING
   ========================================
   
   # Verify logging is working
   - [ ] Check backend/logs/seo_tools/ directory exists
   - [ ] Verify logs are being generated
   - [ ] Check log format and detail level
   
   # Monitor first requests
   - [ ] Watch logs during first audit execution
   - [ ] Check for any error messages
   - [ ] Verify performance (should complete in 15-20 min)
   
   # Set up alerts if using monitoring
   - [ ] High error rate alerts (> 5% failures)
   - [ ] Slow response time alerts (> 30 min)
   - [ ] Service health check alerts


========================================
POST-DEPLOYMENT VERIFICATION
========================================

Functionality Checks:
  ✓ Complete audit returns all 5 component results
  ✓ Quick audit completes in < 5 minutes
  ✓ GSC analysis returns all 8 dimension results
  ✓ Content opportunities ranked by priority
  ✓ AI insights generate without errors
  ✓ Error handling works for invalid inputs
  ✓ Rate limiting enforced correctly
  ✓ Authentication required on all endpoints

Performance Checks:
  ✓ Complete audit: 15-20 minutes
  ✓ Quick audit: < 5 minutes
  ✓ GSC analysis: 2-3 minutes
  ✓ Content opportunities: 3-5 minutes
  ✓ Health checks: < 1 second

Data Checks:
  ✓ Overall scores calculated correctly (0-100)
  ✓ Component scores weighted properly
  ✓ Recommendations prioritized correctly
  ✓ Opportunities ranked by score
  ✓ Timestamps accurate


========================================
ROLLBACK PROCEDURE (If Issues Occur)
========================================

If you encounter critical issues:

1. Stop the service:
   pkill -f "start_alwrity_backend.py"

2. Restore previous version:
   git checkout HEAD~1 backend/services/seo_tools/enterprise_seo_service.py
   git checkout HEAD~1 backend/services/seo_tools/gsc_analyzer_service.py
   git checkout HEAD~1 backend/routers/seo_tools.py

3. Restart service:
   python backend/start_alwrity_backend.py --dev

4. Verify health:
   curl http://localhost:8000/api/seo/health

5. Document the issue:
   Save logs and error messages for debugging


========================================
SUPPORT & TROUBLESHOOTING
========================================

Common Issues:

Issue: "ModuleNotFoundError: No module named 'services.seo_tools.enterprise_seo_service'"
Solution:
  - Verify file exists at: backend/services/seo_tools/enterprise_seo_service.py
  - Check Python path includes backend directory
  - Run: python backend/start_alwrity_backend.py from project root

Issue: "GSC credentials not found"
Solution:
  - Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
  - Ensure gsc_credentials.json exists in backend/ directory
  - Run: python backend/check_gsc_config.py to verify

Issue: Audit timeout (> 30 seconds)
Solution:
  - Check internet connectivity
  - Verify target website is accessible
  - Use quick-audit instead for faster results
  - Check logs for component-specific errors

Issue: "Rate limit exceeded" error
Solution:
  - Complete audit: 1 per hour per user
  - GSC analysis: 5 per hour per user
  - Queue requests if exceeding limits
  - Check frontend for duplicate submissions

For additional help:
  - Check: docs/SEO/PHASE2A_IMPLEMENTATION.md
  - Check logs: backend/logs/seo_tools/
  - Run tests: pytest backend/tests/test_enterprise_gsc_services.py -v
  - Review error details in API response


========================================
SUCCESS CRITERIA
========================================

Phase 2A deployment is successful when:

  ✓ All 6 new endpoints respond with 200 OK
  ✓ Enterprise audit completes and returns all scores
  ✓ GSC analysis identifies content opportunities
  ✓ All components execute in parallel without blocking
  ✓ Error handling works for edge cases
  ✓ Rate limiting prevents abuse
  ✓ Logging captures all important events
  ✓ Response times meet expectations
  ✓ Test suite passes without errors
  ✓ Frontend can call new endpoints with auth
  ✓ Users can view results in dashboard

Once all criteria are met: ✓ PHASE 2A DEPLOYMENT COMPLETE


========================================
PHASE 2B PREVIEW (Next Steps)
========================================

After Phase 2A stabilizes, Phase 2B includes:
  - Schema markup generation service
  - Text readability analyzer integration
  - Custom reporting templates
  - Scheduled audit automation
  - Advanced competitor analysis

Estimated timeline for Phase 2B: 1 week


Last Updated: May 23, 2026
Status: Ready for Deployment
"""
