import { afterEach, expect, test, vi } from 'vitest'
import { SessionTransport } from './transport'

class Socket {
  onopen: (() => void) | null = null
  onmessage: ((e: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  sent: Record<string, unknown>[] = []
  send(raw: string) { this.sent.push(JSON.parse(raw)) }
  close() { this.onclose?.() }
  receive(data: Record<string, unknown>) { this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) })) }
}
afterEach(() => vi.useRealTimers())

test('one outstanding frame, queued config suppresses old frame, stop ignores late result', () => {
  vi.useFakeTimers()
  const socket = new Socket()
  const events: Record<string, unknown>[] = []
  const transport = new SessionTransport(() => socket, e => events.push(e))
  transport.start(0)
  socket.onopen?.()
  socket.receive({ type: 'started', session_id: 'session', mapping_version: 1 })
  vi.advanceTimersByTime(1000)
  expect(socket.sent.filter(x => x.type === 'frame')).toHaveLength(1)
  transport.command({ type: 'configure', mapping: {}, simulate: false })
  socket.receive({ type: 'frame', session_id: 'session', mapping_version: 1 })
  expect(events.filter(x => x.type === 'frame')).toHaveLength(0)
  expect(socket.sent.at(-1)?.type).toBe('configure')
  socket.receive({ type: 'configured', session_id: 'session', mapping_version: 2 })
  vi.advanceTimersByTime(100)
  socket.receive({ type: 'frame', session_id: 'session', mapping_version: 1 })
  expect(events.filter(x => x.type === 'frame')).toHaveLength(0)
  transport.stop()
  socket.receive({ type: 'frame', session_id: 'session', mapping_version: 2 })
  vi.advanceTimersByTime(1000)
  expect(events.at(-1)?.type).toBe('stopped')
})


test('socket error after start reports fatal teardown and old open cannot start new socket', () => {
  const first = new Socket()
  const second = new Socket()
  const events: Record<string, unknown>[] = []
  let count = 0
  const transport = new SessionTransport(() => count++ === 0 ? first : second, e => events.push(e))
  transport.start(0)
  first.onopen?.()
  first.receive({ type: 'started', session_id: 'session', mapping_version: 1 })
  first.onerror?.()
  expect(events.at(-1)).toMatchObject({ type: 'error', fatal: true })
  transport.start(1)
  first.onopen?.()
  expect(second.sent).toHaveLength(0)
  second.onopen?.()
  expect(second.sent).toEqual([{ type: 'start', camera_index: 1 }])
  transport.stop()
})
