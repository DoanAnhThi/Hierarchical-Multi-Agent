"""Flask application with SSE streaming for multi-agent system"""
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json
import os
from config import Config
from agents.graph import MultiAgentGraph
from tools.web_search import create_web_search_tool
from tools.document_analyzer import create_document_analyzer_tool
from tools.data_extractor import create_data_extractor_tool
from utils.logger import logger
from utils.streaming import format_sse_message


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    logger.info("Please set OPENAI_API_KEY in .env file")

# Initialize tools
tools = [
    create_web_search_tool(Config.TAVILY_API_KEY),
    create_document_analyzer_tool(),
    create_data_extractor_tool()
]

# Initialize multi-agent graph
agent_graph = MultiAgentGraph(
    tools=tools,
    model=Config.OPENAI_MODEL,
    temperature=Config.OPENAI_TEMPERATURE,
    max_iterations=Config.MAX_ITERATIONS
)

logger.info("Flask application initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'multi-agent-system',
        'agents': ['strategy', 'planning', 'execution'],
        'tools': [tool.name for tool in tools]
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Non-streaming chat endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Processing query: {query[:100]}...")
        
        # Invoke the agent graph
        result = agent_graph.invoke(query)
        
        return jsonify({
            'query': query,
            'response': result.get('final_response', {}),
            'strategy': result.get('strategy', {}),
            'execution_count': len(result.get('execution_results', []))
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint using SSE"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Starting stream for query: {query[:100]}...")
        
        def generate():
            """Generator function for SSE streaming"""
            try:
                # Send initial message
                yield format_sse_message('start', {'query': query, 'message': 'Starting agent workflow...'})
                
                # Stream agent execution
                for message in agent_graph.stream(query):
                    agent = message.get('agent', 'system')
                    msg_type = message.get('type', 'update')
                    data = message.get('data', {})
                    
                    # Format based on message type
                    if msg_type == 'strategy_complete':
                        yield format_sse_message(
                            'strategy',
                            {
                                'message': 'Strategy determined',
                                'approach': data.get('approach', ''),
                                'complexity': data.get('complexity', 'moderate')
                            },
                            agent='strategy'
                        )
                    
                    elif msg_type == 'plan_created':
                        yield format_sse_message(
                            'planning',
                            {
                                'message': 'Execution plan created',
                                'task_count': len(data.get('tasks', [])),
                                'tasks': [t.get('description', '') for t in data.get('tasks', [])]
                            },
                            agent='planning'
                        )
                    
                    elif msg_type == 'execution_complete':
                        results = data.get('results', [])
                        yield format_sse_message(
                            'execution',
                            {
                                'message': 'Tasks executed',
                                'completed_tasks': len(results),
                                'results_preview': [r.get('status', '') for r in results]
                            },
                            agent='execution'
                        )
                    
                    elif msg_type == 'aggregation_complete':
                        yield format_sse_message(
                            'aggregation',
                            {
                                'message': 'Results aggregated',
                                'summary': data.get('summary', '')[:200]
                            },
                            agent='planning'
                        )
                    
                    elif msg_type == 'synthesis_complete':
                        yield format_sse_message(
                            'final',
                            {
                                'message': 'Final synthesis complete',
                                'answer': data.get('final_answer', '')
                            },
                            agent='strategy'
                        )
                    
                    elif msg_type == 'error':
                        yield format_sse_message(
                            'error',
                            {'message': data.get('error', 'Unknown error')},
                            agent=agent
                        )
                
                # Send completion message
                yield format_sse_message('complete', {'message': 'Workflow completed successfully'})
                
            except GeneratorExit:
                logger.info("Client disconnected from stream")
            except Exception as e:
                logger.error(f"Stream generation error: {e}")
                yield format_sse_message('error', {'message': str(e)})
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
        
    except Exception as e:
        logger.error(f"Stream setup error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    return jsonify({
        'tools': [
            {
                'name': tool.name,
                'description': tool.description
            }
            for tool in tools
        ]
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (non-sensitive)"""
    return jsonify({
        'model': Config.OPENAI_MODEL,
        'temperature': Config.OPENAI_TEMPERATURE,
        'max_iterations': Config.MAX_ITERATIONS,
        'stream_enabled': Config.STREAM_ENABLED,
        'environment': Config.ENV
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = Config.DEBUG
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"CORS origins: {Config.CORS_ORIGINS}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

