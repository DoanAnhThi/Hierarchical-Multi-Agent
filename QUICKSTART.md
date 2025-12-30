# Quick Start Guide

Get the Hierarchical Multi-Agent System running in 5 minutes!

## Step 1: Prerequisites

Install these first:
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Git](https://git-scm.com/)

## Step 2: Get API Keys

### OpenAI (Required)
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Tavily (Optional, for better search)
1. Go to https://tavily.com
2. Sign up for free
3. Get API key from dashboard

## Step 3: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd "Hierarchical Multi-Agent"

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # or use any text editor
```

Edit `.env` and add your keys:
```
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # Optional
```

```bash
# Frontend setup
cd ../frontend
npm install
```

## Step 4: Run the Application

Open two terminals:

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Step 5: Use the System

1. Open browser: http://localhost:3000
2. Type a question: "What are the latest AI developments?"
3. Watch the agents work:
   - 🎯 Strategy Agent analyzes the query
   - 📋 Planning Agent creates a plan
   - ⚡ Execution Agent runs tasks
4. Get your answer!

## Example Queries to Try

- "What are the latest developments in AI?"
- "Summarize recent climate change research"
- "What is LangGraph and how does it work?"
- "Compare Python and JavaScript for web development"

## Troubleshooting

### "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill the process
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

### "Backend Offline" message
- Check Terminal 1 for errors
- Verify .env file has correct API keys
- Ensure port 5000 is free

### "API Error"
- Verify OpenAI API key is correct
- Check you have API credits
- Look at Terminal 1 for error details

## Next Steps

- **Customize**: Edit agent prompts in `backend/agents/`
- **Add tools**: Create new tools in `backend/tools/`
- **Deploy**: Follow [AWS Deployment Guide](deployment/aws-free-tier-guide.md)
- **Learn more**: Read [README.md](README.md) and [DEVELOPMENT.md](DEVELOPMENT.md)

## Project Structure (Quick Reference)

```
Hierarchical Multi-Agent/
├── backend/              # Flask + LangGraph
│   ├── app.py           # Main application
│   ├── agents/          # Agent implementations
│   ├── tools/           # Research tools
│   └── .env             # Your API keys (create this)
├── frontend/            # React UI
│   ├── src/
│   │   ├── App.jsx     # Main app
│   │   └── components/ # UI components
└── deployment/          # AWS deployment scripts
```

## Getting Help

- Check the logs in both terminals
- Read [README.md](README.md) for detailed docs
- See [DEVELOPMENT.md](DEVELOPMENT.md) for dev guide
- Review [Troubleshooting section](README.md#troubleshooting)

## Success Checklist

- [ ] Python and Node.js installed
- [ ] API keys obtained
- [ ] Dependencies installed
- [ ] .env file created with keys
- [ ] Backend running (Terminal 1)
- [ ] Frontend running (Terminal 2)
- [ ] Browser showing UI at localhost:3000
- [ ] Can send queries and get responses

---

**Ready to deploy to AWS?** 
See [deployment/aws-free-tier-guide.md](deployment/aws-free-tier-guide.md)

**Want to customize?**
See [DEVELOPMENT.md](DEVELOPMENT.md)

