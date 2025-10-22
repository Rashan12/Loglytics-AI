'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  FileText, 
  AlertTriangle, 
  FolderOpen, 
  Sparkles,
  Upload,
  BarChart3,
  Activity,
  MessageSquare,
  ArrowRight,
  Plus
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [stats, setStats] = useState({
    totalLogs: 0,
    errorRate: 0,
    activeProjects: 0,
    aiInsights: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
    
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      // No token, show dashboard with default values
      setLoading(false);
      return;
    }
    
    // Set a maximum loading time of 10 seconds
    const loadingTimeout = setTimeout(() => {
      console.warn('Dashboard loading timeout - showing default data');
      setLoading(false);
    }, 10000);
    
    fetchDashboardData().finally(() => {
      clearTimeout(loadingTimeout);
    });
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      // Set a timeout for the entire operation
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 5000)
      );
      
      const fetchData = async () => {
        const promises = [];
        
        // Fetch projects with timeout
        if (token) {
          promises.push(
            fetch('http://localhost:8000/api/v1/projects', {
              headers: { 'Authorization': `Bearer ${token}` },
              signal: AbortSignal.timeout(3000)
            }).catch(err => {
              console.warn('Projects API failed:', err);
              return { ok: false };
            })
          );
          
          // Fetch analytics stats with timeout
          promises.push(
            fetch('http://localhost:8000/api/v1/analytics/dashboard', {
              headers: { 'Authorization': `Bearer ${token}` },
              signal: AbortSignal.timeout(3000)
            }).catch(err => {
              console.warn('Analytics API failed:', err);
              return { ok: false };
            })
          );
        }
        
        const [projectsRes, statsRes] = await Promise.all(promises);
        
        // Handle projects response
        if (projectsRes && projectsRes.ok) {
          const projectsData = await projectsRes.json();
          setProjects(projectsData);
          setStats(prev => ({ ...prev, activeProjects: projectsData.length }));
        }
        
        // Handle analytics response
        if (statsRes && statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(prev => ({
            ...prev,
            totalLogs: statsData.total_logs || 0,
            errorRate: statsData.error_rate || 0,
            aiInsights: statsData.ai_insights || 0
          }));
        }
      };
      
      await Promise.race([fetchData(), timeoutPromise]);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Set default values on error
      setStats({
        totalLogs: 0,
        errorRate: 0,
        activeProjects: 0,
        aiInsights: 0
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Welcome Section - NO EXTRA SPACING */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}! 👋
        </h1>
        <p className="text-gray-400">Here's what's happening with your logs today.</p>
      </div>

      {/* Stats Grid - DIRECTLY BELOW WELCOME MESSAGE */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Logs Card */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 font-medium">Total Logs</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.totalLogs.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <FileText className="w-6 h-6 text-blue-500" />
            </div>
          </div>
          <p className="text-sm text-green-500">+12% from last period</p>
        </div>

        {/* Error Rate Card */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 font-medium">Error Rate</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.errorRate.toFixed(1)}%</h3>
            </div>
            <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-orange-500" />
            </div>
          </div>
          <p className="text-sm text-green-500">-0.3% from last period</p>
        </div>

        {/* Active Projects Card */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 font-medium">Active Projects</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.activeProjects}</h3>
            </div>
            <div className="p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <FolderOpen className="w-6 h-6 text-purple-500" />
            </div>
          </div>
          <p className="text-sm text-green-500">+2 from last period</p>
        </div>

        {/* AI Insights Card */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-400 font-medium">AI Insights</p>
              <h3 className="text-3xl font-bold text-white mt-2">{stats.aiInsights}</h3>
            </div>
            <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
              <Sparkles className="w-6 h-6 text-green-500" />
            </div>
          </div>
          <p className="text-sm text-green-500">+8 from last period</p>
        </div>
      </div>

      {/* Main Content Grid - NO "PERFORMANCE OVERVIEW" SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Projects Section - 2 columns */}
        <div className="lg:col-span-2 bg-[#161B22] border border-[#30363D] rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white">Your Projects</h2>
              <p className="text-sm text-gray-400 mt-1">Manage and monitor your log analysis projects</p>
            </div>
            <button
              onClick={() => router.push('/dashboard/new-project')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Project
            </button>
          </div>

          {projects.length === 0 ? (
            <div className="text-center py-12">
              <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">No projects yet</h3>
              <p className="text-gray-400 mb-6">Create your first project to start analyzing logs</p>
              <button
                onClick={() => router.push('/dashboard/new-project')}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
              >
                Create Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  onClick={() => router.push(`/dashboard/projects/${project.id}`)}
                  className="p-4 bg-[#0F1419] border border-[#30363D] rounded-lg hover:border-blue-600/50 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                      {project.name}
                    </h3>
                    <ArrowRight className="w-4 h-4 text-gray-600 group-hover:text-blue-500 transition-colors" />
                  </div>
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{project.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{new Date(project.created_at).toLocaleDateString()}</span>
                    <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded">Active</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions - 1 column */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-6">Quick Actions</h2>
          
          <div className="space-y-3">
            <button 
              onClick={() => router.push('/dashboard/log-files')}
              className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg text-white font-medium hover:shadow-lg hover:shadow-blue-600/30 transition-all"
            >
              <Upload className="w-5 h-5" />
              <div className="flex-1 text-left">
                <p className="font-semibold">Upload Logs</p>
                <p className="text-xs text-blue-100 mt-0.5">Upload and analyze new log files</p>
              </div>
            </button>

            <button 
              onClick={() => router.push('/dashboard/analytics')}
              className="w-full flex items-center gap-3 p-4 bg-[#1C2128] border border-[#30363D] rounded-lg text-white font-medium hover:border-blue-600/50 hover:bg-[#252C36] transition-all"
            >
              <BarChart3 className="w-5 h-5 text-purple-500" />
              <div className="flex-1 text-left">
                <p className="font-semibold">View Analytics</p>
                <p className="text-xs text-gray-400 mt-0.5">Explore detailed analytics</p>
              </div>
            </button>

            <button 
              onClick={() => router.push('/dashboard/live-logs')}
              className="w-full flex items-center gap-3 p-4 bg-[#1C2128] border border-[#30363D] rounded-lg text-white font-medium hover:border-blue-600/50 hover:bg-[#252C36] transition-all"
            >
              <Activity className="w-5 h-5 text-green-500" />
              <div className="flex-1 text-left">
                <p className="font-semibold">Live Monitoring</p>
                <p className="text-xs text-gray-400 mt-0.5">Monitor logs in real-time</p>
              </div>
            </button>

            <button 
              onClick={() => router.push('/dashboard/ai-assistant')}
              className="w-full flex items-center gap-3 p-4 bg-[#1C2128] border border-[#30363D] rounded-lg text-white font-medium hover:border-blue-600/50 hover:bg-[#252C36] transition-all"
            >
              <MessageSquare className="w-5 h-5 text-orange-500" />
              <div className="flex-1 text-left">
                <p className="font-semibold">AI Chat</p>
                <p className="text-xs text-gray-400 mt-0.5">Ask questions about logs</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
