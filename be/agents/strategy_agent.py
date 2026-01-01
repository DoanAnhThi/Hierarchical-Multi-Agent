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

            # Check for simple conversational queries
            simple_queries = [
                'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
                'good evening', 'how are you', 'how do you do', 'what\'s up',
                'thanks', 'thank you', 'bye', 'goodbye', 'see you', 'later',
                'ok', 'okay', 'yes', 'no', 'sure', 'of course', 'maybe',
                'please', 'help', 'sorry', 'excuse me', 'pardon'
            ]

            query_lower = query.lower().strip()
            word_count = len(query.split())

            # Conversational if:
            # 1. Very short (≤3 words) AND contains conversational words
            # 2. Exact match with conversational phrases
            # 3. Very short queries (< 10 chars) AND no question marks
            is_simple_conversation = (
                (word_count <= 3 and any(word in query_lower for word in simple_queries)) or
                query_lower in simple_queries or
                (len(query.strip()) < 10 and '?' not in query)
            )

            if is_simple_conversation:
                logger.info("Detected simple conversational query - using direct LLM response")
                return {
                    'agent': 'strategy',
                    'query': query,
                    'approach': 'Direct conversational response',
                    'complexity': 'simple',
                    'required_resources': [],
                    'subtasks': ['Generate friendly response'],
                    'expected_output': 'Conversational reply',
                    'is_conversational': True
                }

            # For complex queries, use LLM analysis
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})

            # Parse the response
            strategy = self._parse_strategy(response.content)
            strategy['agent'] = 'strategy'
            strategy['query'] = query
            strategy['is_conversational'] = False

            logger.info(f"Strategy determined: {strategy['approach'][:100]}...")
            return strategy

        except Exception as e:
            logger.error(f"Strategy Agent error: {e}")
            # Fallback strategy - include original query
            return {
                'agent': 'strategy',
                'query': query,  # Include original query
                'approach': 'Simple web search and summarization',
                'complexity': 'simple',
                'required_resources': ['web_search'],
                'subtasks': ['Search for information', 'Summarize findings'],
                'expected_output': 'Summary of search results',
                'error': str(e),
                'is_conversational': False
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
            # Handle conversational responses directly
            if planning_output.get('is_conversational', False) or \
               any(task.get('tool') == 'direct_llm' for task in planning_output.get('execution_results', [])):
                execution_results = planning_output.get('execution_results', [])
                if execution_results and len(execution_results) > 0:
                    task_result = execution_results[0]
                    if isinstance(task_result, dict) and 'result' in task_result:
                        final_answer = task_result['result']
                    else:
                        final_answer = str(task_result)

                    return {
                        'agent': 'strategy',
                        'stage': 'synthesis',
                        'final_answer': final_answer,
                        'status': 'completed',
                        'is_conversational': True
                    }

            # For research queries, synthesize results into natural language
            execution_results = planning_output.get('execution_results', [])
            query = planning_output.get('query', '')

            if not execution_results:
                return {
                    'agent': 'strategy',
                    'stage': 'synthesis',
                    'final_answer': "I wasn't able to find any information for your query. Please try rephrasing your question.",
                    'status': 'completed',
                    'is_conversational': False
                }

            # For now, use direct extraction to avoid API quota issues
            # TODO: Re-enable LLM synthesis when API quota is available
            # try:
            #     synthesis_prompt = f"""Based on the following research results, provide a natural language answer to: "{query}"
            #
            # Research Results: {str(execution_results)[:2000]}...
            #
            # Please provide a concise, natural language summary."""
            #
            #     synthesis_chain = ChatPromptTemplate.from_messages([
            #         ("system", "You are a helpful AI assistant. Provide clear, natural language answers based on research results. Keep responses informative but concise."),
            #         ("human", synthesis_prompt)
            #     ]) | self.llm
            #
            #     response = synthesis_chain.invoke({})
            #
            #     return {
            #         'agent': 'strategy',
            #         'stage': 'synthesis',
            #         'final_answer': response.content.strip(),
            #         'status': 'completed',
            #         'is_conversational': False
            #     }
            #
            # except Exception as e:
            #     logger.error(f"Synthesis LLM error: {e}")

            # Extract and synthesize information from search results
            all_content = []
            for task_result in execution_results:
                if isinstance(task_result, dict) and 'result' in task_result:
                    result_data = task_result['result']
                    if isinstance(result_data, list):
                        for item in result_data[:3]:  # Take top 3 results per task
                            if isinstance(item, dict) and 'content' in item:
                                content = item.get('content', '').strip()
                                if content and len(content) > 50:  # Only meaningful content
                                    all_content.append(content[:300])  # Limit each content

            if all_content:
                # Create a natural synthesis
                combined_content = ' '.join(all_content[:3])  # Combine top contents

                # Simple text processing to create natural answer
                if 'AI' in query.upper() or 'artificial intelligence' in query.lower():
                    final_answer = f"Based on current information about AI: {combined_content[:400]}..."
                elif 'latest' in query.lower() or 'recent' in query.lower():
                    final_answer = f"Recent developments show: {combined_content[:400]}..."
                else:
                    final_answer = f"Here's what I found: {combined_content[:400]}..."

                return {
                    'agent': 'strategy',
                    'stage': 'synthesis',
                    'final_answer': final_answer,
                    'status': 'completed',
                    'is_conversational': False
                }
            else:
                return {
                    'agent': 'strategy',
                    'stage': 'synthesis',
                    'final_answer': "I performed a web search but couldn't extract meaningful information from the results. This might be due to the search terms or content filtering.",
                    'status': 'completed',
                    'is_conversational': False
                }

                # Final fallback
                return {
                    'agent': 'strategy',
                    'stage': 'synthesis',
                    'final_answer': "I've completed the research but encountered an issue formatting the results. The search was successful but the synthesis step had problems.",
                    'status': 'completed',
                    'is_conversational': False
                }

        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {
                'agent': 'strategy',
                'stage': 'synthesis',
                'final_answer': "Sorry, I encountered an error while processing your request.",
                'status': 'error',
                'error': str(e)
            }

