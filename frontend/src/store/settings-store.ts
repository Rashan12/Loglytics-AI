import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

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

export interface SettingsState {
  // User data
  profile: UserProfile | null
  preferences: UserPreferences
  notificationSettings: NotificationSettings
  securitySettings: SecuritySettings
  
  // Subscription and billing
  subscription: Subscription | null
  billingInfo: BillingInfo | null
  
  // API keys
  apiKeys: ApiKey[]
  
  // Security
  activeSessions: ActiveSession[]
  loginHistory: LoginHistory[]
  
  // UI state
  isLoading: boolean
  error: string | null
  lastUpdated: number | null
  
  // Actions
  setProfile: (profile: UserProfile) => void
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>
  uploadAvatar: (file: File) => Promise<void>
  
  setPreferences: (preferences: UserPreferences) => void
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>
  
  setNotificationSettings: (settings: NotificationSettings) => void
  updateNotificationSettings: (updates: Partial<NotificationSettings>) => Promise<void>
  
  setSecuritySettings: (settings: SecuritySettings) => void
  updateSecuritySettings: (updates: Partial<SecuritySettings>) => Promise<void>
  
  setSubscription: (subscription: Subscription) => void
  upgradeSubscription: (tier: 'pro' | 'enterprise') => Promise<void>
  cancelSubscription: () => Promise<void>
  
  setBillingInfo: (billing: BillingInfo) => void
  updatePaymentMethod: (paymentMethod: any) => Promise<void>
  
  setApiKeys: (keys: ApiKey[]) => void
  createApiKey: (name: string, permissions: string[], expiresAt?: string) => Promise<ApiKey>
  revokeApiKey: (keyId: string) => Promise<void>
  
  setActiveSessions: (sessions: ActiveSession[]) => void
  revokeSession: (sessionId: string) => Promise<void>
  revokeAllOtherSessions: () => Promise<void>
  
  setLoginHistory: (history: LoginHistory[]) => void
  
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
  enable2FA: () => Promise<{ qr_code: string; backup_codes: string[] }>
  disable2FA: (code: string) => Promise<void>
  
  deleteAccount: (password: string) => Promise<void>
  exportData: () => Promise<Blob>
  
  refreshData: () => Promise<void>
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

const defaultPreferences: UserPreferences = {
  theme: 'dark',
  accent_color: '#3b82f6',
  font_size: 'medium',
  compact_mode: false,
  code_theme: 'github-dark',
  line_numbers: true,
  word_wrap: true,
  date_format: 'MM/DD/YYYY',
  time_format: '24-hour',
  timezone: 'UTC',
  analytics_tracking: true,
  error_reporting: true,
  data_retention: '1 year',
  developer_mode: false,
  beta_features: false
}

const defaultNotificationSettings: NotificationSettings = {
  email_notifications: {
    new_alerts: true,
    daily_summary: false,
    weekly_reports: true,
    product_updates: true,
    security_alerts: true
  },
  in_app_notifications: {
    desktop_notifications: false,
    sound_alerts: true,
    alert_threshold: 'high+'
  },
  slack_integration: {
    connected: false,
    alert_types: []
  },
  jira_integration: {
    connected: false,
    auto_create_for: []
  }
}

const defaultSecuritySettings: SecuritySettings = {
  two_factor_enabled: false,
  session_timeout: '24h',
  ip_whitelist: [],
  require_2fa: false
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        profile: null,
        preferences: defaultPreferences,
        notificationSettings: defaultNotificationSettings,
        securitySettings: defaultSecuritySettings,
        subscription: null,
        billingInfo: null,
        apiKeys: [],
        activeSessions: [],
        loginHistory: [],
        isLoading: false,
        error: null,
        lastUpdated: null,
        
        // Actions
        setProfile: (profile) => set({ profile }),
        updateProfile: async (updates) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            const updatedProfile = await settingsService.updateProfile(updates)
            
            set({
              profile: updatedProfile,
              isLoading: false,
              lastUpdated: Date.now()
            })
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to update profile'
            })
          }
        },
        
        uploadAvatar: async (file) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            const result = await settingsService.uploadAvatar(file)
            
            set((state) => ({
              profile: state.profile ? { ...state.profile, avatar_url: result.avatar_url } : null,
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to upload avatar'
            })
          }
        },
        
        setPreferences: (preferences) => set({ preferences }),
        updatePreferences: async (updates) => {
          set({ isLoading: true, error: null })
          try {
            // API call would go here
            await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
            
            set((state) => ({
              preferences: { ...state.preferences, ...updates },
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to update preferences'
            })
          }
        },
        
        setNotificationSettings: (settings) => set({ notificationSettings: settings }),
        updateNotificationSettings: async (updates) => {
          set({ isLoading: true, error: null })
          try {
            // API call would go here
            await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
            
            set((state) => ({
              notificationSettings: { ...state.notificationSettings, ...updates },
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to update notification settings'
            })
          }
        },
        
        setSecuritySettings: (settings) => set({ securitySettings: settings }),
        updateSecuritySettings: async (updates) => {
          set({ isLoading: true, error: null })
          try {
            // API call would go here
            await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call
            
            set((state) => ({
              securitySettings: { ...state.securitySettings, ...updates },
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to update security settings'
            })
          }
        },
        
        setSubscription: (subscription) => set({ subscription }),
        upgradeSubscription: async (tier) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.upgradeSubscription(tier)
            
            set((state) => ({
              subscription: state.subscription ? { ...state.subscription, tier } : null,
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to upgrade subscription'
            })
          }
        },
        
        cancelSubscription: async () => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.cancelSubscription()
            
            set((state) => ({
              subscription: state.subscription ? { 
                ...state.subscription, 
                status: 'cancelled',
                cancel_at_period_end: true 
              } : null,
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to cancel subscription'
            })
          }
        },
        
        setBillingInfo: (billing) => set({ billingInfo: billing }),
        updatePaymentMethod: async (paymentMethod) => {
          set({ isLoading: true, error: null })
          try {
            // API call would go here
            await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
            
            set((state) => ({
              billingInfo: state.billingInfo ? { 
                ...state.billingInfo, 
                payment_method: paymentMethod 
              } : null,
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to update payment method'
            })
          }
        },
        
        setApiKeys: (keys) => set({ apiKeys: keys }),
        createApiKey: async (name, permissions, expiresAt) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            const newKey = await settingsService.createApiKey(name, permissions, expiresAt)
            
            set((state) => ({
              apiKeys: [...state.apiKeys, newKey],
              isLoading: false,
              lastUpdated: Date.now()
            }))
            
            return newKey
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to create API key'
            })
            throw error
          }
        },
        
        revokeApiKey: async (keyId) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.revokeApiKey(keyId)
            
            set((state) => ({
              apiKeys: state.apiKeys.filter(key => key.id !== keyId),
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to revoke API key'
            })
          }
        },
        
        setActiveSessions: (sessions) => set({ activeSessions: sessions }),
        revokeSession: async (sessionId) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.revokeSession(sessionId)
            
            set((state) => ({
              activeSessions: state.activeSessions.filter(session => session.id !== sessionId),
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to revoke session'
            })
          }
        },
        
        revokeAllOtherSessions: async () => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.revokeAllOtherSessions()
            
            set((state) => ({
              activeSessions: state.activeSessions.filter(session => session.is_current),
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to revoke sessions'
            })
          }
        },
        
        setLoginHistory: (history) => set({ loginHistory: history }),
        
        changePassword: async (currentPassword, newPassword) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.changePassword(currentPassword, newPassword)
            
            set({
              isLoading: false,
              lastUpdated: Date.now()
            })
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to change password'
            })
          }
        },
        
        enable2FA: async () => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            const result = await settingsService.enable2FA()
            
            set({
              isLoading: false,
              lastUpdated: Date.now()
            })
            
            return result
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to enable 2FA'
            })
            throw error
          }
        },
        
        disable2FA: async (code) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.disable2FA(code)
            
            set((state) => ({
              securitySettings: { ...state.securitySettings, two_factor_enabled: false },
              isLoading: false,
              lastUpdated: Date.now()
            }))
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to disable 2FA'
            })
          }
        },
        
        deleteAccount: async (password) => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            await settingsService.deleteAccount(password)
            
            set({
              isLoading: false,
              lastUpdated: Date.now()
            })
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to delete account'
            })
          }
        },
        
        exportData: async () => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            const blob = await settingsService.exportData()
            
            set({
              isLoading: false,
              lastUpdated: Date.now()
            })
            
            return blob
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to export data'
            })
            throw error
          }
        },
        
        refreshData: async () => {
          set({ isLoading: true, error: null })
          try {
            const { settingsService } = await import('@/services/settings-service')
            
            // Load all data in parallel
            const [
              profile,
              subscription,
              billingInfo,
              apiKeysData,
              activeSessionsData,
              loginHistoryData
            ] = await Promise.all([
              settingsService.getCurrentUser(),
              settingsService.getCurrentSubscription(),
              settingsService.getBillingInfo(),
              settingsService.getApiKeys(),
              settingsService.getActiveSessions(),
              settingsService.getLoginHistory()
            ])
            
            set({
              profile,
              subscription,
              billingInfo,
              apiKeys: apiKeysData.api_keys,
              activeSessions: activeSessionsData.sessions,
              loginHistory: loginHistoryData.login_history,
              isLoading: false,
              lastUpdated: Date.now()
            })
          } catch (error) {
            set({
              isLoading: false,
              error: error instanceof Error ? error.message : 'Failed to refresh data'
            })
          }
        },
        
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error })
      }),
      {
        name: 'settings-store',
        partialize: (state) => ({
          preferences: state.preferences,
          notificationSettings: state.notificationSettings,
          securitySettings: state.securitySettings
        })
      }
    ),
    {
      name: 'settings-store'
    }
  )
)
