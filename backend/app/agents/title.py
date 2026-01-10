"""
Title Relevance Agent - Checks if content matches title, detects clickbait.
"""
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.utils.logging import get_logger

logger = get_logger(__name__)


TITLE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a content accuracy analyst. Your job is to assess how well a video's content matches its title.

Evaluate:
1. RELEVANCE - Does the content actually cover what the title promises?
2. COMPLETENESS - Is the topic fully addressed or just touched on?
3. CLICKBAIT - Is the title sensationalized or misleading?

Scoring:
- 90-100: Title perfectly matches content
- 70-89: Title mostly accurate with minor omissions
- 50-69: Title partially accurate, some misleading elements
- 30-49: Title is misleading or only briefly covers the topic
- 0-29: Title is clickbait or completely unrelated

Return JSON:
{{
    "relevance_score": <0-100>,
    "completeness_score": <0-100>,
    "is_clickbait": <true/false>,
    "clickbait_indicators": ["list", "of", "issues"],
    "title_promise": "What the title implies",
    "content_delivery": "What was actually delivered",
    "explanation": "2-3 sentence explanation"
}}"""),
    ("human", """Analyze how well this video's content matches its title.

Video Title: {title}

Content Summary (from transcript):
{summary}

First 500 words of transcript:
{transcript_preview}

Does the content deliver on the title's promise? Return valid JSON only.""")
])


class TitleRelevanceAgent(BaseAgent):
    """Agent for analyzing title-to-content relevance."""
    
    async def analyze(
        self,
        transcript: str,
        title: str,
        summary: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze title relevance and clickbait.
        
        Args:
            transcript: Full video transcript
            title: Video title
            summary: Content summary (optional, will be generated if not provided)
            
        Returns:
            Dict with title relevance analysis
        """
        logger.info(f"Analyzing title relevance for: {title[:50]}...")
        
        # Get transcript preview (first 500 words)
        words = transcript.split()
        transcript_preview = " ".join(words[:500])
        
        # If no summary, use first and last parts of transcript
        if not summary:
            first_part = " ".join(words[:200])
            last_part = " ".join(words[-200:]) if len(words) > 400 else ""
            summary = f"Beginning: {first_part}\n\nEnding: {last_part}"
        
        try:
            result = await self._invoke_llm(
                TITLE_PROMPT,
                title=title,
                summary=summary[:2000],
                transcript_preview=transcript_preview,
            )
            
            relevance = result.get("relevance_score", 50)
            completeness = result.get("completeness_score", 50)
            is_clickbait = result.get("is_clickbait", False)
            
            # Calculate combined score
            score = int(relevance * 0.6 + completeness * 0.4)
            
            # Reduce score if clickbait
            if is_clickbait:
                score = min(score, 40)
            
            logger.info(f"Title analysis complete: score={score}, clickbait={is_clickbait}")
            
            return {
                "score": score,
                "is_clickbait": is_clickbait,
                "explanation": result.get("explanation", ""),
                "raw_llm_response": result,
            }
            
        except Exception as e:
            logger.error(f"Title analysis failed: {e}")
            return {
                "score": 75,
                "is_clickbait": False,
                "explanation": "Analysis failed - using default values",
                "raw_llm_response": {},
            }


# Singleton instance
title_agent = TitleRelevanceAgent()
