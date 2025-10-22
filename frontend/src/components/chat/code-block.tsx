"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Copy, Check } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface CodeBlockProps {
  content: string
  language?: string
}

export function CodeBlock({ content, language }: CodeBlockProps) {
  const [copied, setCopied] = React.useState(false)
  const [showCopyButton, setShowCopyButton] = React.useState(false)

  const handleCopy = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy code:", err)
    }
  }

  // Custom components for ReactMarkdown
  const components = {
    // Code blocks
    code({ node, inline, className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '')
      const language = match ? match[1] : ''
      
      if (!inline && language) {
        return (
          <div
            className="relative group my-4"
            onMouseEnter={() => setShowCopyButton(true)}
            onMouseLeave={() => setShowCopyButton(false)}
          >
            <div className="bg-muted rounded-lg overflow-hidden">
              {/* Language header */}
              <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b border-border">
                <span className="text-xs font-medium text-muted-foreground">
                  {language}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => handleCopy(String(children).replace(/\n$/, ''))}
                >
                  {copied ? (
                    <Check className="h-3 w-3 text-emerald-500" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </div>
              
              {/* Code content */}
              <pre className="p-4 overflow-x-auto">
                <code className={cn("text-sm", className)} {...props}>
                  {children}
                </code>
              </pre>
            </div>
          </div>
        )
      }
      
      // Inline code
      return (
        <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
          {children}
        </code>
      )
    },
    
    // Headings
    h1: ({ children }: any) => (
      <h1 className="text-2xl font-bold mt-6 mb-4 first:mt-0">{children}</h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-xl font-semibold mt-5 mb-3 first:mt-0">{children}</h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-lg font-medium mt-4 mb-2 first:mt-0">{children}</h3>
    ),
    h4: ({ children }: any) => (
      <h4 className="text-base font-medium mt-3 mb-2 first:mt-0">{children}</h4>
    ),
    
    // Paragraphs
    p: ({ children }: any) => (
      <p className="mb-4 last:mb-0 leading-relaxed">{children}</p>
    ),
    
    // Lists
    ul: ({ children }: any) => (
      <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>
    ),
    ol: ({ children }: any) => (
      <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>
    ),
    li: ({ children }: any) => (
      <li className="leading-relaxed">{children}</li>
    ),
    
    // Links
    a: ({ href, children }: any) => (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-primary hover:underline"
      >
        {children}
      </a>
    ),
    
    // Tables
    table: ({ children }: any) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full border border-border rounded-lg">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }: any) => (
      <thead className="bg-muted">{children}</thead>
    ),
    tbody: ({ children }: any) => (
      <tbody className="divide-y divide-border">{children}</tbody>
    ),
    tr: ({ children }: any) => (
      <tr className="hover:bg-muted/50">{children}</tr>
    ),
    th: ({ children }: any) => (
      <th className="px-4 py-2 text-left text-sm font-medium border-b border-border">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="px-4 py-2 text-sm border-b border-border">
        {children}
      </td>
    ),
    
    // Blockquotes
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-primary pl-4 py-2 my-4 bg-muted/30 rounded-r-lg">
        {children}
      </blockquote>
    ),
    
    // Horizontal rule
    hr: () => (
      <hr className="my-6 border-border" />
    ),
    
    // Strong and emphasis
    strong: ({ children }: any) => (
      <strong className="font-semibold">{children}</strong>
    ),
    em: ({ children }: any) => (
      <em className="italic">{children}</em>
    ),
  }

  return (
    <div className="prose prose-sm max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
