"""Execution Agent - Task execution with tools"""
from typing import Dict, Any, List
from langchain.tools import Tool
from utils.logger import logger


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
            # Handle direct responses for conversational queries
            if tool_name == 'direct_llm':
                # Simple rule-based responses for common conversational queries
                input_lower = task_input.lower().strip()

                if any(word in input_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                    result = "Hello! 👋 How can I help you today?"
                elif any(word in input_lower for word in ['how are you', 'how do you do']):
                    result = "I'm doing great, thanks for asking! I'm here and ready to assist you. How can I help?"
                elif any(word in input_lower for word in ['thanks', 'thank you']):
                    result = "You're welcome! 😊 Is there anything else I can help you with?"
                elif any(word in input_lower for word in ['bye', 'goodbye', 'see you']):
                    result = "Goodbye! 👋 Have a great day!"
                elif input_lower in ['ok', 'okay', 'sure', 'yes']:
                    result = "Great! What would you like to do next?"
                elif input_lower in ['no']:
                    result = "No problem! Let me know if you need anything else."
                elif len(input_lower) < 5:  # Very short queries
                    result = f"I see you said '{task_input}'. How can I assist you with that?"
                else:
                    # Fallback for slightly longer conversational queries
                    result = f"That's interesting! I'd be happy to help you with '{task_input}'. What would you like to know?"

                return {
                    'task_id': task_id,
                    'tool': tool_name,
                    'input': task_input,
                    'result': result,
                    'status': 'success',
                    'agent': 'execution'
                }

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

