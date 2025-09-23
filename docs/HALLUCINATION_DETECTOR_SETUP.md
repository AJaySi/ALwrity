# Hallucination Detector Setup Guide

This guide explains how to set up and configure the hallucination detector feature in ALwrity, which provides fact-checking capabilities using Exa.ai integration.

## 📋 **Overview**

The hallucination detector allows users to:
- Select text in the LinkedIn editor
- Check facts using AI-powered claim extraction and verification
- View confidence scores and source attribution
- Get detailed analysis of factual accuracy

## 🔧 **Backend Setup**

### **1. Environment Variables**

Add the following environment variables to your `.env` file:

```bash
# Exa.ai API Key for Hallucination Detection
EXA_API_KEY=your_exa_api_key_here

# OpenAI API Key for claim extraction and verification
OPENAI_API_KEY=your_openai_api_key_here
```

### **2. Get Exa.ai API Key**

1. Visit [Exa.ai](https://exa.ai/)
2. Sign up for an account
3. Navigate to your API dashboard
4. Generate an API key
5. Add the key to your `.env` file

### **3. Install Dependencies**

The hallucination detector uses the following Python packages (already included in requirements.txt):

```bash
pip install openai requests
```

### **4. Start the Backend**

```bash
cd backend
python start_alwrity_backend.py
```

The hallucination detector API will be available at:
- `POST /api/hallucination-detector/detect` - Main fact-checking endpoint
- `POST /api/hallucination-detector/extract-claims` - Extract claims only
- `POST /api/hallucination-detector/verify-claim` - Verify single claim
- `GET /api/hallucination-detector/health` - Health check
- `GET /api/hallucination-detector/demo` - Demo information

## 🎨 **Frontend Setup**

### **1. Environment Variables**

Add the following to your frontend `.env` file:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000
```

### **2. Start the Frontend**

```bash
cd frontend
npm start
```

## 🚀 **Usage**

### **1. In LinkedIn Editor**

1. Generate or paste content in the LinkedIn editor
2. Select any text (minimum 10 characters)
3. Click "🔍 Check Facts" in the selection menu
4. View the fact-checking results with:
   - Overall confidence score
   - Individual claim assessments
   - Supporting/refuting sources
   - Detailed reasoning

### **2. API Usage**

#### **Detect Hallucinations**

```bash
curl -X POST "http://localhost:8000/api/hallucination-detector/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Eiffel Tower is located in Paris and was built in 1889.",
    "include_sources": true,
    "max_claims": 5
  }'
```

#### **Extract Claims Only**

```bash
curl -X POST "http://localhost:8000/api/hallucination-detector/extract-claims" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Our company increased sales by 25% last quarter.",
    "max_claims": 10
  }'
```

#### **Verify Single Claim**

```bash
curl -X POST "http://localhost:8000/api/hallucination-detector/verify-claim" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "The Eiffel Tower is in Paris",
    "include_sources": true
  }'
```

## 🔍 **How It Works**

### **Three-Step Process**

1. **Claim Extraction**: Uses OpenAI to identify verifiable statements from text
2. **Evidence Search**: Uses Exa.ai to find relevant sources for each claim
3. **Claim Verification**: Uses OpenAI to assess whether sources support or refute claims

### **Assessment Types**

- **Supported**: Claim is backed by credible sources
- **Refuted**: Claim is contradicted by credible sources
- **Insufficient Information**: Not enough evidence to make a determination

### **Confidence Scores**

- **0.8-1.0**: High confidence (green)
- **0.6-0.8**: Medium confidence (orange)
- **0.0-0.6**: Low confidence (red)

## 🛠️ **Configuration Options**

### **Backend Configuration**

In `backend/services/hallucination_detector.py`:

```python
# Adjust claim extraction parameters
max_claims = 10  # Maximum claims to extract
min_claim_length = 10  # Minimum claim length

# Adjust Exa.ai search parameters
num_results = 5  # Number of sources to retrieve
use_autoprompt = True  # Use Exa's autoprompt feature
```

### **Frontend Configuration**

In `frontend/src/services/hallucinationDetectorService.ts`:

```typescript
// Adjust API timeout
const timeout = 30000; // 30 seconds

// Adjust request parameters
const defaultMaxClaims = 10;
const defaultIncludeSources = true;
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **"EXA_API_KEY not found"**
   - Ensure the API key is set in your `.env` file
   - Restart the backend server after adding the key

2. **"OpenAI API key not found"**
   - Ensure the OpenAI API key is set in your `.env` file
   - Verify the key has sufficient credits

3. **"No sources found"**
   - Check your Exa.ai API key and account status
   - Verify internet connectivity
   - Check Exa.ai service status

4. **Frontend connection errors**
   - Ensure the backend is running on the correct port
   - Check CORS configuration
   - Verify the API URL in frontend environment variables

### **Fallback Behavior**

The system includes fallback mechanisms:
- If Exa.ai is unavailable, mock sources are used
- If OpenAI is unavailable, simple keyword matching is used
- If both APIs fail, the system returns a safe error response

## 📊 **Monitoring**

### **Health Check**

```bash
curl http://localhost:8000/api/hallucination-detector/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "exa_api_available": true,
  "openai_api_available": true,
  "timestamp": "2024-01-01T12:00:00"
}
```

### **Logs**

Check backend logs for:
- API call success/failure
- Processing times
- Error messages
- Fallback activations

## 🔒 **Security Considerations**

1. **API Keys**: Store securely and never commit to version control
2. **Rate Limiting**: Respect API rate limits for Exa.ai and OpenAI
3. **Data Privacy**: Text sent to APIs may be logged by third parties
4. **Input Validation**: All user input is validated before processing

## 📈 **Performance Optimization**

1. **Caching**: Consider implementing result caching for repeated queries
2. **Batch Processing**: Process multiple claims in parallel
3. **Source Limiting**: Limit the number of sources retrieved per claim
4. **Timeout Management**: Set appropriate timeouts for API calls

## 🚀 **Future Enhancements**

Potential improvements:
- Integration with additional fact-checking APIs
- Custom claim extraction models
- Source credibility scoring
- Historical fact-checking database
- Real-time fact-checking during content generation
