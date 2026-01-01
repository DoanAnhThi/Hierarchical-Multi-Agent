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

  const addMessage = useCallback((type, content, agent = null, isStreaming = false) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(),
      type,
      content,
      agent,
      timestamp: new Date(),
      isStreaming
    }])
  }, [])

  const updateLastMessage = useCallback((content, agent = null) => {
    setMessages(prev => {
      const newMessages = [...prev]
      if (newMessages.length > 0) {
        const lastMsg = newMessages[newMessages.length - 1]
        newMessages[newMessages.length - 1] = {
          ...lastMsg,
          content: lastMsg.content + content,
          agent: agent || lastMsg.agent
        }
      }
      return newMessages
    })
  }, [])

  const handleSend = useCallback((query) => {
    // Add user message
    addMessage('user', query)
    setIsProcessing(true)
    setCurrentAgent('strategy')

    // Add initial assistant message for streaming
    addMessage('assistant', '', 'strategy', true)

    // Start streaming
    const cancel = streamChat(
      query,
      // onMessage
      (data) => {
        const { type, agent, data: msgData } = data

        switch (type) {
          case 'start':
            addMessage('thinking', msgData.message, 'system')
            setCurrentAgent('strategy')
            break

          case 'strategy':
            addMessage('thinking', `🎯 Strategy: ${msgData.approach || msgData.message}`, 'strategy')
            setCurrentAgent('planning')
            break

          case 'planning':
            const planMsg = msgData.tasks
              ? `📋 Plan: ${msgData.task_count} tasks - ${msgData.tasks.map(t => t.substring(0, 30)).join(', ')}`
              : `📋 Planning: ${msgData.message}`
            addMessage('thinking', planMsg, 'planning')
            setCurrentAgent('execution')
            break

          case 'execution':
            addMessage('thinking', `⚡ Executed ${msgData.completed_tasks} tasks`, 'execution')
            setCurrentAgent('planning')
            break

          case 'aggregation':
            if (msgData.summary) {
              addMessage('thinking', `📊 Synthesized results`, 'planning')
            }
            setCurrentAgent('strategy')
            break

          case 'final':
            if (msgData.answer) {
              // Replace the streaming message with final answer
              setMessages(prev => {
                const newMessages = [...prev]
                const streamingIndex = newMessages.findLastIndex(msg =>
                  msg.isStreaming && msg.agent === 'strategy'
                )

                if (streamingIndex !== -1) {
                  newMessages[streamingIndex] = {
                    ...newMessages[streamingIndex],
                    content: msgData.answer,
                    type: 'final',
                    isStreaming: false
                  }
                } else {
                  // Fallback: add as new message
                  newMessages.push({
                    id: Date.now() + Math.random(),
                    type: 'final',
                    content: msgData.answer,
                    agent: 'strategy',
                    timestamp: new Date(),
                    isStreaming: false
                  })
                }
                return newMessages
              })
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

