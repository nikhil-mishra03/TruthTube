"""
API routes for TruthTube.
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    VideoAnalysis,
    HealthResponse,
    ErrorResponse,
    DensityResult,
    RedundancyResult,
    TitleRelevanceResult,
    OriginalityResult,
)
from app.services.youtube import youtube_service, VideoData
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    }
)
async def analyze_videos(request: AnalyzeRequest):
    """
    Analyze YouTube videos for content quality.
    
    Accepts 2-5 YouTube URLs and returns ranked analysis results.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Starting analysis session {session_id} with {len(request.urls)} URLs")
    
    try:
        # Step 1: Fetch video data (metadata + transcripts)
        logger.info("Fetching video data...")
        video_data_list = await youtube_service.get_multiple_video_data(request.urls)
        
        if len(video_data_list) < settings.min_videos_per_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not fetch data for enough videos. Need at least {settings.min_videos_per_request}, got {len(video_data_list)}"
            )
        
        # Step 2: Run LangGraph analysis workflow (parallel agents with retry)
        from app.workflow.analysis import run_analysis_workflow
        logger.info("Running LangGraph analysis workflow...")
        workflow_results = await run_analysis_workflow(video_data_list)
        
        # Step 3: Convert workflow results to VideoAnalysis objects
        analyses = _build_video_analyses(workflow_results)
        
        # Step 4: Rank videos
        logger.info("Ranking videos...")
        ranked_analyses = _rank_videos(analyses)
        
        # Step 4: Generate summary
        summary = _generate_summary(ranked_analyses)
        
        logger.info(f"Analysis complete for session {session_id}")
        
        return AnalyzeResponse(
            session_id=session_id,
            analyzed_at=datetime.utcnow(),
            videos=ranked_analyses,
            summary=summary,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def _build_video_analyses(workflow_results: list) -> List[VideoAnalysis]:
    """Convert LangGraph workflow results to VideoAnalysis objects."""
    analyses = []
    
    for result in workflow_results:
        analysis = VideoAnalysis(
            youtube_id=result["video_id"],
            title=result["title"],
            duration_seconds=result["duration_seconds"],
            thumbnail_url=result.get("thumbnail_url"),
            density=DensityResult(
                score=result["density"]["score"],
                facts_count=result["density"]["facts_count"],
                insights_per_minute=result["density"]["insights_per_minute"],
                key_facts=result["density"]["key_facts"],
            ),
            redundancy=RedundancyResult(
                score=result["redundancy"]["score"],
                filler_percentage=result["redundancy"]["filler_percentage"],
                repetition_percentage=result["redundancy"]["repetition_percentage"],
                examples=result["redundancy"]["examples"],
            ),
            title_relevance=TitleRelevanceResult(
                score=result["title_relevance"]["score"],
                is_clickbait=result["title_relevance"]["is_clickbait"],
                explanation=result["title_relevance"]["explanation"],
            ),
            originality=OriginalityResult(
                score=result["originality"]["score"],
                unique_aspects=result["originality"]["unique_aspects"],
                common_with_others=result["originality"]["common_with_others"],
            ),
        )
        analyses.append(analysis)
    
    return analyses


def _rank_videos(analyses: List[VideoAnalysis]) -> List[VideoAnalysis]:
    """
    Rank videos based on their analysis scores.
    Higher density, title relevance, originality = better.
    Lower redundancy = better.
    """
    def score_video(analysis: VideoAnalysis) -> float:
        # Weighted composite score
        return (
            analysis.density.score * 0.3 +
            (100 - analysis.redundancy.score) * 0.25 +
            analysis.title_relevance.score * 0.2 +
            analysis.originality.score * 0.25
        )
    
    # Sort by composite score (descending)
    sorted_analyses = sorted(analyses, key=score_video, reverse=True)
    
    # Assign ranks and recommendations
    for rank, analysis in enumerate(sorted_analyses, start=1):
        analysis.overall_rank = rank
        if rank == 1:
            analysis.recommendation = "🏆 Best choice - highest quality content"
        elif rank == 2:
            analysis.recommendation = "👍 Good alternative"
        else:
            analysis.recommendation = "Consider if other options don't meet your needs"
    
    return sorted_analyses


def _generate_summary(ranked_videos: List[VideoAnalysis]) -> str:
    """Generate a summary of the analysis results."""
    if not ranked_videos:
        return "No videos were analyzed."
    
    best = ranked_videos[0]
    return (
        f"Analyzed {len(ranked_videos)} videos. "
        f"Top recommendation: '{best.title[:50]}...' with "
        f"density score {best.density.score}/100 and "
        f"originality score {best.originality.score}/100."
    )
