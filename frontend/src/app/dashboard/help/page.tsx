'use client';

import { Book, MessageCircle, FileText, ExternalLink, Search } from 'lucide-react';
import { useState } from 'react';

const faqItems = [
  {
    question: "How do I upload log files?",
    answer: "Navigate to the Log Files page from the sidebar, click the 'Upload Log File' button, and select your log file. We support .log, .txt, JSON, CSV, and compressed formats (.gz, .zip) up to 100MB.",
  },
  {
    question: "What log formats are supported?",
    answer: "Loglytics AI supports plain text logs (.log, .txt), structured logs (JSON, CSV), and compressed archives (.gz, .zip). We automatically detect and parse common log formats including syslog, Apache, nginx, and custom application logs.",
  },
  {
    question: "How does the AI Assistant work?",
    answer: "The AI Assistant uses advanced language models to analyze your logs and answer questions in natural language. You can ask about error patterns, performance issues, or request summaries of your log data.",
  },
  {
    question: "What is RAG Search?",
    answer: "RAG (Retrieval-Augmented Generation) Search is an AI-powered semantic search that understands the meaning behind your queries. Instead of just matching keywords, it finds relevant logs based on context and meaning.",
  },
  {
    question: "How do I set up live log streaming?",
    answer: "Go to the Live Logs page and use the provided WebSocket endpoint or HTTP API to stream logs in real-time. You'll need to include your API key in the Authorization header.",
  },
  {
    question: "Can I export my data?",
    answer: "Yes! You can export log files, chat conversations, and analytics reports. Look for the export/download buttons on respective pages. You can also use our API to programmatically access your data.",
  },
  {
    question: "What's included in the Free plan?",
    answer: "The Free plan includes up to 5 projects, 10GB storage, basic analytics, local LLM support, and community support. Upgrade to Pro for unlimited projects, 100GB storage, advanced analytics, and priority support.",
  },
  {
    question: "How do I create an API key?",
    answer: "Go to Settings > API Keys and click 'Create New Key'. Give it a name and set permissions. The key will be shown only once, so make sure to copy it and store it securely.",
  },
]

const quickLinks = [
  {
    title: "Getting Started Guide",
    description: "Learn the basics of Loglytics AI",
    icon: Book,
    href: "#",
  },
  {
    title: "Video Tutorials",
    description: "Watch step-by-step video guides",
    icon: Video,
    href: "#",
  },
  {
    title: "API Documentation",
    description: "Complete API reference and examples",
    icon: FileText,
    href: "#",
  },
  {
    title: "Community Forum",
    description: "Join discussions with other users",
    icon: MessageSquare,
    href: "#",
  },
]

const supportChannels = [
  {
    title: "Email Support",
    description: "Get help via email within 24 hours",
    icon: Mail,
    action: "Contact Support",
    href: "mailto:support@loglytics.ai",
  },
  {
    title: "Live Chat",
    description: "Chat with our support team in real-time",
    icon: MessageSquare,
    action: "Start Chat",
    badge: "Pro",
  },
  {
    title: "Documentation",
    description: "Browse our comprehensive documentation",
    icon: Book,
    action: "View Docs",
    href: "#",
  },
]

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = React.useState("")

  const filteredFaqs = faqItems.filter(
    (item) =>
      item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="flex-1 space-y-6 p-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold tracking-tight"
          >
            Help & Support
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-muted-foreground"
          >
            Find answers and get help with Loglytics AI
          </motion.p>
        </div>
      </div>

      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for help..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Links */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <h2 className="text-xl font-semibold mb-4">Quick Links</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickLinks.map((link, index) => {
            const Icon = link.icon
            return (
              <motion.div
                key={link.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
              >
                <Card className="hover:shadow-lg transition-all cursor-pointer">
                  <CardContent className="pt-6">
                    <a href={link.href} className="flex items-start space-x-4">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold mb-1">{link.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {link.description}
                        </p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </a>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* FAQ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
            <CardDescription>
              {filteredFaqs.length} {filteredFaqs.length === 1 ? 'question' : 'questions'} found
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredFaqs.length === 0 ? (
              <div className="text-center py-12">
                <HelpCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  No questions match your search. Try different keywords.
                </p>
              </div>
            ) : (
              <Accordion type="single" collapsible className="w-full">
                {filteredFaqs.map((item, index) => (
                  <AccordionItem key={index} value={`item-${index}`}>
                    <AccordionTrigger className="text-left">
                      {item.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-muted-foreground">
                      {item.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Support Channels */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <h2 className="text-xl font-semibold mb-4">Contact Support</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {supportChannels.map((channel, index) => {
            const Icon = channel.icon
            return (
              <motion.div
                key={channel.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.7 + index * 0.1 }}
              >
                <Card>
                  <CardContent className="pt-6 text-center">
                    <div className="inline-flex p-3 rounded-lg bg-primary/10 mb-4">
                      <Icon className="h-8 w-8 text-primary" />
                    </div>
                    <div className="flex items-center justify-center space-x-2 mb-2">
                      <h3 className="font-semibold">{channel.title}</h3>
                      {channel.badge && (
                        <Badge variant="success" size="sm">
                          {channel.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      {channel.description}
                    </p>
                    <Button
                      variant="outline"
                      className="w-full"
                      disabled={!channel.href}
                      asChild={!!channel.href}
                    >
                      {channel.href ? (
                        <a href={channel.href}>
                          {channel.action}
                          <ExternalLink className="h-4 w-4 ml-2" />
                        </a>
                      ) : (
                        <span>{channel.action}</span>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* Resources */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Additional Resources</CardTitle>
            <CardDescription>
              Helpful links and resources for Loglytics AI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <a
              href="#"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div>
                <p className="font-medium">Release Notes</p>
                <p className="text-sm text-muted-foreground">
                  See what's new in the latest version
                </p>
              </div>
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
            <a
              href="#"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div>
                <p className="font-medium">Status Page</p>
                <p className="text-sm text-muted-foreground">
                  Check system status and uptime
                </p>
              </div>
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
            <a
              href="#"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div>
                <p className="font-medium">Feature Requests</p>
                <p className="text-sm text-muted-foreground">
                  Vote on and submit feature ideas
                </p>
              </div>
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
            <a
              href="#"
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div>
                <p className="font-medium">GitHub Repository</p>
                <p className="text-sm text-muted-foreground">
                  View source code and contribute
                </p>
              </div>
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </a>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
