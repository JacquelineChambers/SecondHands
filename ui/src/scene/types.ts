export type Point = { x: number; y: number; z: number; visibility?: number }
export type Model = { name: string; state: string; runtime: string }
export type Options = { source: 'orbbec' | 'opencv'; camera_index: number; pose: boolean; objects: boolean; scene_model: boolean }
export type SceneFrame = {
  type: 'frame'; session_id: string; frame_id: number; preview: string; captured_ms: number; processing_ms: number
  recognition: {
    image: { width: number; height: number }
    faces: { landmarks: Point[]; blendshapes: Record<string, number> }[]
    hands: { landmarks: Point[]; gestures: { label: string; score: number }[]; handedness: { label: string; score: number }[] }[]
  }
  poses: Point[][]
  objects: { label: string; score: number; box: [number, number, number, number] }[]
  summary: string
  timing_ms: { mediapipe: number; pose: number; objects: number }
  scene: {
    state: string; error: string | null; age_ms?: number | null
    result: { description: string; probability: number; latency_ms: number; preview: string; captured_ms: number; model: string; runtime: string } | null
  }
}
