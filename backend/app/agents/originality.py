"""
Originality Agent - Compares videos against each other for unique content.
"""
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.utils.logging import get_logger

logger = get_logger(__name__)


ORIGINALITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a content comparison analyst. Compare multiple video summaries to identify which offers the most unique and original perspectives.

For each video, assess:
1. UNIQUE_ASPECTS - What insights/perspectives does this video offer that others don't?
2. COMMON_CONTENT - What content is shared across multiple videos?
3. ORIGINALITY_SCORE - How original is this video compared to the others? (0-100)

Consider:
- Unique examples or case studies
- Novel explanations or analogies
- Different angles on the topic
- Depth vs breadth of coverage

Return JSON:
{{
    "videos": [
        {{
            "video_id": "...",
            "originality_score": <0-100>,
            "unique_aspects": ["list of unique points"],
            "common_with_others": ["points shared with other videos"],
            "standout_reason": "Why this video stands out (or doesn't)"
        }}
    ],
    "most_original": "<video_id of most original>",
    "comparison_summary": "Brief summary of how videos compare"
}}"""),
    ("human", """Compare these videos for originality. All cover similar topics.

{video_summaries}

Which video offers the most original perspective? Return valid JSON only.""")
])


class OriginalityAgent(BaseAgent):
    """Agent for comparing videos and assessing originality."""
    
    async def analyze(
        self,
        videos: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple videos for originality.
        
        Args:
            videos: List of dicts with {video_id, title, summary/transcript}
            
        Returns:
            Dict mapping video_id to originality results
        """
        if len(videos) < 2:
            logger.warning("Originality analysis requires at least 2 videos")
            # Return default scores for single video
            if videos:
                return {
                    videos[0]["video_id"]: {
                        "score": 70,
                        "unique_aspects": ["Only video in comparison"],
                        "common_with_others": [],
                        "raw_llm_response": {},
                    }
                }
            return {}
        
        logger.info(f"Analyzing originality across {len(videos)} videos...")
        
        # Build video summaries for prompt
        summaries_text = ""
        for i, video in enumerate(videos, 1):
            # Get summary - use first 300 words of transcript if no summary
            summary = video.get("summary", "")
            if not summary and video.get("transcript"):
                words = video["transcript"].split()[:300]
                summary = " ".join(words)
            
            summaries_text += f"""
Video {i}:
- ID: {video['video_id']}
- Title: {video['title']}
- Summary: {summary[:500]}...

"""
        
        try:
            result = await self._invoke_llm(
                ORIGINALITY_PROMPT,
                video_summaries=summaries_text,
            )
            
            # Parse results into per-video dict
            video_results = {}
            for video_data in result.get("videos", []):
                vid_id = video_data.get("video_id", "")
                video_results[vid_id] = {
                    "score": video_data.get("originality_score", 50),
                    "unique_aspects": video_data.get("unique_aspects", []),
                    "common_with_others": video_data.get("common_with_others", []),
                    "raw_llm_response": video_data,
                }
            
            # If LLM didn't return all videos, add defaults
            for video in videos:
                vid_id = video["video_id"]
                if vid_id not in video_results:
                    video_results[vid_id] = {
                        "score": 50,
                        "unique_aspects": [],
                        "common_with_others": [],
                        "raw_llm_response": {},
                    }
            
            logger.info(f"Originality analysis complete. Most original: {result.get('most_original', 'N/A')}")
            
            # Store comparison summary for reference
            self._last_comparison_summary = result.get("comparison_summary", "")
            self._last_raw_response = result
            
            return video_results
            
        except Exception as e:
            logger.error(f"Originality analysis failed: {e}")
            # Return defaults for all videos
            return {
                video["video_id"]: {
                    "score": 50,
                    "unique_aspects": ["Analysis failed"],
                    "common_with_others": [],
                    "raw_llm_response": {},
                }
                for video in videos
            }
    
    def get_last_comparison(self) -> Dict[str, Any]:
        """Get the full response from the last comparison."""
        return {
            "summary": getattr(self, "_last_comparison_summary", ""),
            "raw_response": getattr(self, "_last_raw_response", {}),
        }


# Singleton instance
originality_agent = OriginalityAgent()
