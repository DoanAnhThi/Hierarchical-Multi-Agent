import { useState } from 'react'

function InputBox({ onSend, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white">
      <div className="flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or request research..."
          disabled={disabled}
          rows="2"
          className="flex-1 input-field resize-none"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="btn btn-primary px-6 self-end"
        >
          {disabled ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Processing...
            </span>
          ) : (
            'Send'
          )}
        </button>
      </div>
      
      {/* Example Queries */}
      <div className="mt-3 flex flex-wrap gap-2">
        <span className="text-xs text-gray-500">Try:</span>
        {[
          'What are the latest AI developments?',
          'Summarize recent climate change research',
          'What is LangGraph?'
        ].map((example, i) => (
          <button
            key={i}
            type="button"
            onClick={() => !disabled && setInput(example)}
            disabled={disabled}
            className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {example}
          </button>
        ))}
      </div>
    </form>
  )
}

export default InputBox

