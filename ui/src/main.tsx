import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import VisionApp from './VisionApp'
import './style.css'

createRoot(document.getElementById('app')!).render(
  <StrictMode><VisionApp /></StrictMode>,
)
