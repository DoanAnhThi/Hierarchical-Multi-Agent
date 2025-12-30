import { useState, useCallback } from 'react'
import MessageList from './MessageList'
import InputBox from './InputBox'
import AgentStatus from './AgentStatus'
import { streamChat } from '../services/api'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentAgent, setCurrentAgent] = useState(null)
  const [streamCancel, setStreamCancel] = useState(null)

  const addMessage = useCallback((type, content, agent = null) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      type,
      content,
      agent,
      timestamp: new Date()
    }])
  }, [])

  const handleSend = useCallback((query) => {
    // Add user message
    addMessage('user', query)
    setIsProcessing(true)
    setCurrentAgent('strategy')

    // Start streaming
    const cancel = streamChat(
      query,
      // onMessage
      (data) => {
        const { type, agent, data: msgData } = data

        switch (type) {
          case 'start':
            addMessage('system', msgData.message, 'system')
            setCurrentAgent('strategy')
            break

          case 'strategy':
            addMessage('status', `Strategy: ${msgData.approach || msgData.message}`, 'strategy')
            setCurrentAgent('planning')
            break

          case 'planning':
            const planMsg = msgData.tasks 
              ? `Plan created with ${msgData.task_count} tasks: ${msgData.tasks.join(', ')}`
              : msgData.message
            addMessage('status', planMsg, 'planning')
            setCurrentAgent('execution')
            break

          case 'execution':
            addMessage('status', `Executed ${msgData.completed_tasks} tasks`, 'execution')
            setCurrentAgent('planning')
            break

          case 'aggregation':
            if (msgData.summary) {
              addMessage('assistant', msgData.summary, 'planning')
            }
            setCurrentAgent('strategy')
            break

          case 'final':
            if (msgData.answer) {
              addMessage('final', msgData.answer, 'strategy')
            }
            break

          case 'complete':
            setIsProcessing(false)
            setCurrentAgent(null)
            break

          case 'error':
            addMessage('error', `Error: ${msgData.message}`)
            setIsProcessing(false)
            setCurrentAgent(null)
            break

          default:
            console.log('Unknown message type:', type, data)
        }
      },
      // onError
      (error) => {
        console.error('Stream error:', error)
        addMessage('error', `Connection error: ${error.message}`)
        setIsProcessing(false)
        setCurrentAgent(null)
      },
      // onComplete
      () => {
        setIsProcessing(false)
        setCurrentAgent(null)
        setStreamCancel(null)
      }
    )

    setStreamCancel(() => cancel)
  }, [addMessage])

  const handleCancel = useCallback(() => {
    if (streamCancel) {
      streamCancel()
      setStreamCancel(null)
    }
    setIsProcessing(false)
    setCurrentAgent(null)
    addMessage('system', 'Request cancelled', 'system')
  }, [streamCancel, addMessage])

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Agent Status Sidebar */}
      <div className="lg:col-span-1">
        <AgentStatus currentAgent={currentAgent} messages={messages} />
        
        {/* Cancel Button */}
        {isProcessing && (
          <button
            onClick={handleCancel}
            className="w-full btn bg-red-600 hover:bg-red-700 text-white"
          >
            Cancel Request
          </button>
        )}
      </div>

      {/* Chat Area */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-lg shadow-lg flex flex-col h-[600px]">
          <MessageList messages={messages} />
          <InputBox onSend={handleSend} disabled={isProcessing} />
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

