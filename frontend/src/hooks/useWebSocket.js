import { useEffect, useRef, useState, useCallback } from 'react'

export function useWebSocket() {
  const [events, setEvents] = useState([])
  const [connected, setConnected] = useState(false)
  const [agentActivity, setAgentActivity] = useState({})
  const ws = useRef(null)
  const reconnectTimer = useRef(null)

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws`

    try {
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        setConnected(true)
        clearTimeout(reconnectTimer.current)
      }

      ws.current.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'PING') return

          if (msg.type === 'BUS_EVENT' && msg.data) {
            const event = msg.data
            setEvents(prev => [event, ...prev].slice(0, 200))

            // Track agent activity
            if (event.agent_id) {
              setAgentActivity(prev => ({
                ...prev,
                [event.agent_id]: {
                  status: event.event_type.includes('DONE') ? 'idle' :
                          event.event_type.includes('ERROR') ? 'error' : 'active',
                  last_event: event.event_type,
                  last_active: event.timestamp,
                }
              }))
            }
          }
        } catch (_) {}
      }

      ws.current.onclose = () => {
        setConnected(false)
        reconnectTimer.current = setTimeout(connect, 3000)
      }

      ws.current.onerror = () => {
        ws.current?.close()
      }
    } catch (_) {}
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])

  return { events, connected, agentActivity }
}
