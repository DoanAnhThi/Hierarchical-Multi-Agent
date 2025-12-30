import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import { getHealth } from './services/api'

function App() {
  const [isBackendHealthy, setIsBackendHealthy] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // Check backend health
    getHealth()
      .then(() => {
        setIsBackendHealthy(true)
      })
      .catch(() => {
        setIsBackendHealthy(false)
      })
      .finally(() => {
        setIsChecking(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Hierarchical Multi-Agent System
          </h1>
          <p className="text-gray-600 mb-4">
            Strategy → Planning → Execution
          </p>
          
          {/* Backend Status */}
          <div className="flex items-center justify-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              isChecking ? 'bg-yellow-400 animate-pulse' :
              isBackendHealthy ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-gray-600">
              {isChecking ? 'Checking backend...' :
               isBackendHealthy ? 'Backend Connected' : 'Backend Offline'}
            </span>
          </div>
        </header>

        {/* Main Content */}
        {!isChecking && !isBackendHealthy ? (
          <div className="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-red-800 mb-2">
              Backend Connection Failed
            </h2>
            <p className="text-red-600 mb-4">
              Unable to connect to the Flask backend. Please ensure:
            </p>
            <ul className="text-left text-red-600 space-y-2 mb-4">
              <li>• The backend server is running (python backend/app.py)</li>
              <li>• The server is accessible at http://localhost:5000</li>
              <li>• Your .env file is configured correctly</li>
            </ul>
            <button
              onClick={() => window.location.reload()}
              className="btn btn-primary"
            >
              Retry Connection
            </button>
          </div>
        ) : (
          <ChatInterface />
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>Powered by LangChain, LangGraph, Flask, and React</p>
          <p className="mt-1">OpenAI GPT-4 • Tavily Search</p>
        </footer>
      </div>
    </div>
  )
}

export default App

