'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import {
  FolderOpen,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Calendar,
  FileText,
  Trash2,
  Eye,
  MessageSquare,
} from 'lucide-react';
import { useProjectStore } from '@/store/project-store';
import { GradientButton } from '@/components/ui/gradient-button';
import { cn } from '@/lib/utils';

export default function ProjectsListPage() {
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { projects, fetchProjects, deleteProject, isLoading } = useProjectStore();
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const isDark = mounted && resolvedTheme === 'dark';

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteProject = async (projectId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project?')) {
      await deleteProject(projectId);
      await fetchProjects();
    }
  };

  return (
    <div className={cn(
      'min-h-screen transition-colors duration-300',
      isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50'
    )}>
      {/* Main Content */}
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className="p-8 max-w-[1800px] mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              <div>
                <h1 className={cn(
                  'text-3xl font-bold mb-2',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  Projects
                </h1>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Manage and organize your log analysis projects
                </p>
              </div>

              <GradientButton
                onClick={() => router.push('/dashboard/projects/new')}
                className="flex items-center gap-2 px-4 py-2.5"
              >
                <Plus className="w-5 h-5" />
                Create Project
              </GradientButton>
            </div>
          </motion.div>

          {/* Search and Filter Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mb-8"
          >
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className={cn(
                  'absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5',
                  isDark ? 'text-[#64748B]' : 'text-gray-400'
                )} />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={cn(
                    'w-full pl-12 pr-4 py-3 rounded-xl border transition-all focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20',
                    isDark
                      ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                      : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                  )}
                />
              </div>

              {/* Filter Button */}
              <button className={cn(
                'px-4 py-3 rounded-xl border transition-all flex items-center gap-2',
                isDark
                  ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#94A3B8] hover:border-[#2E9BFF]/50'
                  : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'
              )}>
                <Filter className="w-5 h-5" />
                <span className="text-sm font-medium">Filter</span>
              </button>
            </div>
          </motion.div>

          {/* Projects Grid */}
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className={cn(
                  "w-16 h-16 border-4 rounded-full animate-spin mx-auto mb-4",
                  isDark ? "border-[#2E9BFF] border-t-transparent" : "border-blue-600 border-t-transparent"
                )} />
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Loading projects...
                </p>
              </div>
            </div>
          ) : filteredProjects.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className={cn(
                'rounded-2xl border p-20 text-center',
                isDark
                  ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200'
              )}
            >
              <div className={cn(
                'w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center',
                isDark
                  ? 'bg-[#2E9BFF]/10 border border-[#2E9BFF]/30'
                  : 'bg-blue-50 border border-blue-200'
              )}>
                <FolderOpen className={cn(
                  'w-10 h-10',
                  isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                )} />
              </div>
              <h3 className={cn(
                'text-xl font-bold mb-2',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {searchQuery ? 'No projects found' : 'No projects yet'}
              </h3>
              <p className={cn(
                'text-base mb-6 max-w-md mx-auto',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                {searchQuery 
                  ? 'Try adjusting your search criteria'
                  : 'Create your first project to get started with log analysis'
                }
              </p>
              {!searchQuery && (
                <GradientButton
                  onClick={() => router.push('/dashboard/projects/new')}
                  className="px-6 py-3"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create your first project
                </GradientButton>
              )}
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredProjects.map((project, index) => (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 + index * 0.05 }}
                  whileHover={{ y: -4 }}
                  onClick={() => router.push(`/dashboard/projects/${project.id}`)}
                  className={cn(
                    'group relative p-6 rounded-2xl border cursor-pointer transition-all',
                    isDark
                      ? 'bg-[#1A1F3A]/60 backdrop-blur-xl border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50'
                      : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-lg'
                  )}
                >
                  {/* Gradient Blob */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />

                  {/* Header */}
                  <div className="relative flex items-start justify-between mb-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 border border-[#2E9BFF]/30">
                      <FolderOpen className="w-6 h-6 text-[#2E9BFF]" />
                    </div>

                    {/* Actions Menu */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // Add dropdown menu logic here
                      }}
                      className={cn(
                        'p-2 rounded-lg transition-all',
                        isDark
                          ? 'hover:bg-[#2E3A5C]'
                          : 'hover:bg-gray-100'
                      )}
                    >
                      <MoreVertical className={cn(
                        'w-5 h-5',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-400'
                      )} />
                    </button>
                  </div>

                  {/* Project Name */}
                  <h3 className={cn(
                    'text-lg font-bold mb-2 group-hover:text-[#2E9BFF] transition-colors',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    {project.name}
                  </h3>

                  {/* Description */}
                  {project.description && (
                    <p className={cn(
                      'text-sm mb-4 line-clamp-2',
                      isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                    )}>
                      {project.description}
                    </p>
                  )}

                  {/* Stats */}
                  <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <FileText className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#64748B]' : 'text-gray-400'
                      )} />
                      <span className={cn(
                        'text-sm',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        {project.log_files_count || 0} files
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#64748B]' : 'text-gray-400'
                      )} />
                      <span className={cn(
                        'text-sm',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        {new Date(project.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'px-3 py-1 text-xs font-semibold rounded-full',
                      project.is_active !== false
                        ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50'
                        : 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/50'
                    )}>
                      {project.is_active !== false ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  {/* Quick Actions - Appears on Hover */}
                  <div className="absolute bottom-6 right-6 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/dashboard/projects/${project.id}`);
                      }}
                      className={cn(
                        'p-2 rounded-lg transition-all',
                        isDark
                          ? 'bg-[#2E3A5C] hover:bg-[#334155]'
                          : 'bg-gray-100 hover:bg-gray-200'
                      )}
                      title="View Project"
                    >
                      <Eye className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/dashboard/projects/${project.id}/chat`);
                      }}
                      className={cn(
                        'p-2 rounded-lg transition-all',
                        isDark
                          ? 'bg-[#2E3A5C] hover:bg-[#334155]'
                          : 'bg-gray-100 hover:bg-gray-200'
                      )}
                      title="AI Chat"
                    >
                      <MessageSquare className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )} />
                    </button>
                    <button
                      onClick={(e) => handleDeleteProject(project.id, e)}
                      className="p-2 rounded-lg bg-[#EF4444]/20 hover:bg-[#EF4444]/30 transition-all"
                      title="Delete Project"
                    >
                      <Trash2 className="w-4 h-4 text-[#EF4444]" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Projects Count */}
          {filteredProjects.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className={cn(
                'mt-8 text-center text-sm',
                isDark ? 'text-[#64748B]' : 'text-gray-500'
              )}
            >
              Showing {filteredProjects.length} of {projects.length} projects
            </motion.div>
          )}
        </div>
      </motion.main>
    </div>
  );
}
