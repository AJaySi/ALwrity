from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class FacebookPage(BaseModel):
    id: str
    name: str
    access_token: str
    category: Optional[str] = None

class FacebookConnectionStatus(BaseModel):
    connected: bool
    user_id: Optional[str] = None
    pages_count: Optional[int] = None

class FacebookPublishRequest(BaseModel):
    page_id: str
    message: str
    link: Optional[str] = None

class FacebookPublishResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    permalink_url: Optional[str] = None
    error: Optional[str] = None

class FacebookTokenData(BaseModel):
    clerk_user_id: str
    user_access_token: str
    token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
