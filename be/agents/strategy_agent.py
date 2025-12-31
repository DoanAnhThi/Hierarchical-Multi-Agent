"""Strategy Agent - High-level planning and decision making"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from utils.logger import logger


class StrategyAgent:
    """
    Strategy Agent: Determines the overall approach to handle user queries
    Decides what type of research/analysis is needed
    """
    
    def __init__(self, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Strategy Agent in a hierarchical multi-agent system.
Your role is to analyze user queries and determine the best high-level approach.

Consider:
1. What type of information is needed? (current events, research, analysis, factual data)
2. What resources should be used? (web search, document analysis, data extraction)
3. What is the complexity level? (simple lookup, multi-step research, deep analysis)
4. What is the expected output format?

Provide a clear, structured strategy in JSON format with:
- approach: overall strategy description
- complexity: simple/moderate/complex
- required_resources: list of tools needed
- subtasks: list of high-level tasks to accomplish
- expected_output: description of final output format

Be concise and actionable."""),
            ("human", "User Query: {query}\n\nProvide your strategic analysis:")
        ])
    
    def analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze query and determine strategy
        
        Args:
            query: User's question or request
            context: Optional context from previous interactions
            
        Returns:
            Strategy dictionary with approach and subtasks
        """
        try:
            logger.info(f"Strategy Agent analyzing query: {query[:100]}...")
            
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse the response
            strategy = self._parse_strategy(response.content)
            strategy['agent'] = 'strategy'
            strategy['query'] = query
            
            logger.info(f"Strategy determined: {strategy['approach'][:100]}...")
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy Agent error: {e}")
            # Fallback strategy
            return {
                'agent': 'strategy',
                'approach': 'Simple web search and summarization',
                'complexity': 'simple',
                'required_resources': ['web_search'],
                'subtasks': ['Search for information', 'Summarize findings'],
                'expected_output': 'Summary of search results',
                'error': str(e)
            }
    
    def _parse_strategy(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured strategy"""
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback parsing
        return {
            'approach': content[:500] if len(content) > 500 else content,
            'complexity': 'moderate',
            'required_resources': ['web_search', 'document_analyzer'],
            'subtasks': ['Research', 'Analyze', 'Synthesize'],
            'expected_output': 'Comprehensive answer'
        }
    
    def synthesize_results(self, planning_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final results from planning agent
        
        Args:
            planning_output: Results from planning agent
            
        Returns:
            Final synthesized response
        """
        try:
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are synthesizing research results into a final answer.
Create a clear, comprehensive response that:
1. Directly answers the user's question
2. Incorporates key findings from research
3. Provides relevant details and context
4. Is well-structured and easy to read

Format your response with:
- Clear main answer
- Supporting details
- Sources/references when applicable"""),
                ("human", """Original Query: {query}

Research Results:
{results}

Provide a synthesized final answer:""")
            ])
            
            chain = synthesis_prompt | self.llm
            response = chain.invoke({
                "query": planning_output.get('query', ''),
                "results": str(planning_output.get('execution_results', []))
            })
            
            return {
                'agent': 'strategy',
                'stage': 'synthesis',
                'final_answer': response.content,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {
                'agent': 'strategy',
                'stage': 'synthesis',
                'final_answer': str(planning_output.get('execution_results', [])),
                'status': 'error',
                'error': str(e)
            }

