"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  Bot,
  Sparkles,
  MessageSquare,
  FileText,
  Search,
  Zap,
  ArrowRight,
  Upload,
  Database,
  BarChart3,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface EmptyChatProps {
  onSendMessage: (content: string, files?: File[]) => void
}

const quickStartPrompts = [
  {
    title: "Analyze Error Patterns",
    description: "Find common error patterns in your logs",
    prompt: "What are the most common error patterns in my logs?",
    icon: Search,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    title: "Performance Issues",
    description: "Identify performance bottlenecks",
    prompt: "Show me performance issues and slow queries in my logs",
    icon: BarChart3,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
  },
  {
    title: "Security Analysis",
    description: "Check for security-related events",
    prompt: "Are there any security concerns or suspicious activities in my logs?",
    icon: Zap,
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
  },
  {
    title: "System Health",
    description: "Get overall system health insights",
    prompt: "What's the overall health and status of my system based on the logs?",
    icon: Database,
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
  },
]

const features = [
  {
    title: "Upload Log Files",
    description: "Drag and drop your log files to get started",
    icon: Upload,
  },
  {
    title: "Ask Questions",
    description: "Ask natural language questions about your logs",
    icon: MessageSquare,
  },
  {
    title: "Get Insights",
    description: "Receive AI-powered insights and recommendations",
    icon: Sparkles,
  },
]

export function EmptyChat({ onSendMessage }: EmptyChatProps) {
  const handleQuickPrompt = (prompt: string) => {
    onSendMessage(prompt)
  }

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6 max-w-4xl"
      >
        {/* Header */}
        <div className="space-y-4">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto">
            <Bot className="h-10 w-10 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Start a New Conversation</h2>
            <p className="text-muted-foreground mt-2">
              Ask questions about your logs, upload files, or get AI-powered insights
            </p>
          </div>
        </div>

        {/* Quick Start Prompts */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Quick Start</h3>
          <div className="grid gap-4 md:grid-cols-2">
            {quickStartPrompts.map((item, index) => {
              const Icon = item.icon
              return (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card 
                    className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                    onClick={() => handleQuickPrompt(item.prompt)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start space-x-3">
                        <div className={cn("p-2 rounded-lg", item.bgColor)}>
                          <Icon className={cn("h-5 w-5", item.color)} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium">{item.title}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {item.description}
                          </p>
                          <div className="flex items-center space-x-2 mt-2">
                            <span className="text-xs text-muted-foreground">
                              Click to try
                            </span>
                            <ArrowRight className="h-3 w-3 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Features */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">What You Can Do</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                >
                  <div className="text-center space-y-2">
                    <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center mx-auto">
                      <Icon className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <h4 className="font-medium">{feature.title}</h4>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.8 }}
          className="bg-muted/50 rounded-lg p-4 max-w-2xl"
        >
          <h4 className="font-medium mb-2">💡 Tips for Better Results</h4>
          <ul className="text-sm text-muted-foreground space-y-1 text-left">
            <li>• Upload your log files first for more accurate analysis</li>
            <li>• Be specific in your questions (e.g., "Show me errors from yesterday")</li>
            <li>• Use natural language - no need for complex queries</li>
            <li>• Ask follow-up questions to dive deeper into insights</li>
          </ul>
        </motion.div>
      </motion.div>
    </div>
  )
}
