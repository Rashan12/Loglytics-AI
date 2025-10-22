'use client';

import { useState } from 'react';
import { X, Cloud, CheckCircle } from 'lucide-react';

interface CloudConnectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (provider: string, credentials: any) => void;
}

export default function CloudConnectionModal({ isOpen, onClose, onConnect }: CloudConnectionModalProps) {
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [credentials, setCredentials] = useState({
    // AWS
    awsAccessKey: '',
    awsSecretKey: '',
    awsRegion: 'us-east-1',
    awsLogGroup: '',
    
    // Azure
    azureClientId: '',
    azureClientSecret: '',
    azureTenantId: '',
    azureSubscriptionId: '',
    azureResourceGroup: '',
    azureWorkspace: '',
    
    // GCloud
    gcloudProjectId: '',
    gcloudCredentials: ''
  });

  if (!isOpen) return null;

  const handleSubmit = () => {
    onConnect(selectedProvider!, credentials);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#161B22] border border-[#30363D] rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#30363D]">
          <div>
            <h2 className="text-2xl font-bold text-white">Connect Cloud Logs</h2>
            <p className="text-sm text-gray-400 mt-1">Connect your cloud-deployed application logs</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-[#1C2128] rounded-lg transition-colors">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Provider Selection */}
        {!selectedProvider ? (
          <div className="p-6 space-y-4">
            <p className="text-sm text-gray-400 mb-4">Select your cloud provider:</p>
            
            {/* AWS */}
            <button
              onClick={() => setSelectedProvider('aws')}
              className="w-full p-6 bg-[#0F1419] border-2 border-[#30363D] rounded-xl hover:border-orange-500/50 transition-all text-left group"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                  <Cloud className="w-8 h-8 text-orange-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white group-hover:text-orange-500 transition-colors">Amazon Web Services (AWS)</h3>
                  <p className="text-sm text-gray-400 mt-1">Connect to AWS CloudWatch Logs</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">CloudWatch</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">EC2</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Lambda</span>
                  </div>
                </div>
              </div>
            </button>

            {/* Azure */}
            <button
              onClick={() => setSelectedProvider('azure')}
              className="w-full p-6 bg-[#0F1419] border-2 border-[#30363D] rounded-xl hover:border-blue-500/50 transition-all text-left group"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <Cloud className="w-8 h-8 text-blue-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white group-hover:text-blue-500 transition-colors">Microsoft Azure</h3>
                  <p className="text-sm text-gray-400 mt-1">Connect to Azure Monitor Logs</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Monitor</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">App Service</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Functions</span>
                  </div>
                </div>
              </div>
            </button>

            {/* Google Cloud */}
            <button
              onClick={() => setSelectedProvider('gcloud')}
              className="w-full p-6 bg-[#0F1419] border-2 border-[#30363D] rounded-xl hover:border-green-500/50 transition-all text-left group"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <Cloud className="w-8 h-8 text-green-500" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white group-hover:text-green-500 transition-colors">Google Cloud Platform</h3>
                  <p className="text-sm text-gray-400 mt-1">Connect to Google Cloud Logging</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Cloud Logging</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Compute Engine</span>
                    <span className="px-2 py-1 bg-gray-700/50 rounded text-xs text-gray-300">Cloud Functions</span>
                  </div>
                </div>
              </div>
            </button>
          </div>
        ) : (
          /* Credentials Form */
          <div className="p-6 space-y-6">
            <button
              onClick={() => setSelectedProvider(null)}
              className="text-sm text-blue-500 hover:text-blue-400"
            >
              ← Back to provider selection
            </button>

            {/* AWS Form */}
            {selectedProvider === 'aws' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    AWS Access Key ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.awsAccessKey}
                    onChange={(e) => setCredentials({...credentials, awsAccessKey: e.target.value})}
                    placeholder="AKIAIOSFODNN7EXAMPLE"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    AWS Secret Access Key <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    value={credentials.awsSecretKey}
                    onChange={(e) => setCredentials({...credentials, awsSecretKey: e.target.value})}
                    placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    AWS Region <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={credentials.awsRegion}
                    onChange={(e) => setCredentials({...credentials, awsRegion: e.target.value})}
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600"
                  >
                    <option value="us-east-1">US East (N. Virginia)</option>
                    <option value="us-west-2">US West (Oregon)</option>
                    <option value="eu-west-1">EU (Ireland)</option>
                    <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    CloudWatch Log Group <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.awsLogGroup}
                    onChange={(e) => setCredentials({...credentials, awsLogGroup: e.target.value})}
                    placeholder="/aws/lambda/my-function"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>
              </div>
            )}

            {/* Azure Form */}
            {selectedProvider === 'azure' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Client ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.azureClientId}
                    onChange={(e) => setCredentials({...credentials, azureClientId: e.target.value})}
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Client Secret <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    value={credentials.azureClientSecret}
                    onChange={(e) => setCredentials({...credentials, azureClientSecret: e.target.value})}
                    placeholder="Enter client secret"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Tenant ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.azureTenantId}
                    onChange={(e) => setCredentials({...credentials, azureTenantId: e.target.value})}
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Subscription ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.azureSubscriptionId}
                    onChange={(e) => setCredentials({...credentials, azureSubscriptionId: e.target.value})}
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Resource Group <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.azureResourceGroup}
                    onChange={(e) => setCredentials({...credentials, azureResourceGroup: e.target.value})}
                    placeholder="my-resource-group"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Log Analytics Workspace <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.azureWorkspace}
                    onChange={(e) => setCredentials({...credentials, azureWorkspace: e.target.value})}
                    placeholder="my-workspace"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>
              </div>
            )}

            {/* Google Cloud Form */}
            {selectedProvider === 'gcloud' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Project ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={credentials.gcloudProjectId}
                    onChange={(e) => setCredentials({...credentials, gcloudProjectId: e.target.value})}
                    placeholder="my-project-id"
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Service Account JSON <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    value={credentials.gcloudCredentials}
                    onChange={(e) => setCredentials({...credentials, gcloudCredentials: e.target.value})}
                    placeholder='{"type": "service_account", "project_id": "...", ...}'
                    rows={8}
                    className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-600 font-mono text-sm resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">Paste your service account JSON credentials</p>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-4 pt-4">
              <button
                onClick={handleSubmit}
                className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
              >
                Connect & Stream Logs
              </button>
              <button
                onClick={onClose}
                className="px-6 py-3 bg-[#0F1419] border border-[#30363D] rounded-lg text-gray-400 hover:text-white hover:border-blue-600/50 font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
