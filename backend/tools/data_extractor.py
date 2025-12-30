"""Data extraction tool for structured data processing"""
import json
import re
from typing import Dict, Any, List, Optional
from langchain.tools import Tool
from ..utils.logger import logger


class DataExtractor:
    """Extract structured data from text"""
    
    def __init__(self):
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        }
    
    def extract(self, text: str, data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data from text
        
        Args:
            text: Input text to extract from
            data_type: Optional specific type to extract (email, url, phone, date)
            
        Returns:
            Dictionary with extracted data
        """
        try:
            if data_type and data_type in self.patterns:
                # Extract specific type
                matches = re.findall(self.patterns[data_type], text)
                result = {
                    'type': data_type,
                    'matches': matches,
                    'count': len(matches)
                }
            else:
                # Extract all types
                result = {
                    'text_length': len(text),
                    'extracted': {}
                }
                
                for dtype, pattern in self.patterns.items():
                    matches = re.findall(pattern, text)
                    if matches:
                        result['extracted'][dtype] = {
                            'matches': matches,
                            'count': len(matches)
                        }
            
            logger.info(f"Data extraction completed: {len(result.get('extracted', {}))} types found")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return {'error': str(e)}
    
    def extract_key_info(self, text: str, keys: List[str]) -> Dict[str, Any]:
        """
        Extract specific key information from text
        
        Args:
            text: Input text
            keys: List of keywords to look for
            
        Returns:
            Dictionary with found information
        """
        result = {}
        text_lower = text.lower()
        
        for key in keys:
            key_lower = key.lower()
            if key_lower in text_lower:
                # Find sentences containing the key
                sentences = text.split('.')
                relevant_sentences = [
                    s.strip() for s in sentences 
                    if key_lower in s.lower()
                ]
                result[key] = relevant_sentences[:3]  # Limit to 3 sentences
        
        return result
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="data_extractor",
            description="Extract structured data like emails, URLs, phone numbers, and dates from text. Input should be the text to extract from.",
            func=lambda text: str(self.extract(text))
        )


def create_data_extractor_tool() -> Tool:
    """Factory function to create data extractor tool"""
    extractor = DataExtractor()
    return extractor.as_langchain_tool()

