import { useCallback, useEffect, useRef, useState } from 'react'
import type { Model, Options, SceneFrame } from './types'

export function useScene() {
  const socket = useRef<WebSocket | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [state, setState] = useState<'stopped' | 'starting' | 'running'>('stopped')
  const [frame, setFrame] = useState<SceneFrame | null>(null)
  const [models, setModels] = useState<Model[]>([])
  const [error, setError] = useState('')
  const close = useCallback(() => {
    if (timer.current) clearTimeout(timer.current)
    const previous = socket.current
    socket.current = null
    previous?.close()
  }, [])
  const stop = useCallback(() => {
    close(); setState('stopped'); setFrame(null); setModels([])
  }, [close])
  useEffect(() => close, [close])
  const start = useCallback((options: Options) => {
    close(); setFrame(null); setModels([]); setError(''); setState('starting')
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const current = new WebSocket(`${protocol}//${location.host}/api/scene`)
    socket.current = current
    let sessionId = ''
    const next = () => {
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(() => {
        if (socket.current === current) current.send(JSON.stringify({ type: 'frame' }))
      }, 100)
    }
    current.onopen = () => {
      if (socket.current === current) current.send(JSON.stringify({ type: 'start', ...options }))
    }
    current.onmessage = event => {
      if (socket.current !== current) return
      try {
        const message = JSON.parse(event.data)
        if (message.type === 'started') {
          sessionId = message.session_id; setModels(message.models); setState('running'); next()
        } else if (message.type === 'frame') {
          if (message.session_id !== sessionId) return
          setFrame(message); next()
        } else if (message.type === 'busy') next()
        else if (message.type === 'error') {
          stop(); setError(message.message)
        }
      } catch {
        stop(); setError('The camera service returned an invalid response.')
      }
    }
    current.onclose = () => {
      if (socket.current === current) { stop(); setError('Camera connection closed. You can start a new session.') }
    }
    current.onerror = () => {
      if (socket.current === current) { stop(); setError('Cannot reach the camera service. Check that the Python API is running.') }
    }
  }, [close, stop])
  return { state, frame, models, error, start, stop }
}
