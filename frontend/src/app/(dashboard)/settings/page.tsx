"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Settings as SettingsIcon, User, Shield, Bell, CreditCard, Key, Palette, FileText } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

// Settings Components
import { ProfileTab } from "@/components/settings/ProfileTab"
import { AccountTab } from "@/components/settings/AccountTab"
import { SubscriptionTab } from "@/components/settings/SubscriptionTab"
import { ApiKeysTab } from "@/components/settings/ApiKeysTab"
import { NotificationsTab } from "@/components/settings/NotificationsTab"
import { SecurityTab } from "@/components/settings/SecurityTab"
import { PreferencesTab } from "@/components/settings/PreferencesTab"
import { BillingTab } from "@/components/settings/BillingTab"

// Store
import { useAuthStore } from "@/store/auth-store"
import { useSettingsStore } from "@/store/settings-store"

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

const cardVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 }
}

const settingsTabs = [
  {
    id: "profile",
    label: "Profile",
    icon: User,
    description: "Manage your personal information"
  },
  {
    id: "account",
    label: "Account",
    icon: Shield,
    description: "Password, 2FA, and account security"
  },
  {
    id: "subscription",
    label: "Subscription",
    icon: CreditCard,
    description: "Manage your subscription plan"
  },
  {
    id: "api-keys",
    label: "API Keys",
    icon: Key,
    description: "Manage your API access keys"
  },
  {
    id: "notifications",
    label: "Notifications",
    icon: Bell,
    description: "Email and in-app notification preferences"
  },
  {
    id: "security",
    label: "Security",
    icon: Shield,
    description: "Sessions, login history, and security settings"
  },
  {
    id: "preferences",
    label: "Preferences",
    icon: Palette,
    description: "Appearance, editor, and general preferences"
  }
]

export default function SettingsPage() {
  const { user } = useAuthStore()
  const { refreshData } = useSettingsStore()
  const [activeTab, setActiveTab] = React.useState("profile")

  // Load settings data on mount
  React.useEffect(() => {
    refreshData()
  }, [refreshData])

  // Add billing tab for Pro users
  const allTabs = React.useMemo(() => {
    if (user?.subscription_tier === "pro") {
      return [
        ...settingsTabs,
        {
          id: "billing",
          label: "Billing",
          icon: FileText,
          description: "Payment methods and billing history"
        }
      ]
    }
    return settingsTabs
  }, [user?.subscription_tier])

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="min-h-screen bg-background"
    >
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Page Header */}
        <motion.div
          variants={cardVariants}
          className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0"
        >
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <SettingsIcon className="h-8 w-8 text-primary" />
              Settings
            </h1>
            <p className="text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>
          
          {user && (
            <div className="flex items-center gap-2">
              <Badge 
                variant={user.subscription_tier === "pro" ? "default" : "secondary"}
                className="capitalize"
              >
                {user.subscription_tier} Plan
              </Badge>
              <Badge variant="outline">
                {user.selected_llm_model} Model
              </Badge>
            </div>
          )}
        </motion.div>

        {/* Settings Content */}
        <motion.div variants={cardVariants}>
          <Card>
            <CardContent className="p-0">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex h-[calc(100vh-200px)]">
                {/* Tab Navigation */}
                <div className="w-64 border-r bg-muted/30 p-4">
                  <TabsList className="grid w-full grid-cols-1 gap-1 h-auto bg-transparent">
                    {allTabs.map((tab) => {
                      const Icon = tab.icon
                      return (
                        <TabsTrigger
                          key={tab.id}
                          value={tab.id}
                          className="flex items-center gap-3 justify-start h-auto p-3 data-[state=active]:bg-background data-[state=active]:shadow-sm"
                        >
                          <Icon className="h-4 w-4" />
                          <div className="text-left">
                            <div className="font-medium">{tab.label}</div>
                            <div className="text-xs text-muted-foreground hidden sm:block">
                              {tab.description}
                            </div>
                          </div>
                        </TabsTrigger>
                      )
                    })}
                  </TabsList>
                </div>

                {/* Tab Content */}
                <div className="flex-1 p-6 overflow-auto">
                  <TabsContent value="profile" className="mt-0">
                    <ProfileTab />
                  </TabsContent>
                  
                  <TabsContent value="account" className="mt-0">
                    <AccountTab />
                  </TabsContent>
                  
                  <TabsContent value="subscription" className="mt-0">
                    <SubscriptionTab />
                  </TabsContent>
                  
                  <TabsContent value="api-keys" className="mt-0">
                    <ApiKeysTab />
                  </TabsContent>
                  
                  <TabsContent value="notifications" className="mt-0">
                    <NotificationsTab />
                  </TabsContent>
                  
                  <TabsContent value="security" className="mt-0">
                    <SecurityTab />
                  </TabsContent>
                  
                  <TabsContent value="preferences" className="mt-0">
                    <PreferencesTab />
                  </TabsContent>
                  
                  {user?.subscription_tier === "pro" && (
                    <TabsContent value="billing" className="mt-0">
                      <BillingTab />
                    </TabsContent>
                  )}
                </div>
              </Tabs>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  )
}
