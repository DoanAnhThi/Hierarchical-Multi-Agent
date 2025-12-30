"""Web search tool using Tavily API with DuckDuckGo fallback"""
from typing import List, Dict, Any, Optional
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.tools import Tool
import os
from ..utils.logger import logger


class WebSearchTool:
    """Enhanced web search tool with multiple providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.use_tavily = bool(self.api_key)
        
        if self.use_tavily:
            try:
                self.tavily = TavilySearchResults(
                    max_results=5,
                    search_depth="advanced",
                    include_answer=True,
                    include_raw_content=False,
                )
                logger.info("Tavily search initialized successfully")
            except Exception as e:
                logger.warning(f"Tavily initialization failed: {e}. Falling back to DuckDuckGo")
                self.use_tavily = False
        
        if not self.use_tavily:
            self.ddg = DuckDuckGoSearchAPIWrapper(max_results=5)
            logger.info("Using DuckDuckGo search")
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, url, content
        """
        try:
            if self.use_tavily:
                results = self.tavily.invoke(query)
                logger.info(f"Tavily search for '{query}' returned {len(results)} results")
                return self._format_tavily_results(results)
            else:
                results = self.ddg.run(query)
                logger.info(f"DuckDuckGo search for '{query}' completed")
                return self._format_ddg_results(results)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [{"error": str(e), "query": query}]
    
    def _format_tavily_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Format Tavily results"""
        formatted = []
        for result in results:
            formatted.append({
                'title': result.get('title', 'No title'),
                'url': result.get('url', ''),
                'content': result.get('content', ''),
                'score': result.get('score', 0)
            })
        return formatted
    
    def _format_ddg_results(self, results: str) -> List[Dict[str, Any]]:
        """Format DuckDuckGo results"""
        # DuckDuckGo returns a string, parse it
        lines = results.split('\n')
        formatted = []
        
        for i, line in enumerate(lines):
            if line.strip():
                formatted.append({
                    'title': f'Result {i+1}',
                    'url': '',
                    'content': line.strip(),
                    'score': 1.0 - (i * 0.1)
                })
        
        return formatted[:5]  # Limit to 5 results
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="web_search",
            description="Search the web for information. Use this when you need current information, facts, news, or research data. Input should be a clear search query.",
            func=lambda query: str(self.search(query))
        )


def create_web_search_tool(api_key: Optional[str] = None) -> Tool:
    """Factory function to create web search tool"""
    search_tool = WebSearchTool(api_key)
    return search_tool.as_langchain_tool()

