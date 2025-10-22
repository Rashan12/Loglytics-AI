"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Search, Plus, Filter } from "lucide-react"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ConnectionCard } from "./ConnectionCard"
import { NewConnectionDialog } from "./NewConnectionDialog"
import { useLiveLogsStore } from "@/store/live-logs-store"

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 }
}

export function ConnectionsList() {
  const { 
    connections, 
    activeConnection, 
    setActiveConnection,
    addConnection 
  } = useLiveLogsStore()

  const [searchQuery, setSearchQuery] = React.useState("")
  const [showNewDialog, setShowNewDialog] = React.useState(false)
  const [statusFilter, setStatusFilter] = React.useState<string>("all")

  // Filter connections based on search and status
  const filteredConnections = React.useMemo(() => {
    return connections.filter(connection => {
      const matchesSearch = connection.connection_name
        .toLowerCase()
        .includes(searchQuery.toLowerCase())
      
      const matchesStatus = statusFilter === "all" || connection.status === statusFilter
      
      return matchesSearch && matchesStatus
    })
  }, [connections, searchQuery, statusFilter])

  const statusCounts = React.useMemo(() => {
    return connections.reduce((acc, conn) => {
      acc[conn.status] = (acc[conn.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [connections])

  const handleConnectionSelect = (connection: any) => {
    setActiveConnection(connection)
  }

  const handleNewConnection = (connection: any) => {
    addConnection(connection)
    setShowNewDialog(false)
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="p-4 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search connections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        {/* Status Filter */}
        <div className="flex gap-1">
          <Button
            variant={statusFilter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("all")}
            className="text-xs"
          >
            All ({connections.length})
          </Button>
          <Button
            variant={statusFilter === "active" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("active")}
            className="text-xs"
          >
            Active ({statusCounts.active || 0})
          </Button>
          <Button
            variant={statusFilter === "paused" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("paused")}
            className="text-xs"
          >
            Paused ({statusCounts.paused || 0})
          </Button>
          <Button
            variant={statusFilter === "error" ? "default" : "outline"}
            size="sm"
            onClick={() => setStatusFilter("error")}
            className="text-xs"
          >
            Error ({statusCounts.error || 0})
          </Button>
        </div>
      </div>

      {/* Connections List */}
      <ScrollArea className="h-[calc(100vh-300px)]">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-2 p-4"
        >
          {filteredConnections.length > 0 ? (
            filteredConnections.map((connection) => (
              <motion.div key={connection.id} variants={itemVariants}>
                <ConnectionCard
                  connection={connection}
                  isActive={activeConnection?.id === connection.id}
                  onClick={() => handleConnectionSelect(connection)}
                />
              </motion.div>
            ))
          ) : (
            <motion.div
              variants={itemVariants}
              className="text-center py-8"
            >
              <div className="text-muted-foreground mb-4">
                {searchQuery || statusFilter !== "all" ? (
                  <>
                    <Filter className="h-8 w-8 mx-auto mb-2" />
                    <p>No connections match your filters</p>
                  </>
                ) : (
                  <>
                    <Plus className="h-8 w-8 mx-auto mb-2" />
                    <p>No connections yet</p>
                    <p className="text-sm">Create your first connection to start monitoring</p>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </motion.div>
      </ScrollArea>

      {/* New Connection Dialog */}
      <NewConnectionDialog
        open={showNewDialog}
        onOpenChange={setShowNewDialog}
        onConnectionCreated={handleNewConnection}
      />
    </div>
  )
}
