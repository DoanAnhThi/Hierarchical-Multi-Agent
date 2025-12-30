import { useState, useEffect } from 'react'

const agentInfo = {
  strategy: {
    name: 'Strategy Agent',
    color: 'purple',
    icon: '🎯',
    description: 'Determining approach'
  },
  planning: {
    name: 'Planning Agent',
    color: 'blue',
    icon: '📋',
    description: 'Creating execution plan'
  },
  execution: {
    name: 'Execution Agent',
    color: 'green',
    icon: '⚡',
    description: 'Executing tasks'
  }
}

function AgentStatus({ currentAgent, messages }) {
  const [activeStages, setActiveStages] = useState({
    strategy: false,
    planning: false,
    execution: false
  })

  useEffect(() => {
    // Update active stages based on messages
    const stages = { strategy: false, planning: false, execution: false }
    
    messages.forEach(msg => {
      if (msg.agent && msg.agent in stages) {
        stages[msg.agent] = true
      }
    })
    
    setActiveStages(stages)
  }, [messages])

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Agent Workflow Status
      </h3>
      
      <div className="space-y-4">
        {Object.entries(agentInfo).map(([key, info], index) => {
          const isActive = currentAgent === key
          const isCompleted = activeStages[key] && !isActive
          const isPending = !activeStages[key] && !isActive
          
          return (
            <div key={key}>
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                  isActive ? `bg-${info.color}-100 ring-4 ring-${info.color}-200` :
                  isCompleted ? `bg-${info.color}-50` :
                  'bg-gray-100'
                }`}>
                  {info.icon}
                </div>
                
                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className={`font-semibold ${
                      isActive ? `text-${info.color}-700` :
                      isCompleted ? 'text-gray-700' :
                      'text-gray-400'
                    }`}>
                      {info.name}
                    </h4>
                    
                    {/* Status Badge */}
                    {isActive && (
                      <span className={`agent-badge agent-${key} animate-pulse`}>
                        In Progress
                      </span>
                    )}
                    {isCompleted && (
                      <span className="text-green-600 text-sm">✓ Complete</span>
                    )}
                  </div>
                  
                  <p className={`text-sm ${
                    isActive ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {isActive ? info.description : 
                     isCompleted ? 'Completed' : 'Pending'}
                  </p>
                </div>
                
                {/* Progress Indicator */}
                <div className="flex-shrink-0">
                  {isActive ? (
                    <div className="w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  ) : isCompleted ? (
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white text-sm">
                      ✓
                    </div>
                  ) : (
                    <div className="w-6 h-6 bg-gray-200 rounded-full" />
                  )}
                </div>
              </div>
              
              {/* Connector Line */}
              {index < Object.keys(agentInfo).length - 1 && (
                <div className={`ml-6 w-0.5 h-8 ${
                  isCompleted ? 'bg-green-300' : 'bg-gray-200'
                }`} />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AgentStatus

