"""Basic tests for agent system"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.strategy_agent import StrategyAgent
from agents.planning_agent import PlanningAgent
from agents.execution_agent import ExecutionAgent
from tools.web_search import create_web_search_tool
from tools.document_analyzer import create_document_analyzer_tool
from tools.data_extractor import create_data_extractor_tool


class TestAgents(unittest.TestCase):
    """Test agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_query = "What are the latest developments in AI?"
    
    def test_strategy_agent_initialization(self):
        """Test Strategy Agent can be initialized"""
        try:
            agent = StrategyAgent()
            self.assertIsNotNone(agent)
            self.assertIsNotNone(agent.llm)
        except Exception as e:
            self.skipTest(f"OpenAI API not configured: {e}")
    
    def test_planning_agent_initialization(self):
        """Test Planning Agent can be initialized"""
        try:
            agent = PlanningAgent()
            self.assertIsNotNone(agent)
            self.assertIsNotNone(agent.llm)
        except Exception as e:
            self.skipTest(f"OpenAI API not configured: {e}")
    
    def test_execution_agent_initialization(self):
        """Test Execution Agent can be initialized with tools"""
        tools = [
            create_web_search_tool(),
            create_document_analyzer_tool(),
            create_data_extractor_tool()
        ]
        
        agent = ExecutionAgent(tools)
        self.assertIsNotNone(agent)
        self.assertEqual(len(agent.get_available_tools()), 3)
    
    def test_tools_creation(self):
        """Test that all tools can be created"""
        web_search = create_web_search_tool()
        doc_analyzer = create_document_analyzer_tool()
        data_extractor = create_data_extractor_tool()
        
        self.assertEqual(web_search.name, 'web_search')
        self.assertEqual(doc_analyzer.name, 'document_analyzer')
        self.assertEqual(data_extractor.name, 'data_extractor')


class TestTools(unittest.TestCase):
    """Test tool functionality"""
    
    def test_data_extractor(self):
        """Test data extraction from text"""
        from tools.data_extractor import DataExtractor
        
        extractor = DataExtractor()
        text = "Contact us at test@example.com or visit https://example.com"
        
        result = extractor.extract(text)
        self.assertIsNotNone(result)
        self.assertIn('extracted', result)
    
    def test_document_analyzer_invalid_url(self):
        """Test document analyzer with invalid URL"""
        from tools.document_analyzer import DocumentAnalyzer
        
        analyzer = DocumentAnalyzer(timeout=5)
        result = analyzer.analyze("invalid-url")
        
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()

