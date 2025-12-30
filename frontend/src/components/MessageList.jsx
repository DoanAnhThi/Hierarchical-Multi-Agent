import { useEffect, useRef } from 'react'

function MessageList({ messages }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const formatMessage = (msg) => {
    if (msg.type === 'user') {
      return (
        <div key={msg.id} className="message message-user">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
              U
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-900">{msg.content}</p>
            </div>
          </div>
        </div>
      )
    }

    if (msg.type === 'assistant' || msg.type === 'final') {
      return (
        <div key={msg.id} className="message message-assistant">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-white font-semibold">
              AI
            </div>
            <div className="flex-1">
              {msg.agent && (
                <span className={`agent-badge agent-${msg.agent} mb-2`}>
                  {msg.agent.charAt(0).toUpperCase() + msg.agent.slice(1)}
                </span>
              )}
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-800 whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          </div>
        </div>
      )
    }

    if (msg.type === 'system' || msg.type === 'status') {
      return (
        <div key={msg.id} className="message message-system">
          <div className="flex items-center gap-2">
            {msg.agent && (
              <span className={`agent-badge agent-${msg.agent}`}>
                {msg.agent}
              </span>
            )}
            <p className="text-gray-600">{msg.content}</p>
          </div>
        </div>
      )
    }

    if (msg.type === 'error') {
      return (
        <div key={msg.id} className="message bg-red-50 border-l-4 border-red-500">
          <div className="flex items-start gap-2">
            <span className="text-red-600 font-bold">⚠️</span>
            <p className="text-red-700">{msg.content}</p>
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 ? (
        <div className="text-center text-gray-400 mt-8">
          <div className="text-6xl mb-4">🤖</div>
          <p className="text-lg">Start a conversation with the multi-agent system</p>
          <p className="text-sm mt-2">Try asking about current events, research topics, or general questions</p>
        </div>
      ) : (
        messages.map(formatMessage)
      )}
      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList

