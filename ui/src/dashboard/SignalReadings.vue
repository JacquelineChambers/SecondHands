<script setup lang="ts">
import { computed } from 'vue'
import type { Frame } from './types'
const props = defineProps<{ frame: Frame | null; loadMs: number | null }>()
const shapes = computed(() => Object.entries(props.frame?.recognition.faces[0]?.blendshapes ?? {})
  .sort((a, b) => b[1] - a[1]))
</script>

<template>
  <section class="panel">
    <h2>Recognition measurements</h2>
    <p>MediaPipe CPU · Face Landmarker + Gesture Recognizer</p>
    <template v-if="frame">
      <div class="metrics"><span>Face <b>{{ frame.recognition.timing_ms.face.toFixed(1) }} ms</b></span>
        <span>Hand <b>{{ frame.recognition.timing_ms.hand.toFixed(1) }} ms</b></span>
        <span>Frame work <b>{{ frame.processing_ms.toFixed(1) }} ms</b></span></div>
      <p class="muted">Camera read {{ frame.capture_ms.toFixed(1) }} ms. Frame work includes resizing, inference and JPEG encoding; excludes network and display. Capture timestamps use the server's monotonic clock.</p>
      <h3>Hands · {{ frame.recognition.hands.length }}</h3>
      <p v-if="!frame.recognition.hands.length" class="muted">No hand detected.</p>
      <p v-if="frame.recognition.hands.length > 1" class="warning">More than one hand detected: hand commands are suspended. Use one participant and one hand.</p>
      <div v-for="(hand, i) in frame.recognition.hands" :key="i" class="reading">
        <b>{{ hand.handedness[0]?.label ?? 'Unknown side' }}</b>
        <span v-for="gesture in hand.gestures" :key="gesture.label">{{ gesture.label }} · {{ gesture.score.toFixed(3) }}</span>
      </div>
      <h3>Facial blendshapes · {{ shapes.length }}</h3>
      <p v-if="!shapes.length" class="muted">No face detected.</p>
      <div class="shapes">
        <div v-for="[name, score] in shapes" :key="name" class="shape">
          <label :for="`shape-${name}`">{{ name }}</label><span>{{ score.toFixed(3) }}</span>
          <meter :id="`shape-${name}`" :value="score" min="0" max="1" />
        </div>
      </div>
    </template>
    <p v-else class="muted">Measurements appear when a frame arrives.</p>
    <p v-if="loadMs !== null" class="muted">Both models loaded in {{ loadMs.toFixed(0) }} ms for this session.</p>
    <p class="muted">Scores measure visible features. They do not establish intent or emotion.</p>
  </section>
</template>

<style scoped>
.shapes { max-height: 290px; overflow: auto; }
.shape { display: grid; grid-template-columns: 1fr auto; gap: 3px 10px; margin: 8px 0; font-size: .85rem; }
.shape meter { width: 100%; grid-column: 1 / -1; height: 7px; }
.metrics { display: flex; flex-wrap: wrap; gap: 12px; }
.metrics span { display: grid; }
.reading { display: flex; gap: 12px; margin: 10px 0; }
</style>
