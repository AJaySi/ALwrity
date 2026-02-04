"""User Website model for ALwrity website automation."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
from loguru import logger

Base = declarative_base()

logger.debug("🔄 Loading UserWebsite model...")


class UserWebsite(Base):
    __tablename__ = "user_websites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=False)
    github_repo_url = Column(String(500), nullable=True)
    netlify_site_id = Column(String(100), nullable=True)
    netlify_site_url = Column(String(500), nullable=True)
    preview_url = Column(String(500), nullable=True)
    template_type = Column(String(50), nullable=False, default="blog")
    status = Column(String(20), nullable=False, default="initializing")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            "UserWebsite("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"template_type='{self.template_type}', "
            f"status='{self.status}'"
            ")"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "github_repo_url": self.github_repo_url,
            "netlify_site_id": self.netlify_site_id,
            "netlify_site_url": self.netlify_site_url,
            "preview_url": self.preview_url,
            "template_type": self.template_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


logger.debug("✅ UserWebsite model loaded successfully!")
