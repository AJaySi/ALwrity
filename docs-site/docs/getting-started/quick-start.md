# Quick Start Guide

Get up and running with ALwrity in just a few minutes! This guide will help you set up the platform and create your first AI-generated content.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** installed on your system
- **Node.js 18+** for the frontend
- **API Keys** for AI services (Gemini, OpenAI, etc.)
- **Git** for version control

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AJaySi/ALwrity.git
cd ALwrity
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the backend directory:

```bash
# AI Service API Keys
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database
DATABASE_URL=sqlite:///./alwrity.db

# Security
SECRET_KEY=your_secret_key
```

### 2. Frontend Configuration

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_key
REACT_APP_COPILOTKIT_API_KEY=your_copilot_key
```

## Running the Application

### 1. Start the Backend

```bash
cd backend
python start_alwrity_backend.py
```

The backend will be available at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Your First Content

### 1. Access the Dashboard

Navigate to `http://localhost:3000` and complete the onboarding process.

### 2. Create a Blog Post

1. Go to **Blog Writer**
2. Enter your topic or keyword
3. Click **Generate Content**
4. Review and edit the generated content
5. Use the **SEO Analysis** feature to optimize

### 3. LinkedIn Content

1. Navigate to **LinkedIn Writer**
2. Select content type (post, article, carousel)
3. Provide your topic and target audience
4. Generate and customize your content

## Next Steps

- **[Configuration Guide](configuration.md)** - Advanced configuration options
- **[First Steps](first-steps.md)** - Detailed walkthrough of key features
- **[API Reference](../api/overview.md)** - Integrate with your applications
- **[Best Practices](../guides/best-practices.md)** - Optimize your content strategy

## Troubleshooting

If you encounter any issues:

1. Check the [Troubleshooting Guide](../guides/troubleshooting.md)
2. Verify your API keys are correctly set
3. Ensure all dependencies are installed
4. Check the console for error messages

## Need Help?

- **GitHub Issues**: [Report bugs and request features](https://github.com/AJaySi/ALwrity/issues)
- **Documentation**: Browse our comprehensive guides
- **Community**: Join our developer community

---

*Ready to create amazing content? Check out our [First Steps Guide](first-steps.md) for a detailed walkthrough!*
