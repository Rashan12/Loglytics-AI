'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Upload, ArrowLeft, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function LogUploadPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Validate file type
      const validTypes = ['.log', '.txt', '.csv'];
      const fileExt = '.' + selectedFile.name.split('.').pop();
      
      if (!validTypes.includes(fileExt.toLowerCase())) {
        setError('Invalid file type. Please upload .log, .txt, or .csv files.');
        return;
      }
      
      // Validate file size (max 100MB)
      if (selectedFile.size > 100 * 1024 * 1024) {
        setError('File too large. Maximum size is 100MB.');
        return;
      }
      
      setFile(selectedFile);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(
        `http://localhost:8000/api/v1/projects/${projectId}/logs`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      setSuccess(true);
      setTimeout(() => {
        router.push(`/dashboard/projects/${projectId}`);
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <button
        onClick={() => router.back()}
        className="mb-6 text-gray-600 hover:text-gray-900 flex items-center gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Project
      </button>

      <h1 className="text-3xl font-bold mb-8">Upload Log File</h1>

      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <input
          type="file"
          onChange={handleFileChange}
          accept=".log,.txt,.csv"
          className="hidden"
          id="file-upload"
        />
        
        <label
          htmlFor="file-upload"
          className="cursor-pointer inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="h-4 w-4 mr-2 inline" />
          Select Log File
        </label>

        {file && (
          <div className="mt-4">
            <p className="text-sm text-gray-600">Selected file:</p>
            <p className="font-semibold flex items-center justify-center gap-2">
              <FileText className="h-4 w-4" />
              {file.name}
            </p>
            <p className="text-sm text-gray-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {success && (
        <div className="mt-4 p-4 bg-green-50 text-green-600 rounded-lg flex items-center gap-2">
          <CheckCircle className="h-4 w-4" />
          Upload successful! Redirecting...
        </div>
      )}

      <Button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="mt-6 w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {uploading ? 'Uploading...' : 'Upload File'}
      </Button>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">Supported Formats</CardTitle>
          <CardDescription>File types and requirements for log uploads</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-blue-500" />
              <h3 className="font-semibold">.log files</h3>
              <p className="text-sm text-gray-600">Standard log format</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <h3 className="font-semibold">.txt files</h3>
              <p className="text-sm text-gray-600">Plain text logs</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <FileText className="h-8 w-8 mx-auto mb-2 text-purple-500" />
              <h3 className="font-semibold">.csv files</h3>
              <p className="text-sm text-gray-600">Comma-separated values</p>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Requirements:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Maximum file size: 100MB</li>
              <li>• Files are processed automatically</li>
              <li>• Processing time depends on file size</li>
              <li>• You'll be notified when processing is complete</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
