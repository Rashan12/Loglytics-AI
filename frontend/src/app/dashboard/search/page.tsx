'use client';

import { useState, useEffect } from 'react';
import { Search, FileText, Calendar, Sparkles, Filter, ArrowRight, TrendingUp, Zap } from 'lucide-react';
import { API_ENDPOINTS } from '@/config/api';

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
  const [stats, setStats] = useState({
    indexedChunks: 0,
    estimatedFiles: 0,
    status: 'no_data'
  });
  const [reindexing, setReindexing] = useState(false);

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(API_ENDPOINTS.ragStats, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
        console.log('📊 RAG Stats:', data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleReindex = async () => {
    if (!confirm('This will re-index all your log files for RAG search. This may take a few minutes. Continue?')) {
      return;
    }
    
    setReindexing(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/rag/reindex-all', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ Re-indexing completed!\n\nIndexed: ${data.indexed} files\nTotal: ${data.total_files} files`);
        loadStats(); // Refresh stats
      } else {
        const error = await response.text();
        alert('Failed to re-index files. Check console for details.');
        console.error('Re-index error:', error);
      }
    } catch (error) {
      console.error('Re-index error:', error);
      alert('Failed to re-index files.');
    } finally {
      setReindexing(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setSearching(true);
    setSearchPerformed(true);
    
    try {
      const token = localStorage.getItem('access_token');
      
      console.log('🔍 Searching:', query);
      console.log('📡 Using endpoint:', API_ENDPOINTS.ragSearch);
      
      const response = await fetch(API_ENDPOINTS.ragSearch, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          query,
          project_id: 'default', // Use default project for now
          limit: 20,
          similarity_threshold: 0.7,
          filters
        })
      });
      
      console.log('📥 Search response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Search results:', data);
        setResults(data.results || []);
      } else {
        const errorText = await response.text();
        console.error('❌ Search error:', errorText);
        setResults([]);
        alert('Search failed. Please check if you have uploaded any log files.');
      }
    } catch (error) {
      console.error('❌ Search error:', error);
      setResults([]);
      alert('Search failed. Check console for details.');
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
    <div className="min-h-screen bg-gradient-to-br from-[#0A0E14] via-[#0D1117] to-[#0A0E14] p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-xl opacity-50 animate-pulse"></div>
              <div className="relative p-3 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl shadow-lg">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                RAG Search
              </h1>
              <p className="text-gray-400 mt-1">AI-powered semantic search through your logs</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 max-w-3xl">
            Uses advanced retrieval-augmented generation to find relevant log entries based on meaning, not just keywords
          </p>
          
          {/* RAG Stats Display */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${stats.status === 'ready' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                <span className="text-gray-400">
                  {stats.status === 'ready' ? 'Ready' : 'No data'} 
                  {stats.indexedChunks > 0 && ` • ${stats.indexedChunks} chunks indexed`}
                  {stats.estimatedFiles > 0 && ` • ~${stats.estimatedFiles} files`}
                </span>
              </div>
              {stats.status === 'no_data' && (
                <span className="text-yellow-400 text-xs">
                  Upload log files to enable search
                </span>
              )}
            </div>
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all text-sm flex items-center gap-2"
            >
              {reindexing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Re-indexing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Re-index All Files
                </>
              )}
            </button>
          </div>
        </div>

        <div className="relative mb-6">
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl blur-lg"></div>
              <div className="relative flex items-center">
                <Search className="absolute left-5 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Describe what you're looking for... (e.g., 'authentication errors from yesterday')"
                  className="w-full pl-14 pr-6 py-5 bg-[#161B22] border-2 border-[#30363D] focus:border-purple-600 rounded-2xl text-white placeholder-gray-500 focus:outline-none transition-all text-base shadow-xl"
                  disabled={searching}
                />
              </div>
            </div>
            <button
              onClick={handleSearch}
              disabled={!query.trim() || searching}
              className="relative group px-8 py-5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-2xl text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-2xl shadow-purple-600/30 hover:shadow-purple-600/50"
            >
              {searching ? (
                <span className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Searching...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Search
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="mb-8 p-6 bg-gradient-to-br from-[#161B22] to-[#1C2128] border border-[#30363D] rounded-2xl shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-purple-400" />
            <span className="text-base font-semibold text-white">Advanced Filters</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-2">Date Range</label>
              <select
                value={filters.dateRange}
                onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                className="w-full px-4 py-3 bg-[#0D1117] border-2 border-[#30363D] focus:border-purple-600 rounded-xl text-white text-sm focus:outline-none transition-all"
              >
                <option value="all">All Time</option>
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-2">Log Level</label>
              <select
                value={filters.logLevel}
                onChange={(e) => setFilters({...filters, logLevel: e.target.value})}
                className="w-full px-4 py-3 bg-[#0D1117] border-2 border-[#30363D] focus:border-purple-600 rounded-xl text-white text-sm focus:outline-none transition-all"
              >
                <option value="all">All Levels</option>
                <option value="error">ERROR</option>
                <option value="warn">WARN</option>
                <option value="info">INFO</option>
                <option value="debug">DEBUG</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-2">Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({...filters, source: e.target.value})}
                className="w-full px-4 py-3 bg-[#0D1117] border-2 border-[#30363D] focus:border-purple-600 rounded-xl text-white text-sm focus:outline-none transition-all"
              >
                <option value="all">All Sources</option>
                <option value="api">API Logs</option>
                <option value="database">Database Logs</option>
                <option value="application">Application Logs</option>
              </select>
            </div>
          </div>
        </div>

        {searching ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full blur-2xl opacity-30 animate-pulse"></div>
              <div className="relative w-24 h-24 border-4 border-purple-600/20 rounded-full">
                <div className="absolute inset-0 w-24 h-24 border-4 border-t-purple-600 border-r-pink-600 border-b-transparent border-l-transparent rounded-full animate-spin"></div>
              </div>
            </div>
            <p className="text-white text-xl font-semibold mb-2">Searching through your logs...</p>
            <p className="text-gray-400 text-sm">Using AI to find the most relevant results</p>
          </div>
        ) : searchPerformed && results.length > 0 ? (
          <div>
            <div className="flex items-center justify-between mb-6 p-4 bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-600/30 rounded-2xl">
              <p className="text-sm text-gray-300">
                Found <span className="text-white font-bold text-lg">{results.length}</span> results for 
                <span className="text-purple-400 font-semibold ml-1">"{query}"</span>
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <span>Ranked by semantic similarity</span>
              </div>
            </div>
            
            <div className="space-y-4">
              {results.map((result, index) => (
                <div
                  key={result.id || index}
                  className="group bg-gradient-to-br from-[#161B22] to-[#1C2128] border border-[#30363D] hover:border-purple-600/50 rounded-2xl p-6 transition-all hover:shadow-2xl hover:shadow-purple-600/20 hover:-translate-y-1"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-xl font-mono text-sm font-bold text-purple-400">
                        #{index + 1}
                      </div>
                      <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-400" />
                        <span className="text-sm font-medium text-gray-300">{result.source || 'Log Entry'}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {result.timestamp && (
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(result.timestamp).toLocaleString()}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-3 px-3 py-1.5 bg-gradient-to-r from-purple-600/10 to-pink-600/10 border border-purple-500/30 rounded-xl">
                        <span className="text-xs font-medium text-gray-400">Relevance</span>
                        <div className="w-24 bg-[#0F1419] rounded-full h-2 overflow-hidden">
                          <div 
                            className="h-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full transition-all shadow-lg shadow-purple-600/50"
                            style={{ width: `${(result.score || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                          {((result.score || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-white font-mono text-sm leading-relaxed bg-[#0D1117] p-5 rounded-xl border border-[#30363D] group-hover:border-purple-600/30 transition-all">
                    {result.content}
                  </p>
                  
                  {result.metadata && Object.keys(result.metadata).length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {Object.entries(result.metadata).map(([key, value]) => (
                        <span key={key} className="px-3 py-1.5 bg-[#0D1117] border border-[#30363D] rounded-lg text-xs">
                          <span className="text-gray-500 font-medium">{key}:</span>{' '}
                          <span className="text-gray-300">{String(value)}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : searchPerformed && results.length === 0 ? (
          <div className="text-center py-20">
            <div className="relative inline-block mb-6">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur-2xl opacity-20"></div>
              <div className="relative w-24 h-24 bg-gradient-to-br from-[#161B22] to-[#1C2128] border-2 border-[#30363D] rounded-3xl flex items-center justify-center">
                <Search className="w-12 h-12 text-gray-600" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-white mb-3">No results found</h3>
            <p className="text-gray-400 mb-2">
              We couldn't find any logs matching <span className="text-purple-400 font-semibold">"{query}"</span>
            </p>
            <div className="inline-block mt-6 p-6 bg-[#161B22] border border-[#30363D] rounded-2xl text-left">
              <p className="text-sm font-semibold text-white mb-3">💡 Try these tips:</p>
              <ul className="text-sm text-gray-400 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">•</span>
                  <span>Use different or more general keywords</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">•</span>
                  <span>Check your filters (date range, log level, source)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">•</span>
                  <span>Upload more log files for better results</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-400 mt-0.5">•</span>
                  <span>Try describing the issue instead of technical terms</span>
                </li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="relative inline-block mb-8">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur-3xl opacity-30 animate-pulse"></div>
              <div className="relative w-28 h-28 bg-gradient-to-br from-purple-600/20 to-pink-600/20 border-2 border-purple-600/30 rounded-3xl flex items-center justify-center">
                <Sparkles className="w-14 h-14 text-purple-500" />
              </div>
            </div>
            <h3 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
              Semantic Log Search
            </h3>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto text-lg leading-relaxed">
              Search your logs using natural language. Our AI understands the meaning behind your query 
              and finds the most relevant log entries, even if they don't contain your exact words.
            </p>
            
            <div className="mb-12">
              <p className="text-sm font-semibold text-gray-400 mb-4">✨ Try these example searches:</p>
              <div className="flex flex-wrap justify-center gap-3">
                {exampleQueries.map((example) => (
                  <button
                    key={example}
                    onClick={() => { setQuery(example); handleSearch(); }}
                    className="group px-5 py-3 bg-gradient-to-r from-[#161B22] to-[#1C2128] hover:from-purple-600/20 hover:to-pink-600/20 border border-[#30363D] hover:border-purple-600/50 rounded-xl text-sm text-gray-400 hover:text-white transition-all flex items-center gap-2 shadow-lg hover:shadow-purple-600/20"
                  >
                    <span>{example}</span>
                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <div className="p-6 bg-gradient-to-br from-[#161B22] to-[#1C2128] border border-[#30363D] hover:border-blue-600/50 rounded-2xl transition-all hover:shadow-xl hover:shadow-blue-600/20 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-600/20 to-blue-400/20 border border-blue-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-7 h-7 text-blue-400" />
                </div>
                <h4 className="text-base font-bold text-white mb-2">Semantic Understanding</h4>
                <p className="text-sm text-gray-400">Finds logs by meaning, not just keywords</p>
              </div>
              
              <div className="p-6 bg-gradient-to-br from-[#161B22] to-[#1C2128] border border-[#30363D] hover:border-purple-600/50 rounded-2xl transition-all hover:shadow-xl hover:shadow-purple-600/20 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-purple-600/20 to-purple-400/20 border border-purple-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-7 h-7 text-purple-400" />
                </div>
                <h4 className="text-base font-bold text-white mb-2">Intelligent Ranking</h4>
                <p className="text-sm text-gray-400">Results sorted by relevance score</p>
              </div>
              
              <div className="p-6 bg-gradient-to-br from-[#161B22] to-[#1C2128] border border-[#30363D] hover:border-pink-600/50 rounded-2xl transition-all hover:shadow-xl hover:shadow-pink-600/20 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-pink-600/20 to-pink-400/20 border border-pink-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Filter className="w-7 h-7 text-pink-400" />
                </div>
                <h4 className="text-base font-bold text-white mb-2">Advanced Filters</h4>
                <p className="text-sm text-gray-400">Narrow down by date, level, and source</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}