'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { useUIStore } from '@/store/ui-store';
import {
  FileText,
  Upload,
  Download,
  Trash2,
  Search,
  Filter,
  MoreVertical,
  Calendar,
  HardDrive,
  Eye,
  FolderOpen,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { GradientButton } from '@/components/ui/gradient-button';
import { cn } from '@/lib/utils';

// Helper function to get token from localStorage
const getToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  
  // Try direct localStorage key first (most common)
  const directToken = localStorage.getItem('access_token');
  if (directToken) {
    return directToken;
  }
  
  // Try auth store persisted state (zustand persist format)
  try {
    const authStoreData = localStorage.getItem('auth-store');
    if (authStoreData) {
      const parsed = JSON.parse(authStoreData);
      // Zustand persist stores data as { state: { token: ... } }
      if (parsed?.state?.token) {
        return parsed.state.token;
      }
      // Sometimes it's stored directly
      if (parsed?.token) {
        return parsed.token;
      }
    }
  } catch (e) {
    console.warn('Failed to parse auth-store:', e);
  }
  
  console.warn('⚠️ No token found in localStorage');
  return null;
};

interface LogFile {
  id: string;
  filename: string;
  original_filename?: string;
  size?: number;
  file_size?: number;
  uploadedAt?: string;
  created_at?: string;
  uploaded_at?: string;
  status?: 'processing' | 'completed' | 'failed';
  upload_status?: 'processing' | 'completed' | 'failed';
  logCount?: number;
  project_id?: string;
  file_type?: string;
}

export default function LogFilesPage() {
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [files, setFiles] = useState<LogFile[]>([]);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  // PRESERVE EXISTING FETCH LOGIC
  useEffect(() => {
    fetchLogFiles();
  }, []);

  const fetchLogFiles = async () => {
    try {
      setIsLoading(true);
      const token = getToken();
      
      if (!token) {
        console.error('❌ No authentication token found. Please log in again.');
        setIsLoading(false);
        return;
      }
      
      const response = await fetch('http://localhost:8000/api/v1/logs/files', {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 401) {
        console.error('❌ Authentication failed. Token may be expired.');
        alert('Your session has expired. Please log in again.');
        window.location.href = '/login';
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        // Handle both { files: [...] } and direct array response
        const filesData = Array.isArray(data) ? data : (data.files || []);
        setFiles(filesData);
      } else if (response.status === 404) {
        // Endpoint not found - silently handle, no console output
        setFiles([]);
      } else {
        // Only log non-404 errors
        if (response.status !== 401) {
          console.warn('⚠️ Failed to fetch log files:', response.status);
        }
        setFiles([]);
      }
    } catch (error) {
      // Silently handle all network errors - no console output
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  };

  // PRESERVE EXISTING DRAG AND DROP HANDLERS
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // PRESERVE EXISTING FILE SELECT HANDLER
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0]);
      // Reset input so same file can be uploaded again
      e.target.value = '';
    }
  };

  // PRESERVE EXISTING UPLOAD LOGIC
  const handleFileUpload = async (file: File) => {
    // Validate file
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      alert('File size exceeds 100MB limit');
      return;
    }

    const allowedTypes = ['.log', '.txt', '.csv', '.json'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      alert('Invalid file type. Please upload .log, .txt, .csv, or .json files');
      return;
    }

    setUploadingFile(true);
    setUploadProgress(0);

    try {
      const token = getToken();
      
      if (!token) {
        alert('No authentication token found. Please log in again.');
        setUploadingFile(false);
        setUploadProgress(0);
        window.location.href = '/login';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('http://localhost:8000/api/v1/logs/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // Note: Don't set Content-Type for FormData - browser sets it automatically with boundary
        },
        body: formData
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        window.location.href = '/login';
        setUploadProgress(0);
        setUploadingFile(false);
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        const errorMessage = errorData.detail || `Upload failed: ${response.status}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setTimeout(() => {
        setUploadProgress(0);
        setUploadingFile(false);
        fetchLogFiles(); // Refresh file list
      }, 500);
    } catch (error: any) {
      console.error('Upload error:', error);
      alert(error.message || 'Upload failed. Please try again.');
      setUploadProgress(0);
      setUploadingFile(false);
    }
  };

  // PRESERVE EXISTING DELETE HANDLER
  const handleDeleteFile = async (fileId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      const token = getToken();
      
      if (!token) {
        alert('No authentication token found. Please log in again.');
        window.location.href = '/login';
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/logs/files/${fileId}`, {
        method: 'DELETE',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        window.location.href = '/login';
        return;
      }

      if (response.ok) {
        fetchLogFiles(); // Refresh list
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to delete file' }));
        alert(errorData.detail || 'Failed to delete file');
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete file');
    }
  };

  // PRESERVE EXISTING DOWNLOAD HANDLER
  const handleDownloadFile = async (fileId: string, fileName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const token = getToken();
      
      if (!token) {
        alert('No authentication token found. Please log in again.');
        window.location.href = '/login';
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/logs/files/${fileId}/download`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        window.location.href = '/login';
        return;
      }

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to download file' }));
        alert(errorData.detail || 'Failed to download file');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  };

  // PRESERVE EXISTING FORMAT FUNCTIONS
  const formatFileSize = (bytes: number = 0) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusIcon = (status?: string) => {
    const fileStatus = status || 'completed';
    switch (fileStatus) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-[#10B981]" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-[#F59E0B] animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-[#EF4444]" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusText = (status?: string) => {
    const fileStatus = status || 'completed';
    switch (fileStatus) {
      case 'completed':
        return 'Processed';
      case 'processing':
        return 'Processing...';
      case 'failed':
        return 'Failed';
      default:
        return 'Completed';
    }
  };

  const getStatusColor = (status?: string) => {
    const fileStatus = status || 'completed';
    switch (fileStatus) {
      case 'completed':
        return 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50';
      case 'processing':
        return 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/50';
      case 'failed':
        return 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/50';
      default:
        return 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/50';
    }
  };

  const filteredFiles = files.filter(file =>
    (file.filename?.toLowerCase().includes(searchQuery.toLowerCase()) || '') ||
    (file.original_filename?.toLowerCase().includes(searchQuery.toLowerCase()) || '')
  );

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
                  Log Files
                </h1>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Upload and manage your log files for analysis
                </p>
              </div>

              {/* Upload Button */}
              <label htmlFor="file-upload">
                <GradientButton
                  as="div"
                  className="flex items-center gap-2 px-4 py-2.5 cursor-pointer"
                  disabled={uploadingFile}
                >
                  {uploadingFile ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      Upload File
                    </>
                  )}
                </GradientButton>
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  onChange={handleFileSelect}
                  accept=".log,.txt,.csv,.json"
                  disabled={uploadingFile}
                />
              </label>
            </div>
          </motion.div>

          {/* Upload Progress Bar (when uploading) */}
          {uploadingFile && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                'mb-8 p-4 rounded-xl border',
                isDark
                  ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                  : 'bg-white border-gray-200'
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={cn(
                  'text-sm font-medium',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  Uploading...
                </span>
                <span className={cn(
                  'text-sm font-semibold',
                  isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                )}>
                  {uploadProgress}%
                </span>
              </div>
              <div className={cn(
                'w-full rounded-full h-2 overflow-hidden',
                isDark ? 'bg-[#0D1117]' : 'bg-gray-200'
              )}>
                <div
                  className="h-full bg-gradient-to-r from-[#2E9BFF] to-[#8B5CF6] transition-all duration-300 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </motion.div>
          )}

          {/* Drag and Drop Area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={cn(
              'mb-8 border-2 border-dashed rounded-2xl p-12 transition-all',
              dragActive
                ? 'border-[#2E9BFF] bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20'
                : isDark
                ? 'border-[#2E3A5C]/50 bg-[#1A1F3A]/60 hover:border-[#2E9BFF]/50'
                : 'border-gray-300 bg-gray-50 hover:border-blue-300',
              uploadingFile && 'opacity-50 pointer-events-none'
            )}
          >
            <div className="text-center">
              <div className={cn(
                'w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center',
                dragActive
                  ? 'bg-gradient-to-br from-[#2E9BFF]/30 to-[#8B5CF6]/30 border-2 border-[#2E9BFF]/50'
                  : isDark
                  ? 'bg-[#2E9BFF]/10 border border-[#2E9BFF]/30'
                  : 'bg-blue-50 border border-blue-200'
              )}>
                <Upload className={cn(
                  'w-10 h-10',
                  dragActive ? 'text-[#2E9BFF]' : isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                )} />
              </div>
              <h3 className={cn(
                'text-xl font-bold mb-3',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {dragActive ? 'Drop your file here' : 'Drop log files here or click to browse'}
              </h3>
              <p className={cn(
                'text-base mb-6',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Supported formats: <span className={cn(
                  'font-semibold',
                  isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                )}>.log, .txt, .csv, .json</span> (Max 100MB)
              </p>
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
                  placeholder="Search files..."
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

          {/* Files Display */}
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
                  Loading files...
                </p>
              </div>
            </div>
          ) : filteredFiles.length === 0 ? (
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
                <FileText className={cn(
                  'w-10 h-10',
                  isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                )} />
              </div>
              <h3 className={cn(
                'text-xl font-bold mb-2',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {searchQuery ? 'No files found' : 'No files uploaded yet'}
              </h3>
              <p className={cn(
                'text-base mb-6 max-w-md mx-auto',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                {searchQuery 
                  ? 'Try adjusting your search criteria'
                  : 'Upload your first log file to start analyzing'
                }
              </p>
              {!searchQuery && (
                <label htmlFor="file-upload-empty">
                  <GradientButton
                    as="div"
                    className="px-6 py-3 cursor-pointer inline-flex items-center gap-2"
                  >
                    <Upload className="w-5 h-5" />
                    Upload your first file
                  </GradientButton>
                  <input
                    id="file-upload-empty"
                    type="file"
                    className="hidden"
                    onChange={handleFileSelect}
                    accept=".log,.txt,.csv,.json"
                  />
                </label>
              )}
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredFiles.map((file, index) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 + index * 0.05 }}
                  whileHover={{ y: -4 }}
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
                    <div className={cn(
                      'p-3 rounded-xl',
                      file.file_type?.includes('json')
                        ? 'bg-gradient-to-br from-[#F59E0B]/20 to-[#EF4444]/20 border border-[#F59E0B]/30'
                        : 'bg-gradient-to-br from-[#2E9BFF]/20 to-[#8B5CF6]/20 border border-[#2E9BFF]/30'
                    )}>
                      <FileText className={cn(
                        'w-6 h-6',
                        file.file_type?.includes('json') ? 'text-[#F59E0B]' : 'text-[#2E9BFF]'
                      )} />
                    </div>

                    {/* Status Icon */}
                    <div className="flex items-center gap-2">
                      {getStatusIcon(file.status || file.upload_status)}
                      <button
                        onClick={(e) => e.stopPropagation()}
                        className={cn(
                          'p-2 rounded-lg transition-all',
                          isDark ? 'hover:bg-[#2E3A5C]' : 'hover:bg-gray-100'
                        )}
                      >
                        <MoreVertical className={cn(
                          'w-5 h-5',
                          isDark ? 'text-[#94A3B8]' : 'text-gray-400'
                        )} />
                      </button>
                    </div>
                  </div>

                  {/* File Name */}
                  <h3 className={cn(
                    'text-base font-bold mb-2 truncate group-hover:text-[#2E9BFF] transition-colors',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )} title={file.original_filename || file.filename}>
                    {file.original_filename || file.filename}
                  </h3>

                  {/* File Info */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <HardDrive className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#64748B]' : 'text-gray-400'
                      )} />
                      <span className={cn(
                        'text-sm',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )}>
                        {formatFileSize(file.size || file.file_size || 0)}
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
                        {new Date(file.uploadedAt || file.created_at || file.uploaded_at || Date.now()).toLocaleDateString()}
                      </span>
                    </div>
                    {file.logCount && (
                      <div className="flex items-center gap-2">
                        <FileText className={cn(
                          'w-4 h-4',
                          isDark ? 'text-[#64748B]' : 'text-gray-400'
                        )} />
                        <span className={cn(
                          'text-sm',
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        )}>
                          {file.logCount.toLocaleString()} log entries
                        </span>
                      </div>
                    )}
                    {file.project_id && (
                      <div className="flex items-center gap-2">
                        <FolderOpen className={cn(
                          'w-4 h-4',
                          isDark ? 'text-[#64748B]' : 'text-gray-400'
                        )} />
                        <span className={cn(
                          'text-sm',
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        )}>
                          In Project
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Status Badge */}
                  <div className="flex items-center gap-2 mb-4">
                    <span className={cn(
                      'px-3 py-1 text-xs font-semibold rounded-full border',
                      getStatusColor(file.status || file.upload_status)
                    )}>
                      {getStatusText(file.status || file.upload_status)}
                    </span>
                  </div>

                  {/* Quick Actions - Appears on Hover */}
                  <div className="absolute bottom-6 right-6 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {(file.status === 'completed' || !file.status) && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          // View functionality - preserve existing behavior
                          alert(`Log file: ${file.original_filename || file.filename}\nView feature coming soon!`);
                        }}
                        className={cn(
                          'p-2 rounded-lg transition-all',
                          isDark
                            ? 'bg-[#2E3A5C] hover:bg-[#334155]'
                            : 'bg-gray-100 hover:bg-gray-200'
                        )}
                        title="View logs (Coming soon)"
                      >
                        <Eye className={cn(
                          'w-4 h-4',
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        )} />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDownloadFile(file.id, file.original_filename || file.filename || 'file', e)}
                      className={cn(
                        'p-2 rounded-lg transition-all',
                        isDark
                          ? 'bg-[#2E3A5C] hover:bg-[#334155]'
                          : 'bg-gray-100 hover:bg-gray-200'
                      )}
                      title="Download"
                    >
                      <Download className={cn(
                        'w-4 h-4',
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      )} />
                    </button>
                    <button
                      onClick={(e) => handleDeleteFile(file.id, e)}
                      className="p-2 rounded-lg bg-[#EF4444]/20 hover:bg-[#EF4444]/30 transition-all"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-[#EF4444]" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {/* Files Count */}
          {filteredFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className={cn(
                'mt-8 text-center text-sm',
                isDark ? 'text-[#64748B]' : 'text-gray-500'
              )}
            >
              Showing {filteredFiles.length} of {files.length} files
            </motion.div>
          )}
        </div>
      </motion.main>
    </div>
  );
}