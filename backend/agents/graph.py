"""LangGraph workflow definition for hierarchical multi-agent system"""
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain.tools import Tool
import operator
from .strategy_agent import StrategyAgent
from .planning_agent import PlanningAgent
from .execution_agent import ExecutionAgent
from ..utils.logger import logger


class AgentState(TypedDict):
    """State shared between agents"""
    query: str
    strategy: Dict[str, Any]
    plan: Dict[str, Any]
    execution_results: List[Dict[str, Any]]
    final_response: Dict[str, Any]
    messages: Annotated[List[Dict[str, Any]], operator.add]
    iteration: int
    max_iterations: int


class MultiAgentGraph:
    """
    Hierarchical multi-agent system using LangGraph
    Flow: Strategy → Planning → Execution → Planning → Strategy
    """
    
    def __init__(
        self,
        tools: List[Tool],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_iterations: int = 10
    ):
        self.strategy_agent = StrategyAgent(model=model, temperature=temperature)
        self.planning_agent = PlanningAgent(model=model, temperature=temperature)
        self.execution_agent = ExecutionAgent(tools=tools)
        self.max_iterations = max_iterations
        
        # Build the graph
        self.graph = self._build_graph()
        logger.info("MultiAgentGraph initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("strategy", self._strategy_node)
        workflow.add_node("planning", self._planning_node)
        workflow.add_node("execution", self._execution_node)
        workflow.add_node("synthesis", self._synthesis_node)
        
        # Define edges
        workflow.set_entry_point("strategy")
        workflow.add_edge("strategy", "planning")
        workflow.add_edge("planning", "execution")
        workflow.add_edge("execution", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    def _strategy_node(self, state: AgentState) -> AgentState:
        """Strategy Agent node"""
        logger.info("=== STRATEGY AGENT ===")
        
        strategy = self.strategy_agent.analyze(state['query'])
        
        state['strategy'] = strategy
        state['messages'].append({
            'agent': 'strategy',
            'type': 'strategy_complete',
            'data': strategy
        })
        
        return state
    
    def _planning_node(self, state: AgentState) -> AgentState:
        """Planning Agent node"""
        logger.info("=== PLANNING AGENT ===")
        
        plan = self.planning_agent.create_plan(state['strategy'])
        
        state['plan'] = plan
        state['messages'].append({
            'agent': 'planning',
            'type': 'plan_created',
            'data': plan
        })
        
        return state
    
    def _execution_node(self, state: AgentState) -> AgentState:
        """Execution Agent node"""
        logger.info("=== EXECUTION AGENT ===")
        
        results = self.execution_agent.execute_plan(state['plan'])
        
        state['execution_results'] = results
        state['messages'].append({
            'agent': 'execution',
            'type': 'execution_complete',
            'data': {'results': results}
        })
        
        return state
    
    def _synthesis_node(self, state: AgentState) -> AgentState:
        """Synthesis node - Planning aggregates, Strategy synthesizes"""
        logger.info("=== SYNTHESIS ===")
        
        # Planning agent aggregates execution results
        aggregated = self.planning_agent.aggregate_results(state['execution_results'])
        
        state['messages'].append({
            'agent': 'planning',
            'type': 'aggregation_complete',
            'data': aggregated
        })
        
        # Strategy agent synthesizes final response
        final_response = self.strategy_agent.synthesize_results(aggregated)
        
        state['final_response'] = final_response
        state['messages'].append({
            'agent': 'strategy',
            'type': 'synthesis_complete',
            'data': final_response
        })
        
        return state
    
    def stream(self, query: str):
        """
        Stream the agent execution
        
        Args:
            query: User query
            
        Yields:
            Events from agent execution
        """
        initial_state: AgentState = {
            'query': query,
            'strategy': {},
            'plan': {},
            'execution_results': [],
            'final_response': {},
            'messages': [],
            'iteration': 0,
            'max_iterations': self.max_iterations
        }
        
        try:
            # Stream the graph execution
            for event in self.graph.stream(initial_state):
                # Each event is a dict with node name as key
                for node_name, node_state in event.items():
                    # Get new messages since last event
                    messages = node_state.get('messages', [])
                    if messages:
                        latest_message = messages[-1]
                        yield latest_message
                        
        except Exception as e:
            logger.error(f"Graph stream error: {e}")
            yield {
                'agent': 'system',
                'type': 'error',
                'data': {'error': str(e)}
            }
    
    def invoke(self, query: str) -> Dict[str, Any]:
        """
        Invoke the agent system (non-streaming)
        
        Args:
            query: User query
            
        Returns:
            Final state with response
        """
        initial_state: AgentState = {
            'query': query,
            'strategy': {},
            'plan': {},
            'execution_results': [],
            'final_response': {},
            'messages': [],
            'iteration': 0,
            'max_iterations': self.max_iterations
        }
        
        try:
            final_state = self.graph.invoke(initial_state)
            return final_state
        except Exception as e:
            logger.error(f"Graph invoke error: {e}")
            return {
                'error': str(e),
                'query': query
            }

