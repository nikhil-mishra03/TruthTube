"""
LangGraph workflow for video analysis orchestration.

Features:
- Parallel execution of independent agents
- Retry logic for failed LLM calls
- Typed state management
"""
import asyncio
from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass
from langgraph.graph import StateGraph, END

from app.services.youtube import VideoData
from app.agents.density import density_agent
from app.agents.redundancy import redundancy_agent
from app.agents.title import title_agent
from app.agents.originality import originality_agent
from app.utils.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# State Definition
# ============================================================================

class VideoAnalysisResult(TypedDict):
    """Analysis result for a single video."""
    video_id: str
    title: str
    duration_seconds: int
    thumbnail_url: Optional[str]
    density: Dict[str, Any]
    redundancy: Dict[str, Any]
    title_relevance: Dict[str, Any]
    originality: Dict[str, Any]


class WorkflowState(TypedDict):
    """State passed through the workflow."""
    videos: List[VideoData]
    video_results: List[Dict[str, Any]]  # Intermediate results
    analyses: List[VideoAnalysisResult]
    errors: List[str]


# ============================================================================
# Retry Helper
# ============================================================================

async def with_retry(func, *args, max_retries: int = 2, **kwargs):
    """Execute an async function with retry logic."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {e}")
                await asyncio.sleep(1)  # Brief delay before retry
            else:
                logger.error(f"All retries failed: {e}")
    raise last_error


# ============================================================================
# Workflow Nodes
# ============================================================================

async def analyze_single_video(video: VideoData) -> Dict[str, Any]:
    """
    Analyze a single video with all individual agents IN PARALLEL.
    
    Runs density, redundancy, and title analysis concurrently.
    """
    logger.info(f"Analyzing video (parallel): {video.title[:50]}...")
    
    # Run density, redundancy, and title in parallel with retry
    density_task = with_retry(
        density_agent.analyze,
        transcript=video.transcript,
        title=video.title,
        duration_seconds=video.duration_seconds,
        word_count=video.word_count,
    )
    
    redundancy_task = with_retry(
        redundancy_agent.analyze,
        transcript=video.transcript,
        title=video.title,
        duration_seconds=video.duration_seconds,
    )
    
    title_task = with_retry(
        title_agent.analyze,
        transcript=video.transcript,
        title=video.title,
    )
    
    # Execute all three in parallel
    density_result, redundancy_result, title_result = await asyncio.gather(
        density_task,
        redundancy_task,
        title_task,
        return_exceptions=True,
    )
    
    # Handle any exceptions
    failed_agents = []
    if isinstance(density_result, Exception):
        logger.error(f"Density failed: {density_result}")
        density_result = {"score": 0, "facts_count": 0, "insights_per_minute": 0, "key_facts": [], "summary": ""}
        failed_agents.append("density")
    
    if isinstance(redundancy_result, Exception):
        logger.error(f"Redundancy failed: {redundancy_result}")
        redundancy_result = {"score": 0, "filler_percentage": 10, "repetition_percentage": 15, "examples": []}
        failed_agents.append("redundancy")
    
    if isinstance(title_result, Exception):
        logger.error(f"Title failed: {title_result}")
        title_result = {"score": 0, "is_clickbait": False, "explanation": "Analysis failed"}
        failed_agents.append("title")
    
    return {
        "video": video,
        "density": density_result,
        "redundancy": redundancy_result,
        "title": title_result,
        "failed_agents": failed_agents,
    }


async def analyze_videos_node(state: WorkflowState) -> WorkflowState:
    """
    Node: Analyze all videos in parallel.
    
    Each video's individual agents also run in parallel.
    """
    logger.info(f"Starting parallel analysis for {len(state['videos'])} videos...")
    
    # Analyze all videos in parallel
    tasks = [analyze_single_video(video) for video in state["videos"]]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    video_results = []
    errors = list(state.get("errors", []))
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"Video {i} analysis failed: {result}")
            logger.error(f"Video {i} analysis failed: {result}")
        elif len(result["failed_agents"]) > 0:
            errors.append(f"Video {i} partial failure: {result['failed_agents']}")
            logger.warning(f"Video {i} partial failure: {result['failed_agents']}")
            video_results.append(result)
        else:
            video_results.append(result)
    
    logger.info(f"Parallel analysis complete: {len(video_results)} succeeded, {len(errors)} errors")
    
    return {
        **state,
        "video_results": video_results,
        "errors": errors,
    }


async def originality_node(state: WorkflowState) -> WorkflowState:
    """
    Node: Run originality comparison across all videos.
    
    Must run after individual analyses because it compares videos.
    """
    video_results = state["video_results"]
    
    if len(video_results) < 2:
        logger.info("Single video analysis - setting originality to 100")
        # Assign full originality score for single video
        for result in video_results:
            result["originality"] = {
                "score": 100,
                "unique_aspects": ["Single video - no comparison available"],
                "common_with_others": [],
            }
        return {**state, "video_results": video_results}
    
    logger.info(f"Running originality comparison for {len(video_results)} videos...")
    
    # Prepare input for originality agent
    originality_input = [
        {
            "video_id": r["video"].youtube_id,
            "title": r["video"].title,
            "transcript": r["video"].transcript,
            "summary": r["density"].get("summary", ""),
        }
        for r in video_results
    ]
    
    # Run with retry
    originality_results = await with_retry(
        originality_agent.analyze,
        videos=originality_input,
    )
    
    # Attach originality results to each video
    for result in video_results:
        video_id = result["video"].youtube_id
        result["originality"] = originality_results.get(video_id, {
            "score": 50,
            "unique_aspects": [],
            "common_with_others": [],
        })
    
    return {**state, "video_results": video_results}


async def build_results_node(state: WorkflowState) -> WorkflowState:
    """
    Node: Transform intermediate results into final analysis format.
    """
    analyses = []
    
    for result in state["video_results"]:
        video = result["video"]
        analysis = VideoAnalysisResult(
            video_id=video.youtube_id,
            title=video.title,
            duration_seconds=video.duration_seconds,
            thumbnail_url=video.thumbnail_url,
            density=result["density"],
            redundancy=result["redundancy"],
            title_relevance=result["title"],
            originality=result["originality"],
        )
        analyses.append(analysis)
    
    logger.info(f"Built {len(analyses)} final analysis results")
    
    return {**state, "analyses": analyses}


# ============================================================================
# Workflow Graph
# ============================================================================

def create_analysis_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for video analysis.
    
    Flow:
      [Start] → analyze_videos (parallel) → originality → build_results → [End]
    """
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analyze_videos", analyze_videos_node)
    workflow.add_node("originality", originality_node)
    workflow.add_node("build_results", build_results_node)
    
    # Define edges
    workflow.set_entry_point("analyze_videos")
    workflow.add_edge("analyze_videos", "originality")
    workflow.add_edge("originality", "build_results")
    workflow.add_edge("build_results", END)
    
    return workflow.compile()


# Create the compiled workflow
analysis_workflow = create_analysis_workflow()


# ============================================================================
# Public API
# ============================================================================

async def run_analysis_workflow(videos: List[VideoData]) -> List[VideoAnalysisResult]:
    """
    Run the full analysis workflow on a list of videos.
    
    Args:
        videos: List of VideoData objects with transcripts
        
    Returns:
        List of VideoAnalysisResult dicts
    """
    initial_state = WorkflowState(
        videos=videos,
        video_results=[],
        analyses=[],
        errors=[],
    )
    
    logger.info(f"Starting LangGraph workflow with {len(videos)} videos...")
    
    # Run the workflow
    final_state = await analysis_workflow.ainvoke(initial_state)
    
    if final_state["errors"]:
        logger.warning(f"Workflow completed with {len(final_state['errors'])} errors")
    
    logger.info(f"Workflow complete: {len(final_state['analyses'])} analyses produced")
    
    return final_state["analyses"]
