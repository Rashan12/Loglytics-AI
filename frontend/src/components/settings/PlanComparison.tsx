"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Check, X, Crown, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/auth-store"
import { useSettingsStore } from "@/store/settings-store"
import { useUIStore } from "@/store/ui-store"

interface PlanFeature {
  name: string
  free: boolean | string
  pro: boolean | string
  description?: string
}

const features: PlanFeature[] = [
  {
    name: "LLM Models",
    free: "Local only",
    pro: "Local + Maverick",
    description: "Access to different AI models"
  },
  {
    name: "Projects",
    free: "5",
    pro: "Unlimited",
    description: "Number of projects you can create"
  },
  {
    name: "Storage",
    free: "10GB",
    pro: "100GB",
    description: "Total storage for log files and data"
  },
  {
    name: "Analytics",
    free: "Basic",
    pro: "Advanced",
    description: "Analytics and reporting features"
  },
  {
    name: "API Access",
    free: true,
    pro: true,
    description: "REST API access"
  },
  {
    name: "WebSocket Streaming",
    free: true,
    pro: true,
    description: "Real-time log streaming"
  },
  {
    name: "Live Log Monitoring",
    free: true,
    pro: true,
    description: "Real-time log monitoring"
  },
  {
    name: "AI Chat",
    free: true,
    pro: true,
    description: "AI-powered log analysis"
  },
  {
    name: "Export Options",
    free: "JSON, CSV",
    pro: "JSON, CSV, PDF",
    description: "Data export formats"
  },
  {
    name: "Priority Support",
    free: false,
    pro: true,
    description: "Priority customer support"
  },
  {
    name: "Custom Integrations",
    free: false,
    pro: true,
    description: "Custom webhook integrations"
  },
  {
    name: "Advanced Security",
    free: false,
    pro: true,
    description: "Enhanced security features"
  }
]

export function PlanComparison() {
  const { user } = useAuthStore()
  const { upgradeSubscription } = useSettingsStore()
  const { addToast } = useUIStore()

  const handleUpgrade = async () => {
    try {
      await upgradeSubscription("pro")
      addToast({
        title: "Subscription Upgraded",
        description: "Welcome to Pro! You now have access to all premium features.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Upgrade Failed",
        description: "Failed to upgrade subscription. Please try again.",
        type: "error"
      })
    }
  }

  const renderFeatureValue = (value: boolean | string, isPro: boolean = false) => {
    if (typeof value === 'boolean') {
      return value ? (
        <Check className="h-5 w-5 text-green-500" />
      ) : (
        <X className="h-5 w-5 text-muted-foreground" />
      )
    }
    
    return (
      <span className={`text-sm font-medium ${isPro ? 'text-primary' : ''}`}>
        {value}
      </span>
    )
  }

  return (
    <div className="space-y-4">
      {/* Plan Headers */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <h3 className="font-semibold text-lg">Features</h3>
        </div>
        <Card className="relative">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-lg">Free</CardTitle>
            <div className="text-2xl font-bold">$0</div>
            <div className="text-sm text-muted-foreground">/month</div>
            {user?.subscription_tier === 'free' && (
              <Badge variant="default" className="mt-2">Current Plan</Badge>
            )}
          </CardHeader>
        </Card>
        <Card className="relative border-primary">
          <CardHeader className="text-center pb-2">
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-gradient-to-r from-blue-600 to-purple-600">
                <Crown className="h-3 w-3 mr-1" />
                Popular
              </Badge>
            </div>
            <CardTitle className="text-lg flex items-center justify-center gap-1">
              <Crown className="h-4 w-4" />
              Pro
            </CardTitle>
            <div className="text-2xl font-bold">$29</div>
            <div className="text-sm text-muted-foreground">/month</div>
            {user?.subscription_tier === 'pro' && (
              <Badge variant="default" className="mt-2">Current Plan</Badge>
            )}
          </CardHeader>
        </Card>
      </div>

      {/* Features Table */}
      <div className="space-y-2">
        {features.map((feature, index) => (
          <motion.div
            key={feature.name}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="grid grid-cols-3 gap-4 p-3 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <div className="space-y-1">
              <h4 className="font-medium">{feature.name}</h4>
              {feature.description && (
                <p className="text-xs text-muted-foreground">{feature.description}</p>
              )}
            </div>
            <div className="flex items-center justify-center">
              {renderFeatureValue(feature.free)}
            </div>
            <div className="flex items-center justify-center">
              {renderFeatureValue(feature.pro, true)}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Upgrade CTA */}
      {user?.subscription_tier === 'free' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center py-6"
        >
          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-xl font-bold">Ready to unlock Pro features?</h3>
              <p className="text-muted-foreground">
                Get unlimited projects, advanced analytics, and priority support
              </p>
            </div>
            <Button
              size="lg"
              onClick={handleUpgrade}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              <Zap className="h-4 w-4 mr-2" />
              Upgrade to Pro
            </Button>
            <p className="text-xs text-muted-foreground">
              Cancel anytime • 30-day money-back guarantee
            </p>
          </div>
        </motion.div>
      )}
    </div>
  )
}
