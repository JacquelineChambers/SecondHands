<script setup lang="ts">
import { computed } from 'vue'
import type { SessionStatus, Frame } from './types'
const props = defineProps<{ status: SessionStatus | null; frame: Frame | null }>()
const events = computed(() => [...(props.status?.events ?? [])].reverse())
</script>

<template>
  <section class="panel">
    <div class="row"><h2>Simulated action</h2><span class="badge">{{ status?.simulate ? 'Simulation enabled' : 'Observe · no actions' }}</span></div>
    <div class="lamp" :class="{ lit: status?.lamp }" role="img" :aria-label="status?.lamp ? 'Simulated lamp on' : 'Simulated lamp off'">{{ status?.lamp ? 'ON' : 'OFF' }}</div>
    <p role="status"><b>{{ status?.state.replaceAll('_', ' ') ?? 'stopped' }}</b></p>
    <p>Selected face: {{ frame?.signals.face?.toFixed(3) ?? 'missing' }} · hand: {{ frame?.signals.hand?.toFixed(3) ?? 'missing' }}.</p>
    <p class="muted">Missing input cancels pending evidence. A held command cannot repeat until release. No physical device is connected.</p>
    <h3>Event history · latest 100</h3>
    <ol class="events"><li v-for="event in events" :key="event.id"><b>{{ event.state.replaceAll('_', ' ') }}</b> · frame {{ event.frame_id }} / mapping {{ event.mapping_version }}<br><span>{{ event.reason }}</span></li></ol>
    <p v-if="!events.length" class="muted">State transitions will appear here.</p>
  </section>
</template>

<style scoped>
.lamp { display: grid; place-items: center; width: 80px; height: 80px; background: #1d293d; border: 2px solid #52617b; border-radius: 50%; margin: 20px 0; font-weight: 800; }
.lit { background: #ffe3a1; color: #423009; box-shadow: 0 0 28px #ffdf8255; border-color: #ffe3a1; }
.events { padding-left: 20px; max-height: 320px; overflow: auto; font-size: .87rem; }
.events li { margin: 12px 0; }
.badge { border: 1px solid #546781; border-radius: 30px; padding: 5px 10px; font-size: .8rem; }
</style>
