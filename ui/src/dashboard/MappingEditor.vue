<script setup lang="ts">
import { reactive, shallowRef } from 'vue'
import { defaultMapping, type Mapping, type Calibration } from './types'
const props = defineProps<{ connected: boolean; calibration: Calibration | null; activeVersion?: number }>()
const emit = defineEmits<{ apply: [mapping: Mapping, simulate: boolean]; cancel: [] }>()
const draft = reactive<Mapping>({ ...defaultMapping })
const simulate = shallowRef(false)
const gestures = ['Open_Palm', 'Closed_Fist', 'Pointing_Up', 'Thumb_Down', 'Thumb_Up', 'Victory', 'ILoveYou']
const faces = ['browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 'jawOpen', 'mouthSmileLeft', 'mouthSmileRight', 'eyeBlinkLeft', 'eyeBlinkRight', 'mouthPucker']
const times = [
  ['hold_ms', 'Hold duration'], ['release_ms', 'Neutral duration'], ['cooldown_ms', 'Cooldown'],
  ['timeout_ms', 'Confirmation timeout'], ['overlap_ms', 'Combined cue overlap'], ['max_gap_ms', 'Maximum frame gap'],
] as const
function applySuggestion(signal: 'face' | 'hand') {
  const suggestion = props.calibration?.[`${signal}_suggestion`]
  if (suggestion) Object.assign(draft, suggestion)
}
</script>

<template>
  <section class="panel">
    <h2>Compose a command</h2>
    <p class="muted">These defaults are editable experiment settings, not demonstration acceptance criteria. One active mapping controls a simulated lamp.</p>
    <form @submit.prevent="emit('apply', { ...draft }, simulate)">
      <div class="fields">
        <label>Mapping<select v-model="draft.mode"><option value="face">Face only</option><option value="hand">Hand only</option><option value="either">Either cue</option><option value="combined">Combined cues</option><option value="sequence">Hand hold → new face cue</option></select></label>
        <label>Face blendshape<input v-model="draft.face_signal" list="face-signals" maxlength="80" required><datalist id="face-signals"><option v-for="name in faces" :key="name" :value="name" /></datalist></label>
        <label>Hand gesture<select v-model="draft.hand_gesture"><option v-for="name in gestures" :key="name">{{ name }}</option></select></label>
        <label>Activation score<input v-model.number="draft.activate" type="number" min="0.01" max="1" step="0.01" required></label>
        <label>Release score<input v-model.number="draft.release" type="number" min="0" :max="draft.activate - .01" step="0.01" required></label>
        <label v-for="[key, label] in times" :key="key">{{ label }} (ms)<input v-model.number="draft[key]" type="number" :min="key === 'timeout_ms' || key === 'max_gap_ms' ? 1 : 0" max="30000" step="1" required></label>
      </div>
      <p class="muted">The activation and release score pair is shared by the selected face and hand cues. Face and hand calibration suggestions each replace this same pair.</p>
      <p class="muted">Combined requires both cues to stay active, with activation edges inside the overlap setting. Sequence requires a hand hold, then a new face activation before timeout. Release is required before another action.</p>
      <div class="row">
        <button type="button" :disabled="!calibration?.face_suggestion" @click="applySuggestion('face')">Use face calibration in draft</button>
        <button type="button" :disabled="!calibration?.hand_suggestion" @click="applySuggestion('hand')">Use hand calibration in draft</button>
      </div>
      <label class="check"><input v-model="simulate" type="checkbox"> Enable simulated commands when applying</label>
      <div class="row"><button class="primary" :disabled="!connected" type="submit">Apply experiment settings</button><button :disabled="!connected" type="button" @click="emit('cancel')">Cancel pending command</button></div>
      <p class="muted">Active mapping version: {{ activeVersion ?? 'none' }}. Applying clears calibration and pending evidence. Observe mode is the default for each new session.</p>
    </form>
  </section>
</template>

<style scoped>
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
.fields label { display: flex; flex-direction: column; gap: 5px; font-size: .88rem; }
.check { display: block; margin: 18px 0; }
</style>
