'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Sparkles,
  FileText,
  Filter,
  SlidersHorizontal,
  Clock,
  TrendingUp,
  Zap,
  ChevronDown,
  ChevronUp,
  Copy,
  ExternalLink,
  Loader2,
  FolderOpen,
  Calendar,
  Hash,
} from 'lucide-react';
import { GradientButton } from '@/components/ui/gradient-button';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';

// PRESERVE EXISTING TYPES - Adjust field names if needed based on actual API response
interface SearchResult {
  id: string;
  content: string;
  source: string;
  timestamp: string;
  score: number;
  metadata?: {
    filename?: string;
    project_name?: string;
    line_number?: number;
    [key: string]: any;
  };
}

export default function RAGSearchPage() {
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [projects, setProjects] = useState<any[]>([]);

  // PRESERVE EXISTING FILTER STATE
  const [filters, setFilters] = useState({
    dateRange: 'all',
    logLevel: 'all',
    source: 'all'
  });

  useEffect(() => {
    setMounted(true);

    // Load search history from localStorage
    const history = localStorage.getItem('rag_search_history');
    if (history) {
      try {
        setSearchHistory(JSON.parse(history));
      } catch (e) {
        console.error('Failed to parse search history:', e);
      }
    }

    // Load projects (optional - only if your backend supports it)
    const loadProjects = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/v1/projects', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setProjects(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    };
    loadProjects();
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  // PRESERVE EXISTING SEARCH HANDLER - Keep your API call logic
  const handleSearch = async () => {
    if (!query.trim() || searching) return;
    
    setSearching(true);
    setSearchPerformed(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      // KEEP YOUR EXISTING API CALL LOGIC
      const response = await fetch('http://localhost:8000/api/v1/rag/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          query,
          limit: 20,
          filters // PRESERVE your existing filter structure
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      } else {
        setResults([]);
      }

      // Add to search history
      const newHistory = [query, ...searchHistory.filter(h => h !== query)].slice(0, 5);
      setSearchHistory(newHistory);
      localStorage.setItem('rag_search_history', JSON.stringify(newHistory));
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const toggleResultExpanded = (resultId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId);
    } else {
      newExpanded.add(resultId);
    }
    setExpandedResults(newExpanded);
  };

  const handleCopyResult = (content: string) => {
    navigator.clipboard.writeText(content);
    // Optional: Show toast notification
  };

  const suggestedSearches = [
    'Error patterns in authentication',
    'Performance issues last 24h',
    'Database connection failures',
    'API timeout errors',
  ];

  const exampleQueries = [
    "database connection errors",
    "authentication failures",
    "high response time",
    "memory leaks",
    "API timeout issues"
  ];

  return (
    <div className={cn(
      'min-h-screen transition-colors duration-300',
      isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
    )}>
      {/* Main Content - Adjusts with sidebar (layout already provides Sidebar/TopBar) */}
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className="p-8 max-w-[1800px] mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#2E9BFF] to-[#00D9FF] rounded-2xl blur-lg opacity-50 animate-pulse" />
                <div className="relative p-3 bg-gradient-to-br from-[#2E9BFF] to-[#00D9FF] rounded-2xl">
                  <Search className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className={cn(
                  'text-3xl font-bold',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  RAG Search
                </h1>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Intelligent semantic search powered by AI
                </p>
              </div>
            </div>

            {/* Search Bar */}
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className={cn(
                  'absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5',
                  isDark ? 'text-[#64748B]' : 'text-gray-400'
                )} />
                <input
                  type="text"
                  placeholder="Search across all your logs with natural language..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={searching}
                  className={cn(
                    'w-full pl-14 pr-32 py-4 rounded-xl border transition-all text-base',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                      : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500',
                    'focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20'
                  )}
                />
                
                {/* Search Button Inside */}
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  {searching && (
                    <div className="flex items-center gap-2 text-sm text-[#2E9BFF] mr-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Searching...</span>
                    </div>
                  )}
                  <GradientButton
                    onClick={handleSearch}
                    disabled={!query.trim() || searching}
                    className="px-6 py-2.5"
                  >
                    <Search className="w-4 h-4 mr-2" />
                    Search
                  </GradientButton>
                </div>
              </div>

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={cn(
                  'px-6 py-4 rounded-xl border transition-all flex items-center gap-3',
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#94A3B8] hover:border-[#2E9BFF]/50'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'
                )}
              >
                <SlidersHorizontal className="w-5 h-5" />
                <span className="text-sm font-medium">Filters</span>
                <ChevronDown className={cn(
                  'w-4 h-4 transition-transform',
                  showFilters ? 'rotate-180' : ''
                )} />
              </button>
            </div>

            {/* Filters Panel */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className={cn(
                    'mt-4 p-6 rounded-xl border',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                      : 'bg-white border-gray-200'
                  )}
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Date Range Filter */}
                    <div>
                      <label className={cn(
                        'block text-sm font-medium mb-2',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        Date Range
                      </label>
                      <select
                        value={filters.dateRange}
                        onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                        className={cn(
                          'w-full px-4 py-2.5 rounded-lg border transition-all',
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                            : 'bg-white border-gray-200 text-gray-900',
                          'focus:outline-none focus:border-[#2E9BFF]'
                        )}
                      >
                        <option value="all">All Time</option>
                        <option value="1h">Last Hour</option>
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                      </select>
                    </div>

                    {/* Log Level Filter */}
                    <div>
                      <label className={cn(
                        'block text-sm font-medium mb-2',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        Log Level
                      </label>
                      <select
                        value={filters.logLevel}
                        onChange={(e) => setFilters({...filters, logLevel: e.target.value})}
                        className={cn(
                          'w-full px-4 py-2.5 rounded-lg border transition-all',
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                            : 'bg-white border-gray-200 text-gray-900',
                          'focus:outline-none focus:border-[#2E9BFF]'
                        )}
                      >
                        <option value="all">All Levels</option>
                        <option value="error">ERROR</option>
                        <option value="warn">WARN</option>
                        <option value="info">INFO</option>
                        <option value="debug">DEBUG</option>
                      </select>
                    </div>

                    {/* Source Filter */}
                    <div>
                      <label className={cn(
                        'block text-sm font-medium mb-2',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        Source
                      </label>
                      <select
                        value={filters.source}
                        onChange={(e) => setFilters({...filters, source: e.target.value})}
                        className={cn(
                          'w-full px-4 py-2.5 rounded-lg border transition-all',
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                            : 'bg-white border-gray-200 text-gray-900',
                          'focus:outline-none focus:border-[#2E9BFF]'
                        )}
                      >
                        <option value="all">All Sources</option>
                        <option value="api">API Logs</option>
                        <option value="database">Database Logs</option>
                        <option value="application">Application Logs</option>
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Search History / Suggested Searches */}
          {results.length === 0 && !searching && !searchPerformed && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="mb-8"
            >
              {searchHistory.length > 0 && (
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className={cn(
                      'w-5 h-5',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                    <h3 className={cn(
                      'text-base font-semibold',
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    )}>
                      Recent Searches
                    </h3>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    {searchHistory.map((query, index) => (
                      <button
                        key={index}
                        onClick={() => {
                          setQuery(query);
                          handleSearch();
                        }}
                        className={cn(
                          'px-4 py-2 rounded-lg text-sm transition-all',
                          isDark
                            ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 text-[#94A3B8] hover:border-[#2E9BFF]/50'
                            : 'bg-white border border-gray-200 text-gray-600 hover:border-blue-300'
                        )}
                      >
                        {query}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className={cn(
                    'w-5 h-5',
                    isDark ? 'text-[#64748B]' : 'text-gray-400'
                  )} />
                  <h3 className={cn(
                    'text-base font-semibold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Try Searching For
                  </h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {exampleQueries.map((suggestion, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
                      onClick={() => {
                        setQuery(suggestion);
                        handleSearch();
                      }}
                      className={cn(
                        'p-4 rounded-xl border transition-all text-left group',
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50'
                          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md'
                      )}
                    >
                      <TrendingUp className={cn(
                        'w-5 h-5 mb-2',
                        isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                      )} />
                      <p className={cn(
                        'text-sm font-medium group-hover:text-[#2E9BFF] transition-colors',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {suggestion}
                      </p>
                    </motion.button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Results */}
          {searching ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader2 className="w-12 h-12 text-[#2E9BFF] animate-spin mx-auto mb-4" />
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Searching through your logs...
                </p>
              </div>
            </div>
          ) : searchPerformed && results.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {/* Results Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Zap className={cn(
                    'w-5 h-5',
                    isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                  )} />
                  <h2 className={cn(
                    'text-xl font-bold',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    Found {results.length} Results
                  </h2>
                </div>
                <p className={cn(
                  'text-sm',
                  isDark ? 'text-[#64748B]' : 'text-gray-500'
                )}>
                  Sorted by relevance
                </p>
              </div>

              {/* Results List */}
              <div className="space-y-4">
                {results.map((result, index) => {
                  const isExpanded = expandedResults.has(result.id || String(index));
                  const displayContent = isExpanded 
                    ? result.content 
                    : result.content.slice(0, 300) + (result.content.length > 300 ? '...' : '');

                  return (
                    <motion.div
                      key={result.id || index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                      className={cn(
                        'p-6 rounded-xl border transition-all',
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50'
                          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md'
                      )}
                    >
                      {/* Result Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start gap-3 flex-1">
                          <div className={cn(
                            'p-2 rounded-lg mt-1',
                            result.score > 0.8
                              ? 'bg-[#10B981]/20 text-[#10B981]'
                              : result.score > 0.6
                              ? 'bg-[#2E9BFF]/20 text-[#2E9BFF]'
                              : 'bg-[#F59E0B]/20 text-[#F59E0B]'
                          )}>
                            <FileText className="w-5 h-5" />
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className={cn(
                                'text-xs font-semibold px-3 py-1 rounded-full',
                                result.score > 0.8
                                  ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50'
                                  : result.score > 0.6
                                  ? 'bg-[#2E9BFF]/20 text-[#2E9BFF] border border-[#2E9BFF]/50'
                                  : 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/50'
                              )}>
                                {(result.score * 100).toFixed(0)}% Match
                              </span>

                              <span className={cn(
                                'text-sm',
                                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                              )}>
                                {result.source || 'Log Entry'}
                              </span>
                            </div>

                            {/* Metadata */}
                            <div className="flex flex-wrap items-center gap-4 mb-3">
                              {result.metadata?.project_name && (
                                <div className="flex items-center gap-2 text-sm">
                                  <FolderOpen className={cn(
                                    'w-4 h-4',
                                    isDark ? 'text-[#64748B]' : 'text-gray-400'
                                  )} />
                                  <span className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                                    {result.metadata.project_name}
                                  </span>
                                </div>
                              )}

                              {result.timestamp && (
                                <div className="flex items-center gap-2 text-sm">
                                  <Calendar className={cn(
                                    'w-4 h-4',
                                    isDark ? 'text-[#64748B]' : 'text-gray-400'
                                  )} />
                                  <span className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                                    {new Date(result.timestamp).toLocaleString()}
                                  </span>
                                </div>
                              )}

                              {result.metadata?.line_number && (
                                <div className="flex items-center gap-2 text-sm">
                                  <Hash className={cn(
                                    'w-4 h-4',
                                    isDark ? 'text-[#64748B]' : 'text-gray-400'
                                  )} />
                                  <span className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                                    Line {result.metadata.line_number}
                                  </span>
                                </div>
                              )}
                            </div>

                            {/* Content */}
                            <pre className={cn(
                              'text-sm font-mono leading-relaxed whitespace-pre-wrap',
                              isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                            )}>
                              {displayContent}
                            </pre>

                            {/* Expand/Collapse */}
                            {result.content.length > 300 && (
                              <button
                                onClick={() => toggleResultExpanded(result.id || String(index))}
                                className={cn(
                                  'mt-3 text-sm font-medium flex items-center gap-2',
                                  isDark
                                    ? 'text-[#2E9BFF] hover:text-[#00D9FF]'
                                    : 'text-blue-600 hover:text-blue-700',
                                  'transition-colors'
                                )}
                              >
                                {isExpanded ? (
                                  <>
                                    Show less
                                    <ChevronUp className="w-4 h-4" />
                                  </>
                                ) : (
                                  <>
                                    Show more
                                    <ChevronDown className="w-4 h-4" />
                                  </>
                                )}
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleCopyResult(result.content)}
                            className={cn(
                              'p-2 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="Copy"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                          <button
                            className={cn(
                              'p-2 rounded-lg transition-all',
                              isDark
                                ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                : 'hover:bg-gray-100 text-gray-600'
                            )}
                            title="View Source"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Additional Metadata Tags */}
                      {result.metadata && Object.keys(result.metadata).length > 0 && (
                        <div className="mt-4 flex flex-wrap gap-2 pt-4 border-t border-[#2E3A5C]/30">
                          {Object.entries(result.metadata)
                            .filter(([key]) => !['filename', 'project_name', 'line_number', 'timestamp'].includes(key))
                            .map(([key, value]) => (
                            <span key={key} className={cn(
                              'px-2 py-1 rounded text-xs',
                              isDark
                                ? 'bg-[#0D1117]/60 border border-[#2E3A5C]/50 text-[#94A3B8]'
                                : 'bg-gray-100 border border-gray-200 text-gray-600'
                            )}>
                              <span className={isDark ? 'text-[#64748B]' : 'text-gray-500'}>{key}:</span>{' '}
                              <span>{String(value)}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ) : searchPerformed && results.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                'text-center py-20 rounded-2xl border',
                isDark
                  ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200'
              )}
            >
              <Search className={cn(
                'w-16 h-16 mx-auto mb-4',
                isDark ? 'text-[#64748B]' : 'text-gray-400'
              )} />
              <h3 className={cn(
                'text-xl font-bold mb-2',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                No results found
              </h3>
              <p className={cn(
                'text-base',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Try adjusting your search query or filters
              </p>
            </motion.div>
          ) : null}
        </div>
      </motion.main>
    </div>
  );
}
