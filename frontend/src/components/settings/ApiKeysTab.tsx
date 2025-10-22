"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Key, 
  Plus, 
  Copy, 
  Trash2, 
  Eye, 
  EyeOff,
  Calendar,
  Clock,
  ExternalLink,
  Check
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
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
import { ApiKeyDialog } from "./ApiKeyDialog"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function ApiKeysTab() {
  const { addToast } = useUIStore()
  const {
    apiKeys,
    isLoading,
    createApiKey,
    revokeApiKey
  } = useSettingsStore()

  const [showCreateDialog, setShowCreateDialog] = React.useState(false)
  const [showKeyDialog, setShowKeyDialog] = React.useState(false)
  const [newKey, setNewKey] = React.useState<any>(null)
  const [copiedKeys, setCopiedKeys] = React.useState<Set<string>>(new Set())

  const handleCreateKey = async (keyData: {
    name: string
    permissions: string[]
    expiresAt?: string
  }) => {
    try {
      const key = await createApiKey(keyData.name, keyData.permissions, keyData.expiresAt)
      setNewKey(key)
      setShowCreateDialog(false)
      setShowKeyDialog(true)
      addToast({
        title: "API Key Created",
        description: "Your new API key has been created successfully.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Creation Failed",
        description: "Failed to create API key. Please try again.",
        type: "error"
      })
    }
  }

  const handleCopyKey = async (key: string, keyId: string) => {
    try {
      await navigator.clipboard.writeText(key)
      setCopiedKeys(prev => new Set(prev).add(keyId))
      setTimeout(() => {
        setCopiedKeys(prev => {
          const newSet = new Set(prev)
          newSet.delete(keyId)
          return newSet
        })
      }, 2000)
      addToast({
        title: "Copied to Clipboard",
        description: "API key has been copied to your clipboard.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Copy Failed",
        description: "Failed to copy API key. Please try again.",
        type: "error"
      })
    }
  }

  const handleRevokeKey = async (keyId: string, keyName: string) => {
    try {
      await revokeApiKey(keyId)
      addToast({
        title: "API Key Revoked",
        description: `API key "${keyName}" has been revoked successfully.`,
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Revocation Failed",
        description: "Failed to revoke API key. Please try again.",
        type: "error"
      })
    }
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

  const getPermissionBadges = (permissions: string[]) => {
    const permissionColors: Record<string, string> = {
      'read': 'bg-blue-100 text-blue-800',
      'write': 'bg-green-100 text-green-800',
      'admin': 'bg-red-100 text-red-800'
    }

    return permissions.map((permission) => (
      <Badge
        key={permission}
        variant="secondary"
        className={permissionColors[permission] || 'bg-gray-100 text-gray-800'}
      >
        {permission}
      </Badge>
    ))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground">
            Manage your API access keys for programmatic access
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create API Key
        </Button>
      </div>

      {/* API Keys List */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              Your API Keys
            </CardTitle>
            <CardDescription>
              Manage and monitor your API access keys
            </CardDescription>
          </CardHeader>
          <CardContent>
            {apiKeys.length > 0 ? (
              <div className="space-y-4">
                {apiKeys.map((key, index) => (
                  <motion.div
                    key={key.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="p-4 border rounded-lg space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <h3 className="font-medium">{key.name}</h3>
                        <div className="flex items-center gap-2">
                          <code className="text-sm bg-muted px-2 py-1 rounded font-mono">
                            {key.masked_key}
                          </code>
                          <Badge variant={key.is_active ? "default" : "secondary"}>
                            {key.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCopyKey(key.key, key.id)}
                        >
                          {copiedKeys.has(key.id) ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="outline" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Revoke API Key</AlertDialogTitle>
                              <AlertDialogDescription>
                                Are you sure you want to revoke the API key "{key.name}"? 
                                This action cannot be undone and will immediately disable access for any applications using this key.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() => handleRevokeKey(key.id, key.name)}
                                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                              >
                                Revoke Key
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-3 text-sm">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <Calendar className="h-4 w-4" />
                          <span>Created</span>
                        </div>
                        <p>{formatDate(key.created_at)}</p>
                      </div>
                      
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>Last Used</span>
                        </div>
                        <p>{key.last_used ? formatDate(key.last_used) : 'Never'}</p>
                      </div>
                      
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-muted-foreground">
                          <Key className="h-4 w-4" />
                          <span>Permissions</span>
                        </div>
                        <div className="flex gap-1">
                          {getPermissionBadges(key.permissions)}
                        </div>
                      </div>
                    </div>

                    {key.expires_at && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>Expires: {formatDate(key.expires_at)}</span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                  <Key className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No API Keys</h3>
                <p className="text-muted-foreground mb-4">
                  Create your first API key to start using our API
                </p>
                <Button onClick={() => setShowCreateDialog(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create API Key
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* API Documentation */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ExternalLink className="h-5 w-5" />
              API Documentation
            </CardTitle>
            <CardDescription>
              Learn how to use our API with your keys
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="font-medium">Getting Started</h4>
                <p className="text-sm text-muted-foreground">
                  Learn the basics of using our API with authentication and common endpoints.
                </p>
                <Button variant="outline" size="sm">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Documentation
                </Button>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">API Reference</h4>
                <p className="text-sm text-muted-foreground">
                  Complete reference for all available endpoints and parameters.
                </p>
                <Button variant="outline" size="sm">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  API Reference
                </Button>
              </div>
            </div>
            
            <Separator />
            
            <div className="space-y-2">
              <h4 className="font-medium">Example Usage</h4>
              <div className="bg-muted p-4 rounded-lg">
                <pre className="text-sm overflow-x-auto">
{`curl -X GET "https://api.loglytics.ai/v1/projects" \\
  -H "Authorization: Bearer sk-...your-api-key-here" \\
  -H "Content-Type: application/json"`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Create API Key Dialog */}
      <ApiKeyDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onCreateKey={handleCreateKey}
      />

      {/* Show New Key Dialog */}
      {newKey && (
        <AlertDialog open={showKeyDialog} onOpenChange={setShowKeyDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>API Key Created</AlertDialogTitle>
              <AlertDialogDescription>
                Your new API key has been created. Please copy it now as you won't be able to see it again.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>API Key</Label>
                <div className="flex items-center gap-2">
                  <Input
                    value={newKey.key}
                    readOnly
                    className="font-mono"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyKey(newKey.key, newKey.id)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> Store this key securely. You won't be able to view it again.
                </p>
              </div>
            </div>
            <AlertDialogFooter>
              <AlertDialogAction onClick={() => setShowKeyDialog(false)}>
                I've Saved the Key
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </div>
  )
}
