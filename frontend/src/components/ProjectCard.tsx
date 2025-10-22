'use client';

import { useRouter } from 'next/navigation';
import { FolderOpen, MoreVertical, Calendar, FileText, AlertTriangle } from 'lucide-react';
import { useState } from 'react';

interface ProjectCardProps {
  id: string;
  name: string;
  description: string;
  logCount?: number;
  errorCount?: number;
  lastActivity?: string;
  createdAt: string;
}

export default function ProjectCard({
  id,
  name,
  description,
  logCount = 0,
  errorCount = 0,
  lastActivity,
  createdAt
}: ProjectCardProps) {
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);

  const handleOpen = () => {
    router.push(`/dashboard/projects/${id}`);
  };

  return (
    <div className="group relative bg-[#161B22] border border-[#30363D] rounded-xl p-6 hover:border-blue-600/50 transition-all duration-300 hover:shadow-xl hover:shadow-blue-600/10 hover:-translate-y-1 cursor-pointer animate-slideUp">
      {/* Neumorphic effect on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-purple-600/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative" onClick={handleOpen}>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3">
            <div className="p-3 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-600/30 rounded-lg">
              <FolderOpen className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-1 group-hover:text-blue-400 transition-colors">
                {name}
              </h3>
              <p className="text-sm text-gray-400 line-clamp-2">{description}</p>
            </div>
          </div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-2 rounded-lg hover:bg-[#1C2128] transition-colors relative"
          >
            <MoreVertical className="w-5 h-5 text-gray-400" />
            
            {showMenu && (
              <div className="absolute right-0 top-10 w-48 bg-[#161B22] border border-[#30363D] rounded-lg shadow-2xl z-10">
                <button className="w-full px-4 py-2 text-left text-sm text-white hover:bg-[#1C2128] rounded-t-lg">
                  Edit Project
                </button>
                <button className="w-full px-4 py-2 text-left text-sm text-white hover:bg-[#1C2128]">
                  View Logs
                </button>
                <button className="w-full px-4 py-2 text-left text-sm text-white hover:bg-[#1C2128]">
                  Settings
                </button>
                <button className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-red-500/10 rounded-b-lg border-t border-[#30363D]">
                  Delete Project
                </button>
              </div>
            )}
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center p-3 bg-[#0F1419] rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Total Logs</p>
            <p className="text-lg font-bold text-white">{logCount.toLocaleString()}</p>
          </div>
          <div className="text-center p-3 bg-[#0F1419] rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Errors</p>
            <p className="text-lg font-bold text-red-500">{errorCount}</p>
          </div>
          <div className="text-center p-3 bg-[#0F1419] rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Status</p>
            <div className="flex items-center justify-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <p className="text-xs font-semibold text-green-500">Active</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t border-[#30363D]">
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>Created {new Date(createdAt).toLocaleDateString()}</span>
          </div>
          {lastActivity && (
            <div className="flex items-center gap-1">
              <span>Updated {lastActivity}</span>
            </div>
          )}
        </div>

        {/* Action Button */}
        <button className="mt-4 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
          <span>Open Project</span>
          <span>→</span>
        </button>
      </div>
    </div>
  );
}
