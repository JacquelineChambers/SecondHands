import { useState } from 'react'
import RecognitionDashboard from './dashboard/RecognitionDashboard'
import SceneDashboard from './scene/SceneDashboard'

export default function VisionApp() {
  const [mode, setMode] = useState<'scene' | 'gestures'>('scene')
  return <>
    <nav className="app-navigation" aria-label="Exploration mode">
      <span>SecondHands</span>
      <button className={mode === 'scene' ? 'primary' : ''} aria-pressed={mode === 'scene'} onClick={() => setMode('scene')}>Scene understanding</button>
      <button className={mode === 'gestures' ? 'primary' : ''} aria-pressed={mode === 'gestures'} onClick={() => setMode('gestures')}>Gesture experiments</button>
    </nav>
    {mode === 'scene' ? <SceneDashboard /> : <RecognitionDashboard />}
  </>
}
