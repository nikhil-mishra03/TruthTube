"""
Agent testing routes - for debugging and testing individual agents.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.youtube import youtube_service
from app.agents.density import density_agent
from app.agents.redundancy import redundancy_agent
from app.agents.title import title_agent
from app.agents.originality import originality_agent
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["Agent Testing"])


# ============================================================================
# Request/Response Models
# ============================================================================

class TestAgentRequest(BaseModel):
    """Request for testing any agent."""
    youtube_url: Optional[str] = None
    transcript: Optional[str] = None
    title: str = "Test Video"
    duration_seconds: int = 60


class TestOriginalityRequest(BaseModel):
    """Request for testing originality agent with multiple videos."""
    youtube_urls: List[str]


class DensityTestResponse(BaseModel):
    """Full density agent response."""
    score: int
    facts_count: int
    insights_per_minute: float
    key_facts: list
    summary: str
    raw_llm_response: dict


class RedundancyTestResponse(BaseModel):
    """Full redundancy agent response."""
    score: int
    filler_percentage: float
    repetition_percentage: float
    examples: list
    regex_fillers_found: list
    raw_llm_response: dict


class TitleTestResponse(BaseModel):
    """Full title relevance agent response."""
    score: int
    is_clickbait: bool
    explanation: str
    raw_llm_response: dict


class OriginalityTestResponse(BaseModel):
    """Full originality agent response."""
    videos: dict
    comparison_summary: str
    raw_llm_response: dict


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_video_data(request: TestAgentRequest):
    """Fetch video data from URL or use provided transcript."""
    transcript = request.transcript
    title = request.title
    duration_seconds = request.duration_seconds
    word_count = 0
    
    if request.youtube_url:
        logger.info(f"Fetching video data: {request.youtube_url}")
        video_data = await youtube_service.get_video_data(request.youtube_url)
        
        if not video_data:
            raise HTTPException(status_code=400, detail="Could not fetch video data")
        
        transcript = video_data.transcript
        title = video_data.title
        duration_seconds = video_data.duration_seconds
        word_count = video_data.word_count
    
    if not transcript:
        raise HTTPException(status_code=400, detail="Either youtube_url or transcript must be provided")
    
    if word_count == 0:
        word_count = len(transcript.split())
    
    return transcript, title, duration_seconds, word_count


# ============================================================================
# Density Agent Routes
# ============================================================================

@router.post("/density/test", response_model=DensityTestResponse)
async def test_density_agent(request: TestAgentRequest):
    """Test the density agent with a YouTube URL or raw transcript."""
    transcript, title, duration_seconds, word_count = await _get_video_data(request)
    
    logger.info(f"Running density test: {title[:50]}...")
    
    result = await density_agent.analyze(
        transcript=transcript,
        title=title,
        duration_seconds=duration_seconds,
        word_count=word_count,
    )
    
    return DensityTestResponse(
        score=result["score"],
        facts_count=result["facts_count"],
        insights_per_minute=result["insights_per_minute"],
        key_facts=result["key_facts"],
        summary=result["summary"],
        raw_llm_response=result.get("raw_llm_response", {}),
    )


@router.get("/density/info")
async def density_agent_info():
    """Get info about the density agent."""
    return {
        "agent": "DensityAgent",
        "model": density_agent.model_name,
        "description": "Analyzes information density in video transcripts",
    }


# ============================================================================
# Redundancy Agent Routes
# ============================================================================

@router.post("/redundancy/test", response_model=RedundancyTestResponse)
async def test_redundancy_agent(request: TestAgentRequest):
    """Test the redundancy agent with a YouTube URL or raw transcript."""
    transcript, title, duration_seconds, word_count = await _get_video_data(request)
    
    logger.info(f"Running redundancy test: {title[:50]}...")
    
    result = await redundancy_agent.analyze(
        transcript=transcript,
        title=title,
        duration_seconds=duration_seconds,
    )
    
    return RedundancyTestResponse(
        score=result["score"],
        filler_percentage=result["filler_percentage"],
        repetition_percentage=result["repetition_percentage"],
        examples=result["examples"],
        regex_fillers_found=result.get("regex_fillers_found", []),
        raw_llm_response=result.get("raw_llm_response", {}),
    )


@router.get("/redundancy/info")
async def redundancy_agent_info():
    """Get info about the redundancy agent."""
    return {
        "agent": "RedundancyAgent",
        "model": redundancy_agent.model_name,
        "description": "Detects filler content, repetition, and fluff",
        "regex_patterns_count": len(redundancy_agent.filler_patterns),
    }


# ============================================================================
# Title Relevance Agent Routes
# ============================================================================

@router.post("/title/test", response_model=TitleTestResponse)
async def test_title_agent(request: TestAgentRequest):
    """Test the title relevance agent with a YouTube URL or raw transcript."""
    transcript, title, duration_seconds, word_count = await _get_video_data(request)
    
    logger.info(f"Running title relevance test: {title[:50]}...")
    
    result = await title_agent.analyze(
        transcript=transcript,
        title=title,
    )
    
    return TitleTestResponse(
        score=result["score"],
        is_clickbait=result["is_clickbait"],
        explanation=result["explanation"],
        raw_llm_response=result.get("raw_llm_response", {}),
    )


@router.get("/title/info")
async def title_agent_info():
    """Get info about the title agent."""
    return {
        "agent": "TitleRelevanceAgent",
        "model": title_agent.model_name,
        "description": "Checks if content matches title, detects clickbait",
    }


# ============================================================================
# Originality Agent Routes  
# ============================================================================

@router.post("/originality/test", response_model=OriginalityTestResponse)
async def test_originality_agent(request: TestOriginalityRequest):
    """Test the originality agent with multiple YouTube URLs."""
    if len(request.youtube_urls) < 2:
        raise HTTPException(status_code=400, detail="At least 2 YouTube URLs required")
    
    logger.info(f"Running originality test with {len(request.youtube_urls)} videos...")
    
    # Fetch all video data
    videos = []
    for url in request.youtube_urls:
        video_data = await youtube_service.get_video_data(url)
        if video_data:
            videos.append({
                "video_id": video_data.youtube_id,
                "title": video_data.title,
                "transcript": video_data.transcript,
            })
    
    if len(videos) < 2:
        raise HTTPException(status_code=400, detail="Could not fetch at least 2 videos")
    
    result = await originality_agent.analyze(videos=videos)
    comparison = originality_agent.get_last_comparison()
    
    return OriginalityTestResponse(
        videos=result,
        comparison_summary=comparison.get("summary", ""),
        raw_llm_response=comparison.get("raw_response", {}),
    )


@router.get("/originality/info")
async def originality_agent_info():
    """Get info about the originality agent."""
    return {
        "agent": "OriginalityAgent",
        "model": originality_agent.model_name,
        "description": "Compares videos against each other for unique content",
    }
