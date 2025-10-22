'use client';

import { useState, useEffect } from 'react';
import { Upload, FileText, Trash2, Download, Eye, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface LogFile {
  id: string;
  filename: string;
  size: number;
  uploadedAt: string;
  status: 'processing' | 'completed' | 'failed';
  logCount?: number;
}

export default function LogFilesPage() {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<LogFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchLogFiles();
  }, []);

  const fetchLogFiles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/logs/files', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (error) {
      console.error('Error fetching log files:', error);
    } finally {
      setLoading(false);
    }
  };

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

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Validate file
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      alert('File size exceeds 100MB limit');
      return;
    }

    const allowedTypes = ['.log', '.txt', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      alert('Invalid file type. Please upload .log, .txt, or .csv files');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      // Simulate progress (you can implement real progress with XMLHttpRequest)
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
        },
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const data = await response.json();
        setTimeout(() => {
          setUploadProgress(0);
          setUploading(false);
          fetchLogFiles(); // Refresh file list
        }, 500);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
      setUploadProgress(0);
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/logs/files/${fileId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchLogFiles(); // Refresh list
      } else {
        alert('Failed to delete file');
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete file');
    }
  };

  const handleDownloadFile = async (fileId: string, filename: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/logs/files/${fileId}/download`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Processed';
      case 'processing':
        return 'Processing...';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/10 text-green-500 border-green-500/30';
      case 'processing':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30';
      case 'failed':
        return 'bg-red-500/10 text-red-500 border-red-500/30';
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/30';
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Log Files</h1>
          <p className="text-gray-400">Upload and manage your application log files</p>
        </div>

        {/* Upload Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-xl p-12 mb-8 transition-all ${
            dragActive 
              ? 'border-blue-600 bg-blue-600/10' 
              : 'border-[#30363D] bg-[#161B22] hover:border-blue-600/50'
          }`}
        >
          {uploading && (
            <div className="absolute inset-0 bg-[#161B22] rounded-xl flex flex-col items-center justify-center z-10">
              <div className="w-full max-w-md px-8">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white font-medium">Uploading...</span>
                  <span className="text-sm text-blue-400 font-semibold">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-[#0F1419] rounded-full h-3 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300 rounded-full"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">Please wait while we process your file</p>
              </div>
            </div>
          )}

          <div className="text-center">
            <div className="w-20 h-20 bg-blue-500/10 border border-blue-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Upload className="w-10 h-10 text-blue-500" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              {dragActive ? 'Drop your file here' : 'Drop log files here or click to browse'}
            </h3>
            <p className="text-gray-400 mb-6">
              Supported formats: <span className="text-blue-400">.log, .txt, .csv</span> (Max 100MB)
            </p>
            
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".log,.txt,.csv"
              className="hidden"
              id="file-upload"
              disabled={uploading}
            />
            <label
              htmlFor="file-upload"
              className={`inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium cursor-pointer transition-colors ${
                uploading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <Upload className="w-4 h-4" />
              {uploading ? 'Uploading...' : 'Select File'}
            </label>
          </div>
        </div>

        {/* Files List */}
        <div className="bg-[#161B22] border border-[#30363D] rounded-xl overflow-hidden">
          <div className="p-6 border-b border-[#30363D]">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Uploaded Files</h2>
                <p className="text-sm text-gray-400 mt-1">
                  {files.length} {files.length === 1 ? 'file' : 'files'} uploaded
                </p>
              </div>
            </div>
          </div>
          
          {loading ? (
            <div className="p-12 text-center">
              <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-gray-400">Loading files...</p>
            </div>
          ) : files.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">No files uploaded yet</h3>
              <p className="text-gray-400 mb-6">Upload your first log file to get started</p>
            </div>
          ) : (
            <div className="divide-y divide-[#30363D]">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="p-6 hover:bg-[#1C2128] transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <FileText className="w-6 h-6 text-blue-500" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1">
                          <h3 className="text-white font-semibold">{file.filename}</h3>
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getStatusColor(file.status)}`}>
                            {getStatusText(file.status)}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>{formatFileSize(file.size)}</span>
                          <span>•</span>
                          <span>{new Date(file.uploadedAt).toLocaleString()}</span>
                          {file.logCount && (
                            <>
                              <span>•</span>
                              <span>{file.logCount.toLocaleString()} log entries</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {file.status === 'completed' && (
                        <>
                          <button
                            onClick={() => router.push(`/dashboard/logs/${file.id}`)}
                            className="p-2 hover:bg-[#0F1419] rounded-lg text-gray-400 hover:text-blue-500 transition-colors"
                            title="View logs"
                          >
                            <Eye className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDownloadFile(file.id, file.filename)}
                            className="p-2 hover:bg-[#0F1419] rounded-lg text-gray-400 hover:text-green-500 transition-colors"
                            title="Download"
                          >
                            <Download className="w-5 h-5" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDeleteFile(file.id)}
                        className="p-2 hover:bg-[#0F1419] rounded-lg text-gray-400 hover:text-red-500 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <h4 className="text-blue-400 font-semibold mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Tips for better log analysis
          </h4>
          <ul className="text-sm text-gray-400 space-y-1">
            <li>• Upload structured log files (JSON, CSV) for better parsing</li>
            <li>• Include timestamps for time-based analysis</li>
            <li>• Larger files provide more insights but take longer to process</li>
            <li>• Use consistent log formats across your applications</li>
          </ul>
        </div>
      </div>
    </div>
  );
}