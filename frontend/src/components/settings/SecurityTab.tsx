"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Shield, 
  Monitor, 
  MapPin, 
  Clock, 
  Trash2,
  Download,
  AlertTriangle,
  CheckCircle,
  Smartphone,
  Globe
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { SessionCard } from "./SessionCard"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function SecurityTab() {
  const { addToast } = useUIStore()
  const {
    securitySettings,
    activeSessions,
    loginHistory,
    isLoading,
    updateSecuritySettings,
    revokeSession,
    revokeAllOtherSessions
  } = useSettingsStore()

  const [settings, setSettings] = React.useState(securitySettings)
  const [ipWhitelist, setIpWhitelist] = React.useState(settings.ip_whitelist.join(', '))
  const [isDirty, setIsDirty] = React.useState(false)

  React.useEffect(() => {
    setSettings(securitySettings)
    setIpWhitelist(securitySettings.ip_whitelist.join(', '))
  }, [securitySettings])

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setIsDirty(true)
  }

  const handleIpWhitelistChange = (value: string) => {
    setIpWhitelist(value)
    const ips = value.split(',').map(ip => ip.trim()).filter(ip => ip)
    setSettings(prev => ({ ...prev, ip_whitelist: ips }))
    setIsDirty(true)
  }

  const handleSave = async () => {
    try {
      await updateSecuritySettings(settings)
      setIsDirty(false)
      addToast({
        title: "Settings Updated",
        description: "Your security settings have been saved.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Update Failed",
        description: "Failed to update security settings. Please try again.",
        type: "error"
      })
    }
  }

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await revokeSession(sessionId)
      addToast({
        title: "Session Revoked",
        description: "The selected session has been revoked successfully.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Revocation Failed",
        description: "Failed to revoke session. Please try again.",
        type: "error"
      })
    }
  }

  const handleRevokeAllOtherSessions = async () => {
    try {
      await revokeAllOtherSessions()
      addToast({
        title: "Sessions Revoked",
        description: "All other sessions have been revoked successfully.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Revocation Failed",
        description: "Failed to revoke sessions. Please try again.",
        type: "error"
      })
    }
  }

  const handleExportLoginHistory = () => {
    const csvContent = [
      ['Timestamp', 'IP Address', 'Location', 'Device', 'Status'].join(','),
      ...loginHistory.map(entry => [
        entry.timestamp,
        entry.ip_address,
        entry.location,
        entry.device,
        entry.status
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `login-history-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    addToast({
      title: "Export Complete",
      description: "Login history has been exported successfully.",
      type: "success"
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Security</h2>
        <p className="text-muted-foreground">
          Manage your account security and active sessions
        </p>
      </div>

      {/* Active Sessions */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Active Sessions
                </CardTitle>
                <CardDescription>
                  Manage your active login sessions across devices
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRevokeAllOtherSessions}
                disabled={isLoading}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Revoke All Others
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {activeSessions.length > 0 ? (
              <div className="space-y-3">
                {activeSessions.map((session, index) => (
                  <SessionCard
                    key={session.id}
                    session={session}
                    onRevoke={() => handleRevokeSession(session.id)}
                    isLoading={isLoading}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <Monitor className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Active Sessions</h3>
                <p className="text-muted-foreground">
                  No active sessions found
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Login History */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Login History
                </CardTitle>
                <CardDescription>
                  Recent login attempts and activity (last 30 days)
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportLoginHistory}
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loginHistory.length > 0 ? (
              <div className="space-y-3">
                {loginHistory.slice(0, 10).map((entry, index) => (
                  <motion.div
                    key={entry.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                        {entry.status === 'success' ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{entry.device}</span>
                          <Badge variant={entry.status === 'success' ? 'default' : 'destructive'}>
                            {entry.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {entry.location}
                          </span>
                          <span className="flex items-center gap-1">
                            <Globe className="h-3 w-3" />
                            {entry.ip_address}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {formatDate(entry.timestamp)}
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No Login History</h3>
                <p className="text-muted-foreground">
                  No recent login activity found
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Security Preferences */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Security Preferences
            </CardTitle>
            <CardDescription>
              Configure additional security settings for your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium">Require 2FA</p>
                <p className="text-sm text-muted-foreground">
                  Force two-factor authentication for all logins
                </p>
              </div>
              <Switch
                checked={settings.require_2fa}
                onCheckedChange={(checked) => handleSettingChange('require_2fa', checked)}
              />
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="session-timeout">Session Timeout</Label>
              <Select
                value={settings.session_timeout}
                onValueChange={(value) => handleSettingChange('session_timeout', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15min">15 minutes</SelectItem>
                  <SelectItem value="30min">30 minutes</SelectItem>
                  <SelectItem value="1h">1 hour</SelectItem>
                  <SelectItem value="24h">24 hours</SelectItem>
                  <SelectItem value="Never">Never</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Automatically log out inactive sessions after this period
              </p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="ip-whitelist">IP Whitelist (Optional)</Label>
              <Textarea
                id="ip-whitelist"
                value={ipWhitelist}
                onChange={(e) => handleIpWhitelistChange(e.target.value)}
                placeholder="192.168.1.1, 10.0.0.1, 203.0.113.0/24"
                rows={3}
              />
              <p className="text-xs text-muted-foreground">
                Restrict access to specific IP addresses or ranges (comma-separated)
              </p>
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
