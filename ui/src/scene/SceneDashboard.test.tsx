// @vitest-environment happy-dom
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import SceneDashboard from './SceneDashboard'

class Socket {
  static instances: Socket[] = []
  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  sent: unknown[] = []
  closed = false
  constructor() { Socket.instances.push(this) }
  send(raw: string) { this.sent.push(JSON.parse(raw)) }
  close() { this.closed = true; this.onclose?.() }
  receive(data: object) { act(() => this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }))) }
}
beforeEach(() => { vi.useFakeTimers(); Socket.instances = []; vi.stubGlobal('WebSocket', Socket) })
afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals() })

test('Orbbec scene settings, matched overlays, delayed scene source and stop', () => {
  render(<SceneDashboard />)
  fireEvent.click(screen.getByRole('button', { name: 'Start scene camera' }))
  const socket = Socket.instances[0]!
  act(() => socket.onopen?.())
  expect(socket.sent[0]).toEqual({ type: 'start', source: 'orbbec', camera_index: 0, pose: true, objects: true, scene_model: true })
  socket.receive({ type: 'started', session_id: 'one', models: [{ name: 'JEVision scene', runtime: 'CPU', state: 'waiting' }] })
  const frame = { type: 'frame', session_id: 'one', frame_id: 2, preview: 'data:image/jpeg;base64,live', processing_ms: 250,
    recognition: { image: { width: 640, height: 360 }, faces: [], hands: [] }, poses: [],
    objects: [{ label: 'chair', score: .8, box: [.1, .2, .3, .4] }], summary: 'Objects detected: 1 chair',
    timing_ms: { mediapipe: 50, pose: 50, objects: 150 },
    scene: { state: 'processing', error: null, age_ms: 12000, result: { description: 'An indoor room.', probability: .6, latency_ms: 9000, runtime: 'CPU', preview: 'data:image/jpeg;base64,old' } } }
  socket.receive(frame)
  expect(screen.getByRole('img', { name: 'Live scene with matching detection overlays' }).querySelector('rect')).toHaveAttribute('x', '64')
  expect(screen.getByRole('img', { name: 'Source frame for the scene interpretation' })).toHaveAttribute('src', 'data:image/jpeg;base64,old')
  expect(screen.getByText(/Source frame age 12.0 s/)).toBeVisible()
  expect(screen.getByText('An indoor room.')).toBeVisible()
  fireEvent.click(screen.getByRole('button', { name: 'Stop scene camera' }))
  expect(socket.closed).toBe(true)
  socket.receive(frame)
  expect(screen.queryByText('An indoor room.')).toBeNull()
  expect(screen.getByRole('button', { name: 'Start scene camera' })).toBeEnabled()
})

test('a late frame from another session is rejected and disconnect clears current observations', () => {
  render(<SceneDashboard />)
  fireEvent.click(screen.getByRole('button', { name: 'Start scene camera' }))
  const socket = Socket.instances[0]!
  act(() => socket.onopen?.())
  socket.receive({ type: 'started', session_id: 'new', models: [] })
  socket.receive({ type: 'frame', session_id: 'old' })
  expect(screen.queryByRole('img', { name: 'Live scene with matching detection overlays' })).toBeNull()
  act(() => socket.onclose?.())
  expect(screen.getByRole('alert')).toHaveTextContent('Camera connection closed')
})
