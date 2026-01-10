"""
Redundancy Agent - Detects filler content, repetition, and fluff in transcripts.
"""
import re
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate

from app.agents.base import BaseAgent
from app.utils.logging import get_logger

logger = get_logger(__name__)


# Common filler phrases to detect via regex
FILLER_PATTERNS = [
    r"don'?t forget to (like|subscribe|hit)",
    r"hit that (bell|notification|like)",
    r"before we (begin|start|dive|get started)",
    r"let me know in the comments",
    r"without further ado",
    r"make sure (to|you) (subscribe|like)",
    r"if you enjoy(ed)? this",
    r"smash that like",
    r"welcome back to (my|the|this) channel",
    r"hey (guys|everyone|folks)",
    r"what'?s up (guys|everyone|folks)",
    r"in today'?s video",
    r"so yeah",
    r"you know what I mean",
    r"like I said",
    r"as I mentioned",
]


REDUNDANCY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a content quality analyst. Analyze the transcript for redundant or low-value content.

Identify:
1. REPETITION - Same concepts explained multiple times without adding new information
2. TANGENTS - Off-topic content unrelated to the video title
3. FILLER - Generic statements that don't add value (beyond obvious social media calls-to-action)

For each issue found, provide:
- type: "REPETITION" | "TANGENT" | "FILLER"
- example: A brief quote or description
- impact: "LOW" | "MEDIUM" | "HIGH"

Return JSON:
{{
    "issues": [
        {{"type": "...", "example": "...", "impact": "..."}}
    ],
    "repetition_percentage": <estimated % of content that is repeated>,
    "tangent_percentage": <estimated % that is off-topic>,
    "filler_percentage": <estimated % that is filler>,
    "summary": "Brief assessment of content quality"
}}

Be fair - some repetition for emphasis is acceptable. Focus on excessive or unnecessary redundancy."""),
    ("human", """Analyze this transcript for redundancy and filler content.

Video Title: {title}
Duration: {duration_mins:.1f} minutes

Transcript:
{transcript}

Identify redundant content. Return valid JSON only.""")
])


class RedundancyAgent(BaseAgent):
    """Agent for detecting redundancy and filler in transcripts."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filler_patterns = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]
    
    def _count_regex_fillers(self, transcript: str) -> List[str]:
        """Count filler phrases using regex patterns."""
        fillers_found = []
        for pattern in self.filler_patterns:
            matches = pattern.findall(transcript)
            if matches:
                fillers_found.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])
        return fillers_found
    
    async def analyze(
        self,
        transcript: str,
        title: str,
        duration_seconds: int,
    ) -> Dict[str, Any]:
        """
        Analyze transcript for redundancy.
        
        Args:
            transcript: Full video transcript
            title: Video title
            duration_seconds: Video duration in seconds
            
        Returns:
            Dict with redundancy analysis results
        """
        duration_mins = max(duration_seconds / 60, 0.5)
        word_count = len(transcript.split())
        
        logger.info(f"Analyzing redundancy for: {title[:50]}...")
        
        # Step 1: Regex-based filler detection
        regex_fillers = self._count_regex_fillers(transcript)
        regex_filler_count = len(regex_fillers)
        
        # Truncate transcript for LLM
        max_chars = 12000
        truncated = transcript[:max_chars]
        if len(transcript) > max_chars:
            truncated += "\n[... truncated ...]"
        
        try:
            # Step 2: LLM analysis
            result = await self._invoke_llm(
                REDUNDANCY_PROMPT,
                transcript=truncated,
                title=title,
                duration_mins=duration_mins,
            )
            
            # Combine regex and LLM findings
            repetition_pct = result.get("repetition_percentage", 0)
            tangent_pct = result.get("tangent_percentage", 0)
            llm_filler_pct = result.get("filler_percentage", 0)
            
            # Add regex fillers to filler percentage
            regex_filler_pct = (regex_filler_count / max(word_count / 10, 1)) * 5
            total_filler_pct = min(100, llm_filler_pct + regex_filler_pct)
            
            # Calculate overall redundancy score (0-100, lower is better)
            score = min(100, int(
                repetition_pct * 0.4 +
                tangent_pct * 0.3 +
                total_filler_pct * 0.3
            ))
            
            # Extract examples for display
            issues = result.get("issues", [])
            examples = [
                issue.get("example", "")[:100] 
                for issue in issues[:3]
            ]
            
            logger.info(f"Redundancy analysis complete: score={score}, rep={repetition_pct}%, filler={total_filler_pct:.1f}%")
            
            return {
                "score": score,
                "filler_percentage": round(total_filler_pct, 1),
                "repetition_percentage": round(repetition_pct, 1),
                "examples": examples if examples else ["No significant redundancy detected"],
                "raw_llm_response": result,
                "regex_fillers_found": regex_fillers[:5],  # Show first 5
            }
            
        except Exception as e:
            logger.error(f"Redundancy analysis failed: {e}")
            return {
                "score": 25,
                "filler_percentage": 10.0,
                "repetition_percentage": 15.0,
                "examples": ["Analysis failed - using default values"],
                "raw_llm_response": {},
                "regex_fillers_found": regex_fillers[:5],
            }


# Singleton instance
redundancy_agent = RedundancyAgent()
