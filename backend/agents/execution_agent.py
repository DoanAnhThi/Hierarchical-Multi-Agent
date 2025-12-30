"""Execution Agent - Task execution with tools"""
from typing import Dict, Any, List
from langchain.tools import Tool
from ..utils.logger import logger


class ExecutionAgent:
    """
    Execution Agent: Executes individual tasks using available tools
    Works with web search, document analysis, and data extraction
    """
    
    def __init__(self, tools: List[Tool]):
        self.tools = {tool.name: tool for tool in tools}
        logger.info(f"Execution Agent initialized with tools: {list(self.tools.keys())}")
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task using appropriate tool
        
        Args:
            task: Task dictionary with tool, input, and description
            
        Returns:
            Task result dictionary
        """
        task_id = task.get('task_id', 'unknown')
        tool_name = task.get('tool', 'web_search')
        task_input = task.get('input', '')
        
        logger.info(f"Executing task {task_id} with {tool_name}")
        
        try:
            # Get the appropriate tool
            if tool_name not in self.tools:
                logger.warning(f"Tool {tool_name} not found, using web_search")
                tool_name = 'web_search'
            
            tool = self.tools[tool_name]
            
            # Execute the tool
            result = tool.func(task_input)
            
            return {
                'task_id': task_id,
                'tool': tool_name,
                'input': task_input,
                'result': result,
                'status': 'success',
                'agent': 'execution'
            }
            
        except Exception as e:
            logger.error(f"Task {task_id} execution error: {e}")
            return {
                'task_id': task_id,
                'tool': tool_name,
                'input': task_input,
                'result': None,
                'status': 'error',
                'error': str(e),
                'agent': 'execution'
            }
    
    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute all tasks in a plan
        
        Args:
            plan: Execution plan from Planning Agent
            
        Returns:
            List of task results
        """
        tasks = plan.get('tasks', [])
        execution_order = plan.get('execution_order', [])
        
        logger.info(f"Executing plan with {len(tasks)} tasks")
        
        results = []
        task_results_map = {}
        
        # Execute tasks in order
        for task_id in execution_order:
            # Find the task
            task = next((t for t in tasks if t['task_id'] == task_id), None)
            if not task:
                logger.warning(f"Task {task_id} not found in plan")
                continue
            
            # Check dependencies
            dependencies = task.get('dependencies', [])
            if dependencies:
                # Ensure dependencies are completed
                deps_completed = all(dep in task_results_map for dep in dependencies)
                if not deps_completed:
                    logger.warning(f"Task {task_id} dependencies not met, skipping")
                    continue
            
            # Execute the task
            result = self.execute_task(task)
            results.append(result)
            task_results_map[task_id] = result
        
        logger.info(f"Plan execution completed: {len(results)} tasks executed")
        return results
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())

