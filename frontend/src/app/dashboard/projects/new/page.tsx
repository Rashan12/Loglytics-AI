'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';
import { useAuthStore } from '@/store/auth-store';
import { FolderOpen, ArrowLeft } from 'lucide-react';
import { GradientButton } from '@/components/ui/gradient-button';
import { FloatingInput } from '@/components/ui/floating-input';
import { GlassCard } from '@/components/ui/glass-card';
import { cn } from '@/lib/utils';

export default function NewProjectPage() {
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { createProject } = useProjectStore();
  const { token, isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [nameError, setNameError] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    // Check authentication
    const checkAuth = () => {
      const storedToken = localStorage.getItem('access_token');
      if (!token && !storedToken && !isAuthenticated) {
        console.warn('⚠️ No authentication found, redirecting to login');
        router.push('/login');
      }
    };
    checkAuth();
  }, [token, isAuthenticated, router]);

  const isDark = mounted && resolvedTheme === 'dark';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    setNameError('');
    setError('');
    
    if (!formData.name.trim()) {
      setNameError('Project name is required');
      return;
    }

    // Check auth before submitting
    const storedToken = localStorage.getItem('access_token');
    if (!token && !storedToken) {
      setError('Authentication required. Please log in again.');
      setTimeout(() => router.push('/login'), 2000);
      return;
    }

    setCreating(true);

    try {
      const project = await createProject(formData.name, formData.description || undefined);
      
      if (project) {
        // Redirect to the new project details page
        router.push(`/dashboard/projects/${project.id}`);
      } else {
        setError('Failed to create project. Please try again.');
      }
    } catch (err: any) {
      console.error('Error creating project:', err);
      const errorMsg = err.message || 'Failed to create project. Please try again.';
      setError(errorMsg);
      
      // If auth error, redirect to login
      if (errorMsg.includes('authentication') || errorMsg.includes('Authentication')) {
        setTimeout(() => router.push('/login'), 2000);
      }
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className={cn('min-h-screen transition-colors duration-300', isDark ? 'bg-[#0A0E1A]' : 'bg-gray-50')}>
      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        className="pt-20"
      >
        <div className="p-8 max-w-3xl mx-auto">
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

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-4 mb-8"
          >
            <div className="p-3 rounded-xl bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 border border-[#2E9BFF]/30">
              <FolderOpen className="w-8 h-8 text-[#2E9BFF]" />
            </div>
            <div>
              <h1 className={cn('text-3xl font-bold mb-1', isDark ? 'text-[#F9FAFB]' : 'text-gray-900')}>
                Create New Project
              </h1>
              <p className={cn('text-base', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
                Set up a new log analysis project
              </p>
            </div>
          </motion.div>

          {/* Form */}
          <GlassCard className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Project Name */}
              <div>
                <FloatingInput
                  label="Project Name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  error={nameError}
                  placeholder="e.g., Production API Logs"
                  required
                />
                <p className={cn('text-xs mt-1', isDark ? 'text-[#64748B]' : 'text-gray-500')}>
                  Choose a descriptive name for your project
                </p>
              </div>

              {/* Description */}
              <div>
                <label className={cn('block text-sm font-medium mb-2', isDark ? 'text-[#94A3B8]' : 'text-gray-700')}>
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe what this project is for..."
                  rows={4}
                  className={cn(
                    'w-full px-4 py-3 rounded-xl border transition-all focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20 resize-none',
                    isDark
                      ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                      : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                  )}
                />
                <p className={cn('text-xs mt-1', isDark ? 'text-[#64748B]' : 'text-gray-500')}>
                  Optional: Add more details about this project
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-xl bg-[#EF4444]/10 border border-[#EF4444]/50"
                >
                  <p className="text-sm text-[#EF4444]">{error}</p>
                </motion.div>
              )}

              {/* Buttons */}
              <div className="flex items-center gap-4 pt-4">
                <GradientButton
                  type="submit"
                  isLoading={creating}
                  fullWidth
                  className="flex-1"
                >
                  {creating ? 'Creating...' : 'Create Project'}
                </GradientButton>
                <button
                  type="button"
                  onClick={() => router.push('/dashboard/projects')}
                  className={cn(
                    'px-6 py-3 rounded-xl border transition-all font-medium',
                    isDark
                      ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#94A3B8] hover:text-[#2E9BFF] hover:border-[#2E9BFF]/50'
                      : 'bg-white border-gray-200 text-gray-600 hover:text-blue-600 hover:border-blue-300'
                  )}
                >
                  Cancel
                </button>
              </div>
            </form>
          </GlassCard>

          {/* Info Box */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className={cn(
              'mt-6 p-6 rounded-xl border',
              isDark
                ? 'bg-[#2E9BFF]/10 border-[#2E9BFF]/30'
                : 'bg-blue-50 border-blue-200'
            )}
          >
            <h4 className={cn('font-semibold mb-3', isDark ? 'text-[#2E9BFF]' : 'text-blue-600')}>
              What's next?
            </h4>
            <ul className={cn('text-sm space-y-2', isDark ? 'text-[#94A3B8]' : 'text-gray-600')}>
              <li>• Upload log files to your project</li>
              <li>• Use AI to analyze and understand patterns</li>
              <li>• Set up real-time monitoring</li>
              <li>• Get insights and recommendations</li>
            </ul>
          </motion.div>
        </div>
      </motion.main>
    </div>
  );
}

