"""
Base agent class for LLM-powered analysis.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all analysis agents."""
    
    def __init__(self, model: str = None, temperature: float = 0):
        settings = get_settings()
        self.model_name = model or settings.openai_model
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
        self.json_parser = JsonOutputParser()
        logger.info(f"Initialized {self.__class__.__name__} with model {self.model_name}")
    
    @abstractmethod
    async def analyze(self, **kwargs) -> Dict[str, Any]:
        """Run analysis and return results."""
        pass
    
    async def _invoke_llm(self, prompt: ChatPromptTemplate, **kwargs) -> Dict[str, Any]:
        """
        Invoke LLM with prompt and parse JSON response.
        
        Args:
            prompt: ChatPromptTemplate to use
            **kwargs: Variables to format into prompt
            
        Returns:
            Parsed JSON response as dict
        """
        try:
            chain = prompt | self.llm | self.json_parser
            result = await chain.ainvoke(kwargs)
            return result
        except Exception as e:
            logger.error(f"LLM invocation error: {e}")
            raise
