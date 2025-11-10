'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Plus, 
  Activity, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Trash2,
  Copy,
  Cloud,
  Server,
  Container,
  Database,
  Radio,
  CloudOff,
  TrendingUp,
  Eye,
} from 'lucide-react';
import { useLiveLogsStore, LiveLogConnectionDetail } from '@/store/live-logs-store';
import { GradientButton } from '@/components/ui/gradient-button';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

const platformIcons = {
  aws: Cloud,
  azure: Database,
  gcp: Server,
  docker: Container,
};

const getProviderColor = (platform: string) => {
  switch (platform) {
    case 'aws':
      return {
        bg: 'bg-[#FF9900]/10',
        text: 'text-[#FF9900]',
        border: 'border-[#FF9900]/30',
      };
    case 'azure':
      return {
        bg: 'bg-[#0078D4]/10',
        text: 'text-[#0078D4]',
        border: 'border-[#0078D4]/30',
      };
    case 'gcp':
      return {
        bg: 'bg-[#EA4335]/10',
        text: 'text-[#EA4335]',
        border: 'border-[#EA4335]/30',
      };
    case 'docker':
      return {
        bg: 'bg-[#2496ED]/10',
        text: 'text-[#2496ED]',
        border: 'border-[#2496ED]/30',
      };
    default:
      return {
        bg: 'bg-[#64748B]/10',
        text: 'text-[#64748B]',
        border: 'border-[#64748B]/30',
      };
  }
};

export default function LiveLogsPage() {
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const { connections, isLoading, fetchConnections, deleteConnection } = useLiveLogsStore();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showSetupDialog, setShowSetupDialog] = useState(false);
  const [newConnection, setNewConnection] = useState<LiveLogConnectionDetail | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    fetchConnections();
  }, [fetchConnections]);

  const isDark = mounted && resolvedTheme === 'dark';

  const handleDeleteConnection = async (id: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      await deleteConnection(id);
    }
  };

  // Calculate stats
  const stats = {
    activeConnections: connections.filter(c => c.status === 'active').length,
    totalLogsReceived: connections.reduce((sum, c) => sum + c.total_logs_received, 0),
    logsPerMinute: connections.reduce((sum, c) => sum + c.logs_per_minute, 0),
  };

  return (
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
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[#10B981] to-[#00D9FF] rounded-2xl blur-lg opacity-50 animate-pulse" />
                <div className="relative p-3 bg-gradient-to-br from-[#10B981] to-[#00D9FF] rounded-2xl">
                  <Activity className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className={cn(
                  'text-3xl font-bold mb-2',
                  isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                )}>
                  Live Logs
                </h1>
                <p className={cn(
                  'text-base',
                  isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                )}>
                  Real-time log monitoring with AI analysis
                </p>
              </div>
            </div>

            {/* New Connection Button */}
            <GradientButton
              onClick={() => setShowCreateDialog(true)}
              className="flex items-center gap-2 px-6 py-3"
            >
              <Plus className="w-5 h-5" />
              New Connection
            </GradientButton>
          </div>
        </motion.div>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className={cn(
            'mb-8 text-base',
            isDark ? 'text-[#94A3B8]' : 'text-gray-600'
          )}
        >
          Connect to your cloud deployments (AWS, Azure, GCP) or Docker hosts to stream logs in real-time. 
          AI continuously monitors your logs for anomalies, errors, and patterns.
        </motion.p>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          {/* Active Connections */}
          <div className={cn(
            'p-6 rounded-xl border transition-all',
            isDark
              ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#10B981]/50'
              : 'bg-white border-gray-200 hover:border-green-300 hover:shadow-md'
          )}>
            <div className="flex items-center justify-between mb-4">
              <div className={cn(
                'p-3 rounded-xl',
                isDark
                  ? 'bg-[#10B981]/10 border border-[#10B981]/30'
                  : 'bg-green-50 border border-green-200'
              )}>
                <Radio className="w-6 h-6 text-[#10B981]" />
              </div>
              <span className="text-xs font-semibold px-3 py-1 rounded-full bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50">
                Live
              </span>
            </div>
            <div>
              <p className={cn(
                'text-sm font-medium mb-1',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Active Connections
              </p>
              <p className={cn(
                'text-3xl font-bold',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {stats.activeConnections}
              </p>
            </div>
          </div>

          {/* Total Logs Received */}
          <div className={cn(
            'p-6 rounded-xl border transition-all',
            isDark
              ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#2E9BFF]/50'
              : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-md'
          )}>
            <div className="flex items-center justify-between mb-4">
              <div className={cn(
                'p-3 rounded-xl',
                isDark
                  ? 'bg-[#2E9BFF]/10 border border-[#2E9BFF]/30'
                  : 'bg-blue-50 border border-blue-200'
              )}>
                <Database className="w-6 h-6 text-[#2E9BFF]" />
              </div>
            </div>
            <div>
              <p className={cn(
                'text-sm font-medium mb-1',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Total Logs Received
              </p>
              <p className={cn(
                'text-3xl font-bold',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {stats.totalLogsReceived.toLocaleString()}
              </p>
            </div>
          </div>

          {/* Logs per Minute */}
          <div className={cn(
            'p-6 rounded-xl border transition-all',
            isDark
              ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 hover:border-[#8B5CF6]/50'
              : 'bg-white border-gray-200 hover:border-purple-300 hover:shadow-md'
          )}>
            <div className="flex items-center justify-between mb-4">
              <div className={cn(
                'p-3 rounded-xl',
                isDark
                  ? 'bg-[#8B5CF6]/10 border border-[#8B5CF6]/30'
                  : 'bg-purple-50 border border-purple-200'
              )}>
                <TrendingUp className="w-6 h-6 text-[#8B5CF6]" />
              </div>
            </div>
            <div>
              <p className={cn(
                'text-sm font-medium mb-1',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Logs per Minute
              </p>
              <p className={cn(
                'text-3xl font-bold',
                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
              )}>
                {stats.logsPerMinute.toLocaleString()}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Connections Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-[#2E9BFF] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className={cn(
                'text-base',
                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
              )}>
                Loading connections...
              </p>
            </div>
          </div>
        ) : connections.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
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
              <CloudOff className={cn(
                'w-10 h-10',
                isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
              )} />
            </div>
            <h3 className={cn(
              'text-xl font-bold mb-2',
              isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
            )}>
              No connections yet
            </h3>
            <p className={cn(
              'text-base mb-6 max-w-md mx-auto',
              isDark ? 'text-[#94A3B8]' : 'text-gray-600'
            )}>
              Connect your first log source to start streaming logs in real-time
            </p>
            <GradientButton
              onClick={() => setShowCreateDialog(true)}
              className="px-6 py-3 inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Create your first connection
            </GradientButton>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {connections.map((connection, index) => {
              const providerColors = getProviderColor(connection.platform);
              const isActive = connection.status === 'active';
              const Icon = platformIcons[connection.platform];

              return (
                <motion.div
                  key={connection.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 + index * 0.05 }}
                  onClick={() => router.push(`/dashboard/live-logs/${connection.id}`)}
                  className={cn(
                    'group relative p-6 rounded-2xl border transition-all cursor-pointer',
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
                      'p-3 rounded-xl border',
                      providerColors.bg,
                      providerColors.border
                    )}>
                      <div className={providerColors.text}>
                        <Icon className="w-6 h-6" />
                      </div>
                    </div>

                    {/* Status Badge */}
                    <span className={cn(
                      'px-3 py-1 text-xs font-semibold rounded-full flex items-center gap-1.5',
                      isActive
                        ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50'
                        : 'bg-[#64748B]/20 text-[#64748B] border border-[#64748B]/50'
                    )}>
                      {isActive ? (
                        <>
                          <Radio className="w-3 h-3 animate-pulse" />
                          Active
                        </>
                      ) : (
                        <>
                          <CloudOff className="w-3 h-3" />
                          {connection.status}
                        </>
                      )}
                    </span>
                  </div>

                  {/* Connection Name */}
                  <h3 className={cn(
                    'text-lg font-bold mb-1 group-hover:text-[#2E9BFF] transition-colors',
                    isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                  )}>
                    {connection.name}
                  </h3>

                  {/* Provider */}
                  <p className={cn(
                    'text-sm mb-4 capitalize',
                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                  )}>
                    {connection.platform}
                  </p>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className={cn(
                      'p-3 rounded-lg',
                      isDark ? 'bg-[#0D1117]/60' : 'bg-gray-50'
                    )}>
                      <p className={cn(
                        'text-xs mb-1',
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      )}>
                        Logs/min
                      </p>
                      <p className={cn(
                        'text-lg font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {connection.logs_per_minute}
                      </p>
                    </div>

                    <div className={cn(
                      'p-3 rounded-lg',
                      isDark ? 'bg-[#0D1117]/60' : 'bg-gray-50'
                    )}>
                      <p className={cn(
                        'text-xs mb-1',
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      )}>
                        Total Logs
                      </p>
                      <p className={cn(
                        'text-lg font-bold',
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      )}>
                        {connection.total_logs_received.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Last Seen */}
                  <div className="flex items-center gap-2 mb-4">
                    <Eye className={cn(
                      'w-4 h-4',
                      isDark ? 'text-[#64748B]' : 'text-gray-400'
                    )} />
                    <p className={cn(
                      'text-xs',
                      isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                    )}>
                      Last Seen: {connection.last_seen 
                        ? new Date(connection.last_seen).toLocaleString()
                        : 'Never'}
                    </p>
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConnection(connection.id);
                    }}
                    className={cn(
                      'w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border transition-all',
                      isDark
                        ? 'bg-[#EF4444]/10 border-[#EF4444]/30 text-[#EF4444] hover:bg-[#EF4444]/20'
                        : 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100'
                    )}
                  >
                    <Trash2 className="w-4 h-4" />
                    <span className="text-sm font-medium">Delete</span>
                  </button>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Connection Count */}
        {connections.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className={cn(
              'mt-8 text-center text-sm',
              isDark ? 'text-[#64748B]' : 'text-gray-500'
            )}
          >
            Showing {connections.length} connection{connections.length !== 1 ? 's' : ''}
          </motion.div>
        )}
      </div>

      {/* Create Connection Dialog */}
      <CreateConnectionDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onSuccess={(connection) => {
          setNewConnection(connection);
          setShowCreateDialog(false);
          setShowSetupDialog(true);
        }}
      />

      {/* Setup Instructions Dialog */}
      {newConnection && (
        <SetupInstructionsDialog
          open={showSetupDialog}
          onOpenChange={setShowSetupDialog}
          connection={newConnection}
        />
      )}
    </motion.main>
  );
}

function CreateConnectionDialog({ 
  open, 
  onOpenChange, 
  onSuccess 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void;
  onSuccess: (connection: LiveLogConnectionDetail) => void;
}) {
  const { createConnection } = useLiveLogsStore();
  const [name, setName] = useState('');
  const [platform, setPlatform] = useState<'aws' | 'azure' | 'gcp' | 'docker'>('aws');
  const [isCreating, setIsCreating] = useState(false);

  const platforms = [
    { value: 'aws', label: 'AWS', icon: Cloud, color: 'from-orange-500 to-yellow-500' },
    { value: 'azure', label: 'Azure', icon: Database, color: 'from-blue-500 to-cyan-500' },
    { value: 'gcp', label: 'Google Cloud', icon: Server, color: 'from-red-500 to-yellow-500' },
    { value: 'docker', label: 'Docker', icon: Container, color: 'from-blue-600 to-blue-400' },
  ];

  const handleCreate = async () => {
    if (!name.trim()) return;
    
    setIsCreating(true);
    try {
      const connection = await createConnection(name, platform);
      onSuccess(connection);
      setName('');
      setPlatform('aws');
    } catch (error) {
      console.error('Failed to create connection:', error);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#161B22] border-[#30363D] text-white max-w-2xl" aria-describedby="create-connection-description">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Create New Connection</DialogTitle>
          <p id="create-connection-description" className="text-sm text-gray-400 mt-2">
            Create a new live log connection to start streaming logs from your infrastructure.
          </p>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Name Input */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-2 block">
              Connection Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Production AWS EKS"
              className="w-full px-4 py-3 bg-[#0D1117] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
              
          {/* Platform Selection */}
          <div>
            <label className="text-sm font-medium text-gray-300 mb-3 block">
              Select Platform
            </label>
            <div className="grid grid-cols-2 gap-4">
              {platforms.map((p) => {
                const Icon = p.icon;
                const isSelected = platform === p.value;
                return (
                  <button
                    key={p.value}
                    onClick={() => setPlatform(p.value as any)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-[#30363D] hover:border-blue-500/50'
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${p.color} flex items-center justify-center mx-auto mb-3`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-sm font-semibold text-white">{p.label}</div>
                  </button>
                );
              })}
            </div>
          </div>
                
          {/* Create Button */}
          <Button
            onClick={handleCreate}
            disabled={!name.trim() || isCreating}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 py-6 text-lg"
          >
            {isCreating ? (
              <>
                <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                Creating...
              </>
            ) : (
              <>
                <Plus className="w-5 h-5 mr-2" />
                Create Connection
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function SetupInstructionsDialog({ 
  open, 
  onOpenChange, 
  connection 
}: { 
  open: boolean; 
  onOpenChange: (open: boolean) => void;
  connection: LiveLogConnectionDetail;
}) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getInstructions = () => {
    const apiKey = connection.api_key || 'YOUR_API_KEY';
    const tenantId = connection.tenant_id;
    
    switch (connection.platform) {
      case 'docker':
        return {
          title: 'Docker Host Setup',
          steps: [
            {
              title: '1. Create Fluent Bit Config',
              description: 'Save this as /etc/fluent-bit/fluent-bit.conf',
              code: `[SERVICE]
    Flush        1
    Daemon       Off
    Log_Level    info

[INPUT]
    Name         tail
    Path         /var/lib/docker/containers/*/*.log
    Parser       docker
    Tag          docker.*

[OUTPUT]
    Name         http
    Match        *
    Host         localhost
    Port         8000
    TLS          Off
    URI          /api/v1/live-logs/ingest
    Header       Authorization Bearer ${apiKey}
    Header       X-Tenant-ID ${tenantId}
    Format       json_lines`
            },
            {
              title: '2. Run Fluent Bit Container',
              description: 'Execute this command on your Docker host',
              code: `docker run -d --name fluent-bit \\
  -v /var/lib/docker/containers:/var/lib/docker/containers:ro \\
  -v /etc/fluent-bit:/fluent-bit/etc:ro \\
  -e API_KEY="${apiKey}" \\
  -e TENANT_ID="${tenantId}" \\
  fluent/fluent-bit:2.2 \\
  /fluent-bit/bin/fluent-bit -c /fluent-bit/etc/fluent-bit.conf`
            }
          ]
        };
      
      case 'aws':
        return {
          title: 'AWS EKS Setup',
          steps: [
            {
              title: '1. Deploy DaemonSet',
              description: 'Apply this Kubernetes manifest',
              code: `kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: log-collector
---
apiVersion: v1
kind: Secret
metadata:
  name: ingest-credentials
  namespace: log-collector
stringData:
  api-key: "${apiKey}"
  tenant-id: "${tenantId}"
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: log-collector
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.2
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: ingest-credentials
              key: api-key
        - name: TENANT_ID
          valueFrom:
            secretKeyRef:
              name: ingest-credentials
              key: tenant-id
EOF`
            }
          ]
        };
      
      default:
        return {
          title: 'Setup Instructions',
          steps: [
            {
              title: 'Coming Soon',
              description: `${connection.platform.toUpperCase()} setup instructions will be available soon.`,
              code: ''
            }
          ]
        };
    }
  };

  const instructions = getInstructions();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#161B22] border-[#30363D] text-white max-w-4xl max-h-[90vh] overflow-y-auto" aria-describedby="setup-instructions-description">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-3">
            <CheckCircle className="w-7 h-7 text-green-500" />
            Connection Created Successfully!
          </DialogTitle>
          <p id="setup-instructions-description" className="text-sm text-gray-400 mt-2">
            Follow these instructions to configure your log forwarding agent and start streaming logs.
          </p>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* API Key Warning */}
          <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-semibold text-yellow-500 mb-1">Save Your API Key</div>
                <p className="text-sm text-gray-300">
                  This is the only time you'll see this API key. Save it securely.
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <code className="flex-1 bg-[#0D1117] px-4 py-2 rounded text-sm font-mono">
                    {connection.api_key}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(connection.api_key!)}
                    className="border-yellow-500/50"
                  >
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div>
            <h3 className="text-xl font-bold mb-4">{instructions.title}</h3>
            
            {instructions.steps.map((step, index) => (
              <div key={index} className="mb-6">
                <h4 className="text-lg font-semibold mb-2">{step.title}</h4>
                <p className="text-sm text-gray-400 mb-3">{step.description}</p>
                
                {step.code && (
                  <div className="relative">
                    <pre className="bg-[#0D1117] border border-[#30363D] rounded-lg p-4 overflow-x-auto text-sm">
                      <code className="text-gray-300">{step.code}</code>
                    </pre>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(step.code)}
                      className="absolute top-2 right-2"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Test Connection Button */}
          <div className="flex gap-3">
            <Button
              onClick={() => onOpenChange(false)}
              variant="outline"
              className="flex-1"
            >
              Done
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
