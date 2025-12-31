import json
from typing import Dict, Any, Generator
from datetime import datetime


class StreamEvent:
    """Represents a streaming event"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], agent: str = None):
        self.event_type = event_type
        self.data = data
        self.agent = agent
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_sse(self) -> str:
        """Convert event to SSE format"""
        payload = {
            'type': self.event_type,
            'agent': self.agent,
            'data': self.data,
            'timestamp': self.timestamp
        }
        return f"data: {json.dumps(payload)}\n\n"


def format_sse_message(event_type: str, data: Dict[str, Any], agent: str = None) -> str:
    """Format a message for Server-Sent Events"""
    event = StreamEvent(event_type, data, agent)
    return event.to_sse()


def stream_generator(messages: Generator) -> Generator[str, None, None]:
    """
    Generator wrapper for streaming messages
    
    Args:
        messages: Generator that yields (event_type, data, agent) tuples
        
    Yields:
        SSE formatted strings
    """
    try:
        for event_type, data, agent in messages:
            yield format_sse_message(event_type, data, agent)
    except GeneratorExit:
        yield format_sse_message('end', {'message': 'Stream closed by client'})
    except Exception as e:
        yield format_sse_message('error', {'message': str(e)})
    finally:
        yield format_sse_message('complete', {'message': 'Stream completed'})

