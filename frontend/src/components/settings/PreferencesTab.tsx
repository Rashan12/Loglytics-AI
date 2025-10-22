"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Palette, 
  Monitor, 
  Code, 
  Calendar, 
  Shield, 
  Settings,
  Moon,
  Sun,
  Monitor as MonitorIcon
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function PreferencesTab() {
  const { addToast } = useUIStore()
  const {
    preferences,
    isLoading,
    updatePreferences
  } = useSettingsStore()

  const [settings, setSettings] = React.useState(preferences)
  const [isDirty, setIsDirty] = React.useState(false)

  React.useEffect(() => {
    setSettings(preferences)
  }, [preferences])

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setIsDirty(true)
  }

  const handleSave = async () => {
    try {
      await updatePreferences(settings)
      setIsDirty(false)
      addToast({
        title: "Preferences Updated",
        description: "Your preferences have been saved.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Update Failed",
        description: "Failed to update preferences. Please try again.",
        type: "error"
      })
    }
  }

  const themeOptions = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: MonitorIcon }
  ]

  const codeThemes = [
    'github-dark',
    'github-light',
    'monokai',
    'solarized-dark',
    'solarized-light',
    'tomorrow',
    'tomorrow-night',
    'vs-dark',
    'vs-light'
  ]

  const accentColors = [
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Purple', value: '#8b5cf6' },
    { name: 'Green', value: '#10b981' },
    { name: 'Red', value: '#ef4444' },
    { name: 'Orange', value: '#f97316' },
    { name: 'Pink', value: '#ec4899' },
    { name: 'Indigo', value: '#6366f1' },
    { name: 'Teal', value: '#14b8a6' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Preferences</h2>
        <p className="text-muted-foreground">
          Customize your application experience
        </p>
      </div>

      {/* Appearance */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Appearance
            </CardTitle>
            <CardDescription>
              Customize the look and feel of the application
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Theme</Label>
              <div className="grid grid-cols-3 gap-2">
                {themeOptions.map((theme) => {
                  const Icon = theme.icon
                  return (
                    <Button
                      key={theme.value}
                      variant={settings.theme === theme.value ? "default" : "outline"}
                      className="flex items-center gap-2"
                      onClick={() => handleSettingChange('theme', theme.value)}
                    >
                      <Icon className="h-4 w-4" />
                      {theme.label}
                    </Button>
                  )
                })}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Accent Color</Label>
              <div className="grid grid-cols-4 gap-2">
                {accentColors.map((color) => (
                  <Button
                    key={color.value}
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-2"
                    onClick={() => handleSettingChange('accent_color', color.value)}
                  >
                    <div
                      className="w-4 h-4 rounded-full border"
                      style={{ backgroundColor: color.value }}
                    />
                    {color.name}
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Font Size</Label>
                <Select
                  value={settings.font_size}
                  onValueChange={(value) => handleSettingChange('font_size', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="small">Small</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="large">Large</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Use more dense UI layout
                  </p>
                </div>
                <Switch
                  checked={settings.compact_mode}
                  onCheckedChange={(checked) => handleSettingChange('compact_mode', checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Editor */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5" />
              Editor
            </CardTitle>
            <CardDescription>
              Configure your code editor preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Code Theme</Label>
              <Select
                value={settings.code_theme}
                onValueChange={(value) => handleSettingChange('code_theme', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {codeThemes.map((theme) => (
                    <SelectItem key={theme} value={theme}>
                      {theme.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>Line Numbers</Label>
                  <p className="text-sm text-muted-foreground">
                    Show line numbers in code blocks
                  </p>
                </div>
                <Switch
                  checked={settings.line_numbers}
                  onCheckedChange={(checked) => handleSettingChange('line_numbers', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label>Word Wrap</Label>
                  <p className="text-sm text-muted-foreground">
                    Wrap long lines in code blocks
                  </p>
                </div>
                <Switch
                  checked={settings.word_wrap}
                  onCheckedChange={(checked) => handleSettingChange('word_wrap', checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Date & Time */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Date & Time
            </CardTitle>
            <CardDescription>
              Configure date and time display preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Date Format</Label>
                <Select
                  value={settings.date_format}
                  onValueChange={(value) => handleSettingChange('date_format', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                    <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                    <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Time Format</Label>
                <Select
                  value={settings.time_format}
                  onValueChange={(value) => handleSettingChange('time_format', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="12-hour">12-hour (AM/PM)</SelectItem>
                    <SelectItem value="24-hour">24-hour</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Timezone</Label>
              <Select
                value={settings.timezone}
                onValueChange={(value) => handleSettingChange('timezone', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC</SelectItem>
                  <SelectItem value="America/New_York">Eastern Time</SelectItem>
                  <SelectItem value="America/Chicago">Central Time</SelectItem>
                  <SelectItem value="America/Denver">Mountain Time</SelectItem>
                  <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                  <SelectItem value="Europe/London">London</SelectItem>
                  <SelectItem value="Europe/Paris">Paris</SelectItem>
                  <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Data & Privacy */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Data & Privacy
            </CardTitle>
            <CardDescription>
              Control how your data is used and stored
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Analytics Tracking</Label>
                <p className="text-sm text-muted-foreground">
                  Help improve the product by sharing usage analytics
                </p>
              </div>
              <Switch
                checked={settings.analytics_tracking}
                onCheckedChange={(checked) => handleSettingChange('analytics_tracking', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Error Reporting</Label>
                <p className="text-sm text-muted-foreground">
                  Send crash reports to help fix bugs
                </p>
              </div>
              <Switch
                checked={settings.error_reporting}
                onCheckedChange={(checked) => handleSettingChange('error_reporting', checked)}
              />
            </div>

            <div className="space-y-2">
              <Label>Data Retention</Label>
              <Select
                value={settings.data_retention}
                onValueChange={(value) => handleSettingChange('data_retention', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="30 days">30 days</SelectItem>
                  <SelectItem value="90 days">90 days</SelectItem>
                  <SelectItem value="1 year">1 year</SelectItem>
                  <SelectItem value="Forever">Forever</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                How long to keep your log data and analytics
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Advanced */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Advanced
            </CardTitle>
            <CardDescription>
              Advanced settings for power users
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Developer Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Show API IDs, debug info, and development tools
                </p>
              </div>
              <Switch
                checked={settings.developer_mode}
                onCheckedChange={(checked) => handleSettingChange('developer_mode', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Beta Features</Label>
                <p className="text-sm text-muted-foreground">
                  Access experimental features and early releases
                </p>
              </div>
              <Switch
                checked={settings.beta_features}
                onCheckedChange={(checked) => handleSettingChange('beta_features', checked)}
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Save Button */}
      {isDirty && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-end"
        >
          <Button onClick={handleSave} disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Changes"}
          </Button>
        </motion.div>
      )}
    </div>
  )
}
