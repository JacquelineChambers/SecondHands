<script setup lang="ts">
import type { Frame, SessionStatus } from './types'
defineProps<{ status: SessionStatus | null; comparison: Frame | null; hasFrame: boolean }>()
const emit = defineEmits<{ calibrate: [label: string]; compare: [] }>()
</script>

<template>
  <section class="panel">
    <h2>Calibrate and compare</h2>
    <p>Choose and apply your signals first. Hold a neutral posture, collect samples, then repeat with your deliberate movement. Sampling disables simulation and stores measurements only in session memory.</p>
    <div class="row"><button :disabled="!status || !!status.calibration.collecting" @click="emit('calibrate', 'neutral')">Collect neutral · 30 frames</button><button :disabled="!status || !!status.calibration.collecting" @click="emit('calibrate', 'deliberate')">Collect deliberate · 30 frames</button></div>
    <template v-if="status">
      <p v-if="status.calibration.collecting" role="status">Collecting {{ status.calibration.collecting }}: {{ status.calibration.remaining }} valid frames remain. Keep the required face/hand visible.</p>
      <div v-for="label in (['neutral', 'deliberate'] as const)" :key="label" class="sample">
        <b>{{ label }} · {{ status.calibration[label].count }} samples</b>
        <span>Face mean {{ status.calibration[label].face_mean?.toFixed(3) ?? 'unavailable' }}</span>
        <span>Hand mean {{ status.calibration[label].hand_mean?.toFixed(3) ?? 'unavailable' }}</span>
      </div>
      <p class="muted">A suggested range appears only when the observed deliberate minimum exceeds the neutral maximum by at least 0.1. This small sample does not establish reliability. Review the draft before applying.</p>
    </template>
    <button :disabled="!hasFrame" @click="emit('compare')">Freeze current observation for comparison</button>
    <template v-if="comparison">
      <h3>Frozen frame {{ comparison.frame_id }} · mapping {{ comparison.mapping_version }}</h3>
      <img class="snapshot" :src="comparison.preview" alt="Frozen comparison observation">
      <p>{{ comparison.note }}</p>
      <ul><li v-for="model in comparison.models" :key="model.name"><b>{{ model.name }}</b> — {{ model.available ? model.runtime : 'Not integrated; no result' }}</li></ul>
      <p>Face: {{ comparison.recognition.faces.length }} detected · {{ comparison.recognition.timing_ms.face.toFixed(1) }} ms.<br>Hand: {{ comparison.recognition.hands.length }} detected · {{ comparison.recognition.timing_ms.hand.toFixed(1) }} ms.</p>
      <p>Selected face score: {{ comparison.signals.face?.toFixed(3) ?? 'missing' }} · selected hand score: {{ comparison.signals.hand?.toFixed(3) ?? 'missing' }}.</p>
    </template>
    <p class="muted">Two recognition tasks are installed. ExecuTorch's synthetic smoke check is separate and is not a recognition model.</p>
  </section>
</template>

<style scoped>
.sample { display: flex; flex-wrap: wrap; gap: 12px; margin: 14px 0; font-size: .9rem; }
.snapshot { width: 180px; border-radius: 10px; }
</style>
