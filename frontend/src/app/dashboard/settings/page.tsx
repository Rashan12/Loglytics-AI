'use client';

import { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Lock, 
  Bell, 
  CreditCard, 
  Key, 
  Trash2, 
  Save, 
  Shield, 
  Globe, 
  Palette, 
  Zap 
} from 'lucide-react';

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [settings, setSettings] = useState({
    fullName: '',
    email: '',
    bio: '',
    theme: 'dark',
    language: 'en',
    timezone: 'UTC',
    notifications: {
      email: true,
      push: true,
      errors: true,
      warnings: false,
      dailySummary: false,
      weeklyReports: true,
      productUpdates: true
    },
    security: {
      twoFactor: false,
      sessions: []
    },
    subscription: {
      plan: 'Free',
      usage: {
        projects: { used: 2, limit: 5 },
        storage: { used: 2.5, limit: 10 },
        apiCalls: { used: 1250, limit: 10000 }
      }
    }
  });

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      setSettings(prev => ({
        ...prev,
        fullName: parsedUser.full_name || '',
        email: parsedUser.email || '',
        bio: parsedUser.bio || ''
      }));
    }
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          full_name: settings.fullName,
          bio: settings.bio
        })
      });

      if (response.ok) {
        setMessage('Settings saved successfully!');
        
        // Update local storage
        const updatedUser = { ...user, full_name: settings.fullName, bio: settings.bio };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setUser(updatedUser);
        
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      setMessage('Error saving settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account settings and preferences</p>
        </div>

        {/* Settings Tabs */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-[#161B22] border border-[#30363D] rounded-lg p-1">
            {[
              { id: 'profile', label: 'Profile', icon: User },
              { id: 'security', label: 'Security', icon: Lock },
              { id: 'notifications', label: 'Notifications', icon: Bell },
              { id: 'subscription', label: 'Subscription', icon: CreditCard },
              { id: 'api', label: 'API Keys', icon: Key }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-[#1C2128]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-6">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <>
              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <User className="w-5 h-5 text-blue-500" />
                  <h2 className="text-xl font-bold text-white">Profile Information</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
                    <input
                      type="text"
                      value={settings.fullName}
                      onChange={(e) => setSettings({...settings, fullName: e.target.value})}
                      className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600 transition-colors"
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                    <input
                      type="email"
                      value={settings.email}
                      disabled
                      className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-gray-500 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Bio</label>
                    <textarea
                      value={settings.bio}
                      onChange={(e) => setSettings({...settings, bio: e.target.value})}
                      className="w-full min-h-[100px] px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600 transition-colors resize-none"
                      placeholder="Tell us about yourself..."
                    />
                  </div>
                </div>
              </div>

              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Palette className="w-5 h-5 text-purple-500" />
                  <h2 className="text-xl font-bold text-white">Preferences</h2>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-white font-medium">Theme</label>
                      <p className="text-sm text-gray-400">Choose your preferred color theme</p>
                    </div>
                    <select 
                      value={settings.theme}
                      onChange={(e) => setSettings({...settings, theme: e.target.value})}
                      className="px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="system">System</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-white font-medium">Language</label>
                      <p className="text-sm text-gray-400">Select your preferred language</p>
                    </div>
                    <select 
                      value={settings.language}
                      onChange={(e) => setSettings({...settings, language: e.target.value})}
                      className="px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600"
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-white font-medium">Timezone</label>
                      <p className="text-sm text-gray-400">Set your local timezone</p>
                    </div>
                    <select 
                      value={settings.timezone}
                      onChange={(e) => setSettings({...settings, timezone: e.target.value})}
                      className="px-3 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600"
                    >
                      <option value="UTC">UTC</option>
                      <option value="EST">EST</option>
                      <option value="PST">PST</option>
                    </select>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <>
              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Lock className="w-5 h-5 text-red-500" />
                  <h2 className="text-xl font-bold text-white">Change Password</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Current Password</label>
                    <input
                      type="password"
                      className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600 transition-colors"
                      placeholder="Enter current password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">New Password</label>
                    <input
                      type="password"
                      className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600 transition-colors"
                      placeholder="Enter new password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                    <input
                      type="password"
                      className="w-full px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white focus:outline-none focus:border-blue-600 transition-colors"
                      placeholder="Confirm new password"
                    />
                  </div>
                  <button className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium transition-colors">
                    <Lock className="w-4 h-4" />
                    Update Password
                  </button>
                </div>
              </div>

              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Shield className="w-5 h-5 text-green-500" />
                  <h2 className="text-xl font-bold text-white">Two-Factor Authentication</h2>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">2FA Status</p>
                    <p className="text-sm text-gray-400">Two-factor authentication is currently disabled</p>
                  </div>
                  <button className="flex items-center gap-2 px-4 py-2 bg-[#0F1419] border border-[#30363D] rounded-lg text-white hover:border-blue-600/50 transition-colors">
                    <Shield className="w-4 h-4" />
                    Enable 2FA
                  </button>
                </div>
              </div>

              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Globe className="w-5 h-5 text-blue-500" />
                  <h2 className="text-xl font-bold text-white">Active Sessions</h2>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-[#0F1419] border border-[#30363D] rounded-lg">
                    <div>
                      <p className="text-white font-medium">Current Session</p>
                      <p className="text-sm text-gray-400">Chrome on Windows • New York, US</p>
                    </div>
                    <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded text-xs font-semibold">Active</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-[#0F1419] border border-[#30363D] rounded-lg">
                    <div>
                      <p className="text-white font-medium">Safari on iPhone</p>
                      <p className="text-sm text-gray-400">Last active 2 hours ago • San Francisco, US</p>
                    </div>
                    <button className="px-3 py-1 bg-red-600/10 text-red-500 rounded text-xs font-semibold hover:bg-red-600/20 transition-colors">
                      Revoke
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <Bell className="w-5 h-5 text-purple-500" />
                <h2 className="text-xl font-bold text-white">Email Notifications</h2>
              </div>
              
              <div className="space-y-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-white font-medium">Error Alerts</p>
                    <p className="text-sm text-gray-400">Get notified about critical errors</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.errors}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {...settings.notifications, errors: e.target.checked}
                    })}
                    className="w-5 h-5 text-blue-600 bg-[#0F1419] border-[#30363D] rounded focus:ring-blue-600"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-white font-medium">Daily Summary</p>
                    <p className="text-sm text-gray-400">Receive a daily summary of your logs</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.dailySummary}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {...settings.notifications, dailySummary: e.target.checked}
                    })}
                    className="w-5 h-5 text-blue-600 bg-[#0F1419] border-[#30363D] rounded focus:ring-blue-600"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-white font-medium">Weekly Reports</p>
                    <p className="text-sm text-gray-400">Get weekly analytics reports</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.weeklyReports}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {...settings.notifications, weeklyReports: e.target.checked}
                    })}
                    className="w-5 h-5 text-blue-600 bg-[#0F1419] border-[#30363D] rounded focus:ring-blue-600"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-white font-medium">Product Updates</p>
                    <p className="text-sm text-gray-400">Stay informed about new features</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.notifications.productUpdates}
                    onChange={(e) => setSettings({
                      ...settings,
                      notifications: {...settings.notifications, productUpdates: e.target.checked}
                    })}
                    className="w-5 h-5 text-blue-600 bg-[#0F1419] border-[#30363D] rounded focus:ring-blue-600"
                  />
                </label>
              </div>
            </div>
          )}

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <>
              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <CreditCard className="w-5 h-5 text-green-500" />
                  <h2 className="text-xl font-bold text-white">Current Plan</h2>
                </div>
                
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-white">Free Plan</h3>
                    <p className="text-sm text-gray-400">Basic features for personal use</p>
                  </div>
                  <span className="px-3 py-1 bg-blue-500/10 text-blue-500 rounded text-sm font-semibold">Current</span>
                </div>

                <div className="mb-6">
                  <h4 className="text-white font-medium mb-3">Included Features:</h4>
                  <ul className="space-y-1 text-sm text-gray-400">
                    <li>• Up to 5 projects</li>
                    <li>• 10GB storage</li>
                    <li>• Basic analytics</li>
                    <li>• Community support</li>
                  </ul>
                </div>

                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors">
                  <Zap className="w-4 h-4" />
                  Upgrade to Pro
                </button>
              </div>

              <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <CreditCard className="w-5 h-5 text-blue-500" />
                  <h2 className="text-xl font-bold text-white">Usage</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-300">Projects</span>
                      <span className="text-white font-medium">{settings.subscription.usage.projects.used} / {settings.subscription.usage.projects.limit}</span>
                    </div>
                    <div className="h-2 bg-[#0F1419] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-600" 
                        style={{ width: `${(settings.subscription.usage.projects.used / settings.subscription.usage.projects.limit) * 100}%` }} 
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-300">Storage</span>
                      <span className="text-white font-medium">{settings.subscription.usage.storage.used} / {settings.subscription.usage.storage.limit} GB</span>
                    </div>
                    <div className="h-2 bg-[#0F1419] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-600" 
                        style={{ width: `${(settings.subscription.usage.storage.used / settings.subscription.usage.storage.limit) * 100}%` }} 
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-300">API Calls</span>
                      <span className="text-white font-medium">{settings.subscription.usage.apiCalls.used.toLocaleString()} / {settings.subscription.usage.apiCalls.limit.toLocaleString()}</span>
                    </div>
                    <div className="h-2 bg-[#0F1419] rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-600" 
                        style={{ width: `${(settings.subscription.usage.apiCalls.used / settings.subscription.usage.apiCalls.limit) * 100}%` }} 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* API Keys Tab */}
          {activeTab === 'api' && (
            <div className="bg-[#161B22] border border-[#30363D] rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <Key className="w-5 h-5 text-yellow-500" />
                  <div>
                    <h2 className="text-xl font-bold text-white">API Keys</h2>
                    <p className="text-sm text-gray-400">Manage your API keys for programmatic access</p>
                  </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors">
                  <Key className="w-4 h-4" />
                  Create New Key
                </button>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-[#0F1419] border border-[#30363D] rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <p className="text-white font-medium">Production API Key</p>
                      <span className="px-2 py-1 bg-green-500/10 text-green-500 rounded text-xs font-semibold">Active</span>
                    </div>
                    <p className="text-sm text-gray-400 font-mono">sk-...abc123</p>
                    <p className="text-xs text-gray-500 mt-1">Created on Jan 15, 2024 • Last used 2 hours ago</p>
                  </div>
                  <button className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-center justify-between p-4 bg-[#0F1419] border border-[#30363D] rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <p className="text-white font-medium">Development API Key</p>
                      <span className="px-2 py-1 bg-gray-500/10 text-gray-500 rounded text-xs font-semibold">Active</span>
                    </div>
                    <p className="text-sm text-gray-400 font-mono">sk-...def456</p>
                    <p className="text-xs text-gray-500 mt-1">Created on Jan 10, 2024 • Never used</p>
                  </div>
                  <button className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Save Button and Message */}
          {activeTab === 'profile' && (
            <>
              {message && (
                <div className={`p-4 rounded-lg ${
                  message.includes('success') 
                    ? 'bg-green-500/10 text-green-500 border border-green-500/30' 
                    : 'bg-red-500/10 text-red-500 border border-red-500/30'
                }`}>
                  {message}
                </div>
              )}

              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save Settings'}
              </button>
            </>
          )}

          {/* Danger Zone */}
          <div className="bg-[#161B22] border border-red-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-6">
              <Trash2 className="w-5 h-5 text-red-500" />
              <h2 className="text-xl font-bold text-red-500">Danger Zone</h2>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-white font-medium">Delete Account</h4>
                <p className="text-sm text-gray-400">Permanently delete your account and all data</p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium transition-colors">
                <Trash2 className="w-4 h-4" />
                Delete Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
