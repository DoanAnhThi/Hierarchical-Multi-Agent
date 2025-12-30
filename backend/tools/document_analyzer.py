"""Document analyzer for extracting and analyzing content from URLs"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from langchain.tools import Tool
from ..utils.logger import logger


class DocumentAnalyzer:
    """Analyze documents and web pages"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Extract and analyze content from URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with title, content, summary, and metadata
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else 'No title'
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Extract metadata
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            result = {
                'url': url,
                'title': title_text,
                'description': description,
                'content': content[:2000],  # Limit content length
                'content_length': len(content),
                'has_content': bool(content)
            }
            
            logger.info(f"Analyzed document from {url}: {len(content)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document from {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'has_content': False
            }
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if main_content:
            # Get text and clean it up
            text = main_content.get_text(separator='\n', strip=True)
            # Remove excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
        
        return ''
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="document_analyzer",
            description="Analyze and extract content from web pages and documents. Use this to get detailed information from a specific URL. Input should be a valid URL.",
            func=lambda url: str(self.analyze(url))
        )


def create_document_analyzer_tool(timeout: int = 10) -> Tool:
    """Factory function to create document analyzer tool"""
    analyzer = DocumentAnalyzer(timeout)
    return analyzer.as_langchain_tool()

