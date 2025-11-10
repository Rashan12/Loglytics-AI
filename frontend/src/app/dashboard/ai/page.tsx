'use client';

import { useState, useRef, useEffect } from 'react';
import { Sparkles, Trash2, MessageSquare, Bot, User, ChevronDown, Check, Copy, ThumbsUp, ThumbsDown, RotateCcw, Loader2 } from 'lucide-react';
import { ChatInput } from '@/components/chat/chat-input';
import { useChatStore } from '@/store/chat-store';
import { Message } from '@/components/chat/message';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import { useAuthStore } from '@/store/auth-store';
import { cn } from '@/lib/utils';

export default function AIAssistantPage() {
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const modelSelectorRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    isLoading,
    isStreaming,
    selectedModel,
    sendMessage,
    clearMessages,
    setSelectedModel,
    stopGeneration
  } = useChatStore();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelSelectorRef.current && !modelSelectorRef.current.contains(event.target as Node)) {
        setShowModelSelector(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';
  const isProUser = user?.subscription_tier === 'pro';

  // Model configurations
  const models = {
    local: {
      name: 'Local LLM',
      description: 'Free, private, runs on your device',
      tags: ['Free', 'Private', 'Fast', 'Offline'],
      isFree: true,
    },
    maverick: {
      name: 'Llama Maverick',
      description: 'Advanced AI model for complex analysis',
      tags: ['Advanced', 'Accurate', 'Context-aware'],
      cost: '$0.002/token',
      tokensUsed: 1250,
      costToday: '$2.50',
    },
  };

  const currentModel = models[selectedModel as keyof typeof models] || models.maverick;

  // Professional suggested prompts with titles and descriptions
  const suggestedPrompts = [
    {
      title: 'Analyze error patterns',
      description: 'Find patterns in error logs',
      prompt: 'Analyze error patterns in my logs',
    },
    {
      title: 'Critical errors today',
      description: 'Show critical issues',
      prompt: 'Show me critical errors from today',
    },
    {
      title: 'Application health',
      description: 'Overall system status',
      prompt: 'Summarize application health status',
    },
    {
      title: 'Common warnings',
      description: 'Frequent warning messages',
      prompt: 'What are the most common warnings?',
    },
  ];

  // PRESERVE ALL EXISTING HANDLERS
  const handleSend = async (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0)) return;
    await sendMessage(content, files);
  };

  const handleSuggestionClick = (prompt: string) => {
    handleSend(prompt);
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      clearMessages();
    }
  };

  const handleModelChange = (model: 'local' | 'maverick') => {
    if (model === 'maverick' && !isProUser) {
      // TODO: Show upgrade modal
      console.log('Upgrade to Pro required');
      return;
    }
    setSelectedModel(model);
    setShowModelSelector(false);
  };

  return (
    <div className={cn(
      'min-h-screen transition-colors duration-300',
      isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
    )}>
      {/* Main Content - Adjusts with sidebar */}
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20 h-screen flex flex-col"
      >
        {/* Header - Fixed with Model Selector */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className={cn(
            'px-8 py-4 border-b flex-shrink-0',
            isDark 
              ? 'border-[#2E3A5C]/50 bg-[#0A0E1A]/95' 
              : 'border-gray-200 bg-white/95'
          )}
          style={{ backdropFilter: 'blur(24px)' }}
        >
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            {/* Left: AI Assistant Title + Model Selector */}
            <div className="flex items-center gap-4">
              {/* Enhanced Icon with Gradient */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF] rounded-xl blur-lg opacity-50 animate-pulse" />
                <div className="relative p-2.5 bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF] rounded-xl shadow-[0_4px_20px_rgba(139,92,246,0.4)]">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div>
                  <h1 className={cn(
                    'text-xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    AI Assistant
                  </h1>
                  <p className={cn(
                    'text-xs',
                    isDark ? 'text-[#64748B]' : 'text-gray-500'
                  )}>
                    Ask me anything about your logs
                  </p>
                </div>

                {/* Model Selector Dropdown - Compact */}
                <div className="relative" ref={modelSelectorRef}>
                  <button
                    onClick={() => setShowModelSelector(!showModelSelector)}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg border transition-all',
                      isDark
                        ? 'bg-[#1A1F3A] border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 text-[#F9FAFB]'
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
                            {/* Local LLM */}
                            <button
                              onClick={() => handleModelChange('local')}
                              className={cn(
                                'w-full p-3 rounded-lg border transition-all text-left',
                                selectedModel === 'local'
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
                                      {models.local.name}
                                    </h4>
                                    {selectedModel === 'local' && (
                                      <Check className="w-4 h-4 text-[#2E9BFF]" />
                                    )}
                                  </div>
                                  <p className={cn(
                                    'text-xs mt-1',
                                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                                  )}>
                                    {models.local.description}
                                  </p>
                                </div>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {models.local.tags.map((tag) => (
                                  <span
                                    key={tag}
                                    className={cn(
                                      'px-2 py-0.5 text-xs font-medium rounded',
                                      'bg-[#10B981]/20 text-[#10B981]'
                                    )}
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </button>

                            {/* Llama Maverick */}
                            <button
                              onClick={() => handleModelChange('maverick')}
                              className={cn(
                                'w-full p-3 rounded-lg border transition-all text-left',
                                selectedModel === 'maverick'
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
                                      {models.maverick.name}
                                    </h4>
                                    {selectedModel === 'maverick' && (
                                      <Check className="w-4 h-4 text-[#2E9BFF]" />
                                    )}
                                  </div>
                                  <p className={cn(
                                    'text-xs mt-1',
                                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                                  )}>
                                    {models.maverick.description}
                                  </p>
                                </div>
                              </div>
                              <div className="flex flex-wrap gap-2 mb-2">
                                {models.maverick.tags.map((tag) => (
                                  <span
                                    key={tag}
                                    className={cn(
                                      'px-2 py-0.5 text-xs font-medium rounded',
                                      isDark
                                        ? 'bg-[#2E9BFF]/20 text-[#2E9BFF]'
                                        : 'bg-blue-100 text-blue-700'
                                    )}
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                              {models.maverick.cost && (
                                <div className={cn(
                                  'text-xs pt-2 border-t',
                                  isDark ? 'border-[#2E3A5C]/30 text-[#64748B]' : 'border-gray-200 text-gray-500'
                                )}>
                                  <div className="flex justify-between">
                                    <span>{models.maverick.cost}</span>
                                    <span>{models.maverick.tokensUsed} tokens used</span>
                                  </div>
                                  <div className="mt-1">
                                    Cost today: <span className="font-semibold">{models.maverick.costToday}</span>
                                  </div>
                                </div>
                              )}
                            </button>
                          </div>

                          {!isProUser && (
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
                                'w-full px-4 py-2 text-sm font-semibold rounded-lg text-white transition-transform hover:scale-[1.02]',
                                'bg-gradient-to-r from-[#8B5CF6] to-[#2E9BFF]'
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
        </motion.div>

        {/* Messages Container - Scrollable */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          <div className="max-w-4xl mx-auto">
            <AnimatePresence mode="wait">
              {messages.length === 0 ? (
                // Empty State with Professional Suggested Prompts
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5 }}
                  className="h-full flex flex-col items-center justify-center py-12"
                >
                  {/* Icon */}
                  <div className={cn(
                    'w-20 h-20 rounded-2xl mb-6 flex items-center justify-center relative',
                    isDark
                      ? 'bg-[#1A1F3A] border border-[#2E3A5C]/50'
                      : 'bg-white border border-gray-200'
                  )}>
                    <div className="absolute inset-0 bg-gradient-to-br from-[#8B5CF6]/20 to-[#2E9BFF]/20 rounded-2xl blur-xl" />
                    <Sparkles className={cn(
                      'w-10 h-10 relative z-10',
                      isDark ? 'text-[#8B5CF6]' : 'text-purple-600'
                    )} />
                  </div>

                  {/* Welcome Text */}
                  <h2 className={cn(
                    'text-2xl font-bold mb-2',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Welcome to AI Assistant
                  </h2>
                  <p className={cn(
                    'text-base mb-8 text-center max-w-md',
                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                  )}>
                    I can help you analyze logs, find patterns, and answer questions about your application
                  </p>

                  {/* Professional Suggested Prompts - 2x2 Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-3xl">
                    {suggestedPrompts.map((item, index) => (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                        onClick={() => handleSuggestionClick(item.prompt)}
                        className={cn(
                          'p-5 rounded-xl border transition-all text-left group',
                          isDark
                            ? 'bg-[#1A1F3A] border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50 hover:bg-[#1A1F3A]/80'
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
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-6 pb-4"
                >
                  {messages.map((message, index) => (
                    <Message
                      key={message.id}
                      message={message}
                      isLast={index === messages.length - 1}
                      isStreaming={isStreaming && index === messages.length - 1}
                    />
                  ))}
                  <div ref={messagesEndRef} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Enhanced Loading Indicator */}
            {isLoading && messages.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start mt-6"
              >
                <div className="flex gap-4 max-w-3xl">
                  <div className={cn(
                    'flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center shadow-lg',
                    isDark
                      ? 'bg-gradient-to-br from-[#8B5CF6] to-[#2E9BFF]'
                      : 'bg-gradient-to-br from-purple-500 to-blue-500'
                  )}>
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className={cn(
                      'inline-block p-5 rounded-xl',
                      isDark
                        ? 'bg-[#1A1F3A] border border-[#2E3A5C]/50'
                        : 'bg-white border border-gray-200'
                    )}>
                      <div className="flex gap-2">
                        <div className="w-2.5 h-2.5 bg-[#2E9BFF] rounded-full animate-bounce"></div>
                        <div className="w-2.5 h-2.5 bg-[#2E9BFF] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2.5 h-2.5 bg-[#2E9BFF] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Input Area - Fixed at Bottom - NO MODEL SELECTOR */}
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          transition={{ duration: 0.3 }}
          className={cn(
            'border-t px-8 py-4 flex-shrink-0',
            isDark 
              ? 'border-[#2E3A5C]/50 bg-[#0A0E1A]/95' 
              : 'border-gray-200 bg-white/95'
          )}
          style={{ backdropFilter: 'blur(24px)' }}
        >
          <div className="max-w-4xl mx-auto">
            {/* Chat Input Component - Solid Background */}
            <div className={cn(
              'relative rounded-xl border transition-all',
              isDark
                ? 'bg-[#1A1F3A] border-[#2E3A5C]/50 focus-within:border-[#2E9BFF]'
                : 'bg-white border-gray-200 focus-within:border-blue-500'
            )}>
              <ChatInput
                onSendMessage={handleSend}
                disabled={isLoading || isStreaming}
                placeholder="Ask me anything about your logs..."
              />
            </div>

            {/* Disclaimer */}
            <p className={cn(
              'text-xs mt-2 text-center',
              isDark ? 'text-[#64748B]' : 'text-gray-500'
            )}>
              Press Enter to send, Shift+Enter for new line • AI can make mistakes
            </p>
          </div>
        </motion.div>
      </motion.main>
    </div>
  );
}
