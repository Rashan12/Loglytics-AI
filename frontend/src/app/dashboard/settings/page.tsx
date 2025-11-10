'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Lock,
  Bell,
  CreditCard,
  Key,
  Save,
  Trash2,
  Shield,
  Globe,
  Palette,
  Clock,
  Check,
  AlertTriangle,
  Smartphone,
  Monitor,
  X,
  Plus,
  Copy,
  Eye,
  EyeOff,
} from 'lucide-react';
import { GradientButton } from '@/components/ui/gradient-button';
import { useUIStore } from '@/store/ui-store';
import { useTheme } from 'next-themes';
import { useAuthStore } from '@/store/auth-store';

type TabType = 'profile' | 'security' | 'notifications' | 'subscription' | 'api-keys';

export default function SettingsPage() {
  const { sidebarCollapsed } = useUIStore();
  const { resolvedTheme } = useTheme();
  const { user } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('profile');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && resolvedTheme === 'dark';

  // PRESERVE EXISTING STATE - Profile
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [bio, setBio] = useState('');
  const [theme, setTheme] = useState('dark');
  const [language, setLanguage] = useState('en');
  const [timezone, setTimezone] = useState('UTC');

  // Security
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [sessions, setSessions] = useState([
    {
      id: '1',
      device: 'Chrome on Windows',
      location: 'New York, US',
      lastActive: 'Current Session',
      isCurrent: true,
    },
    {
      id: '2',
      device: 'Safari on iPhone',
      location: 'San Francisco, US',
      lastActive: 'Last active 2 hours ago',
      isCurrent: false,
    },
  ]);

  // Notifications
  const [notifications, setNotifications] = useState({
    errorAlerts: true,
    dailySummary: false,
    weeklyReports: true,
    productUpdates: true,
  });

  // Subscription
  const [currentPlan, setCurrentPlan] = useState({
    name: 'Free Plan',
    description: 'Basic features for personal use',
    features: [
      'Up to 5 projects',
      '10GB storage',
      'Basic analytics',
      'Community support',
    ],
  });
  const [usage, setUsage] = useState({
    projects: { current: 2, max: 5 },
    storage: { current: 2.5, max: 10 },
    apiCalls: { current: 1250, max: 10000 },
  });

  // API Keys
  const [apiKeys, setApiKeys] = useState([
    {
      id: '1',
      name: 'Production API Key',
      key: 'sk-...abc123',
      status: 'Active',
      created: 'Jan 15, 2024',
      lastUsed: '2 hours ago',
    },
    {
      id: '2',
      name: 'Development API Key',
      key: 'sk-...def456',
      status: 'Active',
      created: 'Jan 10, 2024',
      lastUsed: 'Never used',
    },
  ]);

  // Load user data on mount
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setFullName(parsedUser.full_name || '');
      setEmail(parsedUser.email || '');
      setBio(parsedUser.bio || '');
    }
  }, []);

  // PRESERVE EXISTING HANDLERS
  const handleSaveProfile = async () => {
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
          full_name: fullName,
          bio: bio,
          preferences: {
            theme,
            language,
            timezone,
          },
        }),
      });

      if (response.ok) {
        setMessage('Settings saved successfully!');
        
        // Update local storage
        const updatedUser = { ...user, full_name: fullName, bio: bio };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      setMessage('Error saving settings. Please try again.');
      console.error('Failed to update profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match!');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me/password', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (response.ok) {
        setMessage('Password updated successfully!');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to change password');
      }
    } catch (error) {
      setMessage('Failed to change password. Please try again.');
      console.error('Failed to change password:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleEnable2FA = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me/2fa/enable', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setIs2FAEnabled(true);
        setMessage('2FA enabled successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to enable 2FA');
      }
    } catch (error) {
      setMessage('Failed to enable 2FA. Please try again.');
      console.error('Failed to enable 2FA:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to revoke this session?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/users/me/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSessions(sessions.filter(s => s.id !== sessionId));
        setMessage('Session revoked successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to revoke session');
      }
    } catch (error) {
      setMessage('Failed to revoke session. Please try again.');
      console.error('Failed to revoke session:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleUpdateNotifications = async () => {
    setIsSaving(true);
    setMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me/notifications', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notifications),
      });

      if (response.ok) {
        setMessage('Notification preferences updated!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to update notifications');
      }
    } catch (error) {
      setMessage('Failed to update notifications. Please try again.');
      console.error('Failed to update notifications:', error);
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCreateAPIKey = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me/api-keys', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'New API Key',
        }),
      });

      if (response.ok) {
        const newKey = await response.json();
        setApiKeys([...apiKeys, newKey]);
        setMessage('API key created successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to create API key');
      }
    } catch (error) {
      setMessage('Failed to create API key. Please try again.');
      console.error('Failed to create API key:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleDeleteAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/v1/users/me/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setApiKeys(apiKeys.filter(k => k.id !== keyId));
        setMessage('API key deleted successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        throw new Error('Failed to delete API key');
      }
    } catch (error) {
      setMessage('Failed to delete API key. Please try again.');
      console.error('Failed to delete API key:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmed = confirm(
      'Are you sure you want to delete your account? This action cannot be undone.'
    );
    if (!confirmed) return;

    const doubleConfirm = confirm(
      'This will permanently delete all your data. Are you absolutely sure?'
    );
    if (!doubleConfirm) return;

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        localStorage.clear();
        window.location.href = '/login';
      } else {
        throw new Error('Failed to delete account');
      }
    } catch (error) {
      setMessage('Failed to delete account. Please try again.');
      console.error('Failed to delete account:', error);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const tabs = [
    { id: 'profile' as TabType, label: 'Profile', icon: User },
    { id: 'security' as TabType, label: 'Security', icon: Lock },
    { id: 'notifications' as TabType, label: 'Notifications', icon: Bell },
    { id: 'subscription' as TabType, label: 'Subscription', icon: CreditCard },
    { id: 'api-keys' as TabType, label: 'API Keys', icon: Key },
  ];

  if (!mounted) {
    return null;
  }

  return (
    <motion.main
      initial={false}
      animate={{ marginLeft: sidebarCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
      className="pt-20"
    >
      <div className="px-6 pb-4 max-w-[1400px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="mb-4 pt-2"
        >
            <h1 className={`text-3xl font-bold mb-2 ${
              isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
            }`}>
              Settings
            </h1>
            <p className={`text-base ${
              isDark ? 'text-[#94A3B8]' : 'text-gray-600'
            }`}>
              Manage your account settings and preferences
            </p>
          </motion.div>

          {/* Message Display */}
          {message && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`mb-6 p-4 rounded-lg ${
                message.includes('success') || message.includes('updated') || message.includes('enabled')
                  ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30'
                  : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30'
              }`}
            >
              {message}
            </motion.div>
          )}

          {/* Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className={`mb-8 border-b ${
              isDark ? 'border-[#2E3A5C]/50' : 'border-gray-200'
            }`}
          >
            <div className="flex gap-2 overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 px-6 py-3 border-b-2 transition-all whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'border-[#2E9BFF] text-[#2E9BFF]'
                        : isDark
                        ? 'border-transparent text-[#94A3B8] hover:text-[#F9FAFB]'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </motion.div>

          {/* Tab Content */}
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* PROFILE TAB */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                {/* Profile Information */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <User className={`w-5 h-5 ${
                      isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Profile Information
                    </h2>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className={`w-full px-4 py-3 rounded-lg border transition-all ${
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] focus:border-[#2E9BFF]'
                            : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'
                        } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        placeholder="Enter your full name"
                      />
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Email Address
                      </label>
                      <input
                        type="email"
                        value={email}
                        disabled
                        className={`w-full px-4 py-3 rounded-lg border transition-all ${
                          isDark
                            ? 'bg-[#0D1117]/30 border-[#2E3A5C]/30 text-[#64748B]'
                            : 'bg-gray-50 border-gray-200 text-gray-500'
                        } cursor-not-allowed`}
                      />
                      <p className={`text-xs mt-1 ${
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      }`}>
                        Email cannot be changed
                      </p>
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Bio
                      </label>
                      <textarea
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        placeholder="Tell us about yourself..."
                        rows={4}
                        className={`w-full px-4 py-3 rounded-lg border transition-all resize-none ${
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                            : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                        } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                      />
                    </div>
                  </div>
                </div>

                {/* Preferences */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <Palette className={`w-5 h-5 ${
                      isDark ? 'text-[#8B5CF6]' : 'text-purple-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Preferences
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Theme
                      </label>
                      <div className="relative">
                        <Palette className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${
                          isDark ? 'text-[#64748B]' : 'text-gray-400'
                        }`} />
                        <select
                          value={theme}
                          onChange={(e) => setTheme(e.target.value)}
                          className={`w-full pl-10 pr-4 py-3 rounded-lg border transition-all appearance-none ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        >
                          <option value="light">Light</option>
                          <option value="dark">Dark</option>
                          <option value="system">System</option>
                        </select>
                      </div>
                      <p className={`text-xs mt-1 ${
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      }`}>
                        Choose your preferred color theme
                      </p>
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Language
                      </label>
                      <div className="relative">
                        <Globe className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${
                          isDark ? 'text-[#64748B]' : 'text-gray-400'
                        }`} />
                        <select
                          value={language}
                          onChange={(e) => setLanguage(e.target.value)}
                          className={`w-full pl-10 pr-4 py-3 rounded-lg border transition-all appearance-none ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        >
                          <option value="en">English</option>
                          <option value="es">Spanish</option>
                          <option value="fr">French</option>
                          <option value="de">German</option>
                        </select>
                      </div>
                      <p className={`text-xs mt-1 ${
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      }`}>
                        Select your preferred language
                      </p>
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Timezone
                      </label>
                      <div className="relative">
                        <Clock className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${
                          isDark ? 'text-[#64748B]' : 'text-gray-400'
                        }`} />
                        <select
                          value={timezone}
                          onChange={(e) => setTimezone(e.target.value)}
                          className={`w-full pl-10 pr-4 py-3 rounded-lg border transition-all appearance-none ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        >
                          <option value="UTC">UTC</option>
                          <option value="EST">EST</option>
                          <option value="PST">PST</option>
                          <option value="CST">CST</option>
                        </select>
                      </div>
                      <p className={`text-xs mt-1 ${
                        isDark ? 'text-[#64748B]' : 'text-gray-500'
                      }`}>
                        Set your local timezone
                      </p>
                    </div>
                  </div>

                  <div className="mt-6">
                    <GradientButton
                      onClick={handleSaveProfile}
                      disabled={isSaving}
                      isLoading={isSaving}
                      className="px-6 py-3"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Save Settings
                    </GradientButton>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#EF4444]/5 border-[#EF4444]/30'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
                    <h2 className="text-xl font-bold text-[#EF4444]">
                      Danger Zone
                    </h2>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Delete Account
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <button
                      onClick={handleDeleteAccount}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* SECURITY TAB */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                {/* Change Password */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <Lock className={`w-5 h-5 ${
                      isDark ? 'text-[#EF4444]' : 'text-red-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Change Password
                    </h2>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Current Password
                      </label>
                      <div className="relative">
                        <input
                          type={showCurrentPassword ? 'text' : 'password'}
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                          placeholder="Enter current password"
                          className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        />
                        <button
                          type="button"
                          onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                          className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                            isDark ? 'text-[#64748B] hover:text-[#F9FAFB]' : 'text-gray-400 hover:text-gray-600'
                          }`}
                        >
                          {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        New Password
                      </label>
                      <div className="relative">
                        <input
                          type={showNewPassword ? 'text' : 'password'}
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Enter new password"
                          className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        />
                        <button
                          type="button"
                          onClick={() => setShowNewPassword(!showNewPassword)}
                          className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                            isDark ? 'text-[#64748B] hover:text-[#F9FAFB]' : 'text-gray-400 hover:text-gray-600'
                          }`}
                        >
                          {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className={`block text-sm font-medium mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Confirm Password
                      </label>
                      <div className="relative">
                        <input
                          type={showConfirmPassword ? 'text' : 'password'}
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Confirm new password"
                          className={`w-full px-4 py-3 pr-12 rounded-lg border transition-all ${
                            isDark
                              ? 'bg-[#0D1117]/60 border-[#2E3A5C]/50 text-[#F9FAFB] placeholder-[#64748B] focus:border-[#2E9BFF]'
                              : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400 focus:border-blue-500'
                          } focus:outline-none focus:ring-2 focus:ring-[#2E9BFF]/20`}
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className={`absolute right-3 top-1/2 -translate-y-1/2 ${
                            isDark ? 'text-[#64748B] hover:text-[#F9FAFB]' : 'text-gray-400 hover:text-gray-600'
                          }`}
                        >
                          {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={handleChangePassword}
                      className="flex items-center gap-2 px-6 py-3 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Lock className="w-4 h-4" />
                      Update Password
                    </button>
                  </div>
                </div>

                {/* Two-Factor Authentication */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <Shield className={`w-5 h-5 ${
                      isDark ? 'text-[#10B981]' : 'text-green-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Two-Factor Authentication
                    </h2>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        2FA Status
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Two-factor authentication is currently {is2FAEnabled ? 'enabled' : 'disabled'}
                      </p>
                    </div>
                    <button
                      onClick={handleEnable2FA}
                      disabled={is2FAEnabled}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                        is2FAEnabled
                          ? isDark
                            ? 'bg-[#10B981]/20 border-[#10B981]/50 text-[#10B981] cursor-not-allowed'
                            : 'bg-green-50 border-green-200 text-green-600 cursor-not-allowed'
                          : isDark
                          ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50 text-[#F9FAFB] hover:border-[#2E9BFF]/50'
                          : 'bg-white border-gray-200 text-gray-900 hover:border-blue-300'
                      }`}
                    >
                      <Shield className="w-4 h-4" />
                      {is2FAEnabled ? 'Enabled' : 'Enable 2FA'}
                    </button>
                  </div>
                </div>

                {/* Active Sessions */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <Globe className={`w-5 h-5 ${
                      isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Active Sessions
                    </h2>
                  </div>

                  <div className="space-y-3">
                    {sessions.map((session) => (
                      <div
                        key={session.id}
                        className={`p-4 rounded-lg border ${
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/30'
                            : 'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {session.device.includes('iPhone') ? (
                              <Smartphone className={`w-5 h-5 ${
                                isDark ? 'text-[#64748B]' : 'text-gray-400'
                              }`} />
                            ) : (
                              <Monitor className={`w-5 h-5 ${
                                isDark ? 'text-[#64748B]' : 'text-gray-400'
                              }`} />
                            )}
                            <div>
                              <h3 className={`text-sm font-semibold ${
                                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                              }`}>
                                {session.isCurrent ? 'Current Session' : session.device}
                              </h3>
                              <p className={`text-xs ${
                                isDark ? 'text-[#64748B]' : 'text-gray-500'
                              }`}>
                                {session.device} • {session.location}
                              </p>
                              <p className={`text-xs ${
                                isDark ? 'text-[#64748B]' : 'text-gray-500'
                              }`}>
                                {session.lastActive}
                              </p>
                            </div>
                          </div>

                          {session.isCurrent ? (
                            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50">
                              Active
                            </span>
                          ) : (
                            <button
                              onClick={() => handleRevokeSession(session.id)}
                              className="px-3 py-1 text-xs font-semibold rounded-lg text-[#EF4444] hover:bg-[#EF4444]/10 transition-colors"
                            >
                              Revoke
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Danger Zone */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#EF4444]/5 border-[#EF4444]/30'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
                    <h2 className="text-xl font-bold text-[#EF4444]">
                      Danger Zone
                    </h2>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Delete Account
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <button
                      onClick={handleDeleteAccount}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* NOTIFICATIONS TAB */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                {/* Email Notifications */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <Bell className={`w-5 h-5 ${
                      isDark ? 'text-[#8B5CF6]' : 'text-purple-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Email Notifications
                    </h2>
                  </div>

                  <div className="space-y-4">
                    {[
                      { key: 'errorAlerts', label: 'Error Alerts', description: 'Get notified about critical errors' },
                      { key: 'dailySummary', label: 'Daily Summary', description: 'Receive a daily summary of your logs' },
                      { key: 'weeklyReports', label: 'Weekly Reports', description: 'Get weekly analytics reports' },
                      { key: 'productUpdates', label: 'Product Updates', description: 'Stay informed about new features' },
                    ].map((item) => (
                      <div
                        key={item.key}
                        className="flex items-center justify-between"
                      >
                        <div>
                          <h3 className={`text-base font-semibold ${
                            isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                          }`}>
                            {item.label}
                          </h3>
                          <p className={`text-sm ${
                            isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                          }`}>
                            {item.description}
                          </p>
                        </div>
                        <button
                          onClick={() =>
                            setNotifications({
                              ...notifications,
                              [item.key]: !notifications[item.key as keyof typeof notifications],
                            })
                          }
                          className={`relative w-12 h-6 rounded-full transition-colors ${
                            notifications[item.key as keyof typeof notifications]
                              ? 'bg-[#2E9BFF]'
                              : isDark
                              ? 'bg-[#2E3A5C]'
                              : 'bg-gray-300'
                          }`}
                        >
                          <div
                            className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
                              notifications[item.key as keyof typeof notifications]
                                ? 'translate-x-6'
                                : 'translate-x-0'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6">
                    <GradientButton
                      onClick={handleUpdateNotifications}
                      disabled={isSaving}
                      isLoading={isSaving}
                      className="px-6 py-3"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      Save Preferences
                    </GradientButton>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#EF4444]/5 border-[#EF4444]/30'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
                    <h2 className="text-xl font-bold text-[#EF4444]">
                      Danger Zone
                    </h2>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Delete Account
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <button
                      onClick={handleDeleteAccount}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* SUBSCRIPTION TAB */}
            {activeTab === 'subscription' && (
              <div className="space-y-6">
                {/* Current Plan */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <CreditCard className={`w-5 h-5 ${
                      isDark ? 'text-[#10B981]' : 'text-green-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Current Plan
                    </h2>
                  </div>

                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className={`text-2xl font-bold mb-2 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        {currentPlan.name}
                      </h3>
                      <p className={`text-base mb-4 ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        {currentPlan.description}
                      </p>
                      <div className="space-y-2">
                        <p className={`text-sm font-semibold ${
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        }`}>
                          Included Features:
                        </p>
                        <ul className="space-y-1">
                          {currentPlan.features.map((feature, index) => (
                            <li
                              key={index}
                              className={`text-sm flex items-center gap-2 ${
                                isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                              }`}
                            >
                              <Check className="w-4 h-4 text-[#10B981]" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <span className="px-3 py-1 text-xs font-semibold rounded-full bg-[#2E9BFF]/20 text-[#2E9BFF] border border-[#2E9BFF]/50">
                      Current
                    </span>
                  </div>

                  <GradientButton
                    className="w-full py-3"
                  >
                    <CreditCard className="w-4 h-4 mr-2" />
                    Upgrade to Pro
                  </GradientButton>
                </div>

                {/* Usage */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center gap-3 mb-6">
                    <CreditCard className={`w-5 h-5 ${
                      isDark ? 'text-[#2E9BFF]' : 'text-blue-600'
                    }`} />
                    <h2 className={`text-xl font-bold ${
                      isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                    }`}>
                      Usage
                    </h2>
                  </div>

                  <div className="space-y-6">
                    {/* Projects */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className={`text-sm font-medium ${
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        }`}>
                          Projects
                        </p>
                        <p className={`text-sm ${
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        }`}>
                          {usage.projects.current} / {usage.projects.max}
                        </p>
                      </div>
                      <div className={`w-full h-2 rounded-full ${
                        isDark ? 'bg-[#2E3A5C]' : 'bg-gray-200'
                      }`}>
                        <div
                          className="h-full rounded-full bg-[#2E9BFF]"
                          style={{ width: `${(usage.projects.current / usage.projects.max) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Storage */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className={`text-sm font-medium ${
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        }`}>
                          Storage
                        </p>
                        <p className={`text-sm ${
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        }`}>
                          {usage.storage.current} / {usage.storage.max} GB
                        </p>
                      </div>
                      <div className={`w-full h-2 rounded-full ${
                        isDark ? 'bg-[#2E3A5C]' : 'bg-gray-200'
                      }`}>
                        <div
                          className="h-full rounded-full bg-[#2E9BFF]"
                          style={{ width: `${(usage.storage.current / usage.storage.max) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* API Calls */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <p className={`text-sm font-medium ${
                          isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                        }`}>
                          API Calls
                        </p>
                        <p className={`text-sm ${
                          isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                        }`}>
                          {usage.apiCalls.current.toLocaleString()} / {usage.apiCalls.max.toLocaleString()}
                        </p>
                      </div>
                      <div className={`w-full h-2 rounded-full ${
                        isDark ? 'bg-[#2E3A5C]' : 'bg-gray-200'
                      }`}>
                        <div
                          className="h-full rounded-full bg-[#2E9BFF]"
                          style={{ width: `${(usage.apiCalls.current / usage.apiCalls.max) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#EF4444]/5 border-[#EF4444]/30'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
                    <h2 className="text-xl font-bold text-[#EF4444]">
                      Danger Zone
                    </h2>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Delete Account
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <button
                      onClick={handleDeleteAccount}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* API KEYS TAB */}
            {activeTab === 'api-keys' && (
              <div className="space-y-6">
                {/* API Keys */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#1A1F3A]/60 border-[#2E3A5C]/50'
                    : 'bg-white border-gray-200'
                }`}>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <Key className={`w-5 h-5 ${
                        isDark ? 'text-[#F59E0B]' : 'text-amber-600'
                      }`} />
                      <h2 className={`text-xl font-bold ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        API Keys
                      </h2>
                    </div>
                    <GradientButton
                      onClick={handleCreateAPIKey}
                      className="px-4 py-2"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create New Key
                    </GradientButton>
                  </div>

                  <p className={`text-sm mb-6 ${
                    isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                  }`}>
                    Manage your API keys for programmatic access
                  </p>

                  <div className="space-y-3">
                    {apiKeys.map((apiKey) => (
                      <div
                        key={apiKey.id}
                        className={`p-4 rounded-lg border ${
                          isDark
                            ? 'bg-[#0D1117]/60 border-[#2E3A5C]/30'
                            : 'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Key className={`w-5 h-5 ${
                              isDark ? 'text-[#F59E0B]' : 'text-amber-600'
                            }`} />
                            <div>
                              <h3 className={`text-base font-semibold ${
                                isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                              }`}>
                                {apiKey.name}
                              </h3>
                              <p className={`text-xs ${
                                isDark ? 'text-[#64748B]' : 'text-gray-500'
                              }`}>
                                {apiKey.key}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/50">
                              {apiKey.status}
                            </span>
                            <button
                              onClick={() => navigator.clipboard.writeText(apiKey.key)}
                              className={`p-2 rounded-lg transition-colors ${
                                isDark
                                  ? 'hover:bg-[#2E3A5C] text-[#94A3B8]'
                                  : 'hover:bg-gray-200 text-gray-600'
                              }`}
                              title="Copy"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteAPIKey(apiKey.id)}
                              className="p-2 rounded-lg hover:bg-[#EF4444]/10 text-[#EF4444] transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-xs">
                          <span className={isDark ? 'text-[#64748B]' : 'text-gray-500'}>
                            Created on {apiKey.created}
                          </span>
                          <span className={isDark ? 'text-[#64748B]' : 'text-gray-500'}>
                            • Last used {apiKey.lastUsed}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Danger Zone */}
                <div className={`p-6 rounded-xl border ${
                  isDark
                    ? 'bg-[#EF4444]/5 border-[#EF4444]/30'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#EF4444]" />
                    <h2 className="text-xl font-bold text-[#EF4444]">
                      Danger Zone
                    </h2>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className={`text-base font-semibold mb-1 ${
                        isDark ? 'text-[#F9FAFB]' : 'text-gray-900'
                      }`}>
                        Delete Account
                      </h3>
                      <p className={`text-sm ${
                        isDark ? 'text-[#94A3B8]' : 'text-gray-600'
                      }`}>
                        Permanently delete your account and all data
                      </p>
                    </div>
                    <button
                      onClick={handleDeleteAccount}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </motion.main>
  );
}
