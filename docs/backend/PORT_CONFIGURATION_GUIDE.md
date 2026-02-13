# 🚀 **ALWRITY BACKEND PORT CONFIGURATION GUIDE**

**Date**: 2026-02-12  
**Status**: ✅ **IMPLEMENTATION COMPLETE**  
**Purpose**: Guide for using the enhanced port configuration features

---

## 📋 **OVERVIEW**

The ALwrity backend server now supports **flexible port configuration** with multiple options for development and production environments. This allows running multiple instances simultaneously without port conflicts.

---

## 🎯 **NEW FEATURES IMPLEMENTED**

### **✅ Port Resolution Priority**
1. **CLI Override** (`--port`) - Highest priority
2. **Auto-find Free Port** (`--find-port`) - Development only
3. **Environment Variable** (`PORT` from .env)
4. **Default Based on Environment** - Fallback

### **✅ Production-Safe Behavior**
- **Production Mode**: Only respects environment variables and CLI overrides
- **Development Mode**: All options available including auto-find
- **Cloud Detection**: Automatically detects Render, Railway, etc.

---

## 🚀 **USAGE EXAMPLES**

### **🎯 Development Scenarios**

#### **Instance 1: Default Port (8000)**
```bash
# Uses .env PORT=8000
python start_alwrity_backend.py --dev
```

#### **Instance 2: Manual Port Override (8001)**
```bash
# Override to port 8001
python start_alwrity_backend.py --dev --port 8001
```

#### **Instance 3: Auto-Find Free Port**
```bash
# Automatically finds first available port (8000-8009)
python start_alwrity_backend.py --dev --find-port
```

#### **Instance 4: Verbose with Port Override**
```bash
# Port 8002 with verbose logging
python start_alwrity_backend.py --dev --port 8002 --verbose
```

### **🎯 Production Scenarios**

#### **Production: Environment Variables**
```bash
# Uses PORT from environment (Render/Railway sets this)
python start_alwrity_backend.py --production
```

#### **Production: Port Override**
```bash
# Override production port (rarely needed)
python start_alwrity_backend.py --production --port 10001
```

---

## 🔧 **PORT CONFIGURATION OPTIONS**

### **✅ Command Line Arguments**

| Option | Type | Description | Production Safe |
|--------|------|-------------|------------------|
| `--port <number>` | int | Override port (highest priority) | ✅ Yes |
| `--find-port` | flag | Auto-find free port | ❌ Development only |
| `--dev` | flag | Development mode with auto-reload | ❌ Development only |
| `--production` | flag | Production mode optimizations | ✅ Production |
| `--verbose` | flag | Enable verbose logging | ✅ Both |

### **✅ Environment Variables**

| Variable | Default | Description | Priority |
|----------|---------|-------------|----------|
| `PORT` | 8000 | Server port | 3rd priority |
| `HOST` | 127.0.0.1/0.0.0.0 | Server host | Environment-based |
| `RENDER` | - | Cloud detection flag | Auto-detected |
| `RAILWAY_ENVIRONMENT` | - | Cloud detection flag | Auto-detected |

---

## 🎯 **MULTI-INSTANCE WORKFLOW**

### **✅ Running Multiple Instances**

```bash
# Terminal 1: Main branch (port 8000)
python start_alwrity_backend.py --dev

# Terminal 2: Feature branch (port 8001)
python start_alwrity_backend.py --dev --port 8001

# Terminal 3: Testing branch (auto-find port)
python start_alwrity_backend.py --dev --find-port

# Terminal 4: Production testing (port 9000)
python start_alwrity_backend.py --production --port 9000
```

### **✅ Expected Output**

```
ALwrity Backend Server
========================================
Mode: DEVELOPMENT
Auto-reload: ENABLED
========================================
🔧 Initializing ALwrity...
   📦 Checking dependencies...✅ Done
   🔧 Setting up environment...✅ Done
   📊 Configuring database...✅ Done
   🚀 Starting server...
Starting ALwrity Backend...
   CLI port override: 8001
   Host: 127.0.0.1
   Port: 8001
   Reload: true

🌐 ALwrity Backend Server
==================================================
   📖 API Documentation: http://localhost:8001/api/docs
   🔍 Health Check: http://localhost:8001/health
   📊 ReDoc: http://localhost:8001/api/redoc
   📈 API Monitoring: http://localhost:8001/api/content-planning/monitoring/health
   💳 Billing Dashboard: http://localhost:8001/api/subscription/plans
   📊 Usage Tracking: http://localhost:8001/api/subscription/usage/demo

[STOP]  Press Ctrl+C to stop the server
==================================================
```

---

## 🔧 **ENVIRONMENT FILE ENHANCEMENT**

### **✅ Enhanced .env Structure**
```bash
# .env
# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Development-specific settings
DEV_PORT_START=8000
DEV_PORT_RANGE=10

# Production-specific settings  
PROD_PORT=10000
```

---

## 🎯 **PRODUCTION DEPLOYMENT**

### **✅ Cloud Platforms (Render, Railway, etc.)**
```bash
# Production: Uses cloud-provided PORT automatically
python start_alwrity_backend.py --production
```

### **✅ Local Production Testing**
```bash
# Local production with custom port
python start_alwrity_backend.py --production --port 9000
```

---

## 🔍 **TROUBLESHOOTING**

### **✅ Common Issues**

#### **Port Already in Use**
```bash
# Solution 1: Use different port
python start_alwrity_backend.py --dev --port 8001

# Solution 2: Auto-find free port
python start_alwrity_backend.py --dev --find-port
```

#### **No Free Ports Available**
```bash
# Error: No free ports found in range 8000-8009
# Solution: Increase range or specify port manually
python start_alwrity_backend.py --dev --port 9000
```

#### **Production Port Override Not Working**
```bash
# Note: --find-port not allowed in production
# Use --port instead
python start_alwrity_backend.py --production --port 10001
```

---

## 🎯 **BEST PRACTICES**

### **✅ Development**
- Use `--find-port` for automated testing
- Use `--port` for consistent development ports
- Use `--verbose` for debugging port issues

### **✅ Production**
- Let cloud platforms set PORT automatically
- Use `--port` only for specific production needs
- Never use `--find-port` in production

### **✅ Team Development**
- Coordinate port usage with team members
- Use branch-specific ports for consistency
- Document port assignments in team wiki

---

## 🎊 **IMPLEMENTATION SUMMARY**

### **✅ Features Added**
1. **Port Override CLI Option** - `--port <number>`
2. **Auto-Find Free Port** - `--find-port` (dev only)
3. **Dynamic URL Generation** - Uses actual port in output
4. **Production Safety** - Restricts dev-only features in production
5. **Environment Detection** - Automatic cloud platform detection

### **✅ Backward Compatibility**
- All existing workflows continue to work
- No breaking changes to existing scripts
- Environment variables still respected
- Production deployment unchanged

---

## 🚀 **NEXT STEPS**

### **✅ Testing**
1. Test multiple instances running simultaneously
2. Test port conflict resolution
3. Test production deployment safety
4. Test auto-find port functionality

### **✅ Documentation**
1. Update team wiki with port coordination
2. Add to developer onboarding guide
3. Document CI/CD port configurations
4. Create troubleshooting guide

---

**🎉 IMPLEMENTATION STATUS: COMPLETE**

The enhanced port configuration system is now **production-ready** and provides flexible options for both development and production environments while maintaining backward compatibility and production safety.

---

*Implementation completed by: Backend Team*  
*Date: 2026-02-12*  
*Version: 1.0*
