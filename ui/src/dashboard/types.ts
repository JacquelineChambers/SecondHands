export interface Mapping {
  mode: string
  face_signal: string
  hand_gesture: string
  activate: number
  release: number
  hold_ms: number
  release_ms: number
  cooldown_ms: number
  timeout_ms: number
  overlap_ms: number
  max_gap_ms: number
}
export const defaultMapping: Mapping = {
  mode: 'face', face_signal: 'browInnerUp', hand_gesture: 'Open_Palm', activate: .7,
  release: .3, hold_ms: 500, release_ms: 300, cooldown_ms: 800,
  timeout_ms: 3000, overlap_ms: 500, max_gap_ms: 1000,
}
export interface Landmark { x: number; y: number; z: number }
export interface Category { label: string; score: number }
export interface Recognition {
  image: { width: number; height: number }
  timing_ms: { face: number; hand: number; total: number }
  faces: { landmarks: Landmark[]; blendshapes: Record<string, number> }[]
  hands: { landmarks: Landmark[]; gestures: Category[]; handedness: Category[] }[]
}
export interface Calibration {
  collecting: string | null
  remaining: number
  neutral: { count: number; face_mean: number | null; hand_mean: number | null }
  deliberate: { count: number; face_mean: number | null; hand_mean: number | null }
  face_suggestion: { activate: number; release: number } | null
  hand_suggestion: { activate: number; release: number } | null
}
export interface Model { name: string; available: boolean; runtime: string }
export interface LogEvent { id: string; state: string; reason: string; frame_id: number; mapping_version: number }
export interface SessionStatus {
  session_id: string; mapping_version: number; running: boolean; simulate: boolean
  lamp: boolean; state: string; mapping: Mapping; calibration: Calibration
  events: LogEvent[]; models: Model[]
}
export interface Frame extends SessionStatus {
  type: string; frame_id: number; captured_ms: number; processing_ms: number; capture_ms: number
  preview: string; recognition: Recognition; signals: { face: number | null; hand: number | null }
  note?: string
}
