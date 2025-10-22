"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  X, 
  ChevronLeft, 
  ChevronRight, 
  Check, 
  AlertCircle,
  Loader2,
  Upload,
  Eye,
  EyeOff
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface NewConnectionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConnectionCreated: (connection: any) => void
}

interface ConnectionConfig {
  name: string
  provider: 'aws' | 'azure' | 'gcp'
  region?: string
  accessKeyId?: string
  secretKey?: string
  logGroup?: string
  logStream?: string
  subscriptionId?: string
  resourceGroup?: string
  workspaceId?: string
  clientId?: string
  clientSecret?: string
  projectId?: string
  serviceAccountJson?: string
  logName?: string
}

const steps = [
  { id: 1, title: "Choose Provider", description: "Select your cloud provider" },
  { id: 2, title: "Connection Details", description: "Configure connection settings" },
  { id: 3, title: "Test Connection", description: "Verify your configuration" },
  { id: 4, title: "Configure Filters", description: "Set up log filters (optional)" }
]

const providers = [
  {
    id: 'aws',
    name: 'Amazon Web Services',
    icon: '🟠',
    description: 'Connect to AWS CloudWatch Logs'
  },
  {
    id: 'azure',
    name: 'Microsoft Azure',
    icon: '🔵',
    description: 'Connect to Azure Monitor Logs'
  },
  {
    id: 'gcp',
    name: 'Google Cloud Platform',
    icon: '🟢',
    description: 'Connect to Google Cloud Logging'
  }
]

export function NewConnectionDialog({
  open,
  onOpenChange,
  onConnectionCreated
}: NewConnectionDialogProps) {
  const [currentStep, setCurrentStep] = React.useState(1)
  const [config, setConfig] = React.useState<ConnectionConfig>({
    name: '',
    provider: 'aws'
  })
  const [isTesting, setIsTesting] = React.useState(false)
  const [testResult, setTestResult] = React.useState<{
    success: boolean
    message: string
  } | null>(null)
  const [showSecrets, setShowSecrets] = React.useState(false)
  const [isCreating, setIsCreating] = React.useState(false)

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleProviderSelect = (provider: 'aws' | 'azure' | 'gcp') => {
    setConfig(prev => ({ ...prev, provider }))
  }

  const handleConfigChange = (field: keyof ConnectionConfig, value: string) => {
    setConfig(prev => ({ ...prev, [field]: value }))
  }

  const handleTestConnection = async () => {
    setIsTesting(true)
    setTestResult(null)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock test result
      setTestResult({
        success: Math.random() > 0.3, // 70% success rate for demo
        message: Math.random() > 0.3 
          ? "Connection successful! Credentials are valid."
          : "Connection failed. Please check your credentials and try again."
      })
    } catch (error) {
      setTestResult({
        success: false,
        message: "Connection test failed. Please try again."
      })
    } finally {
      setIsTesting(false)
    }
  }

  const handleCreateConnection = async () => {
    setIsCreating(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const newConnection = {
        id: `conn_${Date.now()}`,
        connection_name: config.name,
        cloud_provider: config.provider,
        status: 'paused' as const,
        created_at: new Date().toISOString(),
        logs_per_second: 0,
        logs_today: 0,
        errors_today: 0
      }
      
      onConnectionCreated(newConnection)
      onOpenChange(false)
      
      // Reset form
      setCurrentStep(1)
      setConfig({ name: '', provider: 'aws' })
      setTestResult(null)
    } catch (error) {
      console.error('Failed to create connection:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return config.provider
      case 2:
        return config.name && (
          (config.provider === 'aws' && config.region && config.accessKeyId && config.secretKey) ||
          (config.provider === 'azure' && config.subscriptionId && config.workspaceId) ||
          (config.provider === 'gcp' && config.projectId && config.serviceAccountJson)
        )
      case 3:
        return testResult?.success
      case 4:
        return true
      default:
        return false
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="grid gap-3">
              {providers.map((provider) => (
                <Card
                  key={provider.id}
                  className={cn(
                    "cursor-pointer transition-all hover:shadow-md",
                    config.provider === provider.id && "ring-2 ring-primary"
                  )}
                  onClick={() => handleProviderSelect(provider.id as any)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{provider.icon}</span>
                      <div>
                        <h3 className="font-medium">{provider.name}</h3>
                        <p className="text-sm text-muted-foreground">{provider.description}</p>
                      </div>
                      {config.provider === provider.id && (
                        <Check className="h-5 w-5 text-primary ml-auto" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="connection-name">Connection Name</Label>
              <Input
                id="connection-name"
                placeholder="My AWS Logs"
                value={config.name}
                onChange={(e) => handleConfigChange('name', e.target.value)}
              />
            </div>

            {config.provider === 'aws' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="region">AWS Region</Label>
                  <Select onValueChange={(value) => handleConfigChange('region', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select region" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="us-east-1">US East (N. Virginia)</SelectItem>
                      <SelectItem value="us-west-2">US West (Oregon)</SelectItem>
                      <SelectItem value="eu-west-1">Europe (Ireland)</SelectItem>
                      <SelectItem value="ap-southeast-1">Asia Pacific (Singapore)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="access-key">Access Key ID</Label>
                  <Input
                    id="access-key"
                    placeholder="AKIA..."
                    value={config.accessKeyId || ''}
                    onChange={(e) => handleConfigChange('accessKeyId', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="secret-key">Secret Access Key</Label>
                  <div className="relative">
                    <Input
                      id="secret-key"
                      type={showSecrets ? "text" : "password"}
                      placeholder="Enter secret key"
                      value={config.secretKey || ''}
                      onChange={(e) => handleConfigChange('secretKey', e.target.value)}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3"
                      onClick={() => setShowSecrets(!showSecrets)}
                    >
                      {showSecrets ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="log-group">Log Group</Label>
                  <Input
                    id="log-group"
                    placeholder="/aws/lambda/my-function"
                    value={config.logGroup || ''}
                    onChange={(e) => handleConfigChange('logGroup', e.target.value)}
                  />
                </div>
              </>
            )}

            {config.provider === 'azure' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="subscription-id">Subscription ID</Label>
                  <Input
                    id="subscription-id"
                    placeholder="12345678-1234-1234-1234-123456789012"
                    value={config.subscriptionId || ''}
                    onChange={(e) => handleConfigChange('subscriptionId', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="workspace-id">Workspace ID</Label>
                  <Input
                    id="workspace-id"
                    placeholder="12345678-1234-1234-1234-123456789012"
                    value={config.workspaceId || ''}
                    onChange={(e) => handleConfigChange('workspaceId', e.target.value)}
                  />
                </div>
              </>
            )}

            {config.provider === 'gcp' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="project-id">Project ID</Label>
                  <Input
                    id="project-id"
                    placeholder="my-gcp-project"
                    value={config.projectId || ''}
                    onChange={(e) => handleConfigChange('projectId', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="service-account">Service Account JSON</Label>
                  <Textarea
                    id="service-account"
                    placeholder="Paste your service account JSON here..."
                    rows={6}
                    value={config.serviceAccountJson || ''}
                    onChange={(e) => handleConfigChange('serviceAccountJson', e.target.value)}
                  />
                </div>
              </>
            )}
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <div className="text-center py-8">
              {!testResult ? (
                <div className="space-y-4">
                  <div className="w-16 h-16 mx-auto bg-muted rounded-full flex items-center justify-center">
                    <AlertCircle className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="font-medium">Test Your Connection</h3>
                    <p className="text-sm text-muted-foreground">
                      We'll verify your credentials and connection settings
                    </p>
                  </div>
                  <Button onClick={handleTestConnection} disabled={isTesting}>
                    {isTesting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Testing...
                      </>
                    ) : (
                      'Test Connection'
                    )}
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className={cn(
                    "w-16 h-16 mx-auto rounded-full flex items-center justify-center",
                    testResult.success ? "bg-green-100" : "bg-red-100"
                  )}>
                    {testResult.success ? (
                      <Check className="h-8 w-8 text-green-600" />
                    ) : (
                      <AlertCircle className="h-8 w-8 text-red-600" />
                    )}
                  </div>
                  <div>
                    <h3 className={cn(
                      "font-medium",
                      testResult.success ? "text-green-600" : "text-red-600"
                    )}>
                      {testResult.success ? "Connection Successful!" : "Connection Failed"}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {testResult.message}
                    </p>
                  </div>
                  {!testResult.success && (
                    <Button variant="outline" onClick={handleTestConnection}>
                      Try Again
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-4">
            <div className="text-center py-4">
              <h3 className="font-medium">Optional: Configure Filters</h3>
              <p className="text-sm text-muted-foreground">
                You can set up filters to reduce noise and focus on important logs
              </p>
            </div>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Log Levels</Label>
                <div className="flex flex-wrap gap-2">
                  {['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'].map((level) => (
                    <Badge key={level} variant="outline" className="cursor-pointer">
                      {level}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="keyword-filter">Keyword Filter</Label>
                <Input
                  id="keyword-filter"
                  placeholder="e.g., error, timeout, failed"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="resource-filter">Resource Filter</Label>
                <Input
                  id="resource-filter"
                  placeholder="e.g., /aws/lambda/my-function"
                />
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create New Connection</DialogTitle>
          <DialogDescription>
            Connect to your cloud provider to start monitoring live logs
          </DialogDescription>
        </DialogHeader>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                currentStep >= step.id 
                  ? "bg-primary text-primary-foreground" 
                  : "bg-muted text-muted-foreground"
              )}>
                {currentStep > step.id ? <Check className="h-4 w-4" /> : step.id}
              </div>
              <div className="ml-2 hidden sm:block">
                <p className="text-sm font-medium">{step.title}</p>
                <p className="text-xs text-muted-foreground">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="w-8 h-px bg-muted mx-2" />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="min-h-[400px]">
          {renderStepContent()}
        </div>

        {/* Actions */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentStep === 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            
            {currentStep < steps.length ? (
              <Button onClick={handleNext} disabled={!canProceed()}>
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button 
                onClick={handleCreateConnection} 
                disabled={!canProceed() || isCreating}
              >
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Connection'
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
