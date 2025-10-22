"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { useParams } from "next/navigation"
import {
  Edit,
  Settings,
  Share,
  Trash2,
  MessageSquare,
  Database,
  BarChart3,
  MoreHorizontal,
  Plus,
  Upload,
  Search,
  Filter,
  Calendar,
  User,
  Clock,
} from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface Project {
  id: string
  name: string
  description: string
  chatCount: number
  logCount: number
  lastAccessed: string
  createdAt: string
  status: "active" | "archived"
  owner: {
    name: string
    email: string
  }
}

interface Chat {
  id: string
  title: string
  lastMessage: string
  updatedAt: string
  unreadCount: number
}

interface LogFile {
  id: string
  name: string
  size: number
  uploadedAt: string
  status: "processing" | "completed" | "error"
  logCount: number
}

const mockProject: Project = {
  id: "1",
  name: "E-commerce Platform",
  description: "Main e-commerce application logs and monitoring for production environment",
  chatCount: 12,
  logCount: 245,
  lastAccessed: "2024-01-15T10:30:00Z",
  createdAt: "2024-01-01T00:00:00Z",
  status: "active",
  owner: {
    name: "John Doe",
    email: "john@example.com",
  },
}

const mockChats: Chat[] = [
  {
    id: "1",
    title: "API Error Analysis",
    lastMessage: "Found the root cause of the 500 errors",
    updatedAt: "2024-01-15T10:30:00Z",
    unreadCount: 0,
  },
  {
    id: "2",
    title: "Performance Optimization",
    lastMessage: "Database queries are taking too long",
    updatedAt: "2024-01-14T15:45:00Z",
    unreadCount: 2,
  },
  {
    id: "3",
    title: "Security Audit",
    lastMessage: "No suspicious activities detected",
    updatedAt: "2024-01-13T09:20:00Z",
    unreadCount: 0,
  },
]

const mockLogFiles: LogFile[] = [
  {
    id: "1",
    name: "application.log",
    size: 1024000,
    uploadedAt: "2024-01-15T08:00:00Z",
    status: "completed",
    logCount: 1250,
  },
  {
    id: "2",
    name: "error.log",
    size: 512000,
    uploadedAt: "2024-01-14T12:30:00Z",
    status: "completed",
    logCount: 890,
  },
  {
    id: "3",
    name: "access.log",
    size: 2048000,
    uploadedAt: "2024-01-13T16:45:00Z",
    status: "processing",
    logCount: 0,
  },
]

export default function ProjectDetailPage() {
  const params = useParams()
  const projectId = params.id as string
  const [activeTab, setActiveTab] = React.useState("chats")
  const [searchQuery, setSearchQuery] = React.useState("")

  const handleProjectAction = (action: string) => {
    console.log(`${action} project ${projectId}`)
    // TODO: Implement project actions
  }

  const handleChatAction = (chatId: string, action: string) => {
    console.log(`${action} chat ${chatId}`)
    if (action === "open") {
      // Navigate to chat interface
      window.location.href = `/dashboard/projects/${projectId}/chats/${chatId}`
    }
    // TODO: Implement other chat actions
  }

  const handleLogAction = (logId: string, action: string) => {
    console.log(`${action} log ${logId}`)
    // TODO: Implement log actions
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="flex-1 space-y-6 p-6">
      {/* Project Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-bold tracking-tight">{mockProject.name}</h1>
            <Badge variant={mockProject.status === "active" ? "default" : "secondary"}>
              {mockProject.status}
            </Badge>
          </div>
          <p className="text-muted-foreground max-w-2xl">{mockProject.description}</p>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <User className="h-4 w-4" />
              <span>Created by {mockProject.owner.name}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="h-4 w-4" />
              <span>{new Date(mockProject.createdAt).toLocaleDateString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="h-4 w-4" />
              <span>Last accessed {new Date(mockProject.lastAccessed).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={() => handleProjectAction("edit")}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button variant="outline" onClick={() => handleProjectAction("share")}>
            <Share className="mr-2 h-4 w-4" />
            Share
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleProjectAction("settings")}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => handleProjectAction("delete")}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Project
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-2xl font-bold">{mockProject.chatCount}</p>
                <p className="text-sm text-muted-foreground">Chats</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Database className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-2xl font-bold">{mockProject.logCount}</p>
                <p className="text-sm text-muted-foreground">Log Entries</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-emerald-500" />
              <div>
                <p className="text-2xl font-bold">3</p>
                <p className="text-sm text-muted-foreground">Log Files</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-amber-500" />
              <div>
                <p className="text-2xl font-bold">1.2K</p>
                <p className="text-sm text-muted-foreground">Vector Embeddings</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="chats">Chats</TabsTrigger>
          <TabsTrigger value="logs">Log Files</TabsTrigger>
          <TabsTrigger value="rag">RAG Statistics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Chats Tab */}
        <TabsContent value="chats" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search chats..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
            <Button onClick={() => {
              // Create a new chat and navigate to it
              const newChatId = Date.now().toString()
              window.location.href = `/dashboard/projects/${projectId}/chats/${newChatId}`
            }}>
              <Plus className="mr-2 h-4 w-4" />
              New Chat
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mockChats.map((chat, index) => (
              <motion.div
                key={chat.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg line-clamp-1">{chat.title}</CardTitle>
                      {chat.unreadCount > 0 && (
                        <Badge variant="destructive" size="sm">
                          {chat.unreadCount}
                        </Badge>
                      )}
                    </div>
                    <CardDescription className="line-clamp-2">
                      {chat.lastMessage}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Updated {new Date(chat.updatedAt).toLocaleDateString()}</span>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleChatAction(chat.id, "open")}>
                            Open Chat
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleChatAction(chat.id, "rename")}>
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => handleChatAction(chat.id, "delete")}
                            className="text-destructive focus:text-destructive"
                          >
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <Button 
                      className="w-full" 
                      variant="outline"
                      onClick={() => handleChatAction(chat.id, "open")}
                    >
                      Open Chat
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search log files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">
                    <Filter className="mr-2 h-4 w-4" />
                    Filter
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem>All Status</DropdownMenuItem>
                  <DropdownMenuItem>Completed</DropdownMenuItem>
                  <DropdownMenuItem>Processing</DropdownMenuItem>
                  <DropdownMenuItem>Error</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <Button onClick={() => {
              // Navigate to log upload page
              window.location.href = `/dashboard/projects/${projectId}/upload`
            }}>
              <Upload className="mr-2 h-4 w-4" />
              Upload Logs
            </Button>
          </div>

          <div className="space-y-4">
            {mockLogFiles.map((log, index) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card className="group hover:shadow-lg transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                          <Database className="h-5 w-5 text-blue-500" />
                        </div>
                        <div className="space-y-1">
                          <h3 className="font-medium">{log.name}</h3>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>{formatFileSize(log.size)}</span>
                            <span>•</span>
                            <span>{log.logCount} entries</span>
                            <span>•</span>
                            <span>{new Date(log.uploadedAt).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant={
                            log.status === "completed" ? "default" : 
                            log.status === "processing" ? "secondary" : 
                            "destructive"
                          }
                        >
                          {log.status}
                        </Badge>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleLogAction(log.id, "view")}>
                              View Logs
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleLogAction(log.id, "download")}>
                              Download
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem 
                              onClick={() => handleLogAction(log.id, "delete")}
                              className="text-destructive focus:text-destructive"
                            >
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </TabsContent>

        {/* RAG Statistics Tab */}
        <TabsContent value="rag" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Vector Statistics</CardTitle>
                <CardDescription>RAG system performance metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Vectors</span>
                  <span className="text-2xl font-bold">1,247</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Storage Used</span>
                  <span className="text-2xl font-bold">2.3 MB</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Avg Query Time</span>
                  <span className="text-2xl font-bold">45ms</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Recent Queries</CardTitle>
                <CardDescription>Latest RAG search queries</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">"What caused the API errors?"</div>
                <div className="text-sm">"Show me performance issues"</div>
                <div className="text-sm">"Find database connection problems"</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Project Settings</CardTitle>
              <CardDescription>Manage your project configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Project Name</label>
                <Input defaultValue={mockProject.name} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input defaultValue={mockProject.description} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Status</label>
                <div className="flex items-center space-x-2">
                  <Badge variant={mockProject.status === "active" ? "default" : "secondary"}>
                    {mockProject.status}
                  </Badge>
                  <Button variant="outline" size="sm">
                    Change Status
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
