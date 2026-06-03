"""Backlink outreach router with Clerk auth."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response

from services.backlink_outreach_models import (
    BacklinkDiscoveryResponse, BacklinkKeywordInput, DeepKeywordInput,
    LeadCreateRequest, LeadStatusUpdateRequest,
    PolicyValidationRequest, PolicyValidationResponse,
    SendOutreachRequest, SendOutreachResponse,
    OutreachAttemptListResponse, OutreachAttemptRecord,
    OutreachReplyListResponse, OutreachReplyRecord,
    ScheduleFollowUpRequest, FollowUpScheduleRecord,
    EmailTemplateRequest, EmailTemplateRecord,
    GenerateEmailRequest, GeneratedEmailResponse,
    PersonalizeEmailRequest, SubjectLinesRequest, SubjectLinesResponse,
    FollowUpRequest,
    BacklinkReportingSnapshot,
    CampaignAnalyticsResponse, CampaignVolumeResponse,
    ConversionFunnelResponse, BulkStatusUpdateRequest, BulkStatusUpdateResponse,
    SuppressionAddRequest,
)
from services.backlink_outreach_service import backlink_outreach_service
from services.backlink_outreach_storage import (
    BacklinkCampaignNotFoundError,
    BacklinkOutreachStorageService,
)
from services.backlink_outreach_sender import backlink_outreach_sender
from services.backlink_outreach_reply_monitor import backlink_outreach_reply_monitor
from services.backlink_outreach_template_generator import (
    generate_outreach_email,
    generate_personalized_email,
    generate_subject_lines,
    generate_follow_up,
)
from middleware.auth_middleware import get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/backlink-outreach", tags=["backlink-outreach"])


class BacklinkCampaignCreateRequest(BaseModel):
    workspace_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=3)


def _resolve_user_id(current_user: Dict[str, Any]) -> str:
    return current_user.get("id") or current_user.get("clerk_user_id") or "default"


# -- Auth-Required Endpoints --

@router.get("/modules")
async def get_backlink_module_registry(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return {"feature": "backlink_outreach", "modules": backlink_outreach_service.list_backlink_modules()}


@router.get("/query-templates")
async def get_backlink_query_templates(
    keyword: str = Query(..., min_length=1),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return {"keyword": keyword, "queries": backlink_outreach_service.generate_guest_post_queries(keyword)}


@router.post("/discover", response_model=BacklinkDiscoveryResponse)
async def discover_backlink_opportunities(
    payload: BacklinkKeywordInput,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return await backlink_outreach_service.discover_opportunities_async(payload.keyword, payload.max_results)


@router.get("/migration-coverage")
async def get_backlink_migration_coverage(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return backlink_outreach_service.get_migration_coverage()


# -- Auth-Required Endpoints --

@router.post("/discover/deep")
async def discover_deep_backlink_opportunities(
    payload: DeepKeywordInput,
    current_user: Dict[str, Any] = Depends(get_current_user),
    scrape_timeout_seconds: float = Query(15.0, ge=1.0, le=60.0),
    scrape_max_concurrency: int = Query(5, ge=1, le=20),
):
    """Enhanced discovery using Exa neural search + DuckDuckGo with full-page scraping."""
    user_id = _resolve_user_id(current_user)
    storage = None
    if payload.campaign_id:
        storage = BacklinkOutreachStorageService()
        if not storage.get_campaign(payload.campaign_id, user_id):
            raise HTTPException(status_code=404, detail="Campaign not found")

    result = await backlink_outreach_service.deep_discover(
        payload.keyword,
        payload.max_results,
        user_id=user_id,
        scrape_timeout_seconds=scrape_timeout_seconds,
        scrape_max_concurrency=scrape_max_concurrency,
    )
    if payload.campaign_id:
        saved = 0
        save_failed = 0
        for opp in result.get("opportunities", []):
            try:
                storage.add_lead(
                    campaign_id=payload.campaign_id,
                    user_id=user_id,
                    url=opp["url"],
                    domain=opp["domain"],
                    page_title=opp.get("page_title", ""),
                    snippet=opp.get("snippet", ""),
                    email=opp.get("email"),
                    confidence_score=opp.get("confidence_score", 0.0),
                    discovery_source=opp.get("discovery_source", "duckduckgo"),
                )
                saved += 1
            except Exception:
                save_failed += 1
        result["saved_to_campaign"] = saved
        result["save_failed"] = save_failed
    return result


@router.post("/campaigns")
async def create_backlink_campaign(
    payload: BacklinkCampaignCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return storage.create_campaign(user_id, payload.workspace_id, payload.name)


@router.get("/campaigns")
async def list_backlink_campaigns(
    workspace_id: str = Query(None),
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return {"campaigns": storage.list_campaigns(user_id, workspace_id or user_id, limit)}


@router.get("/campaigns/{campaign_id}")
async def get_backlink_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get campaign detail with leads."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    campaign = storage.get_campaign(campaign_id, user_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/campaigns/{campaign_id}/leads")
async def list_campaign_leads(
    campaign_id: str,
    status: str = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List leads for a campaign, optionally filtered by status."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    leads = storage.list_leads(campaign_id, user_id, status=status or None)
    return {"leads": leads, "total": len(leads)}


@router.post("/campaigns/{campaign_id}/leads")
async def add_campaign_lead(
    campaign_id: str,
    payload: LeadCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Add a single lead to a campaign."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    try:
        lead = storage.add_lead(
            campaign_id=campaign_id,
            user_id=user_id,
            url=payload.url,
            domain=payload.domain,
            page_title=payload.page_title or "",
            snippet=payload.snippet or "",
            email=payload.email,
            confidence_score=payload.confidence_score,
            notes=payload.notes,
        )
        return lead
    except BacklinkCampaignNotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to add lead")


@router.post("/leads/bulk-status", response_model=BulkStatusUpdateResponse)
async def bulk_update_lead_status(
    payload: BulkStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Bulk update lead statuses for leads owned by the current user."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    access_issues = storage.get_lead_access_issues(
        payload.lead_ids, user_id, campaign_id=payload.campaign_id
    )
    if access_issues["unauthorized"]:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "One or more leads do not belong to the current user",
                "lead_ids": access_issues["unauthorized"],
            },
        )
    if access_issues["missing"]:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "One or more leads were not found",
                "lead_ids": access_issues["missing"],
            },
        )

    updated = 0
    failed: list[str] = []
    for lid in payload.lead_ids:
        try:
            lead = storage.update_lead_status(
                lid,
                user_id,
                payload.status,
                payload.notes,
                campaign_id=payload.campaign_id,
            )
            if lead:
                updated += 1
            else:
                failed.append(lid)
        except PermissionError:
            raise HTTPException(
                status_code=403, detail="Lead does not belong to the current user"
            )
        except Exception:
            failed.append(lid)
    return BulkStatusUpdateResponse(updated=updated, failed=failed)


@router.patch("/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update lead status (discovered -> contacted -> replied -> placed)."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    try:
        lead = storage.update_lead_status(
            lead_id,
            user_id,
            payload.status,
            payload.notes,
            campaign_id=payload.campaign_id,
        )
    except PermissionError:
        raise HTTPException(
            status_code=403, detail="Lead does not belong to the current user"
        )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/policy-validate", response_model=PolicyValidationResponse)
async def validate_outreach_policy(
    payload: PolicyValidationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    return backlink_outreach_service.validate_send_policy(payload)


@router.get("/reporting", response_model=BacklinkReportingSnapshot)
async def get_backlink_reporting_snapshot(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = _resolve_user_id(current_user)
    return backlink_outreach_service.get_reporting_snapshot(user_id=user_id)


# -- Outreach Attempts --

@router.post("/send-outreach", response_model=SendOutreachResponse)
async def send_outreach(
    payload: SendOutreachRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Validate policy, record attempt, personalize, and send email."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    subject = payload.subject
    body = payload.body

    if payload.template_id:
        tmpl = storage.get_template(payload.template_id, user_id)
        if tmpl:
            variables = payload.template_variables or {}
            subject = backlink_outreach_sender.personalize(tmpl.get("subject_template", subject), variables)
            body = backlink_outreach_sender.personalize(tmpl.get("body_template", body), variables)

    result = backlink_outreach_service.send_outreach(
        SendOutreachRequest(
            lead_id=payload.lead_id,
            campaign_id=payload.campaign_id,
            user_id=user_id,
            workspace_id=payload.workspace_id,
            sender_email=payload.sender_email,
            subject=subject,
            body=body,
            idempotency_key=payload.idempotency_key,
        )
    )

    lead_email = ""
    if result.attempt_id:
        lead = storage.get_lead(payload.lead_id, user_id=user_id)
        lead_email = (lead.get("email") or "") if lead else ""

    if result.policy_allowed and lead_email:
        sent = await backlink_outreach_sender.send_email(
            to_email=lead_email,
            subject=subject,
            body=body,
        )
        status = "sent" if sent else "failed"
        storage.update_attempt_status(result.attempt_id, status, user_id=user_id)
        result.status = status
        if sent:
            storage.mark_idempotency(payload.idempotency_key, user_id)
            storage.increment_user_send_counter(user_id)
            domain = lead_email.split("@")[-1] if "@" in lead_email else "unknown"
            storage.increment_domain_send_counter(domain, user_id=user_id)
    elif result.policy_allowed and not lead_email:
        storage.update_attempt_status(result.attempt_id, "failed", user_id=user_id)
        result.status = "failed"
        result.policy_reasons = (result.policy_reasons or []) + ["lead_has_no_email"]

    return result


@router.get("/campaigns/{campaign_id}/attempts", response_model=OutreachAttemptListResponse)
async def list_campaign_attempts(
    campaign_id: str,
    limit: int = Query(50),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List outreach attempts for a campaign."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    attempts = storage.list_attempts(campaign_id, limit, user_id=user_id)
    return {"attempts": attempts, "total": len(attempts)}


# -- Replies --

@router.get("/campaigns/{campaign_id}/replies", response_model=OutreachReplyListResponse)
async def list_campaign_replies(
    campaign_id: str,
    limit: int = Query(50),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List received replies for a campaign."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    replies = storage.list_replies(campaign_id, limit, user_id=user_id)
    return {"replies": replies, "total": len(replies)}


@router.post("/replies/poll")
async def poll_replies(
    sent_from_email: str = Query(..., min_length=3),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Poll IMAP inbox for new replies and store them."""
    user_id = _resolve_user_id(current_user)
    if not backlink_outreach_reply_monitor.is_configured():
        raise HTTPException(status_code=503, detail="IMAP not configured")

    storage = BacklinkOutreachStorageService()
    raw_replies = await backlink_outreach_reply_monitor.poll_replies(sent_from_email)
    stored = []
    skipped = 0
    failed = 0
    for raw in raw_replies:
        try:
            from_email = raw.get("from_email", "")
            subject = raw.get("subject", "")
            if storage.reply_exists(from_email, subject, user_id=user_id):
                skipped += 1
                continue
            attempt_id = storage.find_attempt_by_from_email(from_email, user_id=user_id) or ""
            reply = storage.add_reply(
                attempt_id=attempt_id,
                from_email=from_email,
                subject=subject,
                body=raw.get("body", ""),
                classification=raw.get("classification", "replied"),
                user_id=user_id,
            )
            stored.append(reply)
        except Exception:
            failed += 1
    return {"polled": len(raw_replies), "stored": len(stored), "skipped": skipped, "failed": failed, "replies": stored}


# -- Follow-ups --

@router.post("/campaigns/{campaign_id}/schedule-followup")
async def schedule_followup(
    campaign_id: str,
    payload: ScheduleFollowUpRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Schedule a follow-up for an outreach attempt."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    sched = storage.schedule_followup(
        attempt_id=payload.attempt_id,
        scheduled_for=payload.scheduled_for,
        subject=payload.subject or "",
        body=payload.body or "",
        user_id=user_id,
    )
    return {"campaign_id": campaign_id, "schedule": sched}


@router.get("/campaigns/{campaign_id}/followups")
async def list_followups(
    campaign_id: str,
    limit: int = Query(50),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List scheduled follow-ups for a campaign."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    followups = storage.list_followups(campaign_id, limit, user_id=user_id)
    return {"followups": followups, "total": len(followups)}


# -- Email Templates --

@router.post("/templates")
async def create_template(
    payload: EmailTemplateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Create an email template."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return storage.create_template(
        user_id=user_id,
        name=payload.name,
        subject_template=payload.subject_template,
        body_template=payload.body_template,
        variables=payload.variables,
    )


@router.get("/templates")
async def list_templates(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List email templates for the authenticated user."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return {"templates": storage.list_templates(user_id)}


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get a specific email template."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    tmpl = storage.get_template(template_id, user_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tmpl


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete an email template."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    if not storage.delete_template(template_id, user_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"deleted": True}


@router.post("/templates/generate", response_model=GeneratedEmailResponse)
async def generate_email_template(
    payload: GenerateEmailRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Generate an outreach email using AI."""
    user_id = _resolve_user_id(current_user)
    existing_body = None
    if payload.existing_template_id:
        storage = BacklinkOutreachStorageService()
        tmpl = storage.get_template(payload.existing_template_id, user_id)
        if tmpl:
            existing_body = tmpl.get("body_template")

    result = generate_outreach_email(
        topic=payload.topic,
        target_site=payload.target_site,
        tone=payload.tone,
        user_id=user_id,
        existing_body=existing_body,
    )
    return result


@router.post("/generate/personalized", response_model=GeneratedEmailResponse)
async def generate_personalized_email_endpoint(
    payload: PersonalizeEmailRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Personalize an outreach email for a specific lead."""
    user_id = _resolve_user_id(current_user)
    result = generate_personalized_email(
        lead_name=payload.lead_name,
        lead_site=payload.lead_site,
        lead_content_topic=payload.lead_content_topic,
        pitch_topic=payload.pitch_topic,
        existing_body=payload.existing_body,
        user_id=user_id,
    )
    return result


@router.post("/generate/subject-lines", response_model=SubjectLinesResponse)
async def generate_subject_lines_endpoint(
    payload: SubjectLinesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Generate subject line suggestions for an email body."""
    user_id = _resolve_user_id(current_user)
    subjects = generate_subject_lines(
        body=payload.body,
        count=payload.count,
        user_id=user_id,
    )
    return {"subjects": subjects}


@router.post("/generate/follow-up", response_model=GeneratedEmailResponse)
async def generate_follow_up_endpoint(
    payload: FollowUpRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Generate a follow-up email for an outreach attempt."""
    user_id = _resolve_user_id(current_user)
    result = generate_follow_up(
        original_subject=payload.original_subject,
        original_body=payload.original_body,
        days_elapsed=payload.days_elapsed,
        reply_context=payload.reply_context,
        user_id=user_id,
    )
    return result


# -- Suppression --

@router.get("/suppression")
async def list_suppression(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List suppressed recipients."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return {"suppressed": storage.list_suppressed(user_id)}


@router.post("/suppression")
async def add_suppression(
    payload: SuppressionAddRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Add a recipient to the suppression list."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return storage.add_suppressed(email=payload.email, domain=payload.domain, reason=payload.reason, user_id=user_id)


@router.get("/campaigns/{campaign_id}/analytics/volume", response_model=CampaignVolumeResponse)
async def get_campaign_analytics_volume(
    campaign_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get daily send volume for a campaign over the last N days."""
    user_id = _resolve_user_id(current_user)
    return backlink_outreach_service.get_campaign_volume(campaign_id, days, user_id=user_id)


@router.get("/campaigns/{campaign_id}/analytics/funnel", response_model=ConversionFunnelResponse)
async def get_campaign_analytics_funnel(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get conversion funnel (lead status breakdown) for a campaign."""
    user_id = _resolve_user_id(current_user)
    return backlink_outreach_service.get_campaign_funnel(campaign_id, user_id=user_id)


@router.get("/campaigns/{campaign_id}/export/leads")
async def export_campaign_leads_csv(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Export campaign leads as CSV."""
    user_id = _resolve_user_id(current_user)
    csv_content = backlink_outreach_service.export_leads_csv(campaign_id, user_id=user_id)
    return Response(content=csv_content, media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=leads_{campaign_id}.csv"})


@router.get("/campaigns/{campaign_id}/export/attempts")
async def export_campaign_attempts_csv(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Export campaign outreach attempts as CSV."""
    user_id = _resolve_user_id(current_user)
    csv_content = backlink_outreach_service.export_attempts_csv(campaign_id, user_id=user_id)
    return Response(content=csv_content, media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=attempts_{campaign_id}.csv"})


@router.get("/campaigns/{campaign_id}/export/replies")
async def export_campaign_replies_csv(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Export campaign replies as CSV."""
    user_id = _resolve_user_id(current_user)
    csv_content = backlink_outreach_service.export_replies_csv(campaign_id, user_id=user_id)
    return Response(content=csv_content, media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=replies_{campaign_id}.csv"})


# -- Audit Log --

@router.get("/audit-logs")
async def list_audit_logs(
    campaign_id: str = Query(None),
    limit: int = Query(100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """List audit log entries, optionally filtered by campaign."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    return {"logs": storage.list_audit_logs(campaign_id or None, limit, user_id=user_id)}


# -- Analytics --

@router.get("/campaigns/{campaign_id}/analytics", response_model=CampaignAnalyticsResponse)
async def get_campaign_analytics(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get campaign analytics: send volume, response/placement rates, reply breakdown."""
    user_id = _resolve_user_id(current_user)
    storage = BacklinkOutreachStorageService()
    campaign = storage.get_campaign(campaign_id, user_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    attempts = storage.list_attempts(campaign_id, user_id=user_id)
    replies = storage.list_replies(campaign_id, user_id=user_id)
    leads = storage.list_leads_all(campaign_id, user_id=user_id)

    total_sent = sum(1 for a in attempts if a.get("status") == "sent")
    total_blocked = sum(1 for a in attempts if a.get("status") == "blocked")
    total_replied = len(replies)
    total_placed = sum(1 for l in leads if l.get("status") == "placed")

    reply_classification = {}
    for r in replies:
        cls = r.get("classification", "replied")
        reply_classification[cls] = reply_classification.get(cls, 0) + 1

    return CampaignAnalyticsResponse(
        campaign_id=campaign_id,
        lead_count=campaign.get("lead_count", 0),
        send_volume=total_sent,
        blocked_count=total_blocked,
        reply_count=total_replied,
        response_rate=round(total_replied / total_sent, 4) if total_sent > 0 else 0.0,
        placement_rate=round(total_placed / campaign.get("lead_count", 1), 4) if campaign.get("lead_count", 0) > 0 else 0.0,
        reply_classification=reply_classification,
    )