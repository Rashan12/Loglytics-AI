"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { 
  Crown, 
  Check, 
  X, 
  ArrowUp,
  CreditCard,
  Calendar,
  TrendingUp,
  HardDrive,
  Zap,
  Headphones
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
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
import { PlanComparison } from "./PlanComparison"
import { useSettingsStore } from "@/store/settings-store"
import { useAuthStore } from "@/store/auth-store"
import { useUIStore } from "@/store/ui-store"

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export function SubscriptionTab() {
  const { user } = useAuthStore()
  const { addToast } = useUIStore()
  const {
    subscription,
    isLoading,
    upgradeSubscription,
    cancelSubscription
  } = useSettingsStore()

  const [showComparison, setShowComparison] = React.useState(false)
  const [showCancelDialog, setShowCancelDialog] = React.useState(false)

  const isPro = user?.subscription_tier === "pro"
  const isFree = user?.subscription_tier === "free"

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

  const handleCancel = async () => {
    try {
      await cancelSubscription()
      setShowCancelDialog(false)
      addToast({
        title: "Subscription Cancelled",
        description: "Your subscription will remain active until the end of your billing period.",
        type: "success"
      })
    } catch (error) {
      addToast({
        title: "Cancellation Failed",
        description: "Failed to cancel subscription. Please try again.",
        type: "error"
      })
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Subscription</h2>
        <p className="text-muted-foreground">
          Manage your subscription plan and billing
        </p>
      </div>

      {/* Current Plan */}
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
                  <Crown className="h-5 w-5" />
                  Current Plan
                </CardTitle>
                <CardDescription>
                  Your current subscription details
                </CardDescription>
              </div>
              <Badge 
                variant={isPro ? "default" : "secondary"}
                className="text-lg px-3 py-1"
              >
                {user?.subscription_tier?.toUpperCase()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {isFree ? (
              /* Free Plan */
              <div className="space-y-4">
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                    <Crown className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-2xl font-bold mb-2">Free Plan</h3>
                  <p className="text-muted-foreground mb-6">
                    You're currently on our free plan with basic features
                  </p>
                  <Button 
                    size="lg" 
                    onClick={handleUpgrade}
                    disabled={isLoading}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <ArrowUp className="h-4 w-4 mr-2" />
                    Upgrade to Pro
                  </Button>
                </div>

                <Separator />

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <h4 className="font-medium">Included Features</h4>
                    <div className="space-y-2">
                      {[
                        "Local LLM model",
                        "5 projects",
                        "10GB total storage",
                        "Basic analytics",
                        "Community support"
                      ].map((feature) => (
                        <div key={feature} className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-medium">Pro Features</h4>
                    <div className="space-y-2">
                      {[
                        "Llama Maverick model",
                        "Unlimited projects",
                        "100GB storage",
                        "Advanced analytics",
                        "Priority support"
                      ].map((feature) => (
                        <div key={feature} className="flex items-center gap-2">
                          <X className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              /* Pro Plan */
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold">Pro Plan</h3>
                    <p className="text-muted-foreground">$29/month</p>
                  </div>
                  <Badge variant="default" className="flex items-center gap-1">
                    <Check className="h-3 w-3" />
                    Active
                  </Badge>
                </div>

                {subscription && (
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">Next billing date</span>
                      </div>
                      <p className="font-medium">
                        {formatDate(subscription.current_period_end)}
                      </p>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">Status</span>
                      </div>
                      <Badge variant={subscription.status === 'active' ? 'default' : 'secondary'}>
                        {subscription.status}
                      </Badge>
                    </div>
                  </div>
                )}

                <Separator />

                {/* Usage Stats */}
                <div className="space-y-4">
                  <h4 className="font-medium">Usage This Month</h4>
                  
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4" />
                          LLM Tokens
                        </span>
                        <span>
                          {subscription?.usage.llm_tokens_used.toLocaleString()} / Unlimited
                        </span>
                      </div>
                      <Progress value={Math.min(100, (subscription?.usage.llm_tokens_used || 0) / 10000 * 100)} />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          <HardDrive className="h-4 w-4" />
                          Storage
                        </span>
                        <span>
                          {formatBytes((subscription?.usage.storage_used_gb || 0) * 1024 * 1024 * 1024)} / 100GB
                        </span>
                      </div>
                      <Progress value={(subscription?.usage.storage_used_gb || 0)} />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          <Zap className="h-4 w-4" />
                          API Calls
                        </span>
                        <span>
                          {subscription?.usage.api_calls.toLocaleString()} / Unlimited
                        </span>
                      </div>
                      <Progress value={Math.min(100, (subscription?.usage.api_calls || 0) / 10000 * 100)} />
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Pro Features */}
                <div className="space-y-2">
                  <h4 className="font-medium">Pro Features</h4>
                  <div className="grid gap-2 md:grid-cols-2">
                    {[
                      "Local LLM model",
                      "Llama Maverick model",
                      "Unlimited projects",
                      "100GB storage",
                      "Advanced analytics",
                      "Priority support"
                    ].map((feature) => (
                      <div key={feature} className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Actions */}
                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Manage Subscription
                  </Button>
                  
                  <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" className="flex-1">
                        Cancel Subscription
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Cancel Subscription</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to cancel your Pro subscription? You'll lose access to all Pro features
                          at the end of your current billing period ({formatDate(subscription?.current_period_end || '')}).
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Keep Subscription</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleCancel}
                          className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                          Cancel Subscription
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Plan Comparison */}
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
                <CardTitle>Plan Comparison</CardTitle>
                <CardDescription>
                  Compare features across all available plans
                </CardDescription>
              </div>
              <Button
                variant="outline"
                onClick={() => setShowComparison(!showComparison)}
              >
                {showComparison ? "Hide" : "Show"} Comparison
              </Button>
            </div>
          </CardHeader>
          {showComparison && (
            <CardContent>
              <PlanComparison />
            </CardContent>
          )}
        </Card>
      </motion.div>
    </div>
  )
}
