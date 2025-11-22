# Troubleshooting Guide

This guide helps you resolve common issues with ALwrity. If you don't find your issue here, please check our [GitHub Issues](https://github.com/AJaySi/ALwrity/issues) or create a new one.

## Common Issues

### Backend Issues

#### Server Won't Start
**Symptoms**: Backend server fails to start or crashes immediately

**Solutions**:
1. **Check Python Version**:
   ```bash
   python --version
   # Should be 3.10 or higher
   ```

2. **Verify Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Check Port Availability**:
   ```bash
   # Check if port 8000 is in use
   netstat -an | findstr :8000
   ```

4. **Environment Variables**:
   ```bash
   # Ensure .env file exists with required keys
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```

#### Database Connection Errors
**Symptoms**: Database connection failures or SQL errors

**Solutions**:
1. **Check Database File**:
   ```bash
   # Ensure database file exists
   ls -la backend/alwrity.db
   ```

2. **Reset Database**:
   ```bash
   cd backend
   rm alwrity.db
   python -c "from services.database import init_database; init_database()"
   ```

3. **Check Permissions**:
   ```bash
   # Ensure write permissions
   chmod 664 backend/alwrity.db
   ```

#### API Key Issues
**Symptoms**: 401/403 errors, "Invalid API key" messages

**Solutions**:
1. **Verify API Keys**:
   ```bash
   # Check .env file
   cat backend/.env | grep API_KEY
   ```

2. **Test API Keys**:
   ```bash
   # Test Gemini API
   curl -H "Authorization: Bearer $GEMINI_API_KEY" \
        https://generativelanguage.googleapis.com/v1/models
   ```

3. **Check Key Format**:
   - Gemini: Should start with `AIza...`
   - OpenAI: Should start with `sk-...`
   - Anthropic: Should start with `sk-ant-...`

### Frontend Issues

#### Build Failures
**Symptoms**: `npm start` fails or build errors

**Solutions**:
1. **Clear Cache**:
   ```bash
   cd frontend
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node Version**:
   ```bash
   node --version
   # Should be 18 or higher
   ```

3. **Environment Variables**:
   ```bash
   # Check frontend .env file
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_CLERK_PUBLISHABLE_KEY=your_key
   ```

#### Connection Issues
**Symptoms**: Frontend can't connect to backend, CORS errors

**Solutions**:
1. **Check Backend Status**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify CORS Settings**:
   ```python
   # In backend/app.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Check Firewall**:
   ```bash
   # Windows
   netsh advfirewall firewall show rule name="Python"
   ```

### Content Generation Issues

#### SEO Analysis Not Working
**Symptoms**: SEO analysis fails or returns 422 errors

**Solutions**:
1. **Check API Endpoints**:
   ```bash
   # Test SEO endpoint
   curl -X POST http://localhost:8000/api/blog-writer/seo/analyze \
        -H "Content-Type: application/json" \
        -d '{"content": "test content"}'
   ```

2. **Verify Request Format**:
   ```javascript
   // Ensure proper request structure
   const requestData = {
     content: blogContent,
     researchData: researchData,
     user_id: userId
   };
   ```

3. **Check Backend Logs**:
   ```bash
   # Look for error messages in backend console
   ```

#### Content Generation Failures
**Symptoms**: AI content generation fails or returns errors

**Solutions**:
1. **Check API Quotas**:
   - Verify API key has sufficient credits
   - Check rate limits and usage

2. **Test API Connectivity**:
   ```bash
   # Test Gemini API
   curl -X POST \
     -H "Authorization: Bearer $GEMINI_API_KEY" \
     -H "Content-Type: application/json" \
     https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent
   ```

3. **Check Request Size**:
   - Ensure content isn't too long
   - Break large requests into smaller chunks

### Authentication Issues

#### Clerk Authentication Problems
**Symptoms**: Login failures, authentication errors

**Solutions**:
1. **Verify Clerk Keys**:
   ```bash
   # Check frontend .env
   REACT_APP_CLERK_PUBLISHABLE_KEY=pk_test_...
   ```

2. **Check Clerk Dashboard**:
   - Verify domain configuration
   - Check user permissions
   - Review authentication settings

3. **Clear Browser Cache**:
   ```bash
   # Clear localStorage and cookies
   ```

### Performance Issues

#### Slow Content Generation
**Symptoms**: Long response times, timeouts

**Solutions**:
1. **Check API Response Times**:
   ```bash
   # Monitor API performance
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/blog-writer
   ```

2. **Optimize Request Size**:
   - Reduce content length
   - Use streaming for large responses
   - Implement caching

3. **Check System Resources**:
   ```bash
   # Monitor CPU and memory usage
   top
   ```

#### Database Performance
**Symptoms**: Slow database queries, high response times

**Solutions**:
1. **Optimize Queries**:
   ```python
   # Add database indexes
   # Use connection pooling
   # Implement query caching
   ```

2. **Check Database Size**:
   ```bash
   # Monitor database file size
   ls -lh backend/alwrity.db
   ```

## Debugging Tools

### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Debug: {variable_name}")
```

### Frontend Debugging
```javascript
// Enable React DevTools
// Add console.log statements
console.log('Debug:', data);

// Use React Developer Tools
// Check Network tab for API calls
```

### API Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/health
curl -X POST http://localhost:8000/api/blog-writer \
     -H "Content-Type: application/json" \
     -d '{"topic": "test"}'
```

## Log Analysis

### Backend Logs
```bash
# Check backend console output
# Look for error messages
# Monitor API response times
```

### Frontend Logs
```bash
# Check browser console
# Monitor network requests
# Review error messages
```

### Database Logs
```bash
# Check database queries
# Monitor connection issues
# Review performance metrics
```

## Getting Help

### Self-Service Resources
1. **Documentation**: Check relevant guides
2. **GitHub Issues**: Search existing issues
3. **Community**: Join discussions
4. **FAQ**: Common questions and answers

### Reporting Issues
When reporting issues, include:
1. **Error Messages**: Complete error text
2. **Steps to Reproduce**: Detailed steps
3. **Environment**: OS, Python version, Node version
4. **Logs**: Relevant log entries
5. **Screenshots**: Visual error evidence

### Contact Information
- **GitHub Issues**: [Create an issue](https://github.com/AJaySi/ALwrity/issues)
- **Documentation**: Browse guides and API reference
- **Community**: Join developer discussions

## Prevention Tips

### Regular Maintenance
1. **Update Dependencies**: Keep packages current
2. **Monitor Performance**: Regular performance checks
3. **Backup Data**: Regular database backups
4. **Security Updates**: Keep system secure

### Best Practices
1. **Environment Management**: Use virtual environments
2. **Configuration Management**: Proper .env files
3. **Error Handling**: Implement proper error handling
4. **Monitoring**: Set up performance monitoring

---

*Still having issues? Check our [GitHub Issues](https://github.com/AJaySi/ALwrity/issues) or create a new one with detailed information about your problem.*
