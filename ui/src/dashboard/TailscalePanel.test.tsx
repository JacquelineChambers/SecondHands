// @vitest-environment happy-dom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, expect, test, vi } from 'vitest'
import TailscalePanel, { type Tailnet, type TailnetDevice } from './TailscalePanel'

const device = (extra: Partial<TailnetDevice>): TailnetDevice => ({
  hostname: 'pc', dns_name: 'pc.tail0.ts.net', ip: '100.0.0.1', os: 'windows', owner: 'Owner',
  online: true, sharee: false, last_seen: '', ...extra,
})
const net: Tailnet = {
  installed: true, state: 'Running', tailnet: 'tail0.ts.net', health: [],
  self: device({}),
  devices: [device({ hostname: 'device-of-shared-to-user', ip: '100.0.0.3', owner: 'Teammate', sharee: true })],
  people: [{ name: 'Owner', access: 'member', online: true }, { name: 'Teammate', access: 'shared', online: true }],
}
const tested: Tailnet = { ...net, self: device({ check: { ping: { ok: true, detail: 'this device' }, ssh: { ok: true, detail: 'port 22 open' } } }) }
const reply = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body)))

afterEach(() => { cleanup(); vi.unstubAllGlobals() })

test('lists people with access and runs the connection test', async () => {
  const fetch = vi.fn((url: string) => reply(url.endsWith('/check') ? tested : net))
  vi.stubGlobal('fetch', fetch)
  render(<TailscalePanel />)
  expect(await screen.findByText('connected · tail0.ts.net')).toBeVisible()
  expect(screen.getByText("Teammate's device")).toBeVisible()
  expect(screen.getByText(/machine shared/)).toBeVisible()
  fireEvent.click(screen.getByRole('button', { name: 'Test connections' }))
  expect(await screen.findByText(/port 22 open/)).toBeVisible()
  expect(fetch).toHaveBeenLastCalledWith('/api/tailscale/check', { method: 'POST' })
})

test('explains a missing Tailscale install', async () => {
  vi.stubGlobal('fetch', vi.fn(() => reply({ installed: false, state: 'NotInstalled', self: null, devices: [], people: [] })))
  render(<TailscalePanel />)
  expect(await screen.findByText(/not installed on this PC/)).toBeVisible()
})
