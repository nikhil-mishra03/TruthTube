"""
Density Agent - Analyzes information density in video transcripts.

Extracts key facts, insights, and calculates information-per-minute metrics.
"""
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.utils.logging import get_logger

logger = get_logger(__name__)


DENSITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert content analyst. Your task is to extract key information from video transcripts and assess information density.

Analyze the transcript and identify:
1. KEY FACTS - Specific, verifiable pieces of information
2. CONCEPTS - Ideas or topics that are explained in depth
3. INSIGHTS - Actionable advice or unique perspectives

For each item, rate its importance (1-3):
- 1 = Basic/common knowledge
- 2 = Useful information
- 3 = High-value insight or unique perspective

Return your analysis as JSON with this exact structure:
{{
    "facts": [
        {{"text": "brief description", "category": "FACT|CONCEPT|INSIGHT", "importance": 1-3}}
    ],
    "total_count": <number>,
    "high_value_count": <count of items with importance >= 2>,
    "summary": "2-3 sentence summary of key takeaways"
}}

Be thorough but avoid counting filler content, greetings, or promotional material as facts."""),
    ("human", """Analyze this video transcript for information density.

Video Title: {title}
Duration: {duration_mins:.1f} minutes
Word Count: {word_count} words

Transcript:
{transcript}

Extract all key facts, concepts, and insights. Return valid JSON only.""")
])


class DensityAgent(BaseAgent):
    """Agent for analyzing information density in transcripts."""
    
    async def analyze(
        self,
        transcript: str,
        title: str,
        duration_seconds: int,
        word_count: int,
    ) -> Dict[str, Any]:
        """
        Analyze transcript for information density.
        
        Args:
            transcript: Full video transcript
            title: Video title
            duration_seconds: Video duration in seconds
            word_count: Total word count
            
        Returns:
            Dict with density analysis results
        """
        duration_mins = max(duration_seconds / 60, 0.5)  # Minimum 30 seconds
        
        logger.info(f"Analyzing density for: {title[:50]}... ({duration_mins:.1f} mins)")
        
        # Truncate very long transcripts to avoid token limits
        max_chars = 15000  # ~3750 tokens
        truncated_transcript = transcript[:max_chars]
        if len(transcript) > max_chars:
            truncated_transcript += "\n[... transcript truncated ...]"
            logger.info(f"Transcript truncated from {len(transcript)} to {max_chars} chars")
        
        try:
            # Call LLM
            result = await self._invoke_llm(
                DENSITY_PROMPT,
                transcript=truncated_transcript,
                title=title,
                duration_mins=duration_mins,
                word_count=word_count,
            )
            
            # Calculate metrics
            total_count = result.get("total_count", 0)
            high_value_count = result.get("high_value_count", 0)
            facts = result.get("facts", [])
            
            # Calculate insights per minute
            insights_per_minute = round(total_count / duration_mins, 2) if duration_mins > 0 else 0
            
            # Calculate score (0-100)
            # Base score on insights per minute and quality
            # Typical good video: 2-5 insights per minute
            base_score = min(100, insights_per_minute * 20)
            
            # Boost for high-value content
            quality_boost = (high_value_count / max(total_count, 1)) * 20
            
            score = min(100, int(base_score + quality_boost))
            
            # Extract top facts for display
            key_facts = [
                f["text"] for f in sorted(
                    facts, 
                    key=lambda x: x.get("importance", 1), 
                    reverse=True
                )[:5]
            ]
            
            logger.info(f"Density analysis complete: score={score}, facts={total_count}, insights/min={insights_per_minute}")
            
            return {
                "score": score,
                "facts_count": total_count,
                "insights_per_minute": insights_per_minute,
                "key_facts": key_facts,
                "summary": result.get("summary", ""),
                "raw_llm_response": result,  # Include full LLM response for debugging
            }
            
        except Exception as e:
            logger.error(f"Density analysis failed: {e}")
            # Return fallback values
            return {
                "score": 50,
                "facts_count": 0,
                "insights_per_minute": 0,
                "key_facts": ["Analysis failed - using default values"],
                "summary": "Could not analyze transcript",
            }


# Singleton instance
density_agent = DensityAgent()
