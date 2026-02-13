# Task 5: Wix Router Identification - Analysis and Migration Plan

**Document Version**: 1.0  
**Analysis Date**: 2026-02-11  
**Status**: ✅ **IDENTIFICATION COMPLETE**  
**Phase**: 2 - Unified Router Integration

---

## 🎯 **WIX OAUTH IMPLEMENTATION IDENTIFIED**

### **📍 Location Analysis**

| Component | File Path | Lines | Status |
|-----------|------------|-------|--------|
| **Wix Router** | `backend/api/wix_routes.py` | 678 lines | ✅ **Identified** |
| **Wix OAuth Service** | `backend/services/integrations/wix_oauth.py` | 313 lines | ✅ **Identified** |
| **Wix Service** | `backend/services/wix_service.py` | - | ✅ **Identified** |

### **🔍 Current Implementation Patterns**

#### **Router Structure**
```python
# Current Wix Router Pattern
router = APIRouter(prefix="/api/wix", tags=["Wix Integration"])

# Key Endpoints Identified:
@router.get("/auth/url")           # Get authorization URL
@router.post("/auth/callback")        # Handle OAuth callback (POST)
@router.get("/callback")             # Handle OAuth callback (GET with HTML)
@router.get("/connection/status")     # Get connection status
@router.get("/status")              # Get Wix status (GSC/WordPress pattern)
@router.post("/disconnect")          # Disconnect Wix account
```

#### **OAuth Service Structure**
```python
# Current Wix OAuth Service Pattern
class WixOAuthService:
    def store_tokens(...)           # Store OAuth tokens
    def get_tokens(...)            # Retrieve stored tokens
    def refresh_tokens(...)         # Refresh expired tokens
    def revoke_tokens(...)          # Revoke/delete tokens
    def is_token_valid(...)        # Check token validity
```

#### **Response Models**
```python
# Current Wix Response Models
class WixConnectionStatus(BaseModel):
    connected: bool
    has_permissions: bool
    site_info: Optional[Dict[str, Any]]
    permissions: Optional[Dict[str, Any]]
    error: Optional[str]
```

---

## 🔄 **MIGRATION STRATEGY**

### **🎯 Migration Objectives**

1. **Unified Endpoint Pattern**: Migrate from `/api/wix/*` to `/oauth/wix/*`
2. **Consistent Response Models**: Use unified OAuth response schemas
3. **Backward Compatibility**: Preserve existing endpoints with deprecation warnings
4. **Unified Client Integration**: Use `unifiedOAuthClient` for consistent patterns
5. **Fallback Safety**: Legacy service preserved as backup

### **📋 Migration Tasks**

#### **Task 5.1: Router Pattern Migration**
**Target**: `backend/api/wix_routes.py`
**Approach**: 
- Update router prefix from `/api/wix` to `/oauth/wix`
- Add deprecation warnings to existing endpoints
- Implement unified client integration with fallback
- Transform response models to unified format

#### **Task 5.2: OAuth Service Integration**
**Target**: `backend/services/integrations/wix_oauth.py`
**Approach**:
- Ensure Wix provider is registered in unified registry
- Update token storage to use unified patterns
- Maintain existing database schema for compatibility
- Add unified provider interface compliance

#### **Task 5.3: Response Model Standardization**
**Target**: Response model consistency
**Approach**:
- Map Wix-specific responses to unified OAuth schemas
- Preserve Wix-specific fields (site_info, permissions)
- Ensure token redaction in all responses
- Standardize error handling and HTTP status codes

---

## 📊 **MIGRATION IMPACT ANALYSIS**

### **Current vs Target Patterns**

| Aspect | Current Pattern | Target Pattern | Migration Impact |
|---------|------------------|------------------|------------------|
| **Router Prefix** | `/api/wix/*` | `/oauth/wix/*` | **URL Change** |
| **Auth URL** | `GET /api/wix/auth/url` | `GET /oauth/wix/auth` | **Endpoint Migration** |
| **Callback** | `POST /api/wix/auth/callback` | `POST /oauth/wix/callback` | **Endpoint Migration** |
| **Status** | `GET /api/wix/status` | `GET /oauth/wix/status` | **Endpoint Migration** |
| **Disconnect** | `POST /api/wix/disconnect` | `POST /oauth/wix/disconnect` | **Endpoint Migration** |
| **Response Format** | Wix-specific models | Unified OAuth models | **Model Migration** |

### **Complexity Assessment**

| Component | Complexity | Migration Effort | Risk Level |
|-----------|------------|------------------|------------|
| **Router Endpoints** | Medium | Low | 🟢 **Low** |
| **OAuth Service** | High | Medium | 🟡 **Medium** |
| **Response Models** | Medium | Low | 🟢 **Low** |
| **Database Schema** | Low | Minimal | 🟢 **Low** |
| **Frontend Integration** | Medium | Medium | 🟡 **Medium** |

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Router Migration (Immediate)**
1. **Update Router Registration**: Add `/oauth/wix` router alongside existing `/api/wix`
2. **Add Deprecation Headers**: Warn about old endpoint deprecation
3. **Implement Unified Client**: Use `unifiedOAuthClient` with fallback
4. **Response Transformation**: Map Wix responses to unified format

### **Phase 2: Service Integration (Next Sprint)**
1. **Registry Integration**: Ensure Wix provider in unified registry
2. **Token Storage**: Migrate to unified token patterns
3. **Permission Handling**: Standardize permission checking
4. **Error Handling**: Unified error types and responses

### **Phase 3: Cleanup (Future)**
1. **Monitor Usage**: Track old vs new endpoint usage
2. **Gradual Deprecation**: Increase deprecation warnings
3. **Legacy Removal**: Remove old endpoints after migration period
4. **Documentation Update**: Update API docs with new patterns

---

## 🎯 **SUCCESS CRITERIA**

### **Technical Requirements**
- [ ] All Wix endpoints use `/oauth/wix/*` pattern
- [ ] Consistent Pydantic response models across all providers
- [ ] Unified error handling and HTTP status codes
- [ ] Token redaction in all responses and logs
- [ ] Single frontend OAuth client for Wix operations
- [ ] Wix provider registered in unified registry
- [ ] Backward compatibility preserved during transition

### **Quality Requirements**
- [ ] Zero breaking changes for existing users
- [ ] Comprehensive test coverage for unified endpoints
- [ ] Performance parity or better than existing endpoints
- [ ] Security audit passes for unified implementation
- [ ] Documentation updated with new endpoint patterns

### **Operational Requirements**
- [ ] Monitoring in place for unified endpoints
- [ ] Analytics tracking usage patterns
- [ ] Error rates below 1% for all operations
- [ ] Response times under 200ms for all operations
- [ ] 99.9% uptime for OAuth services

---

## 📋 **NEXT ACTIONS**

### **Immediate (This Sprint)**
1. **Create Wix Unified Router**: Implement `/oauth/wix` router with unified patterns
2. **Update Wix OAuth Service**: Integrate with unified provider registry
3. **Add Deprecation Warnings**: Guide migration to new endpoints
4. **Frontend Client Update**: Create Wix unified client migration

### **Follow-up (Next Sprint)**
1. **Legacy Endpoint Monitoring**: Track usage patterns
2. **Performance Testing**: Ensure unified endpoints meet targets
3. **Security Review**: Audit unified implementation
4. **Documentation Updates**: Update API documentation

---

## 🏆 **EXPECTED OUTCOMES**

### **Developer Experience**
- ✅ **Consistent API**: Same OAuth patterns across all platforms
- ✅ **Better Documentation**: Centralized OAuth API documentation
- ✅ **Easier Testing**: Unified test patterns and mocks
- ✅ **Type Safety**: Full TypeScript support with Zod validation

### **User Experience**
- ✅ **Consistent UI**: Same OAuth flow across all platforms
- ✅ **Better Error Messages**: Clear, actionable error responses
- ✅ **Improved Reliability**: Unified error handling and retry logic
- ✅ **Enhanced Security**: Consistent token protection

### **System Benefits**
- ✅ **Reduced Complexity**: Single OAuth router for all platforms
- ✅ **Improved Maintainability**: Centralized security controls
- ✅ **Better Security**: Consistent token redaction and access controls
- ✅ **Enhanced Monitoring**: Unified logging and analytics

---

**Task 5 Status**: ✅ **IDENTIFICATION COMPLETE** - Wix OAuth implementation fully analyzed and migration strategy defined!

**Next Step**: Proceed with Wix router migration to unified OAuth patterns following the defined strategy.
