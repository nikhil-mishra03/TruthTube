"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ============================================================================
# Request Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request model for video analysis."""
    urls: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of 1-5 YouTube video URLs to analyze"
    )
    
    @field_validator("urls")
    @classmethod
    def validate_youtube_urls(cls, urls: List[str]) -> List[str]:
        """Validate that all URLs are valid YouTube URLs."""
        youtube_pattern = re.compile(
            r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}'
        )
        for url in urls:
            if not youtube_pattern.match(url):
                raise ValueError(f"Invalid YouTube URL: {url}")
        return urls


# ============================================================================
# Response Models
# ============================================================================

class DensityResult(BaseModel):
    """Information density analysis result."""
    score: int = Field(..., ge=0, le=100, description="Density score 0-100")
    facts_count: int = Field(..., description="Number of key facts extracted")
    insights_per_minute: float = Field(..., description="Key insights per minute")
    key_facts: List[str] = Field(default_factory=list, description="List of extracted facts")


class RedundancyResult(BaseModel):
    """Redundancy analysis result."""
    score: int = Field(..., ge=0, le=100, description="Redundancy score 0-100 (lower is better)")
    filler_percentage: float = Field(..., description="Percentage of filler content")
    repetition_percentage: float = Field(..., description="Percentage of repeated content")
    examples: List[str] = Field(default_factory=list, description="Examples of redundant content")


class TitleRelevanceResult(BaseModel):
    """Title-to-content relevance analysis result."""
    score: int = Field(..., ge=0, le=100, description="Relevance score 0-100")
    is_clickbait: bool = Field(..., description="Whether title appears to be clickbait")
    explanation: str = Field(..., description="Explanation of the assessment")


class OriginalityResult(BaseModel):
    """Originality analysis result."""
    score: int = Field(..., ge=0, le=100, description="Originality score 0-100")
    unique_aspects: List[str] = Field(default_factory=list, description="Unique aspects of this video")
    common_with_others: List[str] = Field(default_factory=list, description="Topics shared with other videos")


class VideoAnalysis(BaseModel):
    """Complete analysis result for a single video."""
    youtube_id: str
    title: str
    duration_seconds: int
    thumbnail_url: Optional[str] = None
    
    # Analysis results
    density: DensityResult
    redundancy: RedundancyResult
    title_relevance: TitleRelevanceResult
    originality: OriginalityResult
    
    # Computed fields
    overall_rank: Optional[int] = None
    recommendation: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response model for video analysis."""
    session_id: str
    analyzed_at: datetime
    videos: List[VideoAnalysis]
    summary: str = Field(..., description="Overall summary of the analysis")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
