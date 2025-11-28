"""
Campaign Storage Service
Handles database persistence for campaigns, proposals, and assets.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.product_marketing_models import Campaign, CampaignProposal, CampaignAsset, CampaignStatus
from services.database import SessionLocal


class CampaignStorageService:
    """Service for storing and retrieving campaigns from database."""
    
    def __init__(self):
        """Initialize Campaign Storage Service."""
        self.logger = logger
        logger.info("[Campaign Storage] Service initialized")
    
    def save_campaign(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> Campaign:
        """
        Save campaign blueprint to database.
        
        Args:
            user_id: User ID
            campaign_data: Campaign blueprint data
            
        Returns:
            Saved Campaign object
        """
        db = SessionLocal()
        try:
            campaign_id = campaign_data.get('campaign_id')
            
            # Check if campaign exists
            existing = db.query(Campaign).filter(
                Campaign.campaign_id == campaign_id,
                Campaign.user_id == user_id
            ).first()
            
            if existing:
                # Update existing campaign
                existing.campaign_name = campaign_data.get('campaign_name', existing.campaign_name)
                existing.goal = campaign_data.get('goal', existing.goal)
                existing.kpi = campaign_data.get('kpi', existing.kpi)
                existing.status = campaign_data.get('status', existing.status)
                existing.phases = campaign_data.get('phases', existing.phases)
                existing.channels = campaign_data.get('channels', existing.channels)
                existing.asset_nodes = campaign_data.get('asset_nodes', existing.asset_nodes)
                existing.product_context = campaign_data.get('product_context', existing.product_context)
                db.commit()
                db.refresh(existing)
                logger.info(f"[Campaign Storage] Updated campaign {campaign_id}")
                return existing
            else:
                # Create new campaign
                campaign = Campaign(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    campaign_name=campaign_data.get('campaign_name'),
                    goal=campaign_data.get('goal'),
                    kpi=campaign_data.get('kpi'),
                    status=campaign_data.get('status', 'draft'),
                    phases=campaign_data.get('phases'),
                    channels=campaign_data.get('channels', []),
                    asset_nodes=campaign_data.get('asset_nodes', []),
                    product_context=campaign_data.get('product_context'),
                )
                db.add(campaign)
                db.commit()
                db.refresh(campaign)
                logger.info(f"[Campaign Storage] Saved new campaign {campaign_id}")
                return campaign
        except Exception as e:
            db.rollback()
            logger.error(f"[Campaign Storage] Error saving campaign: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_campaign(
        self,
        user_id: str,
        campaign_id: str
    ) -> Optional[Campaign]:
        """Get campaign by ID."""
        db = SessionLocal()
        try:
            campaign = db.query(Campaign).filter(
                Campaign.campaign_id == campaign_id,
                Campaign.user_id == user_id
            ).first()
            return campaign
        except Exception as e:
            logger.error(f"[Campaign Storage] Error getting campaign: {str(e)}")
            return None
        finally:
            db.close()
    
    def list_campaigns(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Campaign]:
        """List campaigns for user."""
        db = SessionLocal()
        try:
            query = db.query(Campaign).filter(Campaign.user_id == user_id)
            
            if status:
                query = query.filter(Campaign.status == status)
            
            campaigns = query.order_by(desc(Campaign.created_at)).limit(limit).all()
            return campaigns
        except Exception as e:
            logger.error(f"[Campaign Storage] Error listing campaigns: {str(e)}")
            return []
        finally:
            db.close()
    
    def save_proposals(
        self,
        user_id: str,
        campaign_id: str,
        proposals: Dict[str, Any]
    ) -> List[CampaignProposal]:
        """Save asset proposals for a campaign."""
        db = SessionLocal()
        try:
            # Delete existing proposals for this campaign
            db.query(CampaignProposal).filter(
                CampaignProposal.campaign_id == campaign_id,
                CampaignProposal.user_id == user_id
            ).delete()
            
            # Create new proposals
            saved_proposals = []
            for asset_id, proposal_data in proposals.get('proposals', {}).items():
                proposal = CampaignProposal(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    asset_node_id=asset_id,
                    asset_type=proposal_data.get('asset_type'),
                    channel=proposal_data.get('channel'),
                    proposed_prompt=proposal_data.get('proposed_prompt'),
                    recommended_template=proposal_data.get('recommended_template'),
                    recommended_provider=proposal_data.get('recommended_provider'),
                    recommended_model=proposal_data.get('recommended_model'),
                    cost_estimate=proposal_data.get('cost_estimate', 0.0),
                    concept_summary=proposal_data.get('concept_summary'),
                    status='proposed',
                )
                db.add(proposal)
                saved_proposals.append(proposal)
            
            db.commit()
            for proposal in saved_proposals:
                db.refresh(proposal)
            
            logger.info(f"[Campaign Storage] Saved {len(saved_proposals)} proposals for campaign {campaign_id}")
            return saved_proposals
        except Exception as e:
            db.rollback()
            logger.error(f"[Campaign Storage] Error saving proposals: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_proposals(
        self,
        user_id: str,
        campaign_id: str
    ) -> List[CampaignProposal]:
        """Get proposals for a campaign."""
        db = SessionLocal()
        try:
            proposals = db.query(CampaignProposal).filter(
                CampaignProposal.campaign_id == campaign_id,
                CampaignProposal.user_id == user_id
            ).all()
            return proposals
        except Exception as e:
            logger.error(f"[Campaign Storage] Error getting proposals: {str(e)}")
            return []
        finally:
            db.close()
    
    def update_campaign_status(
        self,
        user_id: str,
        campaign_id: str,
        status: str
    ) -> bool:
        """Update campaign status."""
        db = SessionLocal()
        try:
            campaign = db.query(Campaign).filter(
                Campaign.campaign_id == campaign_id,
                Campaign.user_id == user_id
            ).first()
            
            if campaign:
                campaign.status = status
                db.commit()
                logger.info(f"[Campaign Storage] Updated campaign {campaign_id} status to {status}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"[Campaign Storage] Error updating status: {str(e)}")
            return False
        finally:
            db.close()

