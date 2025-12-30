"""Planning Agent - Task breakdown and orchestration"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..utils.logger import logger


class PlanningAgent:
    """
    Planning Agent: Breaks down strategy into detailed, actionable tasks
    Determines which tools to use and in what order
    """
    
    def __init__(self, model: str = "gpt-4-turbo-preview", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Planning Agent in a hierarchical multi-agent system.
Your role is to create detailed execution plans based on high-level strategy.

Available tools:
- web_search: Search the web for current information
- document_analyzer: Extract and analyze content from URLs
- data_extractor: Extract structured data from text

Create a detailed plan in JSON format with:
- tasks: list of specific tasks, each with:
  - task_id: unique identifier
  - description: what to do
  - tool: which tool to use
  - input: what input to provide
  - dependencies: list of task_ids this depends on
- execution_order: list of task_ids in order
- estimated_steps: number of tasks

Be specific and actionable. Keep tasks focused and independent when possible."""),
            ("human", """Strategy:
{strategy}

User Query: {query}

Create a detailed execution plan:""")
        ])
    
    def create_plan(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create detailed execution plan from strategy
        
        Args:
            strategy: Strategy from Strategy Agent
            
        Returns:
            Detailed execution plan
        """
        try:
            logger.info("Planning Agent creating execution plan...")
            
            chain = self.prompt | self.llm
            response = chain.invoke({
                "strategy": str(strategy),
                "query": strategy.get('query', '')
            })
            
            plan = self._parse_plan(response.content, strategy)
            plan['agent'] = 'planning'
            plan['strategy_ref'] = strategy.get('approach', '')
            
            logger.info(f"Plan created with {len(plan.get('tasks', []))} tasks")
            return plan
            
        except Exception as e:
            logger.error(f"Planning Agent error: {e}")
            # Fallback plan
            return self._create_fallback_plan(strategy)
    
    def _parse_plan(self, content: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured plan"""
        import json
        import re
        
        # Try to extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                plan = json.loads(json_match.group())
                if 'tasks' in plan:
                    return plan
            except json.JSONDecodeError:
                pass
        
        # Fallback: create simple plan
        return self._create_fallback_plan(strategy)
    
    def _create_fallback_plan(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simple fallback plan"""
        query = strategy.get('query', '')
        subtasks = strategy.get('subtasks', ['Search for information'])
        
        tasks = []
        for i, subtask in enumerate(subtasks[:3]):  # Limit to 3 tasks
            tasks.append({
                'task_id': f'task_{i+1}',
                'description': subtask,
                'tool': 'web_search',
                'input': query,
                'dependencies': []
            })
        
        return {
            'tasks': tasks,
            'execution_order': [t['task_id'] for t in tasks],
            'estimated_steps': len(tasks)
        }
    
    def aggregate_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate and summarize execution results
        
        Args:
            execution_results: Results from execution agent
            
        Returns:
            Aggregated results
        """
        try:
            summary_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are aggregating results from multiple research tasks.
Combine and summarize the findings into a coherent overview.

Focus on:
1. Key findings and insights
2. Relevant facts and data
3. Connections between different pieces of information
4. Overall answer to the original query

Be concise but comprehensive."""),
                ("human", """Execution Results:
{results}

Provide an aggregated summary:""")
            ])
            
            chain = summary_prompt | self.llm
            response = chain.invoke({
                "results": str(execution_results)
            })
            
            return {
                'agent': 'planning',
                'stage': 'aggregation',
                'summary': response.content,
                'task_count': len(execution_results),
                'execution_results': execution_results
            }
            
        except Exception as e:
            logger.error(f"Aggregation error: {e}")
            return {
                'agent': 'planning',
                'stage': 'aggregation',
                'summary': 'Results aggregated',
                'execution_results': execution_results,
                'error': str(e)
            }

