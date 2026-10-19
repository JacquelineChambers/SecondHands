import { useState } from 'react'
import type { Options, Point } from './types'
import { useScene } from './useScene'

const HAND_EDGES = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]]
const POSE_EDGES = [[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],[23,25],[25,27],[24,26],[26,28]]

export default function SceneDashboard() {
  const [options, setOptions] = useState<Options>({ source: 'orbbec', camera_index: 0, pose: true, objects: true, scene_model: true })
  const [layers, setLayers] = useState({ hands: true, faces: true, poses: true, objects: true })
  const { state, frame, models, error, start, stop } = useScene()
  const active = state !== 'stopped'
  const recognition = frame?.recognition
  const width = recognition?.image.width ?? 640, height = recognition?.image.height ?? 360
  const result = frame?.scene.result
  const skeleton = (points: Point[], edges: number[][], color: string, prefix: string) => <g key={prefix} stroke={color} strokeWidth="2">
    {edges.map(([a,b], i) => points[a!] && points[b!] && (points[a!]!.visibility ?? 1) > .5 && (points[b!]!.visibility ?? 1) > .5 &&
      <line key={i} x1={points[a!]!.x * width} y1={points[a!]!.y * height} x2={points[b!]!.x * width} y2={points[b!]!.y * height} />)}
    {points.map((point, i) => (point.visibility ?? 1) > .5 && <circle key={i} cx={point.x * width} cy={point.y * height} r="2.5" fill={color} stroke="none" />)}
  </g>
  return <main className="dashboard scene-dashboard">
    <header className="header">
      <div><p className="eyebrow">SECONDHANDS / SCENE EXPLORATION</p><h1>Understand what’s in view.</h1><p>Live people, movement, and objects — with a separate scene interpretation.</p></div>
      <div className="controls">
        <label>Camera source<select value={options.source} disabled={active} onChange={e => setOptions({ ...options, source: e.target.value as Options['source'] })}><option value="orbbec">Orbbec Femto Bolt</option><option value="opencv">Standard camera</option></select></label>
        {options.source === 'opencv' && <label>Camera index<input type="number" min="0" max="10" value={options.camera_index} disabled={active} onChange={e => setOptions({ ...options, camera_index: Number(e.target.value) })} /></label>}
        <button className="primary" disabled={active} onClick={() => start(options)}>{state === 'starting' ? 'Loading models…' : 'Start scene camera'}</button>
        <button disabled={!active} onClick={stop}>Stop scene camera</button>
      </div>
    </header>
    {error && <p className="error" role="alert">{error}</p>}
    <section className="scene-model-controls" aria-label="Analysis models">
      <span className="badge">MediaPipe face + hands · CPU</span>
      <label><input type="checkbox" checked={options.pose} disabled={active} onChange={e => setOptions({ ...options, pose: e.target.checked })} /> Body pose</label>
      <label><input type="checkbox" checked={options.objects} disabled={active} onChange={e => setOptions({ ...options, objects: e.target.checked })} /> Object detection</label>
      <label><input type="checkbox" checked={options.scene_model} disabled={active} onChange={e => setOptions({ ...options, scene_model: e.target.checked })} /> JEVision scene analysis</label>
    </section>
    <div className="grid">
      <section className="panel scene-live">
        <div className="row"><h2>Live camera</h2><span className={`badge ${state === 'running' ? 'ok' : ''}`}>{state === 'running' ? 'Live' : state === 'starting' ? 'Starting' : 'Stopped'}</span></div>
        {frame ? <svg className="preview" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Live scene with matching detection overlays">
          <image href={frame.preview} width="100%" height="100%" />
          {layers.faces && recognition?.faces.flatMap((face, index) => face.landmarks.map((p,i) => <circle key={`f${index}-${i}`} cx={p.x * width} cy={p.y * height} r="1" fill="#85e7dd" />))}
          {layers.hands && recognition?.hands.map((hand, i) => skeleton(hand.landmarks, HAND_EDGES, '#ffd28a', `h${i}`))}
          {layers.poses && frame.poses.map((pose, i) => skeleton(pose, POSE_EDGES, '#bdabff', `p${i}`))}
          {layers.objects && frame.objects.map((object,i) => <g key={i}>
            <rect x={object.box[0] * width} y={object.box[1] * height} width={object.box[2] * width} height={object.box[3] * height} fill="none" stroke="#80e0aa" strokeWidth="2" />
            <text x={object.box[0] * width + 4} y={Math.max(15, object.box[1] * height + 15)} fill="white" stroke="#102018" paintOrder="stroke" strokeWidth="3" fontSize="12">{object.label} {(object.score * 100).toFixed(0)}%</text>
          </g>)}
        </svg> : <div className="placeholder"><div><h3>{state === 'starting' ? 'Preparing camera and models…' : 'Your scene appears here'}</h3><p>Connect the Orbbec camera, choose the analyses, and start.</p></div></div>}
        <div className="scene-layers" aria-label="Preview overlays">{(Object.keys(layers) as (keyof typeof layers)[]).map(key => <label key={key}><input type="checkbox" checked={layers[key]} onChange={e => setLayers({ ...layers, [key]: e.target.checked })} /> {key}</label>)}</div>
        {frame && <p className="muted">Frame {frame.frame_id} · {frame.processing_ms.toFixed(0)} ms capture + analysis · unmirrored image</p>}
      </section>
      <section className="panel">
        <h2>Observed in this frame</h2>
        <div className="scene-counts"><span><strong>{recognition?.faces.length ?? '—'}</strong> faces tracked</span><span><strong>{recognition?.hands.length ?? '—'}</strong> hands</span><span><strong>{frame?.poses.length ?? '—'}</strong> poses</span><span><strong>{frame?.objects.length ?? '—'}</strong> objects</span></div>
        <p className="scene-summary">{frame?.summary ?? 'Start the camera to see visible objects and movements.'}</p>
        <h3>Hand gestures</h3>
        {recognition?.hands.length ? recognition.hands.map((hand,i) => <p key={i}>{hand.handedness[0]?.label ?? 'Hand'} · {hand.gestures[0]?.label.replaceAll('_', ' ') ?? 'No category'} <span className="muted">{((hand.gestures[0]?.score ?? 0) * 100).toFixed(0)}%</span></p>) : <p className="muted">No tracked hands.</p>}
        <h3>Objects</h3>
        <div className="scene-object-list">{frame?.objects.length ? frame.objects.map((object,i) => <span className="badge" key={i}>{object.label} · {(object.score * 100).toFixed(0)}%</span>) : <p className="muted">No object detections available.</p>}</div>
      </section>
      <section className="panel">
        <div className="row"><h2>Scene interpretation</h2><span className="badge">{frame?.scene.state ?? (options.scene_model ? 'Waiting for camera' : 'Disabled')}</span></div>
        <p className="muted">JEVision compares scene descriptions from a sampled image. This is a model hypothesis, separate from tracked observations.</p>
        {frame?.scene.error && <p className="warning" role="status">{frame.scene.error}</p>}
        {result ? <div className="scene-interpretation"><img className="snapshot" src={result.preview} alt="Source frame for the scene interpretation" /><div><p className="scene-answer">{result.description}</p><p className="muted">Model probability {(result.probability * 100).toFixed(0)}% · {result.runtime}</p><p className="muted">Source frame age {((frame?.scene.age_ms ?? 0) / 1000).toFixed(1)} s · inference {(result.latency_ms / 1000).toFixed(1)} s</p></div></div> : <p>{options.scene_model ? 'The first interpretation can take tens of seconds. Live tracking continues.' : 'Enable JEVision before starting to compare scene descriptions.'}</p>}
      </section>
      <section className="panel">
        <h2>Models and timing</h2>
        {models.length ? models.map(model => <div className="row scene-model-row" key={model.name}><span>{model.name}</span><span className="muted">{model.runtime} · {model.name.startsWith('JEVision') ? frame?.scene.state ?? model.state : model.state}</span></div>) : <p className="muted">Models load when you start the camera.</p>}
        {frame && <p className="muted">Face + hands {frame.timing_ms.mediapipe.toFixed(0)} ms · pose {frame.timing_ms.pose.toFixed(0)} ms · objects {frame.timing_ms.objects.toFixed(0)} ms</p>}
        <p className="muted">This scene mode uses CPU models. Stop releases the camera and clears observations. No automatic actions or recordings.</p>
      </section>
    </div>
    <footer>Visible appearance only. Model probabilities are not verified accuracy. Person identities, intent, and emotional state are not inferred.</footer>
  </main>
}
