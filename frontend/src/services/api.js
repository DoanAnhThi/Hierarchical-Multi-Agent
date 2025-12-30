/**
 * API service for communicating with the Flask backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Stream chat messages using Server-Sent Events
 * @param {string} query - User query
 * @param {function} onMessage - Callback for each message
 * @param {function} onError - Callback for errors
 * @param {function} onComplete - Callback when stream completes
 * @returns {function} Cleanup function to close the stream
 */
export function streamChat(query, onMessage, onError, onComplete) {
  const url = `${API_BASE_URL}/api/chat/stream`;
  
  // Use fetch for POST with streaming
  const controller = new AbortController();
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
    signal: controller.signal,
  })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      function readStream() {
        reader.read().then(({ done, value }) => {
          if (done) {
            onComplete?.();
            return;
          }
          
          // Decode the chunk
          const chunk = decoder.decode(value, { stream: true });
          
          // Split by newlines and process each line
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                onMessage(data);
              } catch (e) {
                console.error('Failed to parse SSE data:', e);
              }
            }
          }
          
          // Continue reading
          readStream();
        }).catch(error => {
          if (error.name !== 'AbortError') {
            onError?.(error);
          }
        });
      }
      
      readStream();
    })
    .catch(error => {
      if (error.name !== 'AbortError') {
        onError?.(error);
      }
    });
  
  // Return cleanup function
  return () => {
    controller.abort();
  };
}

/**
 * Send a non-streaming chat request
 * @param {string} query - User query
 * @returns {Promise<object>} Response data
 */
export async function sendChat(query) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get health status
 * @returns {Promise<object>} Health data
 */
export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get available tools
 * @returns {Promise<object>} Tools data
 */
export async function getTools() {
  const response = await fetch(`${API_BASE_URL}/api/tools`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

/**
 * Get configuration
 * @returns {Promise<object>} Config data
 */
export async function getConfig() {
  const response = await fetch(`${API_BASE_URL}/api/config`);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}

