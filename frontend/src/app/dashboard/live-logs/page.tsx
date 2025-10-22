'use client';

import { useState, useEffect } from 'react';
import { Activity, Pause, Play, Download, Cloud, CheckCircle, XCircle } from 'lucide-react';
import CloudConnectionModal from '@/components/CloudConnectionModal';

export default function LiveLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [connected, setConnected] = useState(false);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [cloudConnection, setCloudConnection] = useState<any>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');

  useEffect(() => {
    // Check if user has existing cloud connection
    fetchCloudConnection();
  }, []);

  useEffect(() => {
    if (cloudConnection && !isPaused) {
      connectToCloudLogs();
    }
  }, [cloudConnection, isPaused]);

  const fetchCloudConnection = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/live-logs/connection', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCloudConnection(data);
      }
    } catch (error) {
      console.error('Error fetching cloud connection:', error);
    }
  };

  const connectToCloudLogs = () => {
    setConnectionStatus('connecting');
    
    // Connect to WebSocket for live logs
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id || user.nic_number;

    if (!userId) {
      setConnectionStatus('error');
      return;
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/live-logs/${userId}`);

    ws.onopen = () => {
      console.log('Live logs connected');
      setConnected(true);
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      if (!isPaused) {
        try {
          const data = JSON.parse(event.data);
          setLogs(prev => [data, ...prev].slice(0, 200)); // Keep last 200 logs
        } catch (error) {
          console.error('Error parsing log:', error);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
      setConnectionStatus('error');
    };

    ws.onclose = () => {
      console.log('Live logs disconnected');
      setConnected(false);
      setConnectionStatus('disconnected');
    };

    return () => {
      ws.close();
    };
  };

  const handleCloudConnect = async (provider: string, credentials: any) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/live-logs/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ provider, credentials })
      });

      if (response.ok) {
        const data = await response.json();
        setCloudConnection(data);
        setShowConnectionModal(false);
        // Start streaming
        connectToCloudLogs();
      } else {
        alert('Failed to connect. Please check your credentials.');
      }
    } catch (error) {
      console.error('Connection error:', error);
      alert('Connection failed. Please try again.');
    }
  };

  const disconnectCloud = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await fetch('http://localhost:8000/api/v1/live-logs/disconnect', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setCloudConnection(null);
      setConnected(false);
      setConnectionStatus('disconnected');
      setLogs([]);
    } catch (error) {
      console.error('Disconnect error:', error);
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'ERROR': return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'WARN': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'INFO': return 'text-blue-500 bg-blue-500/10 border-blue-500/30';
      case 'DEBUG': return 'text-gray-500 bg-gray-500/10 border-gray-500/30';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/30';
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500 animate-pulse';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      default: return 'Disconnected';
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="bg-[#0F1419] border-b border-[#30363D] px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-green-500" />
            <div>
              <h1 className="text-xl font-bold text-white">Live Logs</h1>
              <p className="text-sm text-gray-400">Real-time log streaming from cloud deployments</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg">
              <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
              <span className="text-sm text-gray-400">{getStatusText()}</span>
            </div>

            {cloudConnection && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#161B22] border border-[#30363D] rounded-lg">
                <Cloud className="w-4 h-4 text-blue-500" />
                <span className="text-sm text-gray-400">{cloudConnection.provider?.toUpperCase()}</span>
              </div>
            )}

            {/* Cloud Connection Button */}
            {!cloudConnection ? (
              <button
                onClick={() => setShowConnectionModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
              >
                <Cloud className="w-4 h-4" />
                <span className="text-sm">Connect Cloud Logs</span>
              </button>
            ) : (
              <>
                {/* Pause/Resume */}
                <button
                  onClick={() => setIsPaused(!isPaused)}
                  className="flex items-center gap-2 px-4 py-2 bg-[#161B22] border border-[#30363D] rounded-lg text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors"
                >
                  {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                  <span className="text-sm font-medium">{isPaused ? 'Resume' : 'Pause'}</span>
                </button>

                {/* Disconnect */}
                <button
                  onClick={disconnectCloud}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600/10 border border-red-600/30 hover:bg-red-600/20 rounded-lg text-red-500 font-medium transition-colors"
                >
                  <XCircle className="w-4 h-4" />
                  <span className="text-sm">Disconnect</span>
                </button>

                {/* Export */}
                <button className="flex items-center gap-2 px-4 py-2 bg-[#161B22] border border-[#30363D] rounded-lg text-gray-400 hover:text-white hover:border-blue-600/50 transition-colors">
                  <Download className="w-4 h-4" />
                  <span className="text-sm">Export</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Cloud Connection Info */}
        {cloudConnection && (
          <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-blue-400">
              <CheckCircle className="w-4 h-4" />
              <span>
                Connected to <strong>{cloudConnection.provider?.toUpperCase()}</strong> - 
                {cloudConnection.region && ` Region: ${cloudConnection.region}`}
                {cloudConnection.logGroup && ` - Log Group: ${cloudConnection.logGroup}`}
                {cloudConnection.workspace && ` - Workspace: ${cloudConnection.workspace}`}
                {cloudConnection.projectId && ` - Project: ${cloudConnection.projectId}`}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Logs Display */}
      <div className="flex-1 overflow-y-auto bg-[#0A0E14] font-mono text-sm">
        {!cloudConnection ? (
          /* No Connection State */
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-2xl px-6">
              <Cloud className="w-20 h-20 text-gray-600 mx-auto mb-6" />
              <h3 className="text-2xl font-bold text-white mb-3">Connect Your Cloud Logs</h3>
              <p className="text-gray-400 mb-8">
                Stream real-time logs from your cloud-deployed applications. 
                Supports AWS CloudWatch, Azure Monitor, and Google Cloud Logging.
              </p>
              
              {/* Pro Plan Badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 rounded-lg mb-6">
                <span className="text-purple-400 font-semibold">✨ PRO FEATURE</span>
              </div>
              
              <button
                onClick={() => setShowConnectionModal(true)}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-semibold transition-colors inline-flex items-center gap-2"
              >
                <Cloud className="w-5 h-5" />
                <span>Connect Cloud Provider</span>
              </button>
              
              {/* Supported Providers */}
              <div className="mt-12 grid grid-cols-3 gap-6">
                <div className="p-4 bg-[#161B22] border border-[#30363D] rounded-lg">
                  <div className="w-12 h-12 bg-orange-500/10 border border-orange-500/30 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Cloud className="w-6 h-6 text-orange-500" />
                  </div>
                  <p className="text-sm font-semibold text-white">AWS</p>
                  <p className="text-xs text-gray-500 mt-1">CloudWatch Logs</p>
                </div>
                
                <div className="p-4 bg-[#161B22] border border-[#30363D] rounded-lg">
                  <div className="w-12 h-12 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Cloud className="w-6 h-6 text-blue-500" />
                  </div>
                  <p className="text-sm font-semibold text-white">Azure</p>
                  <p className="text-xs text-gray-500 mt-1">Monitor Logs</p>
                </div>
                
                <div className="p-4 bg-[#161B22] border border-[#30363D] rounded-lg">
                  <div className="w-12 h-12 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Cloud className="w-6 h-6 text-green-500" />
                  </div>
                  <p className="text-sm font-semibold text-white">GCloud</p>
                  <p className="text-xs text-gray-500 mt-1">Cloud Logging</p>
                </div>
              </div>
            </div>
          </div>
        ) : logs.length === 0 ? (
          /* Waiting for Logs */
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4 animate-pulse" />
              <h3 className="text-lg font-semibold text-white mb-2">Waiting for logs...</h3>
              <p className="text-gray-400">Logs will appear here in real-time as they are generated</p>
              <p className="text-sm text-gray-500 mt-2">Connected to {cloudConnection.provider?.toUpperCase()}</p>
            </div>
          </div>
        ) : (
          /* Logs List */
          <div className="p-4 space-y-1">
            {logs.map((log, index) => (
              <div
                key={`${log.timestamp}-${index}`}
                className="flex items-start gap-3 px-3 py-2 hover:bg-[#1C2128] rounded transition-colors group"
              >
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${getLogLevelColor(log.level)}`}>
                  {log.level || 'INFO'}
                </span>
                <span className="text-gray-500 w-44 flex-shrink-0">
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}
                </span>
                <span className="text-gray-300 flex-1">{log.message || log.content}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="bg-[#0F1419] border-t border-[#30363D] px-8 py-2 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center gap-6">
          <span>Total Logs: {logs.length}</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full" />
            Errors: {logs.filter(l => l.level?.toUpperCase() === 'ERROR').length}
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-yellow-500 rounded-full" />
            Warnings: {logs.filter(l => l.level?.toUpperCase() === 'WARN').length}
          </span>
        </div>
        <div className="flex items-center gap-4">
          {cloudConnection && <span>Provider: {cloudConnection.provider?.toUpperCase()}</span>}
          <span>{isPaused ? 'Paused' : 'Streaming'}</span>
          <span>Last Updated: {logs[0]?.timestamp ? new Date(logs[0].timestamp).toLocaleTimeString() : 'N/A'}</span>
        </div>
      </div>

      {/* Cloud Connection Modal */}
      <CloudConnectionModal
        isOpen={showConnectionModal}
        onClose={() => setShowConnectionModal(false)}
        onConnect={handleCloudConnect}
      />
    </div>
  );
}