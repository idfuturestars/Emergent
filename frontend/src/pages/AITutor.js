import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  SparklesIcon,
  PaperAirplaneIcon,
  ClipboardDocumentIcon,
  HandThumbUpIcon,
  HandThumbDownIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';

const AITutor = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('openai-gpt4');
  const [availableModels, setAvailableModels] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch available AI models
    const fetchModels = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/ai/models`);
        setAvailableModels(response.data);
      } catch (error) {
        console.error('Failed to fetch models:', error);
      }
    };

    fetchModels();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/v1/ai/chat`, {
        message: inputMessage,
        conversation_id: currentConversation?.id,
        model: selectedModel,
        subject: 'general',
        temperature: 0.7,
        max_tokens: 1000
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        model: response.data.model,
        tokens_used: response.data.tokens_used,
        response_time_ms: response.data.response_time_ms,
        message_id: response.data.message_id
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (!currentConversation) {
        setCurrentConversation({ id: response.data.conversation_id });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const rateMessage = async (messageId, rating) => {
    try {
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/v1/ai/rate-message`, {
        message_id: messageId,
        rating: rating
      });
    } catch (error) {
      console.error('Failed to rate message:', error);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 rounded-xl mb-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-xl flex items-center justify-center ai-avatar">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white glow-text">AI Tutor</h1>
              <p className="text-gray-300">Ask me anything - I'm here to help you learn!</p>
            </div>
          </div>

          {/* Model Selector */}
          <div className="flex items-center space-x-4">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="form-input px-4 py-2 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-space-500"
            >
              {availableModels.map((model) => (
                <option key={model.model} value={model.model}>
                  {model.info.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Chat Area */}
      <div className="flex-1 glass-card rounded-xl overflow-hidden flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <SparklesIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-white mb-2">Start a conversation</h3>
              <p className="text-gray-400">
                Ask me anything! I can help with math, science, writing, coding, and more.
              </p>
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {[
                  "Explain quantum physics in simple terms",
                  "Help me solve this algebra problem",
                  "Write a creative story about space",
                  "How does photosynthesis work?"
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(example)}
                    className="p-3 text-left glass border border-gray-600 hover:border-space-400 rounded-lg transition-colors"
                  >
                    <p className="text-sm text-gray-300">{example}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${
                  message.role === 'user' 
                    ? 'chat-bubble-user' 
                    : 'chat-bubble-ai'
                } p-4 rounded-2xl ${message.error ? 'border-red-500/50' : ''}`}>
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-2 mb-2">
                      <SparklesIcon className="w-4 h-4 text-space-400" />
                      <span className="text-xs text-gray-400">
                        {availableModels.find(m => m.model === message.model)?.info?.name || 'AI'}
                        {message.response_time_ms && (
                          <> • {message.response_time_ms}ms</>
                        )}
                      </span>
                    </div>
                  )}
                  
                  <div className="text-white whitespace-pre-wrap">{message.content}</div>
                  
                  {message.role === 'assistant' && !message.error && (
                    <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-600">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="p-1 text-gray-400 hover:text-white transition-colors"
                          title="Copy message"
                        >
                          <ClipboardDocumentIcon className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => rateMessage(message.message_id, 5)}
                          className="p-1 text-gray-400 hover:text-green-400 transition-colors"
                          title="Helpful"
                        >
                          <HandThumbUpIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => rateMessage(message.message_id, 1)}
                          className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                          title="Not helpful"
                        >
                          <HandThumbDownIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
          
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="chat-bubble-ai p-4 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-gray-400">AI is thinking...</span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-gray-800">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className="form-input w-full px-4 py-3 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-space-500 resize-none"
                rows="1"
                style={{ minHeight: '44px', maxHeight: '120px' }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || loading}
              className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white p-3 rounded-lg hover:shadow-neon transition-all duration-300 neon-button disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AITutor;