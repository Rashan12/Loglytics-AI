'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useRouter } from 'next/navigation';
import {
  Send,
  Sparkles,
  Loader2,
  User,
  Bot,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Trash2,
  ChevronDown,
  Check,
  MessageSquare,
  FolderOpen,
  ArrowLeft,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/auth-store';
import { useChatStore } from '@/store/chat-store';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';
import { ChatInput } from '@/components/chat/chat-input';
import { API_V1 } from '@/config/api';

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { user } = useAuthStore();
  const [mounted, setMounted] = React.useState(false);
  const [showModelSelector, setShowModelSelector] = React.useState(false);
  const [projectName, setProjectName] = React.useState('');
  const [projectDescription, setProjectDescription] = React.useState('');
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const messagesContainerRef = React.useRef<HTMLDivElement>(null);
  const modelSelectorRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const { 
    messages, 
    isLoading, 
    isStreaming, 
    currentChat, 
    setCurrentChat,
    sendMessage: storeSendMessage,
    stopGeneration,
    deleteChat,
    clearMessages,
    addMessage,
    selectedModel,
    setSelectedModel,
  } = useChatStore();

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';
  const isProUser = user?.subscription_tier === 'pro';

  // Model configurations
  const models = {
    local: {
      id: 'local',
      name: 'Local LLM',
      description: 'Free, private, runs on your device',
      tags: ['Free', 'Private', 'Fast', 'Offline'],
      isFree: true,
    },
    maverick: {
      id: 'maverick',
      name: 'Llama Maverick',
      description: 'Advanced AI model for complex analysis',
      tags: ['Advanced', 'Accurate', 'Context-aware'],
      cost: '$0.002/token',
      tokensUsed: 1250,
      costToday: '$2.50',
      isFree: false,
    },
  };

  const currentModel = models[selectedModel as keyof typeof models] || models.local;

  // Professional suggested prompts
  const suggestedPrompts = [
    {
      title: 'Analyze error patterns',
      description: 'Find patterns in project logs',
      prompt: 'Analyze the error patterns in my logs',
    },
    {
      title: 'Common issues',
      description: 'Most frequent problems',
      prompt: 'What are the most common issues in my logs?',
    },
    {
      title: 'Performance bottlenecks',
      description: 'Identify slow operations',
      prompt: 'Show me performance bottlenecks',
    },
    {
      title: 'Troubleshoot error',
      description: 'Debug specific issues',
      prompt: 'Help me troubleshoot this error',
    },
  ];

  // PRESERVE EXISTING DATA FETCHING
  const loadProjectDetails = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_V1}/projects/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const project = await response.json();
        setProjectName(project.name);
        setProjectDescription(project.description || '');
      }
    } catch (error) {
      console.error('Error loading project:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const chatId = params.chatId as string;
      
      console.log('📂 Loading chat history for chatId:', chatId, 'project:', params.id);
      
      // If chatId is a timestamp (new chat), create a new chat via API
      if (chatId && !isNaN(Number(chatId))) {
        console.log('🆕 Creating new chat for project:', params.id);
        try {
          const createResponse = await fetch(`${API_V1}/projects/${params.id}/chat/new`, {
            method: 'POST',
            headers: { 
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (createResponse.ok) {
            const newChat = await createResponse.json();
            console.log('✅ Created new chat:', newChat.session_id);
            window.history.replaceState(null, '', `/dashboard/projects/${params.id}/chats/${newChat.session_id}`);
            return;
          }
        } catch (createError) {
          console.error('Error creating new chat:', createError);
        }
      }
      
      // Build URL with session_id parameter if it's a UUID (not a timestamp)
      let historyUrl = `${API_V1}/projects/${params.id}/chat/history`;
      if (chatId && !chatId.match(/^\d+$/)) {
        historyUrl += `?session_id=${chatId}`;
        console.log('📝 Loading specific chat session:', chatId);
      }
      
      const response = await fetch(historyUrl, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('📚 Loaded chat history:', data.messages?.length || 0, 'messages');
        
        const actualSessionId = data.session_id || chatId;
        
        // Create or update chat in store
        const { createChat, clearMessages, setCurrentChat } = useChatStore.getState();
        createChat(params.id as string, projectName || 'Project Chat', selectedModel);
        
        const currentChat = {
          id: actualSessionId,
          title: projectName || 'Project Chat',
          projectId: params.id as string,
          model: selectedModel,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messageCount: data.messages?.length || 0,
          messages: []
        };
        setCurrentChat(currentChat);
        clearMessages();
        
        // Load history
        if (data.messages && data.messages.length > 0) {
          data.messages.forEach((msg: any) => {
            addMessage({
              role: msg.role,
              content: msg.content,
              model: selectedModel
            });
          });
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  React.useEffect(() => {
    const initializeChat = async () => {
      await loadProjectDetails();
      await loadChatHistory();
    };
    initializeChat();
  }, [params.id, params.chatId]);

  // Auto-scroll to bottom
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelSelectorRef.current && !modelSelectorRef.current.contains(event.target as Node)) {
        setShowModelSelector(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // PRESERVE EXISTING MESSAGE SEND HANDLER
  const handleSendMessage = async (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0)) return;
    
    // Add user message to UI immediately
    const userMessage = {
      role: 'user' as const,
      content: content,
      files: files && files.length > 0 ? files.map(f => ({
        id: Math.random().toString(),
        name: f.name,
        size: f.size,
        type: f.type
      })) : undefined
    };
    
    addMessage(userMessage);
    
    try {
      const token = localStorage.getItem('access_token');
      const chatId = params.chatId as string;
      const formData = new FormData();
      
      if (files && files.length > 0) {
        formData.append('file', files[0]);
      }
      formData.append('message', content);
      
      // Add session_id if available
      const { currentChat } = useChatStore.getState();
      if (currentChat?.id && !currentChat.id.match(/^\d+$/)) {
        formData.append('session_id', currentChat.id);
      } else if (chatId && !chatId.match(/^\d+$/)) {
        formData.append('session_id', chatId);
      }
      
      const response = await fetch(`${API_V1}/projects/${params.id}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add AI response
        const aiMessage = {
          role: 'assistant' as const,
          content: data.response || 'I received your message.',
          model: selectedModel
        };
        
        addMessage(aiMessage);
      } else {
        const errorText = await response.text();
        console.error('❌ Server error:', response.status, errorText);
        
        const errorMessage = {
          role: 'assistant' as const,
          content: `Sorry, I encountered an error (${response.status}). Please try again.`
        };
        addMessage(errorMessage);
      }
    } catch (error) {
      console.error('❌ Chat error:', error);
      
      const errorMessage = {
        role: 'assistant' as const,
        content: 'Sorry, I encountered a network error. Please check your connection and try again.'
      };
      addMessage(errorMessage);
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      clearMessages();
    }
  };

  const handleBackToProjects = () => {
    router.push(`/dashboard/projects/${params.id}`);
  };

  const handleSuggestedPrompt = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleModelChange = (model: 'local' | 'maverick') => {
    if (model === 'maverick' && !isProUser) {
      console.log('Upgrade to Pro required');
      return;
    }
    setSelectedModel(model);
    setShowModelSelector(false);
  };

  return (
    <motion.main
      initial={false}
      animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="pt-20 h-screen flex flex-col"
    >
      {/* Header with Project Context + Model Selector */}
      <div className={cn(
        'px-8 py-4 border-b',
        isDark ? 'border-[#2E3A5C]/50 bg-[#0A0E1A]' : 'border-gray-200 bg-white'
      )}>
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          {/* Left: Back + Project + AI Assistant Title + Model Selector */}
          <div className="flex items-center gap-4">
            <button
              onClick={handleBackToProjects}
              className={cn(
                'p-2 rounded-lg transition-all',
                isDark
                  ? 'hover:bg-[#1A1F3A] text-[#94A3B8] hover:text-[#F9FAFB]'
                  : 'hover:bg-gray-100 text-gray-600 hover:text-gray-900'
              )}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-xl blur-lg opacity-50 animate-pulse" />
              <div className="relative p-2.5 bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-xl">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h1 className={cn(
                    'text-xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    AI Assistant
                  </h1>
                  {projectName && (
                    <div className={cn(
                      'flex items-center gap-1.5 px-2 py-1 rounded-lg border',
                      isDark
                        ? 'bg-[#2E9BFF]/10 border-[#2E9BFF]/30'
                        : 'bg-blue-50 border-blue-200'
                    )}>
                      <FolderOpen className={cn(
                        'w-3 h-3',
                        isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                      )} />
                      <span className={cn(
                        'text-xs font-medium',
                        isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                      )}>
                        {projectName}
                      </span>
                    </div>
                  )}
                </div>
                <p className={cn(
                  'text-xs',
                  isDark ? 'text-[#64748B]' : 'text-gray-500'
                )}>
                  Ask questions about this project's logs
                </p>
              </div>

              {/* Model Selector Dropdown */}
              <div className="relative" ref={modelSelectorRef}>
                <button
                  onClick={() => setShowModelSelector(!showModelSelector)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg border transition-all',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 text-[#F9FAFB]'
                      : 'bg-white border-gray-200 hover:border-blue-300 text-gray-900'
                  )}
                >
                  <Sparkles className="w-4 h-4 text-[#8B5CF6]" />
                  <span className="text-sm font-medium">{currentModel.name}</span>
                  <ChevronDown className={cn(
                    'w-4 h-4 transition-transform',
                    showModelSelector ? 'rotate-180' : ''
                  )} />
                </button>

                {/* Dropdown Menu */}
                <AnimatePresence>
                  {showModelSelector && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                      className={cn(
                        'absolute top-full left-0 mt-2 w-96 rounded-xl border shadow-2xl z-50',
                        isDark
                          ? 'bg-[#1A1F3A] border-[#2E3A5C]/50'
                          : 'bg-white border-gray-200'
                      )}
                    >
                      <div className="p-4">
                        <h3 className={cn(
                          'text-sm font-semibold mb-3',
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        )}>
                          Choose AI Model
                        </h3>

                        <div className="space-y-3">
                          {Object.values(models).map((model) => (
                            <button
                              key={model.id}
                              onClick={() => handleModelChange(model.id as 'local' | 'maverick')}
                              className={cn(
                                'w-full p-3 rounded-lg border transition-all text-left',
                                selectedModel === model.id
                                  ? isDark
                                    ? 'bg-[#2E9BFF]/10 border-[#2E9BFF]/50'
                                    : 'bg-blue-50 border-blue-300'
                                  : isDark
                                  ? 'bg-[#0D1117]/60 border-[#2E3A5C]/30 hover:border-[#2E9BFF]/30'
                                  : 'bg-gray-50 border-gray-200 hover:border-blue-200'
                              )}
                            >
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <h4 className={cn(
                                      'text-sm font-semibold',
                                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                                    )}>
                                      {model.name}
                                    </h4>
                                    {selectedModel === model.id && (
                                      <Check className="w-4 h-4 text-[#2E9BFF]" />
                                    )}
                                  </div>
                                  <p className={cn(
                                    'text-xs mt-1',
                                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                                  )}>
                                    {model.description}
                                  </p>
                                </div>
                              </div>

                              <div className="flex flex-wrap gap-2 mb-2">
                                {model.tags.map((tag) => (
                                  <span
                                    key={tag}
                                    className={cn(
                                      'px-2 py-0.5 text-xs font-medium rounded',
                                      tag === 'Free'
                                        ? 'bg-[#10B981]/20 text-[#10B981]'
                                        : isDark
                                        ? 'bg-[#2E9BFF]/20 text-[#2E9BFF]'
                                        : 'bg-blue-100 text-blue-700'
                                    )}
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>

                              {model.cost && (
                                <div className={cn(
                                  'text-xs pt-2 border-t',
                                  isDark ? 'border-[#2E3A5C]/30 text-[#64748B]' : 'border-gray-200 text-gray-500'
                                )}>
                                  <div className="flex justify-between">
                                    <span>{model.cost}</span>
                                    <span>{model.tokensUsed} tokens used</span>
                                  </div>
                                  <div className="mt-1">Cost today: <span className="font-semibold">{model.costToday}</span></div>
                                </div>
                              )}
                            </button>
                          ))}
                        </div>

                        {!currentModel.isFree && (
                          <div className={cn(
                            'mt-4 p-3 rounded-lg border',
                            isDark
                              ? 'bg-gradient-to-r from-[#8B5CF6]/10 to-[#2E9BFF]/10 border-[#8B5CF6]/30'
                              : 'bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200'
                          )}>
                            <h4 className={cn(
                              'text-sm font-semibold mb-1',
                              isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                            )}>
                              Upgrade to Pro
                            </h4>
                            <p className={cn(
                              'text-xs mb-3',
                              isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                            )}>
                              Get access to Llama Maverick and advanced features
                            </p>
                            <button className={cn(
                              'w-full px-4 py-2 text-sm font-semibold rounded-lg text-white transition-transform',
                              'bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] hover:scale-[1.02]'
                            )}>
                              Upgrade Now
                            </button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Right: Clear Chat Button */}
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
                isDark
                  ? 'text-[#94A3B8] hover:text-[#EF4444] hover:bg-[#1E293B]'
                  : 'text-gray-600 hover:text-red-600 hover:bg-gray-100'
              )}
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm font-medium">Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            // Empty State with Professional Suggested Prompts
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="h-full flex flex-col items-center justify-center py-12"
            >
              <div className={cn(
                'w-20 h-20 rounded-2xl mb-6 flex items-center justify-center relative',
                isDark
                  ? 'bg-[#1A1F3A]/60'
                  : 'bg-white border border-gray-200'
              )}>
                <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/20 to-[#2E9BFF]/20 rounded-2xl blur-xl" />
                <Sparkles className={cn(
                  'w-10 h-10 relative',
                  isDark ? 'text-[#8B5CF6]' : 'text-purple-600'
                )} />
              </div>

              <h2 className={cn(
                'text-2xl font-bold mb-2',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                Start a New Conversation
              </h2>
              <p className={cn(
                'text-base mb-8 text-center max-w-md',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Ask questions about your logs, upload files, or get AI-powered insights
              </p>

              {/* Professional Suggested Prompts - 2x2 Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-3xl">
                {suggestedPrompts.map((item, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                    onClick={() => handleSuggestedPrompt(item.prompt)}
                    className={cn(
                      'p-5 rounded-xl border transition-all text-left group',
                      isDark
                        ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 hover:bg-[#1A1F3A]/80'
                        : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-lg'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div className={cn(
                        'p-2 rounded-lg',
                        isDark
                          ? 'bg-[#2E9BFF]/10 text-[#2E9BFF]'
                          : 'bg-blue-50 text-blue-600'
                      )}>
                        <Sparkles className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <h3 className={cn(
                          'text-sm font-semibold mb-1 group-hover:text-[#2E9BFF] transition-colors',
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        )}>
                          {item.title}
                        </h3>
                        <p className={cn(
                          'text-xs',
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        )}>
                          {item.description}
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            // Messages List
            <div className="space-y-6 pb-4">
              {messages.map((message, index) => (
                <motion.div
                  key={message.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    'flex gap-4',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF]">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}

                  <div className={cn(
                    'flex-1 max-w-3xl',
                    message.role === 'user' ? 'flex justify-end' : ''
                  )}>
                    <div className={cn(
                      'rounded-xl px-5 py-4',
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] text-white'
                        : isDark
                        ? 'bg-[#1A1F3A] border border-[#2E3A5C]/50'
                        : 'bg-white border border-gray-200'
                    )}>
                      <p className={cn(
                        'text-sm leading-relaxed whitespace-pre-wrap',
                        message.role === 'assistant' && isDark ? 'text-[#F9FAFB]' : 
                        message.role === 'assistant' ? 'text-gray-900' : ''
                      )}>
                        {message.content}
                        {isStreaming && index === messages.length - 1 && message.role === 'assistant' && (
                          <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse" />
                        )}
                      </p>

                      {message.role === 'assistant' && !isStreaming && (
                        <div className={cn(
                          'flex items-center gap-2 mt-3 pt-3 border-t',
                          isDark ? 'border-[#2E3A5C]/30' : 'border-gray-200'
                        )}>
                          <button
                            onClick={() => handleCopyMessage(message.content)}
                            className={cn(
                              'p-1.5 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="Copy"
                          >
                            <Copy className="w-3.5 h-3.5" />
                          </button>
                          <button
                            className={cn(
                              'p-1.5 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="Good"
                          >
                            <ThumbsUp className="w-3.5 h-3.5" />
                          </button>
                          <button
                            className={cn(
                              'p-1.5 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="Bad"
                          >
                            <ThumbsDown className="w-3.5 h-3.5" />
                          </button>
                          <button
                            className={cn(
                              'p-1.5 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="Regenerate"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>

                    <p className={cn(
                      'text-xs mt-1.5 px-2',
                      isDark ? 'text-[#64748B]' : 'text-gray-500'
                    )}>
                      {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
                    </p>
                  </div>

                  {message.role === 'user' && (
                    <div className={cn(
                      'flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center',
                      isDark ? 'bg-[#2E3A5C]' : 'bg-gray-200'
                    )}>
                      <User className={cn(
                        'w-5 h-5',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )} />
                    </div>
                  )}
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area - Fixed at Bottom */}
      <div className={cn(
        'border-t px-8 py-4',
        isDark ? 'border-[#2E3A5C]/50 bg-[#0A0E1A]' : 'border-gray-200 bg-white'
      )}>
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isStreaming}
            placeholder="Ask me anything about your logs..."
          />

          <p className={cn(
            'text-xs mt-2 text-center',
            isDark ? 'text-[#64748B]' : 'text-gray-500'
          )}>
            Press Enter to send, Shift+Enter for new line • AI can make mistakes
          </p>
        </div>
      </div>
    </motion.main>
  );
}
