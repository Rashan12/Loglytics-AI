"use client"

import * as React from "react"
import { motion } from "framer-motion"
import {
  ChevronDown,
  Bot,
  Sparkles,
  Zap,
  DollarSign,
  Clock,
  Check,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/auth-store"

interface ModelSelectorProps {
  currentModel: "local" | "maverick"
  onModelChange: (model: "local" | "maverick") => void
}

const models = {
  local: {
    name: "Local LLM",
    description: "Free, private, runs on your device",
    icon: Bot,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/20",
    features: ["Free", "Private", "Fast", "Offline"],
    tokensUsed: 0,
    costPerToken: 0,
  },
  maverick: {
    name: "Llama Maverick",
    description: "Advanced AI model for complex analysis",
    icon: Sparkles,
    color: "text-purple-500",
    bgColor: "bg-purple-500/10",
    borderColor: "border-purple-500/20",
    features: ["Advanced", "Accurate", "Context-aware", "RAG-powered"],
    tokensUsed: 1250,
    costPerToken: 0.002,
  },
}

export function ModelSelector({ currentModel, onModelChange }: ModelSelectorProps) {
  const { user } = useAuthStore()
  const [isOpen, setIsOpen] = React.useState(false)
  const isProUser = user?.subscription_tier === "pro"

  const currentModelConfig = models[currentModel]
  const CurrentIcon = currentModelConfig.icon

  const handleModelChange = (model: "local" | "maverick") => {
    if (model === "maverick" && !isProUser) {
      // TODO: Show upgrade modal
      console.log("Upgrade to Pro required")
      return
    }
    
    onModelChange(model)
    setIsOpen(false)
  }

  const calculateCost = (tokens: number, costPerToken: number) => {
    return (tokens * costPerToken).toFixed(4)
  }

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-between h-10 px-3",
            currentModelConfig.borderColor
          )}
        >
          <div className="flex items-center space-x-2">
            <div className={cn("p-1 rounded", currentModelConfig.bgColor)}>
              <CurrentIcon className={cn("h-4 w-4", currentModelConfig.color)} />
            </div>
            <div className="text-left">
              <div className="text-sm font-medium">{currentModelConfig.name}</div>
              <div className="text-xs text-muted-foreground">
                {currentModelConfig.description}
              </div>
            </div>
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="start" className="w-80">
        <DropdownMenuLabel>Choose AI Model</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        {/* Local LLM Option */}
        <DropdownMenuItem
          onClick={() => handleModelChange("local")}
          className="p-3 cursor-pointer"
        >
          <div className="flex items-start space-x-3 w-full">
            <div className={cn("p-2 rounded-lg", models.local.bgColor)}>
              <Bot className={cn("h-5 w-5", models.local.color)} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <h4 className="text-sm font-medium">{models.local.name}</h4>
                {currentModel === "local" && (
                  <Check className="h-4 w-4 text-emerald-500" />
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {models.local.description}
              </p>
              <div className="flex items-center space-x-2 mt-2">
                {models.local.features.map((feature) => (
                  <Badge key={feature} variant="secondary" size="sm">
                    {feature}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <Zap className="h-3 w-3" />
                  <span>Free</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>Fast</span>
                </div>
              </div>
            </div>
          </div>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        {/* Llama Maverick Option */}
        <DropdownMenuItem
          onClick={() => handleModelChange("maverick")}
          className="p-3 cursor-pointer"
          disabled={!isProUser}
        >
          <div className="flex items-start space-x-3 w-full">
            <div className={cn("p-2 rounded-lg", models.maverick.bgColor)}>
              <Sparkles className={cn("h-5 w-5", models.maverick.color)} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <h4 className="text-sm font-medium">{models.maverick.name}</h4>
                {currentModel === "maverick" && (
                  <Check className="h-4 w-4 text-emerald-500" />
                )}
                {!isProUser && (
                  <Badge variant="destructive" size="sm">
                    Pro Required
                  </Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {models.maverick.description}
              </p>
              <div className="flex items-center space-x-2 mt-2">
                {models.maverick.features.map((feature) => (
                  <Badge key={feature} variant="outline" size="sm">
                    {feature}
                  </Badge>
                ))}
              </div>
              <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <DollarSign className="h-3 w-3" />
                  <span>${models.maverick.costPerToken}/token</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span>{models.maverick.tokensUsed.toLocaleString()} tokens used</span>
                </div>
              </div>
              {models.maverick.tokensUsed > 0 && (
                <div className="mt-1 text-xs text-muted-foreground">
                  Cost today: ${calculateCost(models.maverick.tokensUsed, models.maverick.costPerToken)}
                </div>
              )}
            </div>
          </div>
        </DropdownMenuItem>

        {!isProUser && (
          <>
            <DropdownMenuSeparator />
            <div className="p-3">
              <div className="text-center">
                <p className="text-sm font-medium mb-2">Upgrade to Pro</p>
                <p className="text-xs text-muted-foreground mb-3">
                  Get access to Llama Maverick and advanced features
                </p>
                <Button size="sm" className="w-full">
                  Upgrade Now
                </Button>
              </div>
            </div>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
