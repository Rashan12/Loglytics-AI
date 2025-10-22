"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Bell, 
  Mail, 
  Volume2, 
  Slack, 
  ExternalLink,
  TestTube,
  CheckCircle
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
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

export function NotificationsTab() {
  const { addToast } = useUIStore()
  const {
    notificationSettings,
    isLoading,
    updateNotificationSettings
  } = useSettingsStore()

  const [settings, setSettings] = React.useState(notificationSettings)
  const [isDirty, setIsDirty] = React.useState(false)

  React.useEffect(() => {
    setSettings(notificationSettings)
  }, [notificationSettings])

  const handleEmailNotificationChange = (key: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      email_notifications: {
        ...prev.email_notifications,
        [key]: value
      }
    }))
    setIsDirty(true)
  }

  const handleInAppNotificationChange = (key: string, value: boolean | string) => {
    setSettings(prev => ({
      ...prev,
      in_app_notifications: {
        ...prev.in_app_notifications,
        [key]: value
      }
    }))
    setIsDirty(true)
  }

  const handleSlackIntegrationChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      slack_integration: {
        ...prev.slack_integration,
        [key]: value
      }
    }))
    setIsDirty(true)
  }

  const handleJiraIntegrationChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      jira_integration: {
        ...prev.jira_integration,
        [key]: value
      }
    }))
    setIsDirty(true)
  }

  const handleSave = async () => {
    try {
      await updateNotificationSettings(settings)
      setIsDirty(false)
      addToast({
        title: "Settings Updated",
        description: "Your notification preferences have been saved.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Update Failed",
        description: "Failed to update notification settings. Please try again.",
        type: "error"
      })
    }
  }

  const handleTestNotification = async (type: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      addToast({
        title: "Test Notification Sent",
        description: `A test ${type} notification has been sent.`,
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Test Failed",
        description: `Failed to send test ${type} notification.`,
        type: "error"
      })
    }
  }

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      if (permission === 'granted') {
        addToast({
          title: "Permission Granted",
          description: "You'll now receive desktop notifications.",
          type: "success"
        })
      } else {
        addToast({
          title: "Permission Denied",
          description: "Desktop notifications are disabled.",
          type: "warning"
        })
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Notifications</h2>
        <p className="text-muted-foreground">
          Configure how and when you receive notifications
        </p>
      </div>

      {/* Email Notifications */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Email Notifications
            </CardTitle>
            <CardDescription>
              Choose which email notifications you want to receive
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              {
                key: 'new_alerts',
                label: 'New Alerts',
                description: 'Get notified when new alerts are triggered'
              },
              {
                key: 'daily_summary',
                label: 'Daily Summary',
                description: 'Receive a daily summary of your log activity'
              },
              {
                key: 'weekly_reports',
                label: 'Weekly Reports',
                description: 'Get weekly analytics reports'
              },
              {
                key: 'product_updates',
                label: 'Product Updates',
                description: 'Stay informed about new features and updates'
              },
              {
                key: 'security_alerts',
                label: 'Security Alerts',
                description: 'Critical security notifications (always enabled)'
              }
            ].map((notification) => (
              <div key={notification.key} className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="font-medium">{notification.label}</p>
                  <p className="text-sm text-muted-foreground">{notification.description}</p>
                </div>
                <Switch
                  checked={settings.email_notifications[notification.key as keyof typeof settings.email_notifications]}
                  onCheckedChange={(checked) => handleEmailNotificationChange(notification.key, checked)}
                  disabled={notification.key === 'security_alerts'}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* In-App Notifications */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              In-App Notifications
            </CardTitle>
            <CardDescription>
              Configure in-app notification preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium">Desktop Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Show browser notifications for important events
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={settings.in_app_notifications.desktop_notifications}
                  onCheckedChange={(checked) => {
                    handleInAppNotificationChange('desktop_notifications', checked)
                    if (checked) {
                      requestNotificationPermission()
                    }
                  }}
                />
                {settings.in_app_notifications.desktop_notifications && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTestNotification('desktop')}
                  >
                    <TestTube className="h-4 w-4 mr-1" />
                    Test
                  </Button>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium">Sound Alerts</p>
                <p className="text-sm text-muted-foreground">
                  Play sound for notifications
                </p>
              </div>
              <Switch
                checked={settings.in_app_notifications.sound_alerts}
                onCheckedChange={(checked) => handleInAppNotificationChange('sound_alerts', checked)}
              />
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <p className="font-medium">Alert Threshold</p>
                <p className="text-sm text-muted-foreground">
                  Only show notifications for alerts above this severity
                </p>
              </div>
              <Select
                value={settings.in_app_notifications.alert_threshold}
                onValueChange={(value) => handleInAppNotificationChange('alert_threshold', value)}
              >
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical Only</SelectItem>
                  <SelectItem value="high+">High and Critical</SelectItem>
                  <SelectItem value="all">All Alerts</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Slack Integration */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Slack className="h-5 w-5" />
              Slack Integration
            </CardTitle>
            <CardDescription>
              Send notifications to your Slack workspace
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium">Slack Workspace</p>
                <p className="text-sm text-muted-foreground">
                  {settings.slack_integration.connected 
                    ? `Connected to ${settings.slack_integration.workspace_name}`
                    : 'Not connected to Slack'
                  }
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={settings.slack_integration.connected ? "default" : "secondary"}>
                  {settings.slack_integration.connected ? "Connected" : "Not Connected"}
                </Badge>
                <Button variant="outline" size="sm">
                  {settings.slack_integration.connected ? "Disconnect" : "Connect"}
                </Button>
              </div>
            </div>

            {settings.slack_integration.connected && (
              <>
                <div className="space-y-2">
                  <Label>Channel</Label>
                  <Select
                    value={settings.slack_integration.channel || ""}
                    onValueChange={(value) => handleSlackIntegrationChange('channel', value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select channel" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="#general">#general</SelectItem>
                      <SelectItem value="#alerts">#alerts</SelectItem>
                      <SelectItem value="#devops">#devops</SelectItem>
                      <SelectItem value="#monitoring">#monitoring</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-3">
                  <Label>Alert Types to Send</Label>
                  <div className="space-y-2">
                    {[
                      { value: 'critical', label: 'Critical Alerts' },
                      { value: 'high', label: 'High Priority Alerts' },
                      { value: 'medium', label: 'Medium Priority Alerts' },
                      { value: 'low', label: 'Low Priority Alerts' }
                    ].map((alertType) => (
                      <div key={alertType.value} className="flex items-center space-x-2">
                        <Checkbox
                          id={`slack-${alertType.value}`}
                          checked={settings.slack_integration.alert_types.includes(alertType.value)}
                          onCheckedChange={(checked) => {
                            const currentTypes = settings.slack_integration.alert_types
                            const newTypes = checked
                              ? [...currentTypes, alertType.value]
                              : currentTypes.filter(type => type !== alertType.value)
                            handleSlackIntegrationChange('alert_types', newTypes)
                          }}
                        />
                        <Label htmlFor={`slack-${alertType.value}`} className="text-sm">
                          {alertType.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <Button
                  variant="outline"
                  onClick={() => handleTestNotification('Slack')}
                  className="w-full"
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  Send Test Notification
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Jira Integration */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ExternalLink className="h-5 w-5" />
              Jira Integration
            </CardTitle>
            <CardDescription>
              Automatically create Jira issues for critical alerts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium">Jira Instance</p>
                <p className="text-sm text-muted-foreground">
                  {settings.jira_integration.connected 
                    ? `Connected to ${settings.jira_integration.instance_url}`
                    : 'Not connected to Jira'
                  }
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={settings.jira_integration.connected ? "default" : "secondary"}>
                  {settings.jira_integration.connected ? "Connected" : "Not Connected"}
                </Badge>
                <Button variant="outline" size="sm">
                  {settings.jira_integration.connected ? "Disconnect" : "Connect"}
                </Button>
              </div>
            </div>

            {settings.jira_integration.connected && (
              <>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Project Key</Label>
                    <Select
                      value={settings.jira_integration.project_key || ""}
                      onValueChange={(value) => handleJiraIntegrationChange('project_key', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select project" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="PROJ">PROJ</SelectItem>
                        <SelectItem value="DEV">DEV</SelectItem>
                        <SelectItem value="OPS">OPS</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Issue Type</Label>
                    <Select
                      value={settings.jira_integration.issue_type || ""}
                      onValueChange={(value) => handleJiraIntegrationChange('issue_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select issue type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Bug">Bug</SelectItem>
                        <SelectItem value="Task">Task</SelectItem>
                        <SelectItem value="Story">Story</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>Auto-create Issues For</Label>
                  <div className="space-y-2">
                    {[
                      { value: 'critical_errors', label: 'Critical Errors' },
                      { value: 'anomalies', label: 'Anomalies' },
                      { value: 'performance_issues', label: 'Performance Issues' },
                      { value: 'security_alerts', label: 'Security Alerts' }
                    ].map((trigger) => (
                      <div key={trigger.value} className="flex items-center space-x-2">
                        <Checkbox
                          id={`jira-${trigger.value}`}
                          checked={settings.jira_integration.auto_create_for.includes(trigger.value)}
                          onCheckedChange={(checked) => {
                            const currentTriggers = settings.jira_integration.auto_create_for
                            const newTriggers = checked
                              ? [...currentTriggers, trigger.value]
                              : currentTriggers.filter(t => t !== trigger.value)
                            handleJiraIntegrationChange('auto_create_for', newTriggers)
                          }}
                        />
                        <Label htmlFor={`jira-${trigger.value}`} className="text-sm">
                          {trigger.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                <Button
                  variant="outline"
                  onClick={() => handleTestNotification('Jira')}
                  className="w-full"
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  Test Integration
                </Button>
              </>
            )}
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
