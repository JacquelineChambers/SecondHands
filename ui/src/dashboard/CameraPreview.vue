<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import type { Frame } from './types'
const props = defineProps<{ frame: Frame | null }>()
const overlays = shallowRef(true)
const facePoints = computed(() => props.frame?.recognition.faces.flatMap(face => face.landmarks) ?? [])
const handPoints = computed(() => props.frame?.recognition.hands.flatMap(hand => hand.landmarks) ?? [])
</script>

<template>
  <section class="panel">
    <div class="row"><h2>Camera · live signals</h2><label><input v-model="overlays" type="checkbox"> Landmarks</label></div>
    <svg v-if="frame" :key="`${frame.session_id}-${frame.frame_id}`" class="preview"
      :viewBox="`0 0 ${frame.recognition.image.width} ${frame.recognition.image.height}`"
      role="img" aria-label="Camera frame with matching face and hand landmarks">
      <image :href="frame.preview" width="100%" height="100%" />
      <g v-if="overlays">
        <circle v-for="(point, i) in facePoints" :key="`f${i}`" :cx="point.x * frame.recognition.image.width"
          :cy="point.y * frame.recognition.image.height" r="1.5" fill="#7affd4" />
        <circle v-for="(point, i) in handPoints" :key="`h${i}`" :cx="point.x * frame.recognition.image.width"
          :cy="point.y * frame.recognition.image.height" r="4" fill="#ffb85c" />
      </g>
    </svg>
    <div v-else class="placeholder">Start the camera to inspect facial movements and static hand gestures.</div>
    <p v-if="frame" class="muted">Frame {{ frame.frame_id }} · mapping {{ frame.mapping_version }} · unmirrored view</p>
    <p class="muted">Camera access belongs to the Python process on this computer. Frames remain in memory.</p>
  </section>
</template>

<style scoped>
.preview { display: block; width: 100%; max-height: 520px; background: #08101b; border-radius: 12px; }
.placeholder { min-height: 260px; display: grid; place-items: center; text-align: center; padding: 24px; border: 1px dashed #536078; border-radius: 12px; color: #b1bfd1; }
</style>
