"""
Frontend Environment Manager
Handles updating frontend environment variables (for development purposes).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from loguru import logger
import os
from pathlib import Path

router = APIRouter(
    prefix="/api/frontend-env",
    tags=["Frontend Environment"],
)

class FrontendEnvUpdateRequest(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

@router.post("/update")
async def update_frontend_env(request: FrontendEnvUpdateRequest):
    """
    Update frontend environment variable (for development purposes).
    This writes to the frontend/.env file.
    """
    try:
        # Get the frontend directory path
        backend_dir = Path(__file__).parent.parent
        frontend_dir = backend_dir.parent / "frontend"
        env_path = frontend_dir / ".env"
        
        # Ensure the frontend directory exists
        if not frontend_dir.exists():
            raise HTTPException(status_code=404, detail="Frontend directory not found")
        
        # Read existing .env file
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the environment variable
        key_found = False
        updated_lines = []
        for line in env_lines:
            if line.startswith(f"{request.key}="):
                updated_lines.append(f"{request.key}={request.value}\n")
                key_found = True
            else:
                updated_lines.append(line)
        
        if not key_found:
            # Add comment if description provided
            if request.description:
                updated_lines.append(f"# {request.description}\n")
            updated_lines.append(f"{request.key}={request.value}\n")
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        
        logger.info(f"Updated frontend environment variable: {request.key}")
        
        return {
            "success": True,
            "message": f"Environment variable {request.key} updated successfully",
            "key": request.key,
            "value": request.value
        }
        
    except Exception as e:
        logger.error(f"Error updating frontend environment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update environment variable: {str(e)}")

@router.get("/status")
async def get_frontend_env_status():
    """
    Get status of frontend environment file.
    """
    try:
        # Get the frontend directory path
        backend_dir = Path(__file__).parent.parent
        frontend_dir = backend_dir.parent / "frontend"
        env_path = frontend_dir / ".env"
        
        if not env_path.exists():
            return {
                "exists": False,
                "path": str(env_path),
                "message": "Frontend .env file does not exist"
            }
        
        # Read and return basic info about the .env file
        with open(env_path, 'r') as f:
            content = f.read()
        
        return {
            "exists": True,
            "path": str(env_path),
            "size": len(content),
            "lines": len(content.splitlines()),
            "message": "Frontend .env file exists"
        }
        
    except Exception as e:
        logger.error(f"Error checking frontend environment status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check environment status: {str(e)}")
