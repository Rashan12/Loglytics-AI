'use client';

import * as React from 'react';
import { motion } from 'framer-motion';
import { useParams, useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';
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
  ArrowLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { fetchProject, deleteProject, currentProject } = useProjectStore();
  const [mounted, setMounted] = React.useState(false);
  const projectId = params.id as string;
  const [activeTab, setActiveTab] = React.useState('chats');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [analytics, setAnalytics] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [chats, setChats] = React.useState<any[]>([]);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  // Fetch project data
  React.useEffect(() => {
    const fetchProjectData = async () => {
      // Don't try to fetch if projectId is "new" - this should be handled by /projects/new route
      if (projectId === 'new') {
        router.push('/dashboard/projects/new');
        return;
      }

      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        if (!token) {
          setError('Not authenticated. Please log in again.');
          setLoading(false);
          return;
        }

        // Fetch project details
        const project = await fetchProject(projectId);
        if (!project) {
          setError('Project not found');
          setLoading(false);
          return;
        }

        // Fetch project analytics
        try {
          const analyticsResponse = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/analytics`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          if (analyticsResponse.ok) {
            const analyticsData = await analyticsResponse.json();
            setAnalytics(analyticsData);
          }
        } catch (err) {
          console.error('Analytics fetch failed:', err);
        }

        // Fetch chats for this project
        try {
          const chatsResponse = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/chats`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          if (chatsResponse.ok) {
            const chatsData = await chatsResponse.json();
            setChats(Array.isArray(chatsData) ? chatsData : (chatsData.chats || []));
          }
        } catch (err) {
          console.error('Chats fetch failed:', err);
        }
      } catch (err) {
        console.error('Error fetching project:', err);
        setError('Failed to load project');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProjectData();
    }
  }, [projectId, fetchProject, router]);

  const handleProjectAction = (action: string) => {
    if (action === 'delete') {
      if (confirm('Are you sure you want to delete this project?')) {
        deleteProject(projectId).then(() => {
          router.push('/dashboard/projects');
        });
      }
    } else {
      console.log(`${action} project ${projectId}`);
      // TODO: Implement other project actions
    }
  };

  const handleChatAction = (chatId: string, action: string) => {
    if (action === 'open') {
      router.push(`/dashboard/projects/${projectId}/chats/${chatId}`);
    }
    // TODO: Implement other chat actions
  };

  // Show loading state
  if (loading) {
    return (
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className={cn('p-8 max-w-[1800px] mx-auto space-y-6', isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50')}>
          <div className="animate-pulse">
            <div className={cn('h-8 rounded w-1/3 mb-4', isDark ? 'bg-[#1A1F3A]' : 'bg-gray-200')}></div>
            <div className={cn('h-4 rounded w-2/3 mb-2', isDark ? 'bg-[#1A1F3A]' : 'bg-gray-200')}></div>
            <div className={cn('h-4 rounded w-1/2', isDark ? 'bg-[#1A1F3A]' : 'bg-gray-200')}></div>
          </div>
        </div>
      </motion.main>
    );
  }

  // Show error state
  if (error || !currentProject) {
    return (
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className={cn('p-8 max-w-[1800px] mx-auto', isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50')}>
          <div className="text-center py-12">
            <h2 className={cn('text-2xl font-bold mb-2', isDark ? 'text-[#EF4444]' : 'text-red-600')}>Error</h2>
            <p className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>{error || 'Project not found'}</p>
            <Button
              onClick={() => router.push('/dashboard/projects')}
              className="mt-4"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Projects
            </Button>
          </div>
        </div>
      </motion.main>
    );
  }

  const project = currentProject;

  return (
    <div className={cn('min-h-screen transition-colors duration-300', isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50')}>
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className="p-8 max-w-[1800px] mx-auto space-y-6">
          {/* Back Button */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <button
              onClick={() => router.push('/dashboard/projects')}
              className={cn(
                'flex items-center gap-2 mb-6 px-4 py-2 rounded-xl transition-all',
                isDark
                  ? 'text-[#94A3B8] hover:text-[#2E9BFF] hover:bg-[#1E293B]'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-gray-100'
              )}
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium">Back to Projects</span>
            </button>
          </motion.div>

          {/* Project Header */}
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <div className="flex items-center space-x-3">
                <h1 className={cn('text-3xl font-bold tracking-tight', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                  {project.name}
                </h1>
                <Badge variant={project.is_active !== false ? 'default' : 'secondary'}>
                  {project.is_active !== false ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              {project.description && (
                <p className={cn('max-w-2xl', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                  {project.description}
                </p>
              )}
              <div className={cn('flex items-center space-x-4 text-sm', isDark ? 'text-[#64748B]' : 'text-gray-500')}>
                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-4 w-4" />
                  <span>Updated {new Date(project.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                onClick={() => router.push(`/dashboard/projects/${projectId}/chats/new`)}
                className={cn(
                  'bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] hover:from-[#2E9BFF]/90 hover:to-[#8B5CF6]/90 text-white'
                )}
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                Open AI Chat
              </Button>
              <Button variant="outline" onClick={() => handleProjectAction('edit')}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
              <Button variant="outline" onClick={() => handleProjectAction('share')}>
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
                  <DropdownMenuItem onClick={() => handleProjectAction('settings')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => handleProjectAction('delete')}
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
          <div className="grid gap-6 md:grid-cols-4">
            <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-5 w-5 text-[#2E9BFF]" />
                  <div>
                    <p className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      {chats.length}
                    </p>
                    <p className={cn('text-sm', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>Chats</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Database className="h-5 w-5 text-[#8B5CF6]" />
                  <div>
                    <p className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      {analytics?.total_logs || 0}
                    </p>
                    <p className={cn('text-sm', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>Log Entries</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5 text-[#10B981]" />
                  <div>
                    <p className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      {project.log_files_count || analytics?.log_files || 0}
                    </p>
                    <p className={cn('text-sm', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>Log Files</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Search className="h-5 w-5 text-[#F59E0B]" />
                  <div>
                    <p className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      {analytics?.vector_embeddings || 0}
                    </p>
                    <p className={cn('text-sm', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>Vector Embeddings</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList className={cn(isDark ? 'bg-[#1A1F3A]/60' : 'bg-gray-100')}>
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
                    <Search className={cn(
                      'absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                    <Input
                      placeholder="Search chats..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={cn(
                        'pl-10 w-64',
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                          : 'bg-white border-gray-200'
                      )}
                    />
                  </div>
                </div>
                <Button
                  onClick={async () => {
                    try {
                      const token = localStorage.getItem('access_token');
                      const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/chat/new`, {
                        method: 'POST',
                        headers: {
                          'Authorization': `Bearer ${token}`,
                          'Content-Type': 'application/json',
                        },
                      });

                      if (response.ok) {
                        const newChat = await response.json();
                        router.push(`/dashboard/projects/${projectId}/chats/${newChat.session_id}`);
                      } else {
                        const newChatId = Date.now().toString();
                        router.push(`/dashboard/projects/${projectId}/chats/${newChatId}`);
                      }
                    } catch (error) {
                      console.error('Error creating new chat:', error);
                      const newChatId = Date.now().toString();
                      router.push(`/dashboard/projects/${projectId}/chats/${newChatId}`);
                    }
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  New Chat
                </Button>
              </div>

              {chats.length === 0 ? (
                <div className="text-center py-12">
                  <MessageSquare className={cn('w-16 h-16 mx-auto mb-4', isDark ? 'text-[#64748B]' : 'text-gray-400')} />
                  <h3 className={cn('text-lg font-semibold mb-2', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                    No chats yet
                  </h3>
                  <p className={cn('mb-6', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                    Start your first conversation to analyze your logs
                  </p>
                  <Button
                    onClick={async () => {
                      try {
                        const token = localStorage.getItem('access_token');
                        const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/chat/new`, {
                          method: 'POST',
                          headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json',
                          },
                        });

                        if (response.ok) {
                          const newChat = await response.json();
                          router.push(`/dashboard/projects/${projectId}/chats/${newChat.session_id}`);
                        } else {
                          const newChatId = Date.now().toString();
                          router.push(`/dashboard/projects/${projectId}/chats/${newChatId}`);
                        }
                      } catch (error) {
                        console.error('Error creating new chat:', error);
                        const newChatId = Date.now().toString();
                        router.push(`/dashboard/projects/${projectId}/chats/${newChatId}`);
                      }
                    }}
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Start New Chat
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {chats
                    .filter((chat: any) =>
                      chat.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      chat.id?.toString().includes(searchQuery)
                    )
                    .map((chat: any) => (
                      <motion.div
                        key={chat.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => handleChatAction(chat.id, 'open')}
                        className={cn(
                          'rounded-lg p-4 cursor-pointer transition-all',
                          isDark
                            ? 'bg-[#1A1F3A]/60 border border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50'
                            : 'bg-white border border-gray-200 hover:border-blue-500'
                        )}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className={cn('font-semibold truncate', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                            {chat.title || `Chat ${chat.id}`}
                          </h3>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </div>
                        {chat.updated_at && (
                          <p className={cn('text-sm', isDark ? 'text-[#64748B]' : 'text-gray-500')}>
                            {new Date(chat.updated_at).toLocaleDateString()}
                          </p>
                        )}
                      </motion.div>
                    ))}
                </div>
              )}
            </TabsContent>

            {/* Logs Tab */}
            <TabsContent value="logs" className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className={cn(
                      'absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                    <Input
                      placeholder="Search log files..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className={cn(
                        'pl-10 w-64',
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                          : 'bg-white border-gray-200'
                      )}
                    />
                  </div>
                </div>
                <Button onClick={() => router.push(`/dashboard/projects/${projectId}/upload`)}>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Logs
                </Button>
              </div>

              {(!project.log_files_count || project.log_files_count === 0) && (!analytics?.log_files || analytics.log_files === 0) ? (
                <div className="text-center py-12">
                  <Database className={cn('w-16 h-16 mx-auto mb-4', isDark ? 'text-[#64748B]' : 'text-gray-400')} />
                  <h3 className={cn('text-lg font-semibold mb-2', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                    No log files yet
                  </h3>
                  <p className={cn('mb-6', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                    Upload your first log file to start analysis
                  </p>
                  <Button onClick={() => router.push(`/dashboard/projects/${projectId}/upload`)}>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Log Files
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-center py-8">
                    <p className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                      Log files will appear here when uploaded
                    </p>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* RAG Statistics Tab */}
            <TabsContent value="rag" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
                  <CardHeader>
                    <CardTitle className={isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}>Vector Statistics</CardTitle>
                    <CardDescription className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                      RAG system performance metrics
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className={cn('text-sm font-medium', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                        Total Vectors
                      </span>
                      <span className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                        {analytics?.vector_embeddings || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={cn('text-sm font-medium', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                        Storage Used
                      </span>
                      <span className={cn('text-2xl font-bold', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                        {((analytics?.vector_embeddings || 0) * 0.002).toFixed(2)} MB
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Settings Tab */}
            <TabsContent value="settings" className="space-y-4">
              <Card className={cn(isDark ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50' : 'bg-white border-gray-200')}>
                <CardHeader>
                  <CardTitle className={isDark ? 'text-[#F9FAFB]' : 'text-gray-900'}>Project Settings</CardTitle>
                  <CardDescription className={isDark ? 'text-[#94A3B8]' : 'text-gray-600'}>
                    Manage your project configuration
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <label className={cn('text-sm font-medium', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      Project Name
                    </label>
                    <Input
                      defaultValue={project.name}
                      className={cn(
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                          : 'bg-white border-gray-200'
                      )}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className={cn('text-sm font-medium', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      Description
                    </label>
                    <Input
                      defaultValue={project.description || ''}
                      className={cn(
                        isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB]'
                          : 'bg-white border-gray-200'
                      )}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className={cn('text-sm font-medium', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                      Status
                    </label>
                    <div className="flex items-center space-x-2">
                      <Badge variant={project.is_active !== false ? 'default' : 'secondary'}>
                        {project.is_active !== false ? 'Active' : 'Inactive'}
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
      </motion.main>
    </div>
  );
}
