'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FolderOpen, ArrowLeft } from 'lucide-react';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Project name is required');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const project = await response.json();
        // Redirect to the new project or dashboard
        router.push('/dashboard');
      } else {
        const data = await response.json();
        setError(data.detail || 'Failed to create project');
      }
    } catch (err) {
      console.error('Error creating project:', err);
      setError('Failed to create project. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-600/30 rounded-xl">
            <FolderOpen className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">Create New Project</h1>
            <p className="text-gray-400">Set up a new log analysis project</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-[#161B22] border border-[#30363D] rounded-xl p-8">
          <div className="space-y-6">
            {/* Project Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Production API Logs"
                className="w-full px-4 py-3 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600 transition-colors"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Choose a descriptive name for your project</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this project is for..."
                rows={4}
                className="w-full px-4 py-3 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600 transition-colors resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">Optional: Add more details about this project</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-sm">
                {error}
              </div>
            )}

            {/* Buttons */}
            <div className="flex items-center gap-4 pt-4">
              <button
                type="submit"
                disabled={creating}
                className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {creating ? 'Creating...' : 'Create Project'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 bg-[#0F1419] border border-[#30363D] rounded-lg text-gray-400 hover:text-white hover:border-blue-600/50 font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <h4 className="text-blue-500 font-semibold mb-2">What's next?</h4>
          <ul className="text-sm text-gray-400 space-y-1">
            <li>• Upload log files to your project</li>
            <li>• Use AI to analyze and understand patterns</li>
            <li>• Set up real-time monitoring</li>
            <li>• Get insights and recommendations</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
