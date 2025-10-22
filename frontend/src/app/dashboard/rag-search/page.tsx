'use client';

import { useState } from 'react';
import { Search, FileText, Calendar, Sparkles, Filter, ArrowRight } from 'lucide-react';

interface SearchResult {
  id: string;
  content: string;
  source: string;
  timestamp: string;
  score: number;
  metadata?: any;
}

export default function RAGSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: 'all',
    logLevel: 'all',
    source: 'all'
  });

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setSearching(true);
    setSearchPerformed(true);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/rag/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          query,
          limit: 20,
          filters
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setResults(data.results || []);
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const exampleQueries = [
    "database connection errors",
    "authentication failures",
    "high response time",
    "memory leaks",
    "API timeout issues"
  ];

  return (
    <div className="min-h-screen bg-[#0A0E14] p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white">RAG Search</h1>
          </div>
          <p className="text-gray-400">AI-powered semantic search through your logs</p>
          <p className="text-sm text-gray-500 mt-1">
            Uses advanced retrieval-augmented generation to find relevant log entries based on meaning, not just keywords
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative mb-6">
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe what you're looking for..."
                className="w-full pl-12 pr-4 py-4 bg-[#161B22] border border-[#30363D] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-600 transition-all text-base"
                disabled={searching}
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={!query.trim() || searching}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-purple-600/20"
            >
              {searching ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Searching...
                </span>
              ) : (
                'Search'
              )}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-8 p-4 bg-[#161B22] border border-[#30363D] rounded-xl">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-semibold text-gray-300">Filters</span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Date Range</label>
              <select
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                className="w-full px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white text-sm focus:outline-none focus:border-purple-600"
              >
                <option value="all">All Time</option>
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-400 mb-1">Log Level</label>
              <select
                value={filters.logLevel}
                onChange={(e) => setFilters({...filters, logLevel: e.target.value})}
                className="w-full px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white text-sm focus:outline-none focus:border-purple-600"
              >
                <option value="all">All Levels</option>
                <option value="error">ERROR</option>
                <option value="warn">WARN</option>
                <option value="info">INFO</option>
                <option value="debug">DEBUG</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-400 mb-1">Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({...filters, source: e.target.value})}
                className="w-full px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white text-sm focus:outline-none focus:border-purple-600"
              >
                <option value="all">All Sources</option>
                <option value="api">API Logs</option>
                <option value="database">Database Logs</option>
                <option value="application">Application Logs</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {searching ? (
          /* Loading State */
          <div className="flex flex-col items-center justify-center py-20">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-purple-600/20 rounded-full" />
              <div className="absolute inset-0 w-20 h-20 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-gray-400 mt-6 text-lg">Searching through your logs...</p>
            <p className="text-gray-500 text-sm mt-2">Using AI to find the most relevant results</p>
          </div>
        ) : searchPerformed && results.length > 0 ? (
          /* Results List */
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-400">
                Found <span className="text-white font-semibold">{results.length}</span> results for "<span className="text-purple-400">{query}</span>"
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Sparkles className="w-3 h-3" />
                <span>Ranked by semantic similarity</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={result.id || index}
                  className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-purple-600/50 transition-all group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-purple-500/10 border border-purple-500/30 rounded-lg font-mono text-sm text-purple-400">
                        #{index + 1}
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-blue-500" />
                        <span className="text-sm text-gray-400">{result.source || 'Log Entry'}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {result.timestamp && (
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(result.timestamp).toLocaleString()}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">Relevance:</span>
                        <div className="w-24 bg-[#0F1419] rounded-full h-2">
                          <div 
                            className="h-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full transition-all"
                            style={{ width: `${(result.score || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-purple-400 font-semibold">{((result.score || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-white font-mono text-sm leading-relaxed bg-[#0F1419] p-4 rounded-lg border border-[#30363D]">
                    {result.content || result.text}
                  </p>
                  
                  {result.metadata && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {Object.entries(result.metadata).map(([key, value]) => (
                        <span key={key} className="px-2 py-1 bg-[#0F1419] border border-[#30363D] rounded text-xs text-gray-400">
                          <span className="text-gray-500">{key}:</span> <span className="text-gray-300">{String(value)}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : searchPerformed && results.length === 0 ? (
          /* No Results */
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-gray-700/20 border border-gray-700/40 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-10 h-10 text-gray-600" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">No results found</h3>
            <p className="text-gray-400 mb-6">
              We couldn't find any logs matching "<span className="text-purple-400">{query}</span>"
            </p>
            <p className="text-sm text-gray-500 mb-4">Try:</p>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Using different keywords</li>
              <li>• Being more specific or more general</li>
              <li>• Checking your filters</li>
              <li>• Uploading more log files</li>
            </ul>
          </div>
        ) : (
          /* Initial State */
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-600/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-12 h-12 text-purple-500" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">Semantic Log Search</h3>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Search your logs using natural language. Our AI understands the meaning behind your query 
              and finds the most relevant log entries, even if they don't contain your exact words.
            </p>
            
            <div className="mb-8">
              <p className="text-sm text-gray-500 mb-3">Try these example searches:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {exampleQueries.map((example) => (
                  <button
                    key={example}
                    onClick={() => { setQuery(example); handleSearch(); }}
                    className="group px-4 py-2 bg-[#161B22] border border-[#30363D] rounded-lg text-sm text-gray-400 hover:text-white hover:border-purple-600/50 transition-all flex items-center gap-2"
                  >
                    <span>{example}</span>
                    <ArrowRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
            
            {/* Features */}
            <div className="grid grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
              <div className="p-6 bg-[#161B22] border border-[#30363D] rounded-xl">
                <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-6 h-6 text-blue-500" />
                </div>
                <h4 className="text-sm font-semibold text-white mb-2">Semantic Understanding</h4>
                <p className="text-xs text-gray-400">Finds logs by meaning, not just keywords</p>
              </div>
              
              <div className="p-6 bg-[#161B22] border border-[#30363D] rounded-xl">
                <div className="w-12 h-12 bg-purple-500/10 border border-purple-500/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Search className="w-6 h-6 text-purple-500" />
                </div>
                <h4 className="text-sm font-semibold text-white mb-2">Intelligent Ranking</h4>
                <p className="text-xs text-gray-400">Results sorted by relevance score</p>
              </div>
              
              <div className="p-6 bg-[#161B22] border border-[#30363D] rounded-xl">
                <div className="w-12 h-12 bg-pink-500/10 border border-pink-500/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Filter className="w-6 h-6 text-pink-500" />
                </div>
                <h4 className="text-sm font-semibold text-white mb-2">Advanced Filters</h4>
                <p className="text-xs text-gray-400">Narrow down by date, level, and source</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
