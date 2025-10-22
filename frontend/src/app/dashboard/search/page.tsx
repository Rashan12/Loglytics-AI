"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  Search,
  Filter,
  Clock,
  FileText,
  AlertTriangle,
  Info,
  XCircle,
  Sparkles,
  Loader2,
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"

interface SearchResult {
  id: string
  message: string
  timestamp: string
  level: "INFO" | "WARN" | "ERROR" | "DEBUG"
  source: string
  relevance: number
  context: string
}

const mockResults: SearchResult[] = [
  {
    id: "1",
    message: "Database connection timeout after 30 seconds",
    timestamp: new Date().toISOString(),
    level: "ERROR",
    source: "db.connection",
    relevance: 95,
    context: "Connection pool exhausted, retrying...",
  },
  {
    id: "2",
    message: "High memory usage detected (85%)",
    timestamp: new Date().toISOString(),
    level: "WARN",
    source: "system.monitor",
    relevance: 87,
    context: "Memory threshold exceeded, consider scaling",
  },
  {
    id: "3",
    message: "API request completed successfully",
    timestamp: new Date().toISOString(),
    level: "INFO",
    source: "api.gateway",
    relevance: 72,
    context: "Response time: 245ms",
  },
]

const suggestedSearches = [
  "timeout errors",
  "memory leaks",
  "failed requests",
  "performance issues",
]

export default function RAGSearchPage() {
  const [query, setQuery] = React.useState("")
  const [results, setResults] = React.useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = React.useState(false)
  const [hasSearched, setHasSearched] = React.useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return

    setIsSearching(true)
    setHasSearched(true)

    // Simulate search
    setTimeout(() => {
      setResults(mockResults)
      setIsSearching(false)
    }, 1000)
  }

  const useSuggestion = (suggestion: string) => {
    setQuery(suggestion)
  }

  const getLevelIcon = (level: SearchResult["level"]) => {
    switch (level) {
      case "INFO":
        return <Info className="h-4 w-4 text-blue-500" />
      case "WARN":
        return <AlertTriangle className="h-4 w-4 text-amber-500" />
      case "ERROR":
        return <XCircle className="h-4 w-4 text-red-500" />
      case "DEBUG":
        return <FileText className="h-4 w-4 text-purple-500" />
    }
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold tracking-tight"
          >
            RAG Search
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-muted-foreground"
          >
            AI-powered semantic search through your logs
          </motion.p>
        </div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Badge variant="success" className="flex items-center space-x-1">
            <Sparkles className="h-3 w-3" />
            <span>RAG Enabled</span>
          </Badge>
        </motion.div>
      </div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardContent className="pt-6">
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search using natural language (e.g., 'show me database errors from yesterday')..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSearch()
                    }
                  }}
                  className="pl-10"
                />
              </div>
              <Button onClick={handleSearch} disabled={!query.trim() || isSearching}>
                {isSearching ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Search className="h-4 w-4 mr-2" />
                    Search
                  </>
                )}
              </Button>
            </div>
            {!hasSearched && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground mb-2">Try searching for:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedSearches.map((suggestion, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="cursor-pointer hover:bg-accent"
                      onClick={() => useSuggestion(suggestion)}
                    >
                      {suggestion}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Search Results */}
      {hasSearched && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Search Results</CardTitle>
                  <CardDescription>
                    {results.length} results found for "{query}"
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {isSearching ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">Searching through your logs...</p>
                </div>
              ) : results.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Search className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    No results found. Try a different search query.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {results.map((result, index) => (
                    <motion.div
                      key={result.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="p-4 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getLevelIcon(result.level)}
                          <Badge variant="outline" size="sm">
                            {result.level}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {result.source}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="success" size="sm">
                            {result.relevance}% match
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            <Clock className="h-3 w-3 inline mr-1" />
                            {new Date(result.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm font-medium mb-1">{result.message}</p>
                      <p className="text-xs text-muted-foreground">
                        Context: {result.context}
                      </p>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>How RAG Search Works</CardTitle>
            <CardDescription>
              Retrieval-Augmented Generation for intelligent log search
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-blue-500/10">
                    <Sparkles className="h-4 w-4 text-blue-500" />
                  </div>
                  <h4 className="font-medium">Semantic Understanding</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Understands the meaning behind your search query, not just keywords
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-purple-500/10">
                    <FileText className="h-4 w-4 text-purple-500" />
                  </div>
                  <h4 className="font-medium">Context Aware</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Retrieves relevant logs with full context and related information
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-emerald-500/10">
                    <Search className="h-4 w-4 text-emerald-500" />
                  </div>
                  <h4 className="font-medium">AI-Powered</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Uses advanced AI to rank and present the most relevant results
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
