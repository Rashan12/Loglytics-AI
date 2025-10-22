'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { FolderOpen, Plus, Search } from 'lucide-react';

export default function ProjectsListPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Set a maximum loading time of 10 seconds
    const loadingTimeout = setTimeout(() => {
      console.warn('Projects loading timeout - showing empty state');
      setLoading(false);
    }, 10000);
    
    fetchProjects().finally(() => {
      clearTimeout(loadingTimeout);
    });
  }, []);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setProjects([]);
        setLoading(false);
        return;
      }

      // Set a timeout for the entire operation
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 5000)
      );

      const fetchData = async () => {
        const response = await fetch('http://localhost:8000/api/v1/projects', {
          headers: { 'Authorization': `Bearer ${token}` },
          signal: AbortSignal.timeout(3000)
        });
        
        if (response.ok) {
          const data = await response.json();
          setProjects(data);
        } else {
          setProjects([]);
        }
      };

      await Promise.race([fetchData(), timeoutPromise]);
      
    } catch (error) {
      console.error('Error fetching projects:', error);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Projects</h1>
          <p className="text-gray-400">Manage all your log analysis projects</p>
        </div>
        <button
          onClick={() => router.push('/dashboard/new-project')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search projects..."
          className="w-full pl-10 pr-4 py-3 bg-[#161B22] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-20">
          <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">
            {searchQuery ? 'No matching projects' : 'No projects yet'}
          </h3>
          <p className="text-gray-400 mb-6">
            {searchQuery ? 'Try a different search term' : 'Create your first project to get started'}
          </p>
          {!searchQuery && (
            <button
              onClick={() => router.push('/dashboard/new-project')}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
            >
              Create Project
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              onClick={() => router.push(`/dashboard/projects/${project.id}`)}
              className="bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all cursor-pointer group hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-600/10"
            >
              <div className="flex items-start gap-3 mb-4">
                <div className="p-3 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-600/30 rounded-lg">
                  <FolderOpen className="w-6 h-6 text-blue-500" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-white group-hover:text-blue-400 transition-colors mb-1">
                    {project.name}
                  </h3>
                  <p className="text-sm text-gray-400 line-clamp-2">{project.description}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-[#30363D]">
                <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded">Active</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}