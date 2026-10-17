<script setup lang="ts">
import { shallowRef } from 'vue'
import CameraPreview from './CameraPreview.vue'
import SignalReadings from './SignalReadings.vue'
import MappingEditor from './MappingEditor.vue'
import ExperimentPanel from './ExperimentPanel.vue'
import TriggerHistory from './TriggerHistory.vue'
import { useDashboard } from './useDashboard'
const camera = shallowRef(0)
const { status, frame, comparison, error, connecting, connected, loadMs, start, stop, command } = useDashboard()
</script>

<template>
  <main class="dashboard">
    <header class="header">
      <div><p class="eyebrow">SECONDHANDS / LOCAL EXPLORATION</p><h1>Movement into possibility.</h1><p>Inspect facial movements, try hand gestures, and compose a simulated command.</p></div>
      <div class="controls"><label>Camera index <input v-model.number="camera" type="number" min="0" max="10" :disabled="connected || connecting"></label><button class="primary" :disabled="connected || connecting" @click="start(camera)">{{ connecting ? 'Starting…' : 'Start camera' }}</button><button :disabled="!connected && !connecting" @click="stop">Stop</button></div>
    </header>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <div class="grid">
      <CameraPreview :frame="frame" />
      <SignalReadings :frame="frame" :load-ms="loadMs" />
      <MappingEditor :connected="connected" :calibration="status?.calibration ?? null" :active-version="status?.mapping_version"
        @apply="(mapping, simulate) => command({ type: 'configure', mapping, simulate })" @cancel="command({ type: 'cancel' })" />
      <TriggerHistory :status="status" :frame="frame" />
      <ExperimentPanel :status="status" :comparison="comparison" :has-frame="!!frame"
        @calibrate="label => command({ type: 'calibrate', label })" @compare="command({ type: 'compare' })" />
    </div>
    <footer>One participant, one visible hand for command experiments. Frame observations are not proof of intent. Calibration and snapshots are cleared on session end.</footer>
  </main>
</template>

<style scoped>
.dashboard { max-width: 1440px; margin: auto; padding: 32px; }
.header { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 24px; }
.eyebrow { color: #76ddc1; letter-spacing: .14em; font-size: .73rem; font-weight: 800; }
.controls { display: flex; gap: 10px; align-items: end; flex-wrap: wrap; }
.controls label { display: grid; font-size: .8rem; gap: 6px; }
.controls input { width: 80px; }
.grid { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr); gap: 20px; align-items: start; }
.error { padding: 16px; background: #4b232a; border: 1px solid #dc7e8e; border-radius: 12px; }
footer { margin-top: 24px; color: #a7b5c9; font-size: .85rem; }
@media (max-width: 850px) { .grid { grid-template-columns: 1fr; } .dashboard { padding: 16px; } }
</style>
