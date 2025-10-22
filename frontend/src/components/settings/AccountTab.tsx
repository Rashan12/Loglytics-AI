"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Lock, 
  Shield, 
  Key, 
  Trash2, 
  Download,
  Eye,
  EyeOff,
  AlertTriangle,
  CheckCircle,
  ExternalLink
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
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
import { PasswordStrengthMeter } from "./PasswordStrengthMeter"
import { TwoFactorSetup } from "./TwoFactorSetup"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function AccountTab() {
  const { addToast } = useUIStore()
  const {
    securitySettings,
    isLoading,
    error,
    changePassword,
    enable2FA,
    disable2FA,
    deleteAccount,
    exportData
  } = useSettingsStore()

  // Password change form
  const [passwordForm, setPasswordForm] = React.useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [showPasswords, setShowPasswords] = React.useState({
    current: false,
    new: false,
    confirm: false
  })

  // 2FA state
  const [show2FASetup, setShow2FASetup] = React.useState(false)
  const [twoFactorCode, setTwoFactorCode] = React.useState('')

  // Account deletion
  const [deletePassword, setDeletePassword] = React.useState('')
  const [showDeleteDialog, setShowDeleteDialog] = React.useState(false)

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      addToast({
        title: "Password Mismatch",
        description: "New password and confirmation do not match.",
        type: "error"
      })
      return
    }

    try {
      await changePassword(passwordForm.currentPassword, passwordForm.newPassword)
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
      addToast({
        title: "Password Changed",
        description: "Your password has been successfully updated.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Password Change Failed",
        description: "Failed to change password. Please check your current password.",
        type: "error"
      })
    }
  }

  const handleEnable2FA = async () => {
    try {
      const result = await enable2FA()
      setShow2FASetup(true)
      addToast({
        title: "2FA Setup Started",
        description: "Please scan the QR code with your authenticator app.",
        type: "info"
      })
    } catch (error) {
      addToast({
        title: "2FA Setup Failed",
        description: "Failed to enable 2FA. Please try again.",
        type: "error"
      })
    }
  }

  const handleDisable2FA = async () => {
    if (!twoFactorCode) {
      addToast({
        title: "Code Required",
        description: "Please enter your 2FA code to disable.",
        type: "error"
      })
      return
    }

    try {
      await disable2FA(twoFactorCode)
      setTwoFactorCode('')
      addToast({
        title: "2FA Disabled",
        description: "Two-factor authentication has been disabled.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "2FA Disable Failed",
        description: "Failed to disable 2FA. Please check your code.",
        type: "error"
      })
    }
  }

  const handleExportData = async () => {
    try {
      const blob = await exportData()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `loglytics-data-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      addToast({
        title: "Data Exported",
        description: "Your data has been successfully exported.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Export Failed",
        description: "Failed to export your data. Please try again.",
        type: "error"
      })
    }
  }

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      addToast({
        title: "Password Required",
        description: "Please enter your password to confirm account deletion.",
        type: "error"
      })
      return
    }

    try {
      await deleteAccount(deletePassword)
      addToast({
        title: "Account Deleted",
        description: "Your account has been permanently deleted.",
        type: "success"
      })
      // Redirect to login or home page
    } catch (error) {
      addToast({
        title: "Deletion Failed",
        description: "Failed to delete account. Please check your password.",
        type: "error"
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Account</h2>
        <p className="text-muted-foreground">
          Manage your account security and authentication settings
        </p>
      </div>

      {/* Change Password */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5" />
              Change Password
            </CardTitle>
            <CardDescription>
              Update your password to keep your account secure
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current-password">Current Password</Label>
                <div className="relative">
                  <Input
                    id="current-password"
                    type={showPasswords.current ? "text" : "password"}
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                    placeholder="Enter current password"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                  >
                    {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="new-password">New Password</Label>
                <div className="relative">
                  <Input
                    id="new-password"
                    type={showPasswords.new ? "text" : "password"}
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                    placeholder="Enter new password"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                  >
                    {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                <PasswordStrengthMeter password={passwordForm.newPassword} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password">Confirm New Password</Label>
                <div className="relative">
                  <Input
                    id="confirm-password"
                    type={showPasswords.confirm ? "text" : "password"}
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    placeholder="Confirm new password"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                  >
                    {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? "Updating..." : "Update Password"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>

      {/* Two-Factor Authentication */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Two-Factor Authentication
            </CardTitle>
            <CardDescription>
              Add an extra layer of security to your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium">2FA Status</p>
                <div className="flex items-center gap-2">
                  {securitySettings.two_factor_enabled ? (
                    <>
                      <Badge variant="default" className="flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" />
                        Enabled
                      </Badge>
                      <p className="text-xs text-muted-foreground">
                        Your account is protected with 2FA
                      </p>
                    </>
                  ) : (
                    <>
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        Disabled
                      </Badge>
                      <p className="text-xs text-muted-foreground">
                        Add an extra layer of security
                      </p>
                    </>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Switch
                  checked={securitySettings.two_factor_enabled}
                  onCheckedChange={securitySettings.two_factor_enabled ? undefined : handleEnable2FA}
                  disabled={isLoading}
                />
                <span className="text-sm text-muted-foreground">
                  {securitySettings.two_factor_enabled ? "On" : "Off"}
                </span>
              </div>
            </div>

            {securitySettings.two_factor_enabled && (
              <div className="space-y-3">
                <Separator />
                <div className="space-y-2">
                  <Label htmlFor="disable-2fa-code">Disable 2FA</Label>
                  <div className="flex gap-2">
                    <Input
                      id="disable-2fa-code"
                      value={twoFactorCode}
                      onChange={(e) => setTwoFactorCode(e.target.value)}
                      placeholder="Enter 2FA code"
                      className="flex-1"
                    />
                    <Button
                      variant="destructive"
                      onClick={handleDisable2FA}
                      disabled={isLoading || !twoFactorCode}
                    >
                      Disable
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Enter your current 2FA code to disable two-factor authentication
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Connected Accounts */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ExternalLink className="h-5 w-5" />
              Connected Accounts
            </CardTitle>
            <CardDescription>
              Manage your connected third-party accounts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { name: "Google", connected: false, description: "Sign in with Google" },
              { name: "GitHub", connected: false, description: "Connect your GitHub account" },
              { name: "Microsoft", connected: false, description: "Sign in with Microsoft" }
            ].map((account) => (
              <div key={account.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="space-y-1">
                  <p className="font-medium">{account.name}</p>
                  <p className="text-sm text-muted-foreground">{account.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={account.connected ? "default" : "secondary"}>
                    {account.connected ? "Connected" : "Not Connected"}
                  </Badge>
                  <Button variant="outline" size="sm">
                    {account.connected ? "Disconnect" : "Connect"}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* Danger Zone */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
      >
        <Card className="border-destructive/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Danger Zone
            </CardTitle>
            <CardDescription>
              Irreversible and destructive actions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 border border-destructive/20 rounded-lg">
              <div className="space-y-1">
                <p className="font-medium">Export All Data</p>
                <p className="text-sm text-muted-foreground">
                  Download a copy of all your data
                </p>
              </div>
              <Button variant="outline" onClick={handleExportData} disabled={isLoading}>
                <Download className="h-4 w-4 mr-2" />
                Export Data
              </Button>
            </div>

            <div className="flex items-center justify-between p-3 border border-destructive/20 rounded-lg">
              <div className="space-y-1">
                <p className="font-medium text-destructive">Delete Account</p>
                <p className="text-sm text-muted-foreground">
                  Permanently delete your account and all data
                </p>
              </div>
              <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Account
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Account</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete your account
                      and remove all your data from our servers.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <div className="space-y-2">
                    <Label htmlFor="delete-password">Confirm Password</Label>
                    <Input
                      id="delete-password"
                      type="password"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                      placeholder="Enter your password to confirm"
                    />
                  </div>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDeleteAccount}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      disabled={!deletePassword || isLoading}
                    >
                      Delete Account
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* 2FA Setup Modal */}
      {show2FASetup && (
        <TwoFactorSetup
          onClose={() => setShow2FASetup(false)}
          onComplete={() => {
            setShow2FASetup(false)
            addToast({
              title: "2FA Enabled",
              description: "Two-factor authentication has been successfully enabled.",
              type: "success"
            })
          }}
        />
      )}
    </div>
  )
}
