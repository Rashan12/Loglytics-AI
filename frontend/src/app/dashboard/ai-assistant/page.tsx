'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Copy, ThumbsUp, ThumbsDown, RotateCcw, Upload, Paperclip, X, MessageSquare, Plus, Settings } from 'lucide-react';
import { API_ENDPOINTS } from '@/config/api';
import { ChatInput } from '@/components/chat/chat-input';
import { Message } from '@/components/chat/message';
import { EmptyChat } from '@/components/chat/empty-chat';
import { ModelSelector } from '@/components/chat/model-selector';
import { useChatStore } from '@/store/chat-store';
import { motion, AnimatePresence } from 'framer-motion';

export default function AIAssistantPage() {
  const [showConversations, setShowConversations] = useState(false);
  const [userSubscription, setUserSubscription] = useState<string>('free');
  const [showModelSelector, setShowModelSelector] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    currentChat,
    messages,
    isLoading,
    isStreaming,
    chats,
    setCurrentChat,
    addMessage,
    createChat,
    deleteChat,
    sendMessage,
    clearMessages
  } = useChatStore();

  useEffect(() => {
    loadUserInfo();
    // Create a default chat for AI Assistant if none exists
    if (!currentChat) {
      createChat('ai-assistant', 'AI Assistant Chat', 'local');
    }
  }, []);

  const loadUserInfo = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const user = await response.json();
        setUserSubscription(user.subscription_tier || 'free');
      }
    } catch (error) {
      console.error('Error loading user info:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (content: string, files?: File[]) => {
    if ((!content.trim() && (!files || files.length === 0)) || isLoading) return;

    try {
      // Use the chat store's sendMessage method
      await sendMessage(content, files);
    } catch (error: any) {
      console.error('❌ Chat error:', error);
      
      const errorMessage = {
        role: 'assistant' as const,
        content: `I apologize, but I encountered an error: ${error.message || 'Unknown error'}. Please check the console for details and try again.`,
      };
      addMessage(errorMessage);
    }
  };

  const startNewConversation = () => {
    createChat('ai-assistant', 'AI Assistant Chat', userSubscription === 'pro' ? 'maverick' : 'local');
    clearMessages();
  };

  const deleteConversation = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this conversation?')) return;
    
    deleteChat(chatId);
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex bg-gradient-to-br from-[#0A0E14] via-[#0D1117] to-[#0A0E14]">
      {/* Sidebar - Conversation History */}
      <div className={`${showConversations ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-[#30363D]/50 bg-[#0D1117]`}>
        <div className="p-4 border-b border-[#30363D]/50">
          <button
            onClick={startNewConversation}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl text-white font-semibold transition-all shadow-lg"
          >
            <Plus className="w-5 h-5" />
            New Chat
          </button>
        </div>
        
        <div className="overflow-y-auto h-[calc(100vh-12rem)]">
          {chats.length === 0 ? (
            <div className="p-6 text-center">
              <MessageSquare className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-sm text-gray-500">No conversations yet</p>
            </div>
          ) : (
            <div className="p-2 space-y-2">
              {chats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => setCurrentChat(chat)}
                  className={`w-full text-left p-3 rounded-xl transition-all group ${
                    currentChat?.id === chat.id
                      ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-600/30'
                      : 'hover:bg-[#161B22] border border-transparent'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate mb-1">
                        {chat.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(chat.updatedAt).toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={(e) => deleteConversation(chat.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-600/20 rounded-lg text-gray-500 hover:text-red-400 transition-all ml-2"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#161B22] to-[#1C2128] border-b border-[#30363D]/50 px-8 py-5 flex-shrink-0 backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowConversations(!showConversations)}
                className="p-2 hover:bg-[#1C2128] rounded-xl transition-all"
              >
                <MessageSquare className="w-6 h-6 text-gray-400" />
              </button>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur-xl opacity-50 animate-pulse"></div>
                <div className="relative p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  AI Assistant
                </h1>
                <p className="text-sm text-gray-400 mt-0.5">
                  {userSubscription === 'pro' 
                    ? 'Powered by Llama 4 Maverick (Cloud)' 
                    : 'Powered by Llama 3.2 (Local)'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Model Selector for Pro users */}
              {userSubscription === 'pro' && (
                <button
                  onClick={() => setShowModelSelector(!showModelSelector)}
                  className="flex items-center gap-2 px-4 py-2 bg-[#1C2128] hover:bg-[#252C36] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-gray-300 hover:text-white font-medium transition-all"
                >
                  <Settings className="w-4 h-4" />
                  <span className="text-sm">Model</span>
                </button>
              )}
              
              <button
                onClick={startNewConversation}
                className="flex items-center gap-2 px-5 py-2.5 bg-[#1C2128] hover:bg-[#252C36] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-gray-300 hover:text-white font-medium transition-all shadow-lg hover:shadow-blue-600/20"
              >
                <Plus className="w-4 h-4" />
                <span className="text-sm">New Chat</span>
              </button>
            </div>
          </div>
        </div>

        {/* Model Selector Dropdown */}
        <AnimatePresence>
          {showModelSelector && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-[#161B22] border-b border-[#30363D]/50 px-8 py-4"
            >
              <ModelSelector
                currentModel={currentChat?.model || 'local'}
                onModelChange={(model) => {
                  if (currentChat) {
                    setCurrentChat({ ...currentChat, model });
                  }
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <EmptyChat onSendMessage={handleSend} onSuggestionClick={handleSuggestionClick} />
            ) : (
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <Message
                    key={message.id}
                    message={message}
                    isLast={index === messages.length - 1}
                    isStreaming={message.isStreaming || false}
                  />
                ))}
                
                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex justify-start animate-fadeIn">
                    <div className="flex gap-4 max-w-3xl">
                      <div className="flex-shrink-0 w-11 h-11 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                        <Sparkles className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="inline-block p-5 bg-[#161B22] border border-[#30363D] rounded-2xl shadow-xl">
                          <div className="flex gap-2">
                            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce"></div>
                            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-[#30363D]/50 bg-gradient-to-r from-[#161B22] to-[#1C2128] px-8 py-5 flex-shrink-0 backdrop-blur-xl">
          <div className="max-w-4xl mx-auto">
            {/* Suggestions */}
            {messages.length <= 1 && (
              <div className="flex flex-wrap gap-2 mb-3">
                <button 
                  onClick={() => handleSuggestionClick("Analyze the error patterns in my logs")}
                  className="px-4 py-2 bg-[#1C2128] hover:bg-[#252C36] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-sm text-gray-400 hover:text-white transition-all shadow-lg"
                >
                  Analyze error patterns
                </button>
                <button 
                  onClick={() => handleSuggestionClick("What are the most common issues in my logs?")}
                  className="px-4 py-2 bg-[#1C2128] hover:bg-[#252C36] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-sm text-gray-400 hover:text-white transition-all shadow-lg"
                >
                  Common issues
                </button>
                <button 
                  onClick={() => handleSuggestionClick("Show me performance bottlenecks")}
                  className="px-4 py-2 bg-[#1C2128] hover:bg-[#252C36] border border-[#30363D] hover:border-blue-600/50 rounded-xl text-sm text-gray-400 hover:text-white transition-all shadow-lg"
                >
                  Performance issues
                </button>
              </div>
            )}

            {/* Chat Input Component */}
            <ChatInput
              onSendMessage={handleSend}
              disabled={isLoading}
              placeholder="Ask me anything about your logs..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}