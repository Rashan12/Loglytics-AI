"use client"

import { useEffect, useRef, useCallback, useState } from 'react'
import { useLiveLogsStore } from '@/store/live-logs-store'

interface WebSocketMessage {
  type: 'log' | 'alert' | 'stats' | 'connection_status'
  data: any
  timestamp: string
}

interface UseWebSocketOptions {
  projectId?: string
  connectionId?: string
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket({
  projectId,
  connectionId,
  autoReconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5
}: UseWebSocketOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionError, setConnectionError] = useState<string | null>(null)

  const {
    addLog,
    addAlert,
    updateStats,
    setConnected,
    setConnectionError: setStoreError,
    incrementReconnectAttempts,
    resetReconnectAttempts
  } = useLiveLogsStore()

  const connect = useCallback(() => {
    if (!projectId) return

    try {
      // Determine WebSocket URL based on environment
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = process.env.NODE_ENV === 'production' 
        ? window.location.host 
        : 'localhost:8000'
      
      const wsUrl = `${protocol}//${host}/api/v1/live-logs/ws/${projectId}`
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setConnectionError(null)
        setStoreError(null)
        reconnectAttemptsRef.current = 0
        resetReconnectAttempts()

        // Send authentication if needed
        if (connectionId) {
          ws.send(JSON.stringify({
            type: 'auth',
            connection_id: connectionId
          }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          
          switch (message.type) {
            case 'log':
              addLog(message.data)
              break
            case 'alert':
              addAlert(message.data)
              break
            case 'stats':
              updateStats(message.data)
              break
            case 'connection_status':
              // Handle connection status updates
              break
            default:
              console.warn('Unknown message type:', message.type)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        
        if (event.code !== 1000 && autoReconnect) {
          // Attempt to reconnect
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++
            incrementReconnectAttempts()
            
            console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, reconnectInterval)
          } else {
            setConnectionError('Max reconnection attempts reached')
            setStoreError('Max reconnection attempts reached')
          }
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionError('WebSocket connection error')
        setStoreError('WebSocket connection error')
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionError('Failed to create WebSocket connection')
      setStoreError('Failed to create WebSocket connection')
    }
  }, [
    projectId,
    connectionId,
    autoReconnect,
    reconnectInterval,
    maxReconnectAttempts,
    addLog,
    addAlert,
    updateStats,
    setConnected,
    setStoreError,
    incrementReconnectAttempts,
    resetReconnectAttempts
  ])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
      wsRef.current = null
    }

    setIsConnected(false)
    setConnectionError(null)
    setStoreError(null)
  }, [setStoreError])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      return true
    }
    return false
  }, [])

  const ping = useCallback(() => {
    return sendMessage({ type: 'ping', timestamp: new Date().toISOString() })
  }, [sendMessage])

  // Connect on mount and when dependencies change
  useEffect(() => {
    if (projectId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [projectId, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const heartbeatInterval = setInterval(() => {
      if (!ping()) {
        console.warn('Heartbeat failed, connection may be lost')
      }
    }, 30000) // Ping every 30 seconds

    return () => clearInterval(heartbeatInterval)
  }, [isConnected, ping])

  return {
    isConnected,
    connectionError,
    reconnectAttempts: reconnectAttemptsRef.current,
    connect,
    disconnect,
    sendMessage,
    ping
  }
}
