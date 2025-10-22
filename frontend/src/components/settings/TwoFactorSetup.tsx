"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Shield, 
  Smartphone, 
  Copy, 
  Check,
  AlertCircle,
  Download
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface TwoFactorSetupProps {
  onClose: () => void
  onComplete: () => void
}

export function TwoFactorSetup({ onClose, onComplete }: TwoFactorSetupProps) {
  const [step, setStep] = React.useState(1)
  const [verificationCode, setVerificationCode] = React.useState("")
  const [backupCodes, setBackupCodes] = React.useState<string[]>([])
  const [copied, setCopied] = React.useState(false)
  const [isVerifying, setIsVerifying] = React.useState(false)

  // Mock data - in real implementation, this would come from the API
  const qrCodeUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
  const secretKey = "JBSWY3DPEHPK3PXP"
  const mockBackupCodes = [
    "12345678",
    "87654321", 
    "11223344",
    "44332211",
    "55667788",
    "88776655",
    "99887766",
    "66778899"
  ]

  const handleCopySecret = async () => {
    try {
      await navigator.clipboard.writeText(secretKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const handleVerifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      return
    }

    setIsVerifying(true)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock verification - in real implementation, this would validate with the server
    if (verificationCode === "123456") {
      setBackupCodes(mockBackupCodes)
      setStep(3)
    } else {
      // Handle verification failure
      console.error("Invalid verification code")
    }
    
    setIsVerifying(false)
  }

  const handleDownloadBackupCodes = () => {
    const content = `Loglytics AI - Two-Factor Authentication Backup Codes

IMPORTANT: Keep these codes safe! Each code can only be used once.

${backupCodes.map((code, index) => `${index + 1}. ${code}`).join('\n')}

Generated: ${new Date().toLocaleString()}

If you lose access to your authenticator app, you can use these codes to sign in.
Each code can only be used once, so make sure to save them securely.`

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'loglytics-2fa-backup-codes.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleComplete = () => {
    onComplete()
    onClose()
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Set Up Two-Factor Authentication
          </DialogTitle>
          <DialogDescription>
            Add an extra layer of security to your account
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Step 1: Install App */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Smartphone className="h-5 w-5" />
                    Step 1: Install Authenticator App
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Download and install an authenticator app on your mobile device. We recommend:
                  </p>
                  
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="flex items-center gap-3 p-3 border rounded-lg">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 font-bold">G</span>
                      </div>
                      <div>
                        <p className="font-medium">Google Authenticator</p>
                        <p className="text-xs text-muted-foreground">Free • iOS & Android</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 p-3 border rounded-lg">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-purple-600 font-bold">A</span>
                      </div>
                      <div>
                        <p className="font-medium">Authy</p>
                        <p className="text-xs text-muted-foreground">Free • iOS & Android</p>
                      </div>
                    </div>
                  </div>
                  
                  <Button onClick={() => setStep(2)} className="w-full">
                    I've installed an authenticator app
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Step 2: Scan QR Code */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Step 2: Scan QR Code</CardTitle>
                  <CardDescription>
                    Open your authenticator app and scan this QR code
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-center">
                    <div className="p-4 bg-white rounded-lg border">
                      <img
                        src={qrCodeUrl}
                        alt="QR Code for 2FA setup"
                        className="w-48 h-48"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Or enter this code manually:</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        value={secretKey}
                        readOnly
                        className="font-mono"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopySecret}
                      >
                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="verification-code">Enter verification code</Label>
                    <Input
                      id="verification-code"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="123456"
                      maxLength={6}
                      className="text-center text-lg font-mono"
                    />
                    <p className="text-xs text-muted-foreground">
                      Enter the 6-digit code from your authenticator app
                    </p>
                  </div>
                  
                  <Button
                    onClick={handleVerifyCode}
                    disabled={verificationCode.length !== 6 || isVerifying}
                    className="w-full"
                  >
                    {isVerifying ? "Verifying..." : "Verify & Continue"}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Step 3: Backup Codes */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Step 3: Save Backup Codes
                  </CardTitle>
                  <CardDescription>
                    Save these backup codes in a safe place
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    <p className="text-sm text-yellow-800">
                      <strong>Important:</strong> Each code can only be used once. Keep them safe!
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 p-4 bg-muted rounded-lg">
                    {backupCodes.map((code, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                        <span className="text-sm font-mono">{code}</span>
                        <Badge variant="outline" className="text-xs">
                          {index + 1}
                        </Badge>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={handleDownloadBackupCodes} className="flex-1">
                      <Download className="h-4 w-4 mr-2" />
                      Download Codes
                    </Button>
                    <Button onClick={handleComplete} className="flex-1">
                      <Check className="h-4 w-4 mr-2" />
                      Complete Setup
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
