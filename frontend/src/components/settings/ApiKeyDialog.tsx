"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Key, Calendar, Shield } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface ApiKeyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreateKey: (keyData: {
    name: string
    permissions: string[]
    expiresAt?: string
  }) => void
}

const expirationOptions = [
  { value: "never", label: "Never expires" },
  { value: "30d", label: "30 days" },
  { value: "90d", label: "90 days" },
  { value: "1y", label: "1 year" }
]

const permissionOptions = [
  {
    value: "read",
    label: "Read",
    description: "View and read data"
  },
  {
    value: "write",
    label: "Write",
    description: "Create and modify data"
  },
  {
    value: "admin",
    label: "Admin",
    description: "Full administrative access"
  }
]

export function ApiKeyDialog({ open, onOpenChange, onCreateKey }: ApiKeyDialogProps) {
  const [formData, setFormData] = React.useState({
    name: '',
    permissions: [] as string[],
    expiresAt: 'never'
  })
  const [isSubmitting, setIsSubmitting] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.name.trim()) {
      return
    }

    setIsSubmitting(true)
    
    try {
      const expiresAt = formData.expiresAt === 'never' ? undefined : formData.expiresAt
      await onCreateKey({
        name: formData.name,
        permissions: formData.permissions,
        expiresAt
      })
      
      // Reset form
      setFormData({
        name: '',
        permissions: [],
        expiresAt: 'never'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePermissionChange = (permission: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      permissions: checked
        ? [...prev.permissions, permission]
        : prev.permissions.filter(p => p !== permission)
    }))
  }

  const isFormValid = formData.name.trim() && formData.permissions.length > 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Create API Key
          </DialogTitle>
          <DialogDescription>
            Create a new API key for programmatic access to your data
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Key Name */}
          <div className="space-y-2">
            <Label htmlFor="key-name">Key Name</Label>
            <Input
              id="key-name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g., My App Integration"
              required
            />
            <p className="text-xs text-muted-foreground">
              Choose a descriptive name to identify this key
            </p>
          </div>

          {/* Permissions */}
          <div className="space-y-3">
            <Label>Permissions</Label>
            <p className="text-xs text-muted-foreground">
              Select the permissions this API key should have
            </p>
            
            <div className="space-y-3">
              {permissionOptions.map((permission) => (
                <motion.div
                  key={permission.value}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-start space-x-3 p-3 border rounded-lg"
                >
                  <Checkbox
                    id={permission.value}
                    checked={formData.permissions.includes(permission.value)}
                    onCheckedChange={(checked) => 
                      handlePermissionChange(permission.value, checked as boolean)
                    }
                    className="mt-1"
                  />
                  <div className="space-y-1">
                    <Label
                      htmlFor={permission.value}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {permission.label}
                    </Label>
                    <p className="text-xs text-muted-foreground">
                      {permission.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Expiration */}
          <div className="space-y-2">
            <Label htmlFor="expiration">Expiration</Label>
            <Select
              value={formData.expiresAt}
              onValueChange={(value) => setFormData(prev => ({ ...prev, expiresAt: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select expiration" />
              </SelectTrigger>
              <SelectContent>
                {expirationOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Choose when this API key should expire for security
            </p>
          </div>

          {/* Security Notice */}
          <Card className="border-yellow-200 bg-yellow-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Security Notice
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <ul className="text-xs text-yellow-800 space-y-1">
                <li>• Store your API key securely and never share it publicly</li>
                <li>• Use environment variables or secure key management</li>
                <li>• Rotate your keys regularly for better security</li>
                <li>• Monitor your API usage for any suspicious activity</li>
              </ul>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isFormValid || isSubmitting}
            >
              {isSubmitting ? "Creating..." : "Create API Key"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
