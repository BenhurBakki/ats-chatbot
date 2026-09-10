"""
FastAPI Routes for REST API, Batch Processing, Channel Webhooks, and Live Simulator.
"""

from fastapi import APIRouter, Request, Query, HTTPException, Form, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from core.ats_analyzer import ATSAnalyzer, BatchATSQueue
from core.courses_db import COURSE_CATALOG
from adapters.channel_manager import channel_manager
from adapters.whatsapp_adapter import WhatsAppAdapter
from adapters.slack_adapter import SlackAdapter
from adapters.instagram_adapter import InstagramAdapter

router = APIRouter()
analyzer = ATSAnalyzer()
batch_queue = BatchATSQueue()

# Pydantic Schemas
class AnalyzeRequest(BaseModel):
    job_description: str = Field(..., description="Full text or summary of Job Description")
    resume: str = Field(..., description="Full text of Candidate Resume")
    role_hint: Optional[str] = Field(None, description="Optional explicit role name")
    candidate_hint: Optional[str] = Field(None, description="Optional explicit candidate name")

class BatchItem(BaseModel):
    jd: str
    resume: str
    role_hint: Optional[str] = None
    candidate_hint: Optional[str] = None

class BatchAnalyzeRequest(BaseModel):
    items: List[BatchItem]

class ChatSimulateRequest(BaseModel):
    channel: str = Field(..., description="whatsapp, slack, instagram, or web")
    user_id: str = Field("sim_user_01", description="Unique user/session ID")
    message: str = Field(..., description="User message text")


# 1. Health Endpoint
@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ATS Optimization & Tracking Bot",
        "channels_supported": ["whatsapp", "slack", "instagram", "web_api"],
        "version": "1.0.0"
    }

# 2. REST API: Single Analyze
@router.post("/api/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    result = analyzer.analyze(
        jd_text=req.job_description,
        resume_text=req.resume,
        role_hint=req.role_hint or "",
        candidate_hint=req.candidate_hint or ""
    )
    return result

# 3. REST API: Batch Analyze (Prioritized in order received)
@router.post("/api/batch-analyze")
def batch_analyze_endpoint(req: BatchAnalyzeRequest):
    raw_items = [item.dict() for item in req.items]
    results = batch_queue.process_batch(raw_items)
    return {
        "total_processed": len(results),
        "results": results
    }

# 4. Multi-Channel Chat Simulator API
@router.post("/api/chat-simulate")
def chat_simulate_endpoint(req: ChatSimulateRequest):
    response = channel_manager.handle_message(
        user_id=req.user_id,
        channel=req.channel,
        text=req.message
    )
    return response

# 5. Course Catalog Listing
@router.get("/api/courses")
def get_courses():
    return {"catalog": list(COURSE_CATALOG.values())}

# 6. Meta WhatsApp Webhooks
@router.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    challenge = WhatsAppAdapter.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request):
    payload = await request.json()
    res = WhatsAppAdapter.handle_meta_webhook(payload)
    return res

# 7. Meta Instagram Webhooks
@router.get("/webhook/instagram")
def verify_instagram_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    challenge = InstagramAdapter.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook/instagram")
async def handle_instagram_webhook(request: Request):
    payload = await request.json()
    res = InstagramAdapter.handle_webhook_payload(payload)
    return res

# 8. Slack Events & Commands Webhooks
@router.post("/webhook/slack")
async def handle_slack_events(request: Request):
    payload = await request.json()
    res = SlackAdapter.handle_events_payload(payload)
    return res

@router.post("/webhook/slack/command")
async def handle_slack_command(request: Request):
    form_data = await request.form()
    dict_form = dict(form_data)
    res = SlackAdapter.handle_slash_command(dict_form)
    return res
