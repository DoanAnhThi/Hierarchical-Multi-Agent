# Development Guide

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

### Initial Setup

1. **Clone and setup:**
```bash
git clone <repo-url>
cd "Hierarchical Multi-Agent"
```

2. **Backend setup:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

3. **Frontend setup:**
```bash
cd frontend
npm install
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
FLASK_ENV=development python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at: http://localhost:3000

## Project Structure Explained

### Backend (`/backend`)

#### `app.py`
Main Flask application with:
- Health check endpoint
- Chat endpoints (streaming and non-streaming)
- Tool and config endpoints
- SSE streaming implementation

#### `config.py`
Configuration management:
- Environment variable loading
- API key validation
- Default values
- CORS configuration

#### `agents/`

**`strategy_agent.py`**
- Analyzes incoming queries
- Determines high-level approach
- Synthesizes final responses
- Returns structured strategy

**`planning_agent.py`**
- Creates detailed execution plans
- Breaks down strategy into tasks
- Aggregates execution results
- Manages task dependencies

**`execution_agent.py`**
- Executes individual tasks
- Uses appropriate tools
- Returns structured results
- Handles errors gracefully

**`graph.py`**
- LangGraph workflow definition
- State management (TypedDict)
- Node definitions
- Edge configurations
- Streaming implementation

#### `tools/`

**`web_search.py`**
- Tavily API integration
- DuckDuckGo fallback
- Result formatting
- Error handling

**`document_analyzer.py`**
- URL content extraction
- BeautifulSoup parsing
- Text cleaning
- Metadata extraction

**`data_extractor.py`**
- Regex-based extraction
- Email, URL, phone, date patterns
- Key information extraction
- Structured output

#### `utils/`

**`logger.py`**
- Centralized logging
- Console output
- Log formatting
- Log levels

**`streaming.py`**
- SSE event formatting
- Stream event class
- Helper functions
- Error handling

### Frontend (`/frontend`)

#### `src/App.jsx`
- Main application component
- Backend health check
- Layout and routing
- Error boundary

#### `src/components/`

**`ChatInterface.jsx`**
- Main chat component
- State management
- Stream handling
- Message coordination

**`MessageList.jsx`**
- Message display
- Auto-scrolling
- Message formatting
- Empty state

**`InputBox.jsx`**
- User input handling
- Submit logic
- Example queries
- Keyboard shortcuts

**`AgentStatus.jsx`**
- Agent workflow visualization
- Status indicators
- Progress tracking
- Animation effects

#### `src/services/api.js`
- Backend communication
- SSE streaming
- HTTP requests
- Error handling

## Development Workflow

### Adding a New Tool

1. **Create tool file:**
```bash
cd backend/tools
touch my_new_tool.py
```

2. **Implement tool:**
```python
from langchain.tools import Tool

class MyNewTool:
    def __init__(self):
        pass
    
    def run(self, input: str):
        # Your logic here
        return result
    
    def as_langchain_tool(self) -> Tool:
        return Tool(
            name="my_new_tool",
            description="What it does",
            func=self.run
        )

def create_my_new_tool() -> Tool:
    tool = MyNewTool()
    return tool.as_langchain_tool()
```

3. **Register tool:**
```python
# In app.py
from tools.my_new_tool import create_my_new_tool

tools = [
    create_web_search_tool(),
    create_document_analyzer_tool(),
    create_data_extractor_tool(),
    create_my_new_tool(),  # Add here
]
```

4. **Test tool:**
```bash
cd backend
python -c "from tools.my_new_tool import create_my_new_tool; tool = create_my_new_tool(); print(tool.run('test'))"
```

### Adding a New Agent

1. **Create agent file:**
```bash
cd backend/agents
touch my_new_agent.py
```

2. **Implement agent:**
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class MyNewAgent:
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Your system prompt"),
            ("human", "{input}")
        ])
    
    def process(self, input_data):
        chain = self.prompt | self.llm
        response = chain.invoke({"input": input_data})
        return response.content
```

3. **Add to graph:**
```python
# In graph.py
from .my_new_agent import MyNewAgent

class MultiAgentGraph:
    def __init__(self, ...):
        self.my_new_agent = MyNewAgent()
        # Add to workflow...
```

### Modifying the UI

1. **Component structure:**
```jsx
// New component in src/components/
import { useState } from 'react'

function MyComponent({ prop1, prop2 }) {
  const [state, setState] = useState(initial)
  
  return (
    <div className="...">
      {/* Your JSX */}
    </div>
  )
}

export default MyComponent
```

2. **Styling with Tailwind:**
```jsx
<div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
  {/* Content */}
</div>
```

3. **Custom styles:**
```css
/* In src/styles/main.css */
@layer components {
  .my-custom-class {
    @apply bg-blue-500 text-white px-4 py-2 rounded;
  }
}
```

## Testing

### Backend Tests

**Unit tests:**
```bash
cd backend
python -m pytest tests/test_agents.py -v
```

**Test specific agent:**
```python
# In tests/test_agents.py
def test_strategy_agent():
    agent = StrategyAgent()
    result = agent.analyze("test query")
    assert result is not None
```

**Manual API testing:**
```bash
# Health check
curl http://localhost:5000/health

# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

### Frontend Tests

**Manual testing:**
1. Start dev server
2. Open browser console
3. Check for errors
4. Test all interactions

**Component testing:**
```bash
npm run test  # If configured
```

## Debugging

### Backend Debugging

**Enable debug logging:**
```python
# In config.py
DEBUG = True

# In utils/logger.py
logger.setLevel(logging.DEBUG)
```

**Use breakpoints:**
```python
import pdb; pdb.set_trace()
```

**Check LangChain:**
```python
from langchain.globals import set_debug
set_debug(True)
```

### Frontend Debugging

**Console logging:**
```javascript
console.log('Debug:', variable)
console.table(arrayData)
```

**React DevTools:**
- Install browser extension
- Inspect component props/state

**Network inspection:**
- Browser DevTools → Network tab
- Check SSE connection
- Monitor API calls

## Performance Optimization

### Backend

**Profile code:**
```python
import cProfile
cProfile.run('function_to_profile()')
```

**Optimize queries:**
- Cache LLM responses
- Batch operations
- Use async where possible

**Monitor memory:**
```bash
pip install memory_profiler
python -m memory_profiler app.py
```

### Frontend

**React optimizations:**
```javascript
import { memo, useMemo, useCallback } from 'react'

const MyComponent = memo(({ data }) => {
  const processed = useMemo(() => process(data), [data])
  const handler = useCallback(() => {}, [])
  return <div>{processed}</div>
})
```

**Bundle analysis:**
```bash
npm run build -- --analyze
```

## Git Workflow

**Branches:**
- `main` - Production
- `develop` - Development
- `feature/*` - New features
- `fix/*` - Bug fixes

**Commit messages:**
```
feat: Add new web search tool
fix: Resolve streaming connection issue
docs: Update README
refactor: Improve agent state management
```

**Before committing:**
```bash
# Format Python
black backend/

# Lint JavaScript
npm run lint

# Run tests
pytest backend/tests/
```

## Common Issues

### "Module not found"
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### "Port already in use"
```bash
# Kill process
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

### "API key not found"
```bash
# Check .env file
cat backend/.env

# Ensure it's loaded
python -c "from config import Config; print(Config.OPENAI_API_KEY)"
```

### "CORS error"
```bash
# Update CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Best Practices

### Python
- Use type hints
- Follow PEP 8
- Write docstrings
- Handle exceptions
- Log appropriately

### JavaScript
- Use functional components
- Destructure props
- Use modern ES6+
- Handle errors
- Clean up effects

### General
- Keep functions small
- Write descriptive names
- Comment complex logic
- Test edge cases
- Document changes

## Resources

- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [React Docs](https://react.dev/)
- [Flask Guide](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)

## Getting Help

1. Check documentation
2. Review code comments
3. Search existing issues
4. Ask in discussions
5. Create detailed bug report

