import { api } from '@/lib/api'

export interface UserProfile {
  id: string
  email: string
  full_name?: string
  bio?: string
  company?: string
  timezone: string
  language: string
  avatar_url?: string
  subscription_tier: 'free' | 'pro' | 'enterprise'
  selected_llm_model: 'local' | 'openai' | 'anthropic' | 'maverick'
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  accent_color: string
  font_size: 'small' | 'medium' | 'large'
  compact_mode: boolean
  code_theme: string
  line_numbers: boolean
  word_wrap: boolean
  date_format: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD'
  time_format: '12-hour' | '24-hour'
  timezone: string
  analytics_tracking: boolean
  error_reporting: boolean
  data_retention: '30 days' | '90 days' | '1 year' | 'Forever'
  developer_mode: boolean
  beta_features: boolean
}

export interface NotificationSettings {
  email_notifications: {
    new_alerts: boolean
    daily_summary: boolean
    weekly_reports: boolean
    product_updates: boolean
    security_alerts: boolean
  }
  in_app_notifications: {
    desktop_notifications: boolean
    sound_alerts: boolean
    alert_threshold: 'critical' | 'high+' | 'all'
  }
  slack_integration: {
    connected: boolean
    workspace_name?: string
    channel?: string
    alert_types: string[]
  }
  jira_integration: {
    connected: boolean
    instance_url?: string
    project_key?: string
    issue_type?: string
    auto_create_for: string[]
  }
}

export interface SecuritySettings {
  two_factor_enabled: boolean
  session_timeout: '15min' | '30min' | '1h' | '24h' | 'Never'
  ip_whitelist: string[]
  require_2fa: boolean
}

export interface ApiKey {
  id: string
  name: string
  key: string
  masked_key: string
  created_at: string
  last_used?: string
  expires_at?: string
  permissions: string[]
  is_active: boolean
}

export interface Subscription {
  tier: 'free' | 'pro' | 'enterprise'
  status: 'active' | 'cancelled' | 'past_due' | 'incomplete'
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  features: {
    local_llm: boolean
    cloud_llm: boolean
    max_projects: number
    storage_gb: number
    advanced_analytics: boolean
    priority_support: boolean
  }
  usage: {
    llm_tokens_used: number
    storage_used_gb: number
    api_calls: number
  }
}

export interface BillingInfo {
  payment_method: {
    type: 'card'
    last4: string
    brand: string
    expiry_month: number
    expiry_year: number
  }
  billing_address: {
    name: string
    line1: string
    line2?: string
    city: string
    state: string
    postal_code: string
    country: string
  }
  invoices: Array<{
    id: string
    date: string
    amount: number
    status: 'paid' | 'pending' | 'failed'
    download_url: string
  }>
}

export interface ActiveSession {
  id: string
  device: string
  browser: string
  ip_address: string
  location: string
  last_active: string
  is_current: boolean
}

export interface LoginHistory {
  id: string
  timestamp: string
  ip_address: string
  location: string
  device: string
  status: 'success' | 'failed'
  user_agent: string
}

export const settingsService = {
  // User Profile
  async getCurrentUser(): Promise<UserProfile> {
    const response = await api.get('/settings/me')
    return response.data
  },

  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.put('/settings/me', updates)
    return response.data
  },

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/settings/me/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Password Management
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.put('/settings/me/password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  // Two-Factor Authentication
  async enable2FA(): Promise<{ qr_code: string; backup_codes: string[] }> {
    const response = await api.post('/settings/me/2fa/enable')
    return response.data
  },

  async disable2FA(code: string): Promise<void> {
    await api.post('/settings/me/2fa/disable', { code })
  },

  // Subscription Management
  async getCurrentSubscription(): Promise<Subscription> {
    const response = await api.get('/settings/subscription/current')
    return response.data
  },

  async upgradeSubscription(tier: 'pro' | 'enterprise'): Promise<void> {
    await api.post('/settings/subscription/upgrade', { tier })
  },

  async cancelSubscription(): Promise<void> {
    await api.post('/settings/subscription/cancel')
  },

  // API Keys Management
  async getApiKeys(): Promise<{ api_keys: ApiKey[] }> {
    const response = await api.get('/settings/api-keys')
    return response.data
  },

  async createApiKey(
    name: string, 
    permissions: string[], 
    expiresAt?: string
  ): Promise<ApiKey> {
    const response = await api.post('/settings/api-keys', {
      name,
      permissions,
      expires_at: expiresAt
    })
    return response.data
  },

  async revokeApiKey(keyId: string): Promise<void> {
    await api.delete(`/settings/api-keys/${keyId}`)
  },

  // Notification Settings
  async getNotificationSettings(): Promise<NotificationSettings> {
    const response = await api.get('/settings/notifications')
    return response.data
  },

  async updateNotificationSettings(settings: Partial<NotificationSettings>): Promise<void> {
    await api.put('/settings/notifications', settings)
  },

  // Security Settings
  async getActiveSessions(): Promise<{ sessions: ActiveSession[] }> {
    const response = await api.get('/settings/security/sessions')
    return response.data
  },

  async revokeSession(sessionId: string): Promise<void> {
    await api.delete(`/settings/security/sessions/${sessionId}`)
  },

  async revokeAllOtherSessions(): Promise<void> {
    await api.delete('/settings/security/sessions')
  },

  async getLoginHistory(): Promise<{ login_history: LoginHistory[] }> {
    const response = await api.get('/settings/security/login-history')
    return response.data
  },

  // Billing Information
  async getBillingInfo(): Promise<BillingInfo> {
    const response = await api.get('/settings/billing/info')
    return response.data
  },

  async getBillingUsage(): Promise<{
    llm_tokens_used: number
    storage_used_gb: number
    api_calls: number
    current_month_charges: number
  }> {
    const response = await api.get('/settings/billing/usage')
    return response.data
  },

  // Account Management
  async deleteAccount(password: string): Promise<void> {
    await api.delete('/settings/me', { data: { password } })
  },

  async exportData(): Promise<Blob> {
    const response = await api.post('/settings/me/export', {}, {
      responseType: 'blob'
    })
    return response.data
  }
}
