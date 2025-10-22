'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Copy, ThumbsUp, ThumbsDown, RotateCcw } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI assistant for log analysis. I can help you:\n\n• Understand patterns in your logs\n• Detect anomalies and errors\n• Troubleshoot issues\n• Generate insights from log data\n• Answer questions about your applications\n\nWhat would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          message: input,
          conversation_history: messages.slice(-5) // Last 5 messages for context
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response || "I'm here to help! Please ask me about your logs.",
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    textareaRef.current?.focus();
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    // Could add a toast notification here
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: "Chat cleared. How can I help you with your logs?",
        timestamp: new Date()
      }
    ]);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-[#0A0E14]">
      {/* Header */}
      <div className="bg-[#0F1419] border-b border-[#30363D] px-8 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">AI Assistant</h1>
              <p className="text-sm text-gray-400">Powered by advanced language models</p>
            </div>
          </div>
          
          <button
            onClick={clearChat}
            className="flex items-center gap-2 px-4 py-2 bg-[#161B22] border border-[#30363D] rounded-lg text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-sm">Clear Chat</span>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
            >
              <div className={`flex gap-4 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white'
                    : 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                }`}>
                  {message.role === 'user' ? (
                    <span className="text-sm">U</span>
                  ) : (
                    <Sparkles className="w-5 h-5" />
                  )}
                </div>

                {/* Message Content */}
                <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block p-4 rounded-2xl ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-[#161B22] border border-[#30363D] text-gray-100'
                  }`}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Message Actions (for assistant messages) */}
                  {message.role === 'assistant' && index > 0 && (
                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={() => copyMessage(message.content)}
                        className="p-1.5 hover:bg-[#1C2128] rounded text-gray-500 hover:text-gray-300 transition-colors"
                        title="Copy message"
                      >
                        <Copy className="w-3.5 h-3.5" />
                      </button>
                      <button
                        className="p-1.5 hover:bg-[#1C2128] rounded text-gray-500 hover:text-green-500 transition-colors"
                        title="Good response"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                      </button>
                      <button
                        className="p-1.5 hover:bg-[#1C2128] rounded text-gray-500 hover:text-red-500 transition-colors"
                        title="Poor response"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className={`mt-1 text-xs text-gray-500 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start animate-fadeIn">
              <div className="flex gap-4 max-w-3xl">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="inline-block p-4 bg-[#161B22] border border-[#30363D] rounded-2xl">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-[#30363D] bg-[#0F1419] px-8 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          {/* Suggestions (show when input is empty) */}
          {input === '' && messages.length <= 1 && (
            <div className="flex flex-wrap gap-2 mb-3">
              <button 
                onClick={() => handleSuggestionClick("Analyze the error patterns in my logs")}
                className="px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
              >
                Analyze error patterns
              </button>
              <button 
                onClick={() => handleSuggestionClick("What are the most common issues in my logs?")}
                className="px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
              >
                Common issues
              </button>
              <button 
                onClick={() => handleSuggestionClick("Show me performance bottlenecks")}
                className="px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
              >
                Performance issues
              </button>
              <button 
                onClick={() => handleSuggestionClick("Help me troubleshoot authentication errors")}
                className="px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
              >
                Troubleshoot auth errors
              </button>
            </div>
          )}

          {/* Input Field */}
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask me anything about your logs..."
              rows={1}
              className="w-full px-4 py-3 pr-14 bg-[#161B22] border border-[#30363D] rounded-xl text-white placeholder-gray-500 resize-none focus:outline-none focus:border-blue-600 transition-all"
              style={{ minHeight: '52px', maxHeight: '200px' }}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="absolute right-2 bottom-2 p-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* Help Text */}
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
