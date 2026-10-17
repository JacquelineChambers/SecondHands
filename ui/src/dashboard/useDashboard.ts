import { onUnmounted, shallowRef } from 'vue'
import { SessionTransport, type Message } from './transport'
import type { Frame, SessionStatus } from './types'

export function useDashboard() {
  const status = shallowRef<SessionStatus | null>(null)
  const frame = shallowRef<Frame | null>(null)
  const comparison = shallowRef<Frame | null>(null)
  const error = shallowRef('')
  const connecting = shallowRef(false)
  const connected = shallowRef(false)
  const loadMs = shallowRef<number | null>(null)
  const transport = new SessionTransport(
    () => new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/api/session`),
    (data: Message) => {
      if (data.type === 'error') {
        error.value = String(data.message)
        connecting.value = false
        if (data.fatal) {
          connected.value = false
          status.value = null
          frame.value = null
          comparison.value = null
        }
      } else if (['stopped', 'disconnected'].includes(String(data.type))) {
        connected.value = false
        connecting.value = false
        status.value = null
        frame.value = null
        comparison.value = null
        if (data.type === 'disconnected') error.value = 'Session disconnected. Camera capture has stopped.'
      } else if (data.type === 'comparison') {
        comparison.value = data as unknown as Frame
      } else if (data.session_id) {
        status.value = data as unknown as SessionStatus
        if (data.type === 'started') {
          connected.value = true
          connecting.value = false
          loadMs.value = Number(data.model_load_ms)
        }
        if (data.type === 'frame') frame.value = data as unknown as Frame
        if (['configured', 'calibrating', 'cancelled'].includes(String(data.type))) {
          frame.value = null
          comparison.value = null
        }
      }
    },
  )
  function start(index: number) {
    error.value = ''
    connecting.value = true
    comparison.value = null
    transport.start(index)
  }
  function command(message: Message) {
    error.value = ''
    if (!transport.command(message)) error.value = 'Wait for the current command to finish.'
  }
  onUnmounted(() => transport.stop())
  return { status, frame, comparison, error, connecting, connected, loadMs, start, command,
    stop: () => transport.stop() }
}
