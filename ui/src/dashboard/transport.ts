export type Message = Record<string, unknown>
type SocketLike = Pick<WebSocket, 'onopen' | 'onmessage' | 'onclose' | 'onerror' | 'send' | 'close'>

/** One outstanding command/frame and one pending user command; no frame queue. */
export class SessionTransport {
  private socket: SocketLike | null = null
  private timer: ReturnType<typeof setTimeout> | undefined
  private busy = false
  private pending: Message | null = null
  private session = ''
  private version = 0
  constructor(private factory: () => SocketLike, private receive: (data: Message) => void) {}

  start(camera: number) {
    this.stop(false)
    const socket = this.factory()
    this.socket = socket
    socket.onopen = () => {
      if (this.socket === socket) this.send({ type: 'start', camera_index: camera })
    }
    socket.onmessage = event => {
      if (this.socket !== socket) return
      const data = JSON.parse(event.data) as Message
      this.busy = false
      if (data.type === 'started') this.session = String(data.session_id)
      if (data.type !== 'frame' && data.type !== 'comparison' && data.mapping_version) {
        this.version = Number(data.mapping_version)
      }
      const frame = data.type === 'frame' || data.type === 'comparison'
      const invalidated = this.pending && ['configure', 'calibrate', 'cancel'].includes(String(this.pending.type))
      if (!frame || (!invalidated && data.session_id === this.session && data.mapping_version === this.version)) {
        this.receive(data)
      }
      if (data.type === 'error' && (data.fatal || !this.session)) {
        this.stop(false)
        return
      }
      if (this.pending) {
        const next = this.pending
        this.pending = null
        this.send(next)
      } else if (this.session) {
        this.timer = setTimeout(() => this.send({ type: 'frame' }), 80)
      }
    }
    socket.onerror = () => {
      if (this.socket !== socket) return
      this.receive({ type: 'error', fatal: true, message: 'Connection failed. Start or check the Python dashboard service.' })
      this.stop(false)
    }
    socket.onclose = () => {
      if (this.socket !== socket) return
      this.stop(false)
      this.receive({ type: 'disconnected' })
    }
  }

  private send(command: Message) {
    if (!this.socket) return
    clearTimeout(this.timer)
    this.busy = true
    this.socket.send(JSON.stringify(command))
  }

  command(command: Message) {
    if (!this.socket || !this.session || this.pending) return false
    clearTimeout(this.timer)
    if (this.busy) this.pending = command
    else this.send(command)
    return true
  }

  stop(notify = true) {
    clearTimeout(this.timer)
    const socket = this.socket
    this.socket = null
    this.pending = null
    this.busy = false
    this.session = ''
    this.version = 0
    socket?.close()
    if (notify) this.receive({ type: 'stopped' })
  }
}
