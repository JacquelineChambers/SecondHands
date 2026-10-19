import { useEffect, useState } from 'react'

type Probe = { ok: boolean; detail: string }
export type TailnetDevice = {
  hostname: string; dns_name: string; ip: string; os: string; owner: string
  online: boolean; sharee: boolean; last_seen: string; check?: { ping: Probe; ssh: Probe }
}
export type Tailnet = {
  installed: boolean; state: string; tailnet?: string; health?: string[]
  self: TailnetDevice | null; devices: TailnetDevice[]
  people: { name: string; access: 'member' | 'shared'; online: boolean }[]
}

function Result({ probe }: { probe?: Probe }) {
  if (!probe) return <span className="muted">—</span>
  return <span className={probe.ok ? 'ok' : 'warning'} title={probe.detail}>{probe.ok ? '✓' : '✗'} {probe.detail}</span>
}

function DeviceRow({ device, self = false }: { device: TailnetDevice; self?: boolean }) {
  const name = device.sharee ? `${device.owner || 'Teammate'}'s device` : device.hostname
  const note = device.sharee ? 'shared to them · connects in' : !device.online ? 'offline' : ''
  return <tr>
    <td><b>{name}</b>{self && <span className="badge">this PC</span>}<br /><span className="muted">{device.ip} {device.os}</span></td>
    <td>{device.online ? <span className="ok">online</span> : <span className="muted">offline</span>}</td>
    {device.check ? <><td><Result probe={device.check.ping} /></td><td><Result probe={device.check.ssh} /></td></>
      : <td colSpan={2} className="muted">{note || 'not tested yet'}</td>}
  </tr>
}

/** Shows who can reach this PC over Tailscale and tests SSH reachability from here. */
export default function TailscalePanel() {
  const [net, setNet] = useState<Tailnet | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function load(test: boolean) {
    setBusy(true)
    setError('')
    try {
      const response = await fetch(test ? '/api/tailscale/check' : '/api/tailscale', { method: test ? 'POST' : 'GET' })
      if (!response.ok) throw new Error(String(response.status))
      setNet(await response.json() as Tailnet)
    } catch {
      setError('Cannot read Tailscale status. Start the Python dashboard service.')
    } finally {
      setBusy(false)
    }
  }
  useEffect(() => { void load(false) }, [])

  const running = net?.state === 'Running'
  return <section className="panel">
    <div className="row">
      <h2>Tailscale access</h2>
      <span className="badge">{!net ? 'checking…' : !net.installed ? 'not installed' : running ? `connected · ${net.tailnet}` : net.state}</span>
    </div>
    {error && <p className="warning">{error}</p>}
    {net && !net.installed && <p className="warning">Tailscale is not installed on this PC. See the Wiki Tailscale runbook.</p>}
    {net && net.installed && !running && <p className="warning">Tailscale is installed but not connected. Run <code>tailscale up</code>.</p>}
    {!!net?.health?.length && <ul className="warning">{net.health.map(h => <li key={h}>{h}</li>)}</ul>}
    {!!net?.people.length && <>
      <h3>People with access</h3>
      <ul className="people">{net.people.map(p => <li key={p.name}>
        <span className={p.online ? 'ok' : 'muted'}>●</span> {p.name} <span className="muted">· {p.access === 'member' ? 'tailnet member' : 'machine shared'} · {p.online ? 'online' : 'offline'}</span>
      </li>)}</ul>
    </>}
    {net?.self && <table className="tailnet">
      <thead><tr><th>Device</th><th>Status</th><th>Tailscale ping</th><th>SSH (port 22)</th></tr></thead>
      <tbody>
        <DeviceRow device={net.self} self />
        {net.devices.map((d, i) => <DeviceRow key={`${d.ip}-${i}`} device={d} />)}
      </tbody>
    </table>}
    <div className="row">
      <button className="primary" disabled={busy} onClick={() => void load(true)}>{busy ? 'Testing…' : 'Test connections'}</button>
      <button disabled={busy} onClick={() => void load(false)}>Refresh</button>
    </div>
    <p className="muted">Tests run from this PC. Shared teammates can connect in but cannot be reached from here; they check from their own machine with <code>tailscale ping</code> and <code>ssh</code>.</p>
  </section>
}
