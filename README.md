# Hierarchical Multi-Agent System

A sophisticated multi-agent system built with LangChain, LangGraph, Flask, and React that implements a **Strategy → Planning → Execution** architecture for intelligent task handling and research.

![System Architecture](https://img.shields.io/badge/Architecture-Hierarchical-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![React](https://img.shields.io/badge/React-18.2-61dafb)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

- **Hierarchical Agent Architecture**: Three-tier system with Strategy, Planning, and Execution agents
- **Real-time Streaming**: Server-Sent Events (SSE) for live agent updates
- **Research Capabilities**: Web search, document analysis, and data extraction
- **Modern UI**: Beautiful React interface with agent status visualization
- **Production-Ready**: Optimized for AWS EC2 Free Tier deployment
- **Extensible**: Easy to add new agents and tools

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🏗️ Architecture

### Agent Hierarchy

```
┌─────────────────────────────────────────────────┐
│           Strategy Agent (GPT-4)                 │
│   • Analyzes queries                             │
│   • Determines approach                          │
│   • Synthesizes final response                   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          Planning Agent (GPT-4)                  │
│   • Breaks down strategy                         │
│   • Creates execution plan                       │
│   • Aggregates results                           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         Execution Agent (Tools)                  │
│   • Web Search (Tavily/DuckDuckGo)              │
│   • Document Analysis                            │
│   • Data Extraction                              │
└─────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- LangChain 0.1 - Agent framework
- LangGraph 0.0.40 - State management
- OpenAI GPT-4 - Language model
- Tavily API - Web search
- Gunicorn - Production server

**Frontend:**
- React 18.2 - UI framework
- Vite 5.0 - Build tool
- Tailwind CSS 3.4 - Styling
- EventSource API - SSE streaming

**Deployment:**
- Nginx - Reverse proxy & static files
- Supervisor - Process management
- AWS EC2 t2.micro - Hosting

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Tavily API Key (optional, [Get one here](https://tavily.com))

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd "Hierarchical Multi-Agent"
```

2. **Set up backend:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Add your API keys
```

4. **Set up frontend:**
```bash
cd ../frontend
npm install
```

5. **Start the application:**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

6. **Access the application:**
   - Open http://localhost:3000
   - The backend runs on http://localhost:5000

## 📁 Project Structure

```
hierarchical-multi-agent/
├── backend/
│   ├── app.py                      # Flask application
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Python dependencies
│   ├── agents/
│   │   ├── strategy_agent.py      # High-level strategy
│   │   ├── planning_agent.py      # Task planning
│   │   ├── execution_agent.py     # Task execution
│   │   └── graph.py               # LangGraph workflow
│   ├── tools/
│   │   ├── web_search.py          # Web search tool
│   │   ├── document_analyzer.py   # Document analysis
│   │   └── data_extractor.py      # Data extraction
│   ├── utils/
│   │   ├── logger.py              # Logging
│   │   └── streaming.py           # SSE utilities
│   └── tests/
│       └── test_agents.py         # Unit tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main app
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # Chat UI
│   │   │   ├── MessageList.jsx    # Messages
│   │   │   ├── InputBox.jsx       # Input
│   │   │   └── AgentStatus.jsx    # Agent status
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   └── styles/
│   │       └── main.css           # Styles
│   ├── package.json
│   └── vite.config.js
├── deployment/
│   ├── setup.sh                   # EC2 setup script
│   ├── deploy.sh                  # Deployment script
│   ├── nginx.conf                 # Nginx config
│   ├── supervisor.conf            # Supervisor config
│   ├── ssl-setup.sh              # SSL configuration
│   └── aws-free-tier-guide.md    # AWS guide
├── .env.example                   # Environment template
├── .gitignore
└── README.md
```

## 💻 Local Development

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
FLASK_ENV=development python app.py

# Run tests
python -m pytest tests/

# Check logs
tail -f logs/app.log
```

### Frontend Development

```bash
cd frontend

# Development mode (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create `.env` file in the backend directory:

```bash
# Required
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
MAX_ITERATIONS=10
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## ☁️ AWS Deployment

### Option 1: Automated Setup

1. **Launch EC2 t2.micro instance** (Amazon Linux 2023 or Ubuntu 22.04)

2. **Upload files and run setup:**
```bash
# Upload project
scp -i your-key.pem -r * ec2-user@YOUR_IP:/tmp/multi-agent/

# SSH into instance
ssh -i your-key.pem ec2-user@YOUR_IP

# Move files
sudo mkdir -p /var/www/multi-agent
sudo cp -r /tmp/multi-agent/* /var/www/multi-agent/
sudo chown -R $USER:$USER /var/www/multi-agent

# Run setup
cd /var/www/multi-agent
chmod +x deployment/setup.sh
./deployment/setup.sh
```

3. **Configure environment:**
```bash
cd /var/www/multi-agent/backend
cp .env.example .env
nano .env  # Add your API keys
```

4. **Deploy:**
```bash
cd /var/www/multi-agent
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

5. **Access your app:**
   - Open http://YOUR_EC2_PUBLIC_IP

### Option 2: Manual Setup

See detailed guide: [deployment/aws-free-tier-guide.md](deployment/aws-free-tier-guide.md)

### SSL Setup (Optional)

If you have a domain:

```bash
cd /var/www/multi-agent/deployment
chmod +x ssl-setup.sh
./ssl-setup.sh your-domain.com
```

## ⚙️ Configuration

### Agent Configuration

Modify `backend/config.py` to adjust:
- Model selection (GPT-4, GPT-3.5-turbo)
- Temperature settings
- Max iterations
- Streaming settings

### Tool Configuration

Add new tools in `backend/tools/`:

```python
from langchain.tools import Tool

def create_my_tool() -> Tool:
    return Tool(
        name="my_tool",
        description="What it does",
        func=lambda x: your_function(x)
    )
```

Register in `backend/app.py`:

```python
from tools.my_tool import create_my_tool

tools = [
    create_web_search_tool(),
    create_my_tool(),  # Add here
]
```

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "service": "multi-agent-system",
  "agents": ["strategy", "planning", "execution"],
  "tools": ["web_search", "document_analyzer", "data_extractor"]
}
```

#### Chat (Non-streaming)
```
POST /api/chat
Content-Type: application/json

{
  "query": "What are the latest AI developments?"
}
```

#### Chat (Streaming)
```
POST /api/chat/stream
Content-Type: application/json

{
  "query": "What are the latest AI developments?"
}
```
Returns SSE stream with events:
- `start` - Query received
- `strategy` - Strategy determined
- `planning` - Plan created
- `execution` - Tasks executed
- `aggregation` - Results aggregated
- `final` - Final answer
- `complete` - Stream finished
- `error` - Error occurred

#### Get Tools
```
GET /api/tools
```

#### Get Config
```
GET /api/config
```

## 🔧 Troubleshooting

### Backend Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**API key errors:**
```bash
# Check .env file
cat backend/.env
# Ensure keys are set correctly
```

**Port already in use:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
```bash
# Check CORS_ORIGINS in backend .env
# Ensure it includes frontend URL
```

### AWS Deployment Issues

**Service won't start:**
```bash
# Check logs
sudo tail -f /var/log/multiagent/error.log

# Restart services
sudo supervisorctl restart multiagent
sudo systemctl restart nginx
```

**Out of memory:**
```bash
# Check swap
free -h

# Add more swap
sudo fallocate -l 4G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Can't access from browser:**
- Check security group allows HTTP (80)
- Check Nginx is running: `sudo systemctl status nginx`
- Check backend is running: `sudo supervisorctl status`

## 🧪 Testing

Run backend tests:
```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

Manual testing checklist:
- [ ] Backend health endpoint responds
- [ ] Frontend loads successfully
- [ ] Can send a query
- [ ] Streaming works (see agent updates)
- [ ] Final answer is displayed
- [ ] Error handling works

## 📊 Monitoring

### View Logs

**Development:**
```bash
# Backend
tail -f backend/logs/app.log

# Flask console
# (prints to terminal)
```

**Production (AWS):**
```bash
# Application logs
sudo tail -f /var/log/multiagent/error.log

# Nginx logs
sudo tail -f /var/log/nginx/multiagent_error.log

# Supervisor logs
sudo tail -f /var/log/multiagent/supervisor_output.log
```

### Performance Monitoring

**AWS CloudWatch** (automatically enabled):
- CPU utilization
- Network in/out
- Disk read/write

**Set up alarms:**
- High CPU usage (> 80%)
- High memory usage (> 90%)
- Billing alerts

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. **Add more tools**: APIs, databases, custom functions
2. **Enhance agents**: More sophisticated reasoning
3. **Improve UI**: Better visualizations, chat history
4. **Add features**: User authentication, rate limiting
5. **Optimize performance**: Caching, async operations

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - Agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - State management
- [OpenAI](https://openai.com/) - Language models
- [Tavily](https://tavily.com/) - Search API
- [React](https://react.dev/) - UI framework

## 📞 Support

For issues and questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [AWS Deployment Guide](deployment/aws-free-tier-guide.md)
- Check application logs
- Open an issue on GitHub

## 🚀 What's Next?

Future enhancements:
- [ ] Add conversation history persistence
- [ ] Implement user authentication
- [ ] Add more specialized agents
- [ ] Support for file uploads
- [ ] Integration with more APIs
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Monitoring dashboard
- [ ] Rate limiting and quotas

---

Built with ❤️ using LangChain, LangGraph, Flask, and React

